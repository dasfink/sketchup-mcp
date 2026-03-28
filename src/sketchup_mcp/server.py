from mcp.server.fastmcp import FastMCP, Context
import socket
import json
import time
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List

from sketchup_mcp.ruby_templates import (
    boolean_subtract_ruby, make_box_ruby, safe_cut_dado_ruby,
    safe_drill_hole_ruby, verify_bounds_ruby, take_screenshot_ruby,
    create_scene_ruby, verify_scenes_ruby, generate_cutlist_ruby,
    exploded_view_ruby,
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SketchupMCPServer")

# Define version directly to avoid pkg_resources dependency
__version__ = "0.2.0"
logger.info(f"SketchupMCP Server version {__version__} starting up")

@dataclass
class SketchupConnection:
    host: str
    port: int
    sock: socket.socket = None

    def connect(self) -> bool:
        """Create a fresh connection to the Sketchup extension socket server.

        The SketchUp Ruby extension closes the socket after each request,
        so we always create a new connection per request.
        """
        self.disconnect()
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Sketchup at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Sketchup: {str(e)}")
            self.sock = None
            return False

    def disconnect(self):
        """Disconnect from the Sketchup extension"""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            finally:
                self.sock = None

    def receive_full_response(self, sock, timeout=30.0, buffer_size=8192):
        """Receive the complete JSON response, potentially in multiple chunks"""
        chunks = []
        sock.settimeout(timeout)

        while True:
            try:
                chunk = sock.recv(buffer_size)
                if not chunk:
                    if not chunks:
                        raise ConnectionError("Connection closed before receiving any data")
                    break

                chunks.append(chunk)

                # Check if we have complete JSON
                data = b''.join(chunks)
                try:
                    json.loads(data.decode('utf-8'))
                    logger.info(f"Received complete response ({len(data)} bytes)")
                    return data
                except json.JSONDecodeError:
                    continue
            except socket.timeout:
                if chunks:
                    break
                raise ConnectionError("Timed out waiting for response from Sketchup")
            except (ConnectionError, BrokenPipeError, ConnectionResetError, OSError) as e:
                raise ConnectionError(f"Socket error during receive: {e}")

        if chunks:
            data = b''.join(chunks)
            try:
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                raise ConnectionError("Incomplete JSON response received")
        raise ConnectionError("No data received")

    def send_command(self, method: str, params: Dict[str, Any] = None, request_id: Any = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to Sketchup and return the response.

        Creates a fresh TCP connection for each request (the Ruby extension
        closes the connection after responding). Retries on any connection error.
        """
        # Build the JSON-RPC request
        if method == "tools/call" and params and "name" in params and "arguments" in params:
            request = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": request_id
            }
        else:
            request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": method,
                    "arguments": params or {}
                },
                "id": request_id
            }

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                # Fresh connection for each attempt
                if not self.connect():
                    raise ConnectionError("Cannot connect to Sketchup")

                request_bytes = json.dumps(request).encode('utf-8') + b'\n'
                logger.info(f"Attempt {attempt+1}: sending {request.get('params', {}).get('name', method)}")

                self.sock.sendall(request_bytes)

                # Use longer timeout for geometry operations (eval_ruby, create_component)
                tool_name = request.get("params", {}).get("name", "")
                timeout = 60.0 if tool_name in ("eval_ruby", "create_component", "create_mortise_tenon", "create_dovetail", "create_finger_joint") else 30.0

                response_data = self.receive_full_response(self.sock, timeout=timeout)
                response = json.loads(response_data.decode('utf-8'))

                if "error" in response:
                    error_msg = response["error"].get("message", "Unknown error")
                    raise Exception(f"Sketchup error: {error_msg}")

                return response.get("result", {})

            except (ConnectionError, BrokenPipeError, ConnectionResetError,
                    OSError, socket.timeout, socket.error) as e:
                last_error = e
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed (connection): {e}")
                self.disconnect()
                if attempt < max_retries - 1:
                    time.sleep(0.2 * (attempt + 1))

            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed (bad JSON): {e}")
                self.disconnect()
                if attempt < max_retries - 1:
                    time.sleep(0.2 * (attempt + 1))

            except Exception as e:
                # For non-connection errors (e.g. Sketchup returned an error), don't retry
                error_str = str(e)
                if "Sketchup error:" in error_str:
                    raise
                # Anything else might be a transient issue, retry
                last_error = e
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {e}")
                self.disconnect()
                if attempt < max_retries - 1:
                    time.sleep(0.2 * (attempt + 1))

        raise Exception(f"Failed after {max_retries} attempts: {last_error}")


def get_sketchup_connection():
    """Get a SketchupConnection instance.

    No caching — each send_command() creates its own fresh TCP connection,
    matching the Ruby extension's one-shot-per-connection design.
    """
    return SketchupConnection(host="localhost", port=9876)

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    try:
        logger.info("SketchupMCP server starting up")
        # Verify SketchUp is reachable on startup
        conn = get_sketchup_connection()
        if conn.connect():
            logger.info("Successfully verified Sketchup is reachable on startup")
            conn.disconnect()
        else:
            logger.warning("Could not reach Sketchup on startup — make sure the extension is running")
        yield {}
    finally:
        logger.info("SketchupMCP server shut down")

# Create MCP server with lifespan support
mcp = FastMCP(
    "SketchupMCP",
    instructions="Sketchup integration through the Model Context Protocol",
    lifespan=server_lifespan
)

# Tool endpoints
@mcp.tool()
def create_component(
    ctx: Context,
    type: str = "cube",
    position: List[float] = None,
    dimensions: List[float] = None
) -> str:
    """Create a new component in Sketchup"""
    try:
        logger.info(f"create_component called with type={type}, position={position}, dimensions={dimensions}, request_id={ctx.request_id}")
        
        sketchup = get_sketchup_connection()
        
        params = {
            "name": "create_component",
            "arguments": {
                "type": type,
                "position": position or [0,0,0],
                "dimensions": dimensions or [1,1,1]
            }
        }
        
        logger.info(f"Calling send_command with method='tools/call', params={params}, request_id={ctx.request_id}")
        
        result = sketchup.send_command(
            method="tools/call",
            params=params,
            request_id=ctx.request_id
        )
        
        logger.info(f"create_component result: {result}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in create_component: {str(e)}")
        return f"Error creating component: {str(e)}"

@mcp.tool()
def delete_component(
    ctx: Context,
    id: str
) -> str:
    """Delete a component by ID"""
    try:
        sketchup = get_sketchup_connection()
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "delete_component",
                "arguments": {"id": id}
            },
            request_id=ctx.request_id
        )
        return json.dumps(result)
    except Exception as e:
        return f"Error deleting component: {str(e)}"

@mcp.tool()
def transform_component(
    ctx: Context,
    id: str,
    position: List[float] = None,
    rotation: List[float] = None,
    scale: List[float] = None
) -> str:
    """Transform a component's position, rotation, or scale"""
    try:
        sketchup = get_sketchup_connection()
        arguments = {"id": id}
        if position is not None:
            arguments["position"] = position
        if rotation is not None:
            arguments["rotation"] = rotation
        if scale is not None:
            arguments["scale"] = scale
            
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "transform_component",
                "arguments": arguments
            },
            request_id=ctx.request_id
        )
        return json.dumps(result)
    except Exception as e:
        return f"Error transforming component: {str(e)}"

@mcp.tool()
def get_selection(ctx: Context) -> str:
    """Get currently selected components"""
    try:
        sketchup = get_sketchup_connection()
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "get_selection",
                "arguments": {}
            },
            request_id=ctx.request_id
        )
        return json.dumps(result)
    except Exception as e:
        return f"Error getting selection: {str(e)}"

@mcp.tool()
def set_material(
    ctx: Context,
    id: str,
    material: str
) -> str:
    """Set material for a component"""
    try:
        sketchup = get_sketchup_connection()
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "set_material",
                "arguments": {
                    "id": id,
                    "material": material
                }
            },
            request_id=ctx.request_id
        )
        return json.dumps(result)
    except Exception as e:
        return f"Error setting material: {str(e)}"

@mcp.tool()
def export_scene(
    ctx: Context,
    format: str = "skp"
) -> str:
    """Export the current scene"""
    try:
        sketchup = get_sketchup_connection()
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "export",
                "arguments": {
                    "format": format
                }
            },
            request_id=ctx.request_id
        )
        return json.dumps(result)
    except Exception as e:
        return f"Error exporting scene: {str(e)}"

@mcp.tool()
def create_mortise_tenon(
    ctx: Context,
    mortise_id: str,
    tenon_id: str,
    width: float = 1.0,
    height: float = 1.0,
    depth: float = 1.0,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    offset_z: float = 0.0
) -> str:
    """Create a mortise and tenon joint between two components"""
    try:
        logger.info(f"create_mortise_tenon called with mortise_id={mortise_id}, tenon_id={tenon_id}, width={width}, height={height}, depth={depth}, offsets=({offset_x}, {offset_y}, {offset_z})")
        
        sketchup = get_sketchup_connection()
        
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "create_mortise_tenon",
                "arguments": {
                    "mortise_id": mortise_id,
                    "tenon_id": tenon_id,
                    "width": width,
                    "height": height,
                    "depth": depth,
                    "offset_x": offset_x,
                    "offset_y": offset_y,
                    "offset_z": offset_z
                }
            },
            request_id=ctx.request_id
        )
        
        logger.info(f"create_mortise_tenon result: {result}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in create_mortise_tenon: {str(e)}")
        return f"Error creating mortise and tenon joint: {str(e)}"

@mcp.tool()
def create_dovetail(
    ctx: Context,
    tail_id: str,
    pin_id: str,
    width: float = 1.0,
    height: float = 1.0,
    depth: float = 1.0,
    angle: float = 15.0,
    num_tails: int = 3,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    offset_z: float = 0.0
) -> str:
    """Create a dovetail joint between two components"""
    try:
        logger.info(f"create_dovetail called with tail_id={tail_id}, pin_id={pin_id}, width={width}, height={height}, depth={depth}, angle={angle}, num_tails={num_tails}")
        
        sketchup = get_sketchup_connection()
        
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "create_dovetail",
                "arguments": {
                    "tail_id": tail_id,
                    "pin_id": pin_id,
                    "width": width,
                    "height": height,
                    "depth": depth,
                    "angle": angle,
                    "num_tails": num_tails,
                    "offset_x": offset_x,
                    "offset_y": offset_y,
                    "offset_z": offset_z
                }
            },
            request_id=ctx.request_id
        )
        
        logger.info(f"create_dovetail result: {result}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in create_dovetail: {str(e)}")
        return f"Error creating dovetail joint: {str(e)}"

@mcp.tool()
def create_finger_joint(
    ctx: Context,
    board1_id: str,
    board2_id: str,
    width: float = 1.0,
    height: float = 1.0,
    depth: float = 1.0,
    num_fingers: int = 5,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    offset_z: float = 0.0
) -> str:
    """Create a finger joint (box joint) between two components"""
    try:
        logger.info(f"create_finger_joint called with board1_id={board1_id}, board2_id={board2_id}, width={width}, height={height}, depth={depth}, num_fingers={num_fingers}")
        
        sketchup = get_sketchup_connection()
        
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "create_finger_joint",
                "arguments": {
                    "board1_id": board1_id,
                    "board2_id": board2_id,
                    "width": width,
                    "height": height,
                    "depth": depth,
                    "num_fingers": num_fingers,
                    "offset_x": offset_x,
                    "offset_y": offset_y,
                    "offset_z": offset_z
                }
            },
            request_id=ctx.request_id
        )
        
        logger.info(f"create_finger_joint result: {result}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in create_finger_joint: {str(e)}")
        return f"Error creating finger joint: {str(e)}"

@mcp.tool()
def eval_ruby(
    ctx: Context,
    code: str
) -> str:
    """Evaluate arbitrary Ruby code in Sketchup"""
    try:
        logger.info(f"eval_ruby called with code length: {len(code)}")
        
        sketchup = get_sketchup_connection()
        
        result = sketchup.send_command(
            method="tools/call",
            params={
                "name": "eval_ruby",
                "arguments": {
                    "code": code
                }
            },
            request_id=ctx.request_id
        )
        
        logger.info(f"eval_ruby result: {result}")
        
        # Format the response to include the result
        response = {
            "success": True,
            "result": result.get("content", [{"text": "Success"}])[0].get("text", "Success") if isinstance(result.get("content"), list) and len(result.get("content", [])) > 0 else "Success"
        }
        
        return json.dumps(response)
    except Exception as e:
        logger.error(f"Error in eval_ruby: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

# ── Furniture Design Tools ──────────────────────────────────────────

@mcp.tool()
def boolean_subtract(
    ctx: Context,
    target: str,
    cutter_type: str,
    position: List[float],
    dimensions: List[float],
    axis: List[float] = None
) -> str:
    """Boolean subtract a shape from a component using SketchUp Pro Solid Tools.
    Deterministic — no pushpull inversion possible.
    target: component name. cutter_type: 'box' or 'cylinder'.
    position: [x,y,z] in component-local coords.
    dimensions: box=[w,d,h], cylinder=[length, radius, 0].
    axis: cylinder direction [nx,ny,nz], default [1,0,0]."""
    try:
        code = boolean_subtract_ruby(target, cutter_type, position, dimensions, axis)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def create_component_box(
    ctx: Context,
    name: str,
    position: List[float],
    dimensions: List[float],
    material: str = "Pine",
    tag: str = "Frame",
    species: str = "Pine",
    nominal_size: str = "",
    finish: str = ""
) -> str:
    """Create a furniture component as a box using 6-face construction (never pushpull).
    Guaranteed correct geometry. Sets material, tag, and woodworking attributes."""
    try:
        attrs = {}
        if species: attrs["species"] = species
        if nominal_size: attrs["nominal_size"] = nominal_size
        if finish: attrs["finish"] = finish
        code = make_box_ruby(name, position, dimensions, material, tag, attrs)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def safe_cut_dado(
    ctx: Context,
    component_name: str,
    face: str,
    z_start: float,
    z_end: float,
    depth: float = 1.5
) -> str:
    """Cut a dado into a component via boolean subtract. No pushpull inversion possible.
    face: 'x+', 'x-', 'y+', 'y-' — which face to cut into."""
    try:
        code = safe_cut_dado_ruby(component_name, face, z_start, z_end, depth)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def safe_drill_hole(
    ctx: Context,
    component_name: str,
    center: List[float],
    normal: List[float],
    radius: float = 0.197,
    depth: float = 3.5
) -> str:
    """Drill a hole via boolean subtract. No add_face nil issues, no inversion.
    Default radius 0.197\" = M8 (10mm) bolt hole."""
    try:
        code = safe_drill_hole_ruby(component_name, center, normal, radius, depth)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def verify_bounds(
    ctx: Context,
    expected: str
) -> str:
    """Verify component bounds match expected dimensions. Pass expected as JSON string:
    {"PostBC": {"x": [0, 3.5], "y": [0, 3.5], "z": [0, 71.25]}}"""
    try:
        expected_dict = json.loads(expected)
        code = verify_bounds_ruby(expected_dict)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def take_screenshot(
    ctx: Context,
    scene_name: str = "",
    width: int = 1920,
    height: int = 1080,
    hide_tags: str = ""
) -> str:
    """Take a screenshot, optionally activating a scene first.
    Returns the file path to the PNG. hide_tags: comma-separated tag names to hide."""
    try:
        hide_list = [t.strip() for t in hide_tags.split(",") if t.strip()] if hide_tags else None
        code = take_screenshot_ruby(scene_name or None, width, height, hide_list)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def create_scene(
    ctx: Context,
    name: str,
    eye: List[float],
    target: List[float],
    up: List[float] = None,
    perspective: bool = True,
    ortho_height: float = 90,
    visible_tags: str = "",
    section_point: List[float] = None,
    section_normal: List[float] = None
) -> str:
    """Create a SketchUp scene with camera, layer visibility, and optional section plane.
    Sets all state BEFORE adding the page. visible_tags: comma-separated tag names."""
    try:
        up_vec = up or [0, 0, 1]
        vis_list = [t.strip() for t in visible_tags.split(",") if t.strip()] if visible_tags else None
        code = create_scene_ruby(name, eye, target, up_vec, perspective, ortho_height,
                                  vis_list, section_point, section_normal)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def verify_scenes(ctx: Context) -> str:
    """Cycle through all scenes and report camera type + visible layers for each.
    Catches the critical bug where tags bleed between scenes."""
    try:
        code = verify_scenes_ruby()
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def generate_cutlist(
    ctx: Context,
    auto_orient: bool = True,
    part_folding: bool = True
) -> str:
    """Generate a cut list using OpenCutList. Returns structured JSON with
    part names, quantities, and dimensions."""
    try:
        code = generate_cutlist_ruby(auto_orient, part_folding)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def create_exploded_view(
    ctx: Context,
    offsets: str,
    tag_name: str = "Exploded"
) -> str:
    """Create exploded view by duplicating components at Z offsets onto a separate tag.
    offsets: JSON string mapping tag names to Z offsets, e.g. {"Railing": 25, "Slats": 18}"""
    try:
        offsets_dict = json.loads(offsets)
        code = exploded_view_ruby(offsets_dict, tag_name)
        sketchup = get_sketchup_connection()
        result = sketchup.send_command("tools/call",
            {"name": "eval_ruby", "arguments": {"code": code}},
            request_id=ctx.request_id)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def main():
    mcp.run()

if __name__ == "__main__":
    main()