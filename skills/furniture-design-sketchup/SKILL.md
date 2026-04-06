---
name: furniture-design-sketchup
description: Use when designing, sketching, or modeling furniture using the SketchUp MCP server. Trigger when user mentions SketchUp, 3D modeling furniture, loft beds, shelves, cabinets, stairs, desks, or any woodworking project that needs visualization. Also use when creating cut lists, shop drawings, or validating furniture designs before building.
---

# Furniture Design with SketchUp MCP

Design and produce build-ready plans for furniture using SketchUp via MCP (`eval_ruby`). Two key challenges: the pushpull inversion bug corrupts geometry ~50% of the time, and scenes silently fail to capture state. Verify everything visually — never trust that SketchUp did what you asked.

## Architecture

```
Claude Code → stdio → sketchup-mcp (Python) → TCP :9876 → SketchUp Ruby Extension
```

## Before Starting Any Design

Check these BEFORE modeling (see `references/materials-and-tools.md`):
1. **What tools does the builder have?** → Constrains joint selection
2. **What's the finish?** → Affects joint visibility and material choice
3. **Indoor or outdoor?** → Affects species, joints, and fasteners
4. **Project archetype?** → Sets defaults (see `references/project-archetypes.md`)

Then select plan tier (see `references/plan-tiers.md`):
- Simple shelf/box → Tier 1
- Furniture → Tier 2
- Complex/modular → Tier 3

## Design Phases

1. **Concept** — Identify archetype, select joints (see `references/joint-selection.md`). Block out volumes with `create_component_box`. Get proportions right first. Use ACTUAL lumber dimensions (not nominal).
2. **Detail** — Real lumber dimensions. Convert Groups → Components. Apply materials + tags. Follow archetype tag conventions.
3. **Joinery** — Apply joints per selection guide. Prefer MCP tools (`safe_cut_dado`, `create_mortise_tenon`, etc.) for simple operations; use `WW.*` via `eval_ruby` for complex multi-joint scripts. **Always verify bounds after every operation.**
4. **Shop Drawings** — Generate plan artifacts per tier. Scenes for Layout, `generate_cutlist` for cut lists. Verify with `verify_scenes`.

## Critical: The Pushpull Inversion Bug

`face.pushpull(distance)` direction depends on face normal winding order — **unpredictable**. Affects boxes, dados, AND bolt holes.

### For boxes: Never use pushpull

```ruby
module MCP_Helpers
  def self.make_box(entities, model, name, x, y, z, w, d, h, color_rgb)
    grp = entities.add_group
    ge = grp.entities
    ge.add_face([0,0,0],[w,0,0],[w,d,0],[0,d,0])
    ge.add_face([0,0,h],[0,d,h],[w,d,h],[w,0,h])
    ge.add_face([0,0,0],[w,0,0],[w,0,h],[0,0,h])
    ge.add_face([0,d,0],[0,d,h],[w,d,h],[w,d,0])
    ge.add_face([0,0,0],[0,0,h],[0,d,h],[0,d,0])
    ge.add_face([w,0,0],[w,d,0],[w,d,h],[w,0,h])
    tr = Geom::Transformation.new([x, y, z])
    grp.transform!(tr)
    grp.name = name
    mat = model.materials.add("#{name}_mat_#{rand(9999)}")
    mat.color = Sketchup::Color.new(*color_rgb)
    mat.alpha = color_rgb[3] if color_rgb.length > 3
    grp.material = mat
    grp
  end
end
```

### For dados: Rebuild the definition (preferred)

Instead of pushpull (which inverts ~50% of the time), rebuild the entire component definition with the dado as explicit geometry. A 6-face solid becomes a 10-face solid with the notch:

```ruby
# Example: 1x6 drawer side (0.75 × 22 × 5.5) with 1/2" dado, 1/4" deep, 1/2" up from bottom
defn.entities.clear!
de = defn.entities
w, d, h = 0.75, 22.0, 5.5
dado_z1, dado_z2, dado_depth = 0.5, 1.0, 0.25  # 1/2" wide, 1/4" deep

# Bottom, top, outside — full rectangles (unchanged)
de.add_face([0,0,0],[w,0,0],[w,d,0],[0,d,0])
de.add_face([0,0,h],[0,d,h],[w,d,h],[w,0,h])
de.add_face([w,0,0],[w,d,0],[w,d,h],[w,0,h])

# Inside face — split into 2 sub-faces (below dado + above dado)
de.add_face([0,0,0],[0,d,0],[0,d,dado_z1],[0,0,dado_z1])
de.add_face([0,0,dado_z2],[0,d,dado_z2],[0,d,h],[0,0,h])

# Dado groove — 3 faces (bottom, top, back wall)
de.add_face([0,0,dado_z1],[0,d,dado_z1],[dado_depth,d,dado_z1],[dado_depth,0,dado_z1])
de.add_face([0,0,dado_z2],[dado_depth,0,dado_z2],[dado_depth,d,dado_z2],[0,d,dado_z2])
de.add_face([dado_depth,0,dado_z1],[dado_depth,d,dado_z1],[dado_depth,d,dado_z2],[dado_depth,0,dado_z2])

# End faces — with dado notch profile
de.add_face([0,0,0],[w,0,0],[w,0,h],[0,0,h],[0,0,dado_z2],[dado_depth,0,dado_z2],[dado_depth,0,dado_z1],[0,0,dado_z1])
de.add_face([0,d,0],[0,d,dado_z1],[dado_depth,d,dado_z1],[dado_depth,d,dado_z2],[0,d,dado_z2],[0,d,h],[w,d,h],[w,d,0])
```

This avoids pushpull entirely. The dado is geometrically exact and visible when zoomed in.

### For dados/holes: Pushpull then VERIFY bounds (fallback)

Only use pushpull when rebuilding the definition is impractical (e.g., complex existing geometry):

```ruby
expected_max = 77.0  # record BEFORE cutting
face = ents.add_face(pts)
face.pushpull(-1.5) if face
# MANDATORY: check bounds didn't grow
if defn.bounds.max.y.to_f > expected_max + 0.01
  # Inversion! Trim with helper in references/sketchup-ruby-api.md
end
```

### Bolt holes: add_face returns nil

`add_circle` splits existing faces; `add_face` returns nil. Use fallback:
```ruby
edges = ents.add_circle(center, normal, radius, 16)
face = ents.add_face(edges)
face ||= edges.first.faces.select { |f| f.valid? && f.area < 0.5 }.first rescue nil
face.pushpull(-depth) if face
```
**Verify bounds after every hole.** See `references/sketchup-ruby-api.md` for the full `drill_hole` and `trim_extrusion` helpers.

## OpenCutList Integration

**Requirements:** Components (not Groups), materials applied, woodworking attributes set.

```ruby
# Convert group to component
inst = grp.to_component
inst.definition.name = "RailB"  # Watch for #1 suffix if name exists
inst.material = pine
inst.set_attribute("woodworking", "species", "Pine")
inst.set_attribute("woodworking", "nominal_size", "2x12")
```

**Fold repeated parts** (e.g., 15 slats → "BedSlat x15"): all instances must share one ComponentDefinition. Keep one definition, erase others, re-place as instances of the kept definition.

**Programmatic cut list:**
```ruby
worker = Ladb::OpenCutList::CutlistGenerateWorker.new(
  auto_orient: true, smart_material: true, part_folding: true
)
cutlist = worker.run
cutlist.groups.each { |g| g.parts.each { |p| "#{p.count}x #{p.name} | #{p.cutting_length}" } }
```

## Verification Discipline

SketchUp's Ruby API silently produces wrong results. The geometry is fully queryable — use programmatic verification as the primary check and screenshots as visual confirmation.

### Level 1: Programmatic Verification (after every operation)

The model state is queryable through `eval_ruby`. Always verify programmatically before moving on:

**After pushpull (dados, holes, mortises):**
```ruby
# Bounds check — catches pushpull inversions
defn = inst.definition
bb = defn.bounds
issues = []
issues << "X: #{bb.min.x.to_f.round(2)}..#{bb.max.x.to_f.round(2)}" if bb.max.x.to_f > expected_x + 0.01
issues << "Y: #{bb.min.y.to_f.round(2)}..#{bb.max.y.to_f.round(2)}" if bb.max.y.to_f > expected_y + 0.01
# Entity count — confirms geometry was actually modified
face_count = defn.entities.select { |e| e.is_a?(Sketchup::Face) }.count
issues << "face_count=#{face_count} (expected >6)" if face_count <= 6
```

**After scene creation:**
```ruby
# Query scene state — no screenshot needed for basic checks
page = m.pages[idx]
cam = page.camera
checks = []
checks << "perspective=#{cam.perspective?}" # should match intent
checks << "height=#{cam.height.to_f.round(1)}" # ortho height
# Activate scene and check layer visibility
m.pages.selected_page = page
visible = m.layers.select { |l| l.visible? && l.name != "Layer0" }.map(&:name)
checks << "visible=[#{visible.join(',')}]"
# Compare against expected
```

**Batch verification after all joinery:**
```ruby
# Verify ALL component bounds match expected dimensions in one pass
expected = {
  "PostBC" => {x: [0, 3.5], y: [0, 3.5], z: [0, 71.25]},
  "RailB"  => {x: [0, 1.5], y: [0, 77],  z: [0, 11.25]},
  # ... all parts
}
issues = []
expected.each do |name, dims|
  inst = entities.find { |e| e.is_a?(Sketchup::ComponentInstance) && e.definition.name == name }
  bb = inst.definition.bounds
  dims.each do |axis, range|
    val = axis == :x ? [bb.min.x, bb.max.x] : axis == :y ? [bb.min.y, bb.max.y] : [bb.min.z, bb.max.z]
    issues << "#{name} #{axis} #{val[0].to_f.round(2)}..#{val[1].to_f.round(2)}" if (val[0].to_f - range[0]).abs > 0.01 || (val[1].to_f - range[1]).abs > 0.01
  end
end
issues.empty? ? "All clean" : issues.join("\n")
```

### Level 2: Visual Verification (after scenes, after joinery batches)

Screenshots confirm what programmatic checks can't — camera framing, visual clarity of joints, overall composition. Take screenshots at two checkpoints:

**After each scene:** Activate with `ShowTransition = false`, take screenshot, Read the PNG:
```ruby
m.options["PageOptions"]["ShowTransition"] = false
m.pages.selected_page = page
path = File.join(Dir.tmpdir, "verify_#{page.name.gsub(' ','_')}.png")
m.active_view.write_image(path, 1920, 1080, true)
```

When reviewing the screenshot, check:
- Correct parts visible (no duplicates, no tag bleed)
- Camera framing (subject centered, not cropped)
- Joinery clearly visible (dados read as pockets, holes read as holes)
- Orthographic scenes show no perspective convergence

**After all scenes — transition test:** Cycle through every scene and verify layer visibility programmatically. The critical failure: tags created after scenes were saved bleed into all views.

### Level 3: Annotated Screenshots (for joint details)

For joint detail scenes, add temporary dimensions before the screenshot to make the drawing self-documenting:
```ruby
# Add dimensions that explain the joint
d1 = ents.add_dimension_linear([0,0,60], [0,0,71.25], [5,0,0])  # rail height
d2 = ents.add_dimension_linear([2.0,0,65], [3.5,0,65], [0,0,5]) # dado depth
# Screenshot
m.active_view.write_image(path, 1920, 1080, true)
# Remove temporary dimensions if not wanted in final model
# d1.erase!; d2.erase!
```

This produces screenshots that a builder (or an LLM reviewing the work) can interpret without needing to read the model file.

## Scenes for Layout

**Critical pattern — set state BEFORE adding page:**
```ruby
# 1. Set layers
m.layers.each { |l| l.visible = visible_tags.include?(l.name) }
# 2. Set camera
cam = Sketchup::Camera.new
cam.set(eye, target, up)
cam.perspective = false; cam.height = 95  # for orthographic
m.active_view.camera = cam
# 3. THEN add page
page = m.pages.add("Front Elevation")
page.use_camera = true
# 4. VERIFY — take screenshot and confirm visually
m.options["PageOptions"]["ShowTransition"] = false
m.pages.selected_page = page
path = File.join(Dir.tmpdir, "verify_#{page.name.gsub(' ','_')}.png")
m.active_view.write_image(path, 1920, 1080, true)
# Read the PNG to check framing, visibility, camera type
```

Update existing: `page.update(1 | 32)` (1=camera, 32=layers).

**Exploded views:** Scenes don't capture entity positions. Duplicate geometry to an "Exploded" tag at Z offsets, show only that tag in the exploded scene.

### Standard Scene Set

| Type | Camera | Shows |
|------|--------|-------|
| Assembly Overview | Perspective | All parts |
| Elevations (3-4) | Orthographic | All parts, different angles |
| Plan View | Ortho top-down | All parts |
| Section Cuts | Ortho + section plane | Joint details |
| Post/Rail Details | Perspective close-up | Joinery close-ups |
| Assembly Stages | Shared perspective | Progressive tag visibility |
| Exploded | Perspective | Exploded tag only |

## Standard Plywood Sizes (Lowe's)

Designs MUST use standard available sizes. Common mistake: specifying 3/8" plywood — most stores don't stock it in hardwood species.

| Thickness | Actual | Available Species | Typical Use |
|-----------|--------|-------------------|-------------|
| 1/4" | 0.25" | Maple, birch, oak, lauan | Back panels, drawer bottoms (light duty) |
| 1/2" | 0.47-0.50" | Maple, birch, oak | Drawer bottoms (captured in dados), panels |
| 3/4" | 0.73" | Maple, birch, oak | Cabinet carcasses, structural panels |

**Before specifying plywood in a design, verify the thickness is available in the desired species at the builder's store.**

## Cabinet/Dresser Archetype

Standard construction for face-frame cabinets with drawers — the most common beginner furniture project.

**Structure:**
- 3/4" plywood sides, top, bottom (the carcass)
- 1/4" or 1/2" plywood back panel (keeps it square)
- 1x2 pine face frame (stiles + rails, pocket-holed)
- Drawer boxes: 1x6 pine sides with dadoed plywood bottoms
- Overlay drawer fronts (hardwood for contrast)

**Key principles:**
- Freestanding is simpler than built-in (no mounting to surrounding structure)
- Side-mount drawer slides need 3/4" plywood or solid wood — 3/8" is too thin for slide screws
- The back panel is the squaring tool — measure diagonals, nail it when square
- Overlay fronts hide imprecision in the face frame openings
- Pocket holes face INSIDE the cabinet (hidden when drawers installed)

**Modeling order:**
1. Carcass (sides, top, bottom) as shared components
2. Back panel
3. Face frame (stiles + rails)
4. Individual drawer box pieces (sides, front/back, bottom — NOT solid blocks)
5. Drawer fronts (overlay)
6. Tags: assign all to "Drawers" or similar

**Cut planning:** Verify all pieces fit on standard 4×8 plywood sheets before finalizing dimensions. Draw the cutting layout.

## Component Detail Level

For shop drawings and exploded views, components must be modeled at the **individual piece level**, not as simplified blocks.

| Wrong | Right |
|-------|-------|
| Drawer box as 1 solid block | 4 sides + 1 bottom = 5 components |
| Face frame as 1 piece | 2 stiles + N rails = N+2 components |
| Cabinet as 1 box | 2 sides + top + bottom + back = 5 components |

Solid blocks are fine for **concept phase** (blocking out volumes). But before creating shop drawings, exploded views, or cut lists, every piece that gets cut separately must be a separate component.

## Exploded View Technique

Scenes don't capture entity positions. Duplicate all parts to an "Exploded" tag at offset positions:

```ruby
# Offset strategy by part type
offsets = {
  "Side"   => -> (e) { e.bounds.min.x < center_x ? [-spread, 0, 0] : [spread, 0, 0] },
  "TopBot" => -> (e) { e.bounds.min.z > mid_z ? [0, 0, spread*2] : [0, 0, -spread] },
  "Back"   => -> (e) { [0, -spread*1.5, 0] },
  "Front"  => -> (e) { [0, spread*2.5, 0] },
  "Drawer" => -> (e) { [0, spread*1.5, spread*0.3] },
  "FF"     => -> (e) { [0, spread*1.5, 0] },  # face frame
}

parts.each do |e|
  type = offsets.keys.find { |k| e.definition.name.include?(k) }
  ox, oy, oz = offsets[type]&.call(e) || [0, 0, 0]
  new_inst = entities.add_instance(e.definition,
    Geom::Transformation.new([e.transformation.origin.x + ox, ...]))
  new_inst.layer = exploded_tag
  new_inst.material = e.material
end
```

Then create a scene showing only the Exploded tag. The assembled view shows the original components (Drawers tag), the exploded view shows the duplicates (Exploded tag).

## Tags

| Tag | Contents |
|-----|----------|
| Posts | Structural posts/legs |
| FrameRails | Side rails, end rails |
| Stretchers | Cross-bracing |
| Slats, Ledgers | Platform components |
| Railing | Guard rails, guard posts |
| Ladder | Ladder + hardware |
| Drawers | Cabinet/dresser components |
| Room | Context geometry (hide for shop drawings) |
| Exploded | Duplicate geometry for exploded view |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Pushpull for boxes | `MCP_Helpers.make_box` — always |
| Not verifying bounds after pushpull | Check definition bounds after EVERY cut |
| `add_face` nil for holes | `edges.first.faces.select { f.area < 0.5 }` |
| Scene camera/layers not saved | Set state BEFORE `pages.add()` |
| Not screenshotting each scene | Take screenshot + Read it after EVERY scene |
| Assuming scene transitions work | Cycle through all scenes with `ShowTransition=false`, verify each |
| Exploded tag bleeds into other scenes | Create Exploded tag BEFORE scenes, or update all scenes after |
| Exploded view reverts | Duplicate geometry on Exploded tag |
| Joint details not visible | Check camera angle shows dado depth, bolt holes, connections |
| Parts don't fold in OpenCutList | Share one ComponentDefinition |
| Definition name collision | Delete/rename old def before creating new |
| Groups for parts | Components required for cut lists |
| Joinery before sizing | Finalize dimensions first |
| Drawer box as solid block | Model individual sides/front/back/bottom for shop drawings |
| Specifying 3/8" plywood | Not stocked at most stores — use 1/4", 1/2", or 3/4" |
| 3/8" ply for slide mounting panels | Too thin — slides need 3/4" ply or solid wood |
| Building into existing structure | Consider freestanding first — simpler, removable, build in garage |
| Dados via pushpull | Rebuild definition with explicit notch geometry instead |

## References

| File | Contents |
|------|----------|
| `references/joint-selection.md` | Joint decision framework, lookup tables, anti-patterns, bail-out rules |
| `references/plan-tiers.md` | Tier 1/2/3 artifact checklists, project-to-tier mapping |
| `references/materials-and-tools.md` | Lumber sizes, plywood gotchas, tool tiers, species guide |
| `references/project-archetypes.md` | 6 archetypes with default parts, joints, tags, modeling order |
| `references/sketchup-ruby-api.md` | Ruby API details, helpers, component/transformation patterns |
