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

## Design Phases

1. **Concept** — Block out volumes with `MCP_Helpers.make_box`. Get proportions right first.
2. **Detail** — Real lumber dimensions. Convert Groups → Components. Apply materials + tags.
3. **Joinery** — Dados, bolt holes, mortises. **Always verify bounds after every pushpull.**
4. **Shop Drawings** — Scenes for Layout, OpenCutList for cut lists.

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

### For dados/holes: Pushpull then VERIFY bounds

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

## Tags

| Tag | Contents |
|-----|----------|
| Posts | Structural posts/legs |
| FrameRails | Side rails, end rails |
| Stretchers | Cross-bracing |
| Slats, Ledgers | Platform components |
| Railing | Guard rails, guard posts |
| Ladder | Ladder + hardware |
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

## Reference

Ruby API details, helpers (`drill_hole`, `trim_extrusion`), and component/transformation patterns: see `references/sketchup-ruby-api.md`.
