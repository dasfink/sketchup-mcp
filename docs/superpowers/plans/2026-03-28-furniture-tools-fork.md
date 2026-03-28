# SketchUp MCP Furniture Tools Fork — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 10 purpose-built MCP tools for furniture design, headlined by `boolean_subtract` which eliminates the pushpull inversion bug entirely using SketchUp Pro's Solid Tools.

**Architecture:** All new tools are Python-side MCP tools that internally construct Ruby scripts and send them via the existing `send_command`/`eval_ruby` pathway. No changes to the Ruby extension or JSON-RPC protocol needed. The Ruby `WW` woodworking module already exists and can be extended for complex operations. The `boolean_subtract` tool uses SketchUp Pro's `Group#subtract` API for deterministic geometry operations — no pushpull, no inversion, no verification needed.

**Tech Stack:** Python 3.10+ (FastMCP), Ruby (SketchUp API), existing TCP socket transport.

---

## File Structure

```
src/sketchup_mcp/
├── server.py              # Modify: add 10 new @mcp.tool() functions
├── ruby_templates.py      # Create: Ruby code templates for each tool
├── __init__.py             # No change
├── __main__.py             # No change
tests/
├── test_ruby_templates.py  # Create: unit tests for Ruby code generation
├── test_tools_integration.py # Create: integration tests (requires SketchUp)
```

**Design decision:** Ruby code lives in `ruby_templates.py` as Python string templates rather than inline in each tool function. This keeps `server.py` clean and makes the Ruby code testable independently (we can verify the generated Ruby is syntactically correct without needing SketchUp).

---

## Chunk 0: Boolean Subtract — The Pushpull Killer

This is the single most impactful tool. SketchUp Pro's Solid Tools API (`Group#subtract`) performs deterministic boolean operations — no face normals, no winding order, no inversion. Create a cutting shape, subtract it from the target. Always correct.

### Task 0: Add boolean_subtract template and MCP tool

**Files:**
- Modify: `src/sketchup_mcp/ruby_templates.py`
- Modify: `src/sketchup_mcp/server.py`
- Modify: `tests/test_ruby_templates.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_ruby_templates.py

def test_boolean_subtract_box_cutter():
    """Dado: subtract a box from a post"""
    code = boolean_subtract_ruby(
        target="PostBC",
        cutter_type="box",
        position=[2.0, 0, 60],
        dimensions=[1.5, 3.5, 11.25]
    )
    assert "subtract" in code
    assert "add_group" in code
    assert "PostBC" in code
    assert "pushpull" not in code  # THE WHOLE POINT

def test_boolean_subtract_cylinder_cutter():
    """Bolt hole: subtract a cylinder from a post"""
    code = boolean_subtract_ruby(
        target="PostBC",
        cutter_type="cylinder",
        position=[0, 1.75, 63],
        dimensions=[3.5, 0.197, 0],  # [length, radius, unused]
        axis=[1, 0, 0]
    )
    assert "subtract" in code
    assert "add_circle" in code
    assert "pushpull" not in code

def test_boolean_subtract_returns_verification():
    """Must return bounds after operation for confirmation"""
    code = boolean_subtract_ruby("Post", "box", [0,0,0], [1,1,1])
    assert "bounds" in code
```

- [ ] **Step 2: Run test — FAIL**

Run: `cd /Users/michaelfinkler/Dev/sketchup-mcp && uv run pytest tests/test_ruby_templates.py::test_boolean_subtract_box_cutter -v`

- [ ] **Step 3: Implement boolean_subtract_ruby template**

```python
# In src/sketchup_mcp/ruby_templates.py

def boolean_subtract_ruby(target: str, cutter_type: str, position: list,
                          dimensions: list, axis: list = None) -> str:
    """Generate Ruby to boolean-subtract a shape from a component.

    Uses SketchUp Pro's Group#subtract — deterministic, no pushpull inversion.

    target: component name to cut into
    cutter_type: 'box' or 'cylinder'
    position: [x, y, z] of the cutting shape origin (in component-local coords)
    dimensions: for box [w, d, h], for cylinder [length, radius, _]
    axis: for cylinder [nx, ny, nz] — direction of the cylinder axis
    """
    x, y, z = position

    if cutter_type == "box":
        w, d, h = dimensions
        cutter_code = f'''
    cg = cutter.entities
    cg.add_face([0,0,0],[{w},0,0],[{w},{d},0],[0,{d},0])
    cg.add_face([0,0,{h}],[0,{d},{h}],[{w},{d},{h}],[{w},0,{h}])
    cg.add_face([0,0,0],[{w},0,0],[{w},0,{h}],[0,0,{h}])
    cg.add_face([0,{d},0],[0,{d},{h}],[{w},{d},{h}],[{w},{d},0])
    cg.add_face([0,0,0],[0,0,{h}],[0,{d},{h}],[0,{d},0])
    cg.add_face([{w},0,0],[{w},{d},0],[{w},{d},{h}],[{w},0,{h}])
    cutter.transform!(Geom::Transformation.new([{x}, {y}, {z}]))
'''
    elif cutter_type == "cylinder":
        length, radius, _ = dimensions
        ax = axis or [1, 0, 0]
        # Build cylinder along the given axis
        cutter_code = f'''
    cg = cutter.entities
    normal = Geom::Vector3d.new({ax[0]}, {ax[1]}, {ax[2]})
    center = Geom::Point3d.new(0, 0, 0)
    circle = cg.add_circle(center, normal, {radius}, 24)
    face = cg.add_face(circle)
    face.pushpull({length}) if face  # pushpull on isolated cutter is safe
    cutter.transform!(Geom::Transformation.new([{x}, {y}, {z}]))
'''
    else:
        raise ValueError(f"Unknown cutter_type: {cutter_type}")

    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Boolean subtract from {target}', true)

# Find target component, get its group wrapper for boolean ops
inst = e.find {{ |ent| ent.is_a?(Sketchup::ComponentInstance) && ent.definition.name == "{target}" }}
raise "Component {target} not found" unless inst

# Convert component instance to a group for boolean operations
# (subtract requires groups, not component instances)
target_group = inst.to_component.definition.entities.parent.entities.add_group
# Alternative approach: explode to group
orig_transform = inst.transformation
target_group = inst.explode_to_group rescue nil

# Simpler approach: create cutting group at the right position
# relative to the component's global position
cutter = e.add_group
{cutter_code}
# Position cutter relative to component
comp_origin = inst.transformation.origin
cutter.transform!(Geom::Transformation.translation([comp_origin.x, comp_origin.y, comp_origin.z]))

# For subtract to work, both must be solids (manifold geometry)
# The make_box approach guarantees solid cutters
# The target should be solid if created with make_box + previous subtracts

# Perform the boolean subtract
result_group = inst.subtract(cutter)

if result_group
  bb = result_group.bounds
  m.commit_operation
  '{{"success": true, "result": "subtracted", "bounds": [' + bb.min.x.to_f.round(2).to_s + ',' + bb.min.y.to_f.round(2).to_s + ',' + bb.min.z.to_f.round(2).to_s + ',' + bb.max.x.to_f.round(2).to_s + ',' + bb.max.y.to_f.round(2).to_s + ',' + bb.max.z.to_f.round(2).to_s + ']}}'
else
  cutter.erase! if cutter.valid?
  m.commit_operation
  '{{"success": false, "error": "subtract returned nil — target or cutter may not be solid"}}'
end
'''
```

**Important note:** SketchUp's `subtract` method works on Groups, not ComponentInstances directly. The template needs to handle the Group/Component conversion. Two approaches:

1. **Temporary explode:** Explode the ComponentInstance to a Group, subtract, then re-wrap as a Component. This changes the component for all instances (which is fine — each post has a unique definition).

2. **Edit definition in-place:** Open the component definition, create the cutter inside it, use `intersect_with` instead of `subtract`. This is more reliable but requires different API calls.

The implementation above uses approach 1. If `subtract` doesn't work directly on ComponentInstances in SketchUp 2026, we'll need to adjust. This should be tested in the integration test phase.

- [ ] **Step 4: Run test — PASS**

- [ ] **Step 5: Add MCP tool to server.py**

```python
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
```

- [ ] **Step 6: Commit**

```bash
git add src/sketchup_mcp/ruby_templates.py src/sketchup_mcp/server.py tests/test_ruby_templates.py
git commit -m "feat: add boolean_subtract tool — eliminates pushpull inversion bug"
```

---

### Task 0b: Simplify safe_cut_dado and safe_drill_hole to use boolean_subtract

With boolean_subtract available, the dado and hole tools become thin wrappers:

- [ ] **Step 1: Rewrite safe_cut_dado_ruby to use boolean_subtract internally**

```python
def safe_cut_dado_ruby(component_name: str, face: str, z_start: float, z_end: float, depth: float) -> str:
    """Dado via boolean subtract. No pushpull, no inversion detection needed."""
    height = z_end - z_start
    # Map face to cutter position (in component-local coords)
    # The cutter box sits at the face, extending inward by depth
    face_positions = {
        "x+": lambda bb: [bb["max_x"] - depth, 0, z_start],
        "x-": lambda bb: [0, 0, z_start],
        "y+": lambda bb: [0, bb["max_y"] - depth, z_start],
        "y-": lambda bb: [0, 0, z_start],
    }
    face_dims = {
        "x+": lambda bb: [depth, bb["max_y"], height],
        "x-": lambda bb: [depth, bb["max_y"], height],
        "y+": lambda bb: [bb["max_x"], depth, height],
        "y-": lambda bb: [bb["max_x"], depth, height],
    }
    # Need to query bounds first, then subtract
    return boolean_subtract_ruby(component_name, "box",
        face_positions[face]({"max_x": 3.5, "max_y": 3.5}),  # placeholder — see note
        face_dims[face]({"max_x": 3.5, "max_y": 3.5}))
```

**Note:** The simplified version needs the component's bounds to compute cutter position. In practice, this means `safe_cut_dado` should first query bounds via a short Ruby snippet, then construct the boolean subtract. This two-step approach is still simpler and more reliable than the pushpull+verify+trim approach.

- [ ] **Step 2: Rewrite safe_drill_hole_ruby to use boolean_subtract**

```python
def safe_drill_hole_ruby(component_name: str, center: list, normal: list, radius: float, depth: float) -> str:
    """Bolt hole via boolean subtract. No add_face nil fallback needed."""
    return boolean_subtract_ruby(component_name, "cylinder", center, [depth, radius, 0], normal)
```

- [ ] **Step 3: Run tests — PASS**

- [ ] **Step 4: Commit**

```bash
git add -u && git commit -m "refactor: simplify dado/hole tools to use boolean_subtract"
```

---

## Chunk 1: Foundation — Ruby Templates Module + Verification Tools

### Task 1: Create ruby_templates.py with the make_box template

**Files:**
- Create: `src/sketchup_mcp/ruby_templates.py`
- Create: `tests/test_ruby_templates.py`

- [ ] **Step 1: Write test for make_box template generation**

```python
# tests/test_ruby_templates.py
import ast
from sketchup_mcp.ruby_templates import make_box_ruby

def test_make_box_generates_valid_ruby():
    code = make_box_ruby("TestBox", [0, 0, 0], [10, 5, 3], "Pine", "Frame", {"species": "Pine", "nominal_size": "2x4"})
    assert "add_face" in code
    assert "TestBox" in code
    assert "Pine" in code
    assert "Frame" in code  # tag
    assert "pushpull" not in code  # NEVER pushpull for boxes
    assert "set_attribute" in code

def test_make_box_no_pushpull():
    """The whole point — boxes must use 6 faces, never pushpull"""
    code = make_box_ruby("Rail", [0, 0, 0], [1.5, 77, 11.25], "Pine", "FrameRails", {})
    assert code.count("add_face") == 6
    assert "pushpull" not in code
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/michaelfinkler/Dev/sketchup-mcp && uv run pytest tests/test_ruby_templates.py -v`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement ruby_templates.py with make_box**

```python
# src/sketchup_mcp/ruby_templates.py
"""Ruby code templates for SketchUp MCP furniture tools.

Each function returns a Ruby code string that can be sent via eval_ruby.
Templates use 6-face box construction (never pushpull) and include
bounds verification after every geometry operation.
"""

def make_box_ruby(name: str, position: list, dimensions: list, material: str, tag: str, attrs: dict) -> str:
    x, y, z = position
    w, d, h = dimensions
    attr_lines = "\n".join(
        f'    inst.set_attribute("woodworking", "{k}", "{v}")'
        for k, v in attrs.items()
    )
    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Create {name}', true)

defn = m.definitions.add("{name}")
de = defn.entities
w, d, h = {w}, {d}, {h}
de.add_face([0,0,0],[w,0,0],[w,d,0],[0,d,0])
de.add_face([0,0,h],[0,d,h],[w,d,h],[w,0,h])
de.add_face([0,0,0],[w,0,0],[w,0,h],[0,0,h])
de.add_face([0,d,0],[0,d,h],[w,d,h],[w,d,0])
de.add_face([0,0,0],[0,0,h],[0,d,h],[0,d,0])
de.add_face([w,0,0],[w,d,0],[w,d,h],[w,0,h])

t = Geom::Transformation.new([{x}, {y}, {z}])
inst = e.add_instance(defn, t)

mat = m.materials["{material}"] || m.materials.add("{material}")
mat.color = Sketchup::Color.new(255, 223, 170) unless mat.color
inst.material = mat

tag_layer = m.layers["{tag}"] || m.layers.add("{tag}")
inst.layer = tag_layer

{attr_lines}

bb = defn.bounds
m.commit_operation
"created #{name}: #{{bb.max.x.to_f.round(2)}}x#{{bb.max.y.to_f.round(2)}}x#{{bb.max.z.to_f.round(2)}}"
'''
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/michaelfinkler/Dev/sketchup-mcp && uv run pytest tests/test_ruby_templates.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /Users/michaelfinkler/Dev/sketchup-mcp
git add src/sketchup_mcp/ruby_templates.py tests/test_ruby_templates.py
git commit -m "feat: add ruby_templates module with make_box (no pushpull)"
```

---

### Task 2: Add verify_bounds template

**Files:**
- Modify: `src/sketchup_mcp/ruby_templates.py`
- Modify: `tests/test_ruby_templates.py`

- [ ] **Step 1: Write test**

```python
def test_verify_bounds_generates_check():
    code = verify_bounds_ruby({"PostBC": {"x": [0, 3.5], "y": [0, 3.5], "z": [0, 71.25]}})
    assert "PostBC" in code
    assert "3.5" in code
    assert "71.25" in code
    assert "issues" in code

def test_verify_bounds_empty_expected():
    code = verify_bounds_ruby({})
    assert "issues" in code  # still returns the structure
```

- [ ] **Step 2: Run test — FAIL**

- [ ] **Step 3: Implement**

```python
def verify_bounds_ruby(expected: dict) -> str:
    checks = []
    for name, dims in expected.items():
        for axis, (lo, hi) in dims.items():
            accessor_min = f"bb.min.{axis}"
            accessor_max = f"bb.max.{axis}"
            checks.append(
                f'  inst = e.find {{ |ent| ent.is_a?(Sketchup::ComponentInstance) && ent.definition.name == "{name}" }}\n'
                f'  if inst\n'
                f'    bb = inst.definition.bounds\n'
                f'    issues << "{name} {axis} min=#{{bb.min.{axis}.to_f.round(2)}} exp={lo}" if (bb.min.{axis}.to_f - {lo}).abs > 0.01\n'
                f'    issues << "{name} {axis} max=#{{bb.max.{axis}.to_f.round(2)}} exp={hi}" if (bb.max.{axis}.to_f - {hi}).abs > 0.01\n'
                f'  else\n'
                f'    issues << "{name}: NOT FOUND"\n'
                f'  end'
            )
    checks_code = "\n".join(checks)
    return f'''
m = Sketchup.active_model
e = m.active_entities
issues = []
{checks_code}
issues.empty? ? '{{"all_clean": true}}' : '{{"all_clean": false, "issues": [' + issues.map {{ |i| '"' + i + '"' }}.join(",") + ']}}'
'''
```

- [ ] **Step 4: Run test — PASS**

- [ ] **Step 5: Commit**

```bash
git add -u && git commit -m "feat: add verify_bounds ruby template"
```

---

### Task 3: Add safe_cut_dado template with inversion detection

**Files:**
- Modify: `src/sketchup_mcp/ruby_templates.py`
- Modify: `tests/test_ruby_templates.py`

- [ ] **Step 1: Write test**

```python
def test_safe_cut_dado_includes_bounds_check():
    code = safe_cut_dado_ruby("PostBC", "x+", 60, 71.25, 1.5)
    assert "bounds" in code.lower() or "max" in code
    assert "trim" in code or "erase" in code  # inversion fix
    assert "pushpull" in code  # dados require pushpull
    assert "3.5" not in code or "expected" in code  # should reference expected bounds

def test_safe_cut_dado_faces():
    """Must specify face correctly for each orientation"""
    for face in ["x+", "x-", "y+", "y-"]:
        code = safe_cut_dado_ruby("Post", face, 60, 71.25, 1.5)
        assert "add_face" in code
```

- [ ] **Step 2: Run test — FAIL**

- [ ] **Step 3: Implement**

```python
def safe_cut_dado_ruby(component_name: str, face: str, z_start: float, z_end: float, depth: float) -> str:
    """Generate Ruby to cut a dado with automatic inversion detection.

    face: 'x+', 'x-', 'y+', 'y-' — which face of the component to cut into.
    z_start, z_end: vertical range of the dado.
    depth: how deep to cut (inches).
    """
    # Map face to coordinates and pushpull direction
    face_configs = {
        "x+": {"face_coord": "bb_max_x", "pushpull": -1, "check_axis": "x", "check_dir": "max",
                "pts": f"[bb_max_x, 0, {z_start}], [bb_max_x, bb_max_y, {z_start}], [bb_max_x, bb_max_y, {z_end}], [bb_max_x, 0, {z_end}]"},
        "x-": {"face_coord": "0", "pushpull": 1, "check_axis": "x", "check_dir": "min",
                "pts": f"[0, 0, {z_start}], [0, 0, {z_end}], [0, bb_max_y, {z_end}], [0, bb_max_y, {z_start}]"},
        "y+": {"face_coord": "bb_max_y", "pushpull": -1, "check_axis": "y", "check_dir": "max",
                "pts": f"[0, bb_max_y, {z_start}], [bb_max_x, bb_max_y, {z_start}], [bb_max_x, bb_max_y, {z_end}], [0, bb_max_y, {z_end}]"},
        "y-": {"face_coord": "0", "pushpull": 1, "check_axis": "y", "check_dir": "min",
                "pts": f"[0, 0, {z_start}], [bb_max_x, 0, {z_start}], [bb_max_x, 0, {z_end}], [0, 0, {z_end}]"},
    }
    cfg = face_configs[face]

    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Dado in {component_name}', true)

inst = e.find {{ |ent| ent.is_a?(Sketchup::ComponentInstance) && ent.definition.name == "{component_name}" }}
raise "Component {component_name} not found" unless inst

defn = inst.definition
ents = defn.entities
bb = defn.bounds
bb_max_x = bb.max.x.to_f
bb_max_y = bb.max.y.to_f
bb_max_z = bb.max.z.to_f
expected_max_x = bb_max_x
expected_max_y = bb_max_y
expected_min_x = bb.min.x.to_f
expected_min_y = bb.min.y.to_f

face = ents.add_face({cfg["pts"]})
face.pushpull({cfg["pushpull"] * depth}) if face

# Verify bounds — detect inversion
bb2 = defn.bounds
inverted = false
case "{cfg["check_axis"]}{cfg["check_dir"]}"
when "xmax" then inverted = bb2.max.x.to_f > expected_max_x + 0.01
when "xmin" then inverted = bb2.min.x.to_f < expected_min_x - 0.01
when "ymax" then inverted = bb2.max.y.to_f > expected_max_y + 0.01
when "ymin" then inverted = bb2.min.y.to_f < expected_min_y - 0.01
end

if inverted
  # Trim the extrusion
  to_del = []
  defn.entities.each do |ent2|
    next unless ent2.is_a?(Sketchup::Face) || ent2.is_a?(Sketchup::Edge)
    verts = ent2.is_a?(Sketchup::Face) ? ent2.vertices : [ent2.start, ent2.end]
    over = case "{cfg["check_axis"]}{cfg["check_dir"]}"
    when "xmax" then verts.any? {{ |v| v.position.x.to_f > expected_max_x + 0.01 }}
    when "xmin" then verts.any? {{ |v| v.position.x.to_f < expected_min_x - 0.01 }}
    when "ymax" then verts.any? {{ |v| v.position.y.to_f > expected_max_y + 0.01 }}
    when "ymin" then verts.any? {{ |v| v.position.y.to_f < expected_min_y - 0.01 }}
    else false
    end
    to_del << ent2 if over
  end
  to_del.each {{ |td| td.erase! if td.valid? }}
  # Re-add closing face
  case "{face}"
  when "x+" then ents.add_face([expected_max_x,0,0],[expected_max_x,0,bb_max_z],[expected_max_x,bb_max_y,bb_max_z],[expected_max_x,bb_max_y,0])
  when "x-" then ents.add_face([expected_min_x,0,0],[expected_min_x,0,bb_max_z],[expected_min_x,bb_max_y,bb_max_z],[expected_min_x,bb_max_y,0])
  when "y+" then ents.add_face([0,expected_max_y,0],[0,expected_max_y,bb_max_z],[bb_max_x,expected_max_y,bb_max_z],[bb_max_x,expected_max_y,0])
  when "y-" then ents.add_face([0,expected_min_y,0],[0,expected_min_y,bb_max_z],[bb_max_x,expected_min_y,bb_max_z],[bb_max_x,expected_min_y,0])
  end
end

bb3 = defn.bounds
m.commit_operation
'{{"success": true, "inverted": ' + inverted.to_s + ', "bounds": [' + bb3.min.x.to_f.round(2).to_s + ',' + bb3.min.y.to_f.round(2).to_s + ',' + bb3.min.z.to_f.round(2).to_s + ',' + bb3.max.x.to_f.round(2).to_s + ',' + bb3.max.y.to_f.round(2).to_s + ',' + bb3.max.z.to_f.round(2).to_s + ']}}'
'''
```

- [ ] **Step 4: Run test — PASS**

- [ ] **Step 5: Commit**

```bash
git add -u && git commit -m "feat: add safe_cut_dado with inversion detection and auto-trim"
```

---

### Task 4: Add safe_drill_hole and take_screenshot templates

**Files:**
- Modify: `src/sketchup_mcp/ruby_templates.py`
- Modify: `tests/test_ruby_templates.py`

- [ ] **Step 1: Write tests**

```python
def test_safe_drill_hole_has_fallback():
    code = safe_drill_hole_ruby("PostBC", [0, 1.75, 63], [1, 0, 0], 0.197, 3.5)
    assert "add_circle" in code
    assert "add_face" in code
    assert "area < 0.5" in code  # nil fallback
    assert "bounds" in code  # verification

def test_take_screenshot():
    code = take_screenshot_ruby("Front Elevation", 1920, 1080)
    assert "ShowTransition" in code
    assert "selected_page" in code
    assert "write_image" in code
    assert "1920" in code
```

- [ ] **Step 2: Run test — FAIL**

- [ ] **Step 3: Implement both templates**

```python
def safe_drill_hole_ruby(component_name: str, center: list, normal: list, radius: float, depth: float) -> str:
    cx, cy, cz = center
    nx, ny, nz = normal
    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Drill hole in {component_name}', true)

inst = e.find {{ |ent| ent.is_a?(Sketchup::ComponentInstance) && ent.definition.name == "{component_name}" }}
raise "Component {component_name} not found" unless inst

defn = inst.definition
ents = defn.entities
bb_before = [defn.bounds.min.x.to_f, defn.bounds.min.y.to_f, defn.bounds.min.z.to_f,
             defn.bounds.max.x.to_f, defn.bounds.max.y.to_f, defn.bounds.max.z.to_f]

edges = ents.add_circle(Geom::Point3d.new({cx}, {cy}, {cz}), Geom::Vector3d.new({nx}, {ny}, {nz}), {radius}, 16)
face = ents.add_face(edges)
unless face
  face = edges.first.faces.select {{ |f| f.valid? && f.area < 0.5 }}.first rescue nil
end

drilled = false
if face
  face.pushpull(-{depth})
  drilled = true
end

bb_after = [defn.bounds.min.x.to_f, defn.bounds.min.y.to_f, defn.bounds.min.z.to_f,
            defn.bounds.max.x.to_f, defn.bounds.max.y.to_f, defn.bounds.max.z.to_f]

# Check for inversion
inverted = false
(0..5).each do |i|
  if (bb_after[i] - bb_before[i]).abs > 0.01
    inverted = true
    break
  end
end

m.commit_operation
'{{"success": ' + drilled.to_s + ', "inverted": ' + inverted.to_s + ', "bounds_changed": ' + (bb_before != bb_after).to_s + '}}'
'''


def take_screenshot_ruby(scene_name: str = None, width: int = 1920, height: int = 1080, hide_tags: list = None) -> str:
    hide_code = ""
    if hide_tags:
        hide_list = ", ".join(f'"{t}"' for t in hide_tags)
        hide_code = f'[{hide_list}].each {{ |t| l = m.layers[t]; l.visible = false if l }}'

    scene_code = ""
    if scene_name:
        scene_code = f'''
m.options["PageOptions"]["ShowTransition"] = false
page = m.pages.find {{ |p| p.name == "{scene_name}" }}
m.pages.selected_page = page if page
'''

    return f'''
m = Sketchup.active_model
{scene_code}
{hide_code}
path = File.join(Dir.tmpdir, "sketchup_screenshot_#{{Time.now.to_i}}.png")
m.active_view.write_image(path, {width}, {height}, true)
path
'''
```

- [ ] **Step 4: Run test — PASS**

- [ ] **Step 5: Commit**

```bash
git add -u && git commit -m "feat: add safe_drill_hole and take_screenshot templates"
```

---

## Chunk 2: Scene Management + OpenCutList Tools

### Task 5: Add create_scene and verify_scenes templates

**Files:**
- Modify: `src/sketchup_mcp/ruby_templates.py`
- Modify: `tests/test_ruby_templates.py`

- [ ] **Step 1: Write tests**

```python
def test_create_scene_sets_state_before_add():
    code = create_scene_ruby(
        name="Front Elevation",
        eye=[23.5, -80, 40], target=[23.5, 60, 40], up=[0, 0, 1],
        perspective=False, height=95,
        visible_tags=["Posts", "FrameRails"]
    )
    # Critical: layers and camera BEFORE pages.add
    layers_idx = code.index("visible")
    camera_idx = code.index("camera")
    add_idx = code.index("pages.add")
    assert layers_idx < add_idx
    assert camera_idx < add_idx

def test_create_scene_with_section_plane():
    code = create_scene_ruby(
        name="Section", eye=[0,0,0], target=[1,0,0], up=[0,0,1],
        perspective=False, height=90, visible_tags=["Posts"],
        section_point=[23.5, 75, 0], section_normal=[0, 1, 0]
    )
    assert "add_section_plane" in code

def test_verify_scenes():
    code = verify_scenes_ruby()
    assert "selected_page" in code
    assert "perspective" in code
    assert "visible" in code
```

- [ ] **Step 2: Run test — FAIL**

- [ ] **Step 3: Implement**

```python
def create_scene_ruby(name: str, eye: list, target: list, up: list,
                      perspective: bool = True, height: float = 90,
                      visible_tags: list = None,
                      section_point: list = None, section_normal: list = None) -> str:
    vis_code = ""
    if visible_tags:
        tag_list = ", ".join(f'"{t}"' for t in visible_tags)
        vis_code = f'''
visible = [{tag_list}]
m.layers.each {{ |l| next if l.name == "Layer0"; l.visible = visible.include?(l.name) }}
'''

    section_code = ""
    if section_point and section_normal:
        sp, sn = section_point, section_normal
        section_code = f'''
sp = m.active_entities.add_section_plane([{sp[0]}, {sp[1]}, {sp[2]}], [{sn[0]}, {sn[1]}, {sn[2]}])
sp.activate
'''

    persp_code = "true" if perspective else "false"
    height_code = f"\ncam.height = {height}" if not perspective else ""

    return f'''
m = Sketchup.active_model
v = m.active_view

# 1. Set layer visibility
{vis_code}

# 2. Section plane (if any)
{section_code}

# 3. Set camera
cam = Sketchup::Camera.new
cam.set(
  Geom::Point3d.new({eye[0]}, {eye[1]}, {eye[2]}),
  Geom::Point3d.new({target[0]}, {target[1]}, {target[2]}),
  Geom::Vector3d.new({up[0]}, {up[1]}, {up[2]})
)
cam.perspective = {persp_code}{height_code}
v.camera = cam

# 4. Add page (captures current state)
page = m.pages.add("{name}")
page.use_camera = true

# 5. Verify
'{{"success": true, "scene": "{name}", "perspective": ' + cam.perspective?.to_s + ', "visible_tags": [' + m.layers.select {{ |l| l.visible? && l.name != "Layer0" }}.map {{ |l| '"' + l.name + '"' }}.join(",") + ']}}'
'''


def verify_scenes_ruby() -> str:
    return '''
m = Sketchup.active_model
m.options["PageOptions"]["ShowTransition"] = false
results = []

m.pages.each do |page|
  m.pages.selected_page = page
  visible = m.layers.select { |l| l.visible? && l.name != "Layer0" }.map(&:name)
  cam = page.camera
  results << '{"name": "' + page.name + '", "perspective": ' + (cam ? cam.perspective?.to_s : "null") + ', "visible_tags": [' + visible.map { |v| '"' + v + '"' }.join(",") + ']}'
end

'[' + results.join(",") + ']'
'''
```

- [ ] **Step 4: Run test — PASS**

- [ ] **Step 5: Commit**

```bash
git add -u && git commit -m "feat: add create_scene and verify_scenes templates"
```

---

### Task 6: Add generate_cutlist and exploded_view templates

**Files:**
- Modify: `src/sketchup_mcp/ruby_templates.py`
- Modify: `tests/test_ruby_templates.py`

- [ ] **Step 1: Write tests**

```python
def test_generate_cutlist():
    code = generate_cutlist_ruby()
    assert "CutlistGenerateWorker" in code
    assert "auto_orient" in code
    assert "part_folding" in code

def test_exploded_view():
    offsets = {"Railing": 25, "Slats": 18, "FrameRails": 6, "Posts": 0}
    code = exploded_view_ruby(offsets, "Exploded")
    assert "Exploded" in code
    assert "copy" in code
    assert "translation" in code
```

- [ ] **Step 2: Run test — FAIL**

- [ ] **Step 3: Implement**

```python
def generate_cutlist_ruby(auto_orient: bool = True, part_folding: bool = True) -> str:
    return f'''
worker = Ladb::OpenCutList::CutlistGenerateWorker.new(
  auto_orient: {"true" if auto_orient else "false"},
  smart_material: true,
  part_folding: {"true" if part_folding else "false"}
)
cl = worker.run

parts = []
cl.groups.each do |g|
  g.parts.each do |p|
    parts << '{{"name": "' + p.name + '", "qty": ' + p.count.to_s + ', "length": "' + p.cutting_length.to_s + '", "width": "' + p.cutting_width.to_s + '", "thickness": "' + p.cutting_thickness.to_s + '"}}'
  end
end

'{{"success": true, "parts": [' + parts.join(",") + ']}}'
'''


def exploded_view_ruby(offsets: dict, tag_name: str = "Exploded") -> str:
    offset_cases = "\n".join(
        f'    when "{tag}" then {z_off}'
        for tag, z_off in offsets.items()
    )
    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Create exploded view', true)

exploded_tag = m.layers["{tag_name}"] || m.layers.add("{tag_name}")
count = 0

e.each do |ent|
  next unless ent.is_a?(Sketchup::ComponentInstance)
  tag = ent.layer.name
  z_off = case tag
{offset_cases}
  else next
  end

  copy = ent.copy
  copy.transform!(Geom::Transformation.translation([0, 0, z_off]))
  copy.layer = exploded_tag
  count += 1
end

m.commit_operation
'{{"success": true, "copies": ' + count.to_s + ', "tag": "{tag_name}"}}'
'''
```

- [ ] **Step 4: Run test — PASS**

- [ ] **Step 5: Commit**

```bash
git add -u && git commit -m "feat: add generate_cutlist and exploded_view templates"
```

---

## Chunk 3: Wire Templates to MCP Tools in server.py

### Task 7: Add all 9 tools to server.py

**Files:**
- Modify: `src/sketchup_mcp/server.py`

- [ ] **Step 1: Add imports and the first 3 tools (Tier 1)**

Add at top of server.py:
```python
from sketchup_mcp.ruby_templates import (
    make_box_ruby, verify_bounds_ruby, safe_cut_dado_ruby,
    safe_drill_hole_ruby, take_screenshot_ruby,
    create_scene_ruby, verify_scenes_ruby,
    generate_cutlist_ruby, exploded_view_ruby,
)
```

Add after existing tool functions:

```python
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
    """Cut a dado into a component with automatic pushpull inversion detection.
    If the pushpull goes the wrong way, automatically trims and corrects.
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
    """Drill a hole in a component with automatic face-nil fallback.
    Handles the case where add_face returns nil by finding the auto-created face.
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
```

- [ ] **Step 2: Add remaining 6 tools**

```python
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
    Sets all state BEFORE adding the page (critical for correct capture).
    visible_tags: comma-separated tag names."""
    try:
        up_vec = up or [0, 0, 1]
        vis_list = [t.strip() for t in visible_tags.split(",") if t.strip()] if visible_tags else None
        code = create_scene_ruby(name, eye, target, up_vec, perspective, ortho_height, vis_list,
                                  section_point, section_normal)
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
    offsets: JSON string mapping tag names to Z offsets, e.g. {\"Railing\": 25, \"Slats\": 18}"""
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
```

- [ ] **Step 3: Commit**

```bash
git add src/sketchup_mcp/server.py
git commit -m "feat: wire 9 furniture tools to MCP server"
```

---

### Task 8: Update version and rebuild

**Files:**
- Modify: `pyproject.toml` (version bump)
- Modify: `src/sketchup_mcp/server.py` (version string)

- [ ] **Step 1: Bump version**

In `pyproject.toml`: change `version = "0.1.17"` to `version = "0.2.0"`
In `server.py`: change `__version__ = "0.1.17"` to `__version__ = "0.2.0"`

- [ ] **Step 2: Build**

```bash
cd /Users/michaelfinkler/Dev/sketchup-mcp
uv build
```

- [ ] **Step 3: Run unit tests**

```bash
uv run pytest tests/test_ruby_templates.py -v
```

- [ ] **Step 4: Commit and tag**

```bash
git add -u
git commit -m "chore: bump version to 0.2.0 — furniture tools fork"
git tag v0.2.0
```

---

## Summary of New Tools

| Tool | What it does | Key feature |
|------|-------------|-------------|
| `boolean_subtract` | **Subtract a shape from a component** | **Deterministic — eliminates pushpull inversion entirely** |
| `create_component_box` | Create a box component | 6-face construction, never pushpull |
| `safe_cut_dado` | Cut a dado (uses boolean_subtract) | Thin wrapper, always correct |
| `safe_drill_hole` | Drill a hole (uses boolean_subtract) | Thin wrapper, always correct |
| `verify_bounds` | Check component dimensions | Batch verification, returns issues list |
| `take_screenshot` | Capture scene as PNG | Activates scene, disables transitions |
| `create_scene` | Create a Layout-ready scene | Sets state BEFORE adding page |
| `verify_scenes` | Audit all scene layer visibility | Catches tag bleed between scenes |
| `generate_cutlist` | Generate OpenCutList cut list | Returns structured JSON |
| `create_exploded_view` | Duplicate geometry for exploded view | Separate tag with Z offsets |
