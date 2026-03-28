# SketchUp MCP Woodworking Library Design

## Problem
The SketchUp MCP has 2 bugs and lacks the capabilities needed to model detailed furniture with precise joinery. The target use case is a modular loft bed with storage stairs — hundreds of operations including dados, mortises, through-tenons, tapers, chamfers, bolt holes, and component hierarchy.

## Approach: Ruby Helper Library + eval_ruby
Fix the bugs, then build a **WW (Woodworking) Ruby module** loaded into SketchUp. Claude generates Ruby code calling WW functions via the existing `eval_ruby` MCP tool. This is infinitely flexible and avoids the rigidity of fixed MCP tool endpoints.

## Bug Fixes

### Bug 1: Socket poisoning in get_sketchup_connection()
**Root cause:** `get_sketchup_connection()` sends a `{"method": "ping"}` request to test liveness but never reads the response. Ruby side returns "Method not found" error that sits in the TCP buffer, poisoning the next tool call's response.
**Fix:** Remove the ping. Use a simple socket-level liveness test instead (`sock.send(b'')` which is already in `SketchupConnection.connect()`).

### Bug 2: Entities#subtract doesn't exist
**Root cause:** 5 call sites in `main.rb` call `.subtract()` on `Sketchup::Entities` objects. The correct API is `Sketchup::Group#subtract(other_group)`.
**Fix:** Change each call site to use the parent group. Both groups must be solid (watertight manifold). This fix applies to `boolean_operation`, `create_mortise_tenon`, `create_dovetail`, and `create_finger_joint`.

## WW Module API

### File: `su_mcp/woodworking.rb`
Auto-loaded when MCP server starts. Available globally for `eval_ruby` calls.

### Stock & Structure
- `WW.board(name, size, length, material: nil)` — Create board from nominal lumber size ("2x8") or exact dims ([t, w, l])
- `WW.panel(name, size, width:, depth:)` — Edge-glued panel
- `WW.module_group(name)` — Create organizational component group
- `WW.add_to(group, *entities)` — Move entities into a group
- `WW.place(entity, position)` — Position entity at [x, y, z]
- `WW.rotate(entity, axis, angle)` — Rotate entity

### Joinery (subtractive — uses face+pushpull or Group#subtract)
- `WW.dado(board, face:, at:, width:, depth:)` — Channel across grain
- `WW.rabbet(board, edge:, width:, depth:)` — Step cut along edge
- `WW.groove(board, face:, from_edge:, width:, depth:)` — Channel with grain
- `WW.mortise(board, face:, at:, size:, depth:, through:)` — Rectangular pocket/through
- `WW.tenon(board, end_face:, size:, length:, kerf:)` — Projection with optional wedge kerf
- `WW.half_lap(board, face:, at:, width:, depth:)` — Overlapping notch

### Shaping
- `WW.taper(board, faces:, from:, to:, start:, over:)` — Gradual width reduction
- `WW.chamfer(board, edges:, size:)` — Bevel edges
- `WW.roundover(board, edge:, radius:, both_faces:)` — Rounded edge profile
- `WW.finger_pull(board, edge:, diameter:, depth:)` — Drilled half-moon pull

### Hardware
- `WW.bolt_hole(board, face:, at:, hole:, cbore:, cbore_depth:)` — Through-hole + counterbore
- `WW.barrel_nut_hole(board, face:, at:, hole:, depth:, cross_hole:, cross_at:)` — End-grain bolt + cross hole
- `WW.pilot_hole(board, face:, at:, dia:, depth:)` — Screw pilot hole

### Query
- `WW.cut_list(group)` — Extract dimensions from all WW boards in a group
- `WW.board_feet(group)` — Calculate total board feet
- `WW.check_solids(group)` — Validate all groups are manifold

## Implementation Notes
- All dimensions in inches (SketchUp's native unit)
- Boards created in local coordinates: length along X, width along Y, thickness along Z
- Face references: `:top`, `:bottom`, `:front`, `:back`, `:left`, `:right`
- Subtractive joinery uses face+pushpull where possible (no Pro requirement), falls back to Group#subtract for complex shapes
- Board metadata stored as SketchUp attributes (name, nominal size, material)
- The WW module maintains a `@boards` hash for name-based lookup

## Existing MCP Tools
Keep all working tools (`create_component`, `transform_component`, `delete_component`, `set_material`, `export_scene`, `get_selection`, `eval_ruby`). The WW library supplements them — it doesn't replace them.
