# Plan Artifact Specification

What constitutes a "complete plan" at each project complexity level. Defines three tiers with concrete artifact requirements, tool call recipes, verification steps, and common mistakes.

Used by Layer 1 evals (does the model know what to produce?) and Layer 3 evals (did it actually produce a complete package?).

---

## Tier Overview

| Tier | Name | When | Artifact count |
|------|------|------|----------------|
| 1 | Minimum Viable Plan | Every project | 4 |
| 2 | Buildable Plan | Furniture | 9+ |
| 3 | Shop-Ready Plan | Complex/modular | 14+ |

Each tier includes all artifacts from the tier below it.

---

## Project-to-Tier Mapping

| Project type | Minimum tier | Examples |
|---|---|---|
| Simple box/shelf | Tier 1 | Garage shelf, planter box, tool tote, spice rack |
| Furniture | Tier 2 | Bookshelf, table, bed frame, nightstand, dresser |
| Complex/modular | Tier 3 | Loft bed, built-in cabinets, Murphy bed, entertainment center |
| Outdoor/structural | Tier 2 (Tier 3 if multi-structure) | Shed, pergola, workbench, deck railing |

Decision rule: if the project has sub-assemblies that ship as independent units, or knockdown hardware, it is Tier 3. If it has joinery beyond pocket screws and butt joints, it is at least Tier 2.

---

## Tier 1: Minimum Viable Plan

Every project produces these four artifacts. A Tier 1 package answers: "What am I building, what do I need to buy, and how big is it?"

### Artifact 1.1: Assembly Overview (3/4 Perspective)

**What it looks like:** A single screenshot showing the completed project from a 3/4 perspective angle (above, in front, and to the right). All components visible. Material colors applied so wood species are distinguishable. No section planes active.

**How to create it:**

```
create_scene(
  name: "Assembly Overview",
  eye: [W*1.5, -D*1.5, H*1.2],    # front-right, above
  target: [W/2, D/2, H/2],          # center of bounding box
  perspective: true
)

take_screenshot(
  scene_name: "Assembly Overview",
  width: 1920,
  height: 1080
)
```

Camera placement rule: position the eye at roughly 1.5x the bounding box dimensions away, looking at the center. The up vector defaults to `[0, 0, 1]`. Adjust eye position so that the longest dimension runs roughly diagonal in the frame.

**How to verify:**
- All components are visible (no hidden tags)
- Camera is perspective, not ortho
- Model fills at least 60% of the frame (not a tiny speck in the distance)
- Materials are applied (no default white/gray)
- No section planes are active

**Common mistakes:**
- Using orthographic camera instead of perspective (produces a flat, hard-to-read overview)
- Eye position too close, clipping the model
- Eye position too far, model is tiny
- Forgetting to show all tags, leaving parts invisible
- Section plane left active from a previous scene (use `verify_scenes` to catch)

---

### Artifact 1.2: Cut List

**What it looks like:** A structured table with columns: Part Name, Quantity, Species, Nominal Size (lumber as purchased), Actual Size (after milling). Grouped by material/species. Includes total board feet per species.

**How to create it:**

```
generate_cutlist(
  auto_orient: true,
  part_folding: true
)
```

This invokes OpenCutList and returns JSON with part names, quantities, and dimensions. The `auto_orient` flag ensures grain direction is respected. The `part_folding` flag groups identical parts and increments quantity.

Post-processing: convert the raw JSON into a formatted table. Add nominal lumber sizes (e.g., a part that is 0.75" x 3.5" x 36" comes from a 1x4 @ 36"). Calculate board feet per species: `(T x W x L) / 144` where all dimensions are in inches.

**How to verify:**
- Every component in the model appears in the cut list (compare component count vs. cut list row count times quantity)
- Dimensions are actual, not nominal (0.75" not 1", 3.5" not 4")
- Species is assigned to every part (no "unspecified" entries)
- Board feet totals are arithmetically correct
- Parts with identical dimensions and species are folded into a single row with qty > 1

**Common mistakes:**
- Components without the `material` attribute set, producing "unspecified" species
- Nested components counted at wrong level (sub-component parts double-counted)
- Confusing nominal and actual dimensions in the output
- Forgetting to add 10-15% waste factor to board feet estimates
- Not running `auto_orient: true`, causing grain direction errors in plywood parts

---

### Artifact 1.3: Materials List

**What it looks like:** A shopping list derived from the cut list. Two sections: (1) Lumber, listed by species with total board feet and suggested purchase quantity (e.g., "Pine: 42 bf -- buy 6x 8ft 1x12 + 2x 8ft 2x4"), and (2) Hardware, listing fasteners, screws, bolts, and other non-wood items with type, size, and quantity.

**How to create it:**

Derived from the cut list output plus project metadata. Lumber quantities come from `generate_cutlist` board feet totals with a waste factor applied. Hardware counts come from the model's component attributes or from the assembly specification.

For lumber, use `eval_ruby` with `WW.board_feet` to calculate totals per species:

```
eval_ruby(code: "WW.board_feet('Pine')")
```

**How to verify:**
- Every species in the cut list has a board feet entry in the materials list
- Board feet include waste factor (10% for straight cuts, 15-20% for angled/curved)
- Hardware list accounts for every joint (e.g., 4 pocket screws per butt joint, 2 bolts per knockdown connection)
- No missing categories (glue, finish, sandpaper are optional but often forgotten)

**Common mistakes:**
- Listing board feet without rounding up to purchasable lumber lengths
- Forgetting that hardware comes in specific package quantities (box of 100 screws, not 87)
- Omitting finish materials (Rubio Monocoat, polyurethane, etc.)
- Not accounting for test cuts and setup waste

---

### Artifact 1.4: Overall Dimensions

**What it looks like:** A single line or small table stating the project's finished Width x Depth x Height. For asymmetric projects, include footprint dimensions.

**How to create it:**

```
verify_bounds(
  expected: '{"<ProjectName>": {"x": [0, W], "y": [0, D], "z": [0, H]}}'
)
```

If the model is not wrapped in a single top-level component, use `eval_ruby` to query the model bounding box:

```
eval_ruby(code: "bb = Sketchup.active_model.bounds; [bb.width, bb.depth, bb.height].map{|d| d.to_f.round(2)}.to_s")
```

**How to verify:**
- Dimensions match the design intent (not off by a board thickness)
- All components are included in the bounds (nothing hidden or on an invisible tag)
- Units are consistent (all inches, or all mm -- never mixed)

**Common mistakes:**
- Measuring with hidden components excluded, producing undersized bounds
- Reporting the bounding box of a single component instead of the full assembly
- Confusing SketchUp's axis orientation (red=X=width, green=Y=depth, blue=Z=height)

---

## Tier 2: Buildable Plan

Adds orthographic views, joinery details, exploded view, and assembly sequence to the Tier 1 package. A Tier 2 package answers: "How do I actually build this? What goes where? What joints do I cut?"

### Artifact 2.1: Front Elevation (Orthographic)

**What it looks like:** A straight-on front view with no perspective distortion. Shows the face the user will see most often. Dimension lines or annotations showing key heights and widths. No depth foreshortening.

**How to create it:**

The camera eye is placed directly in front of the model center, looking along the Y axis (green axis). The `perspective: false` flag activates orthographic projection. The `ortho_height` parameter controls zoom level -- set it to slightly more than the model height to include margins.

```
create_scene(
  name: "Front Elevation",
  eye: [W/2, -100, H/2],        # centered on X, far back on Y, centered on Z
  target: [W/2, 0, H/2],         # center of front face
  up: [0, 0, 1],
  perspective: false,
  ortho_height: H * 1.15          # 15% margin above and below
)

take_screenshot(scene_name: "Front Elevation")
```

The eye Y coordinate should be far enough back that nothing clips (use -100 or more for furniture-scale projects). The exact distance does not matter in ortho mode -- only `ortho_height` controls the visible area.

**How to verify:**
- Camera is orthographic (`perspective: false`)
- View is truly front-on: eye and target share the same X and Z, differ only in Y
- `ortho_height` captures the full model height plus margins
- No perspective distortion visible (parallel lines stay parallel)
- Section planes are NOT active (unless intentionally showing a cross-section)

**Common mistakes:**
- Forgetting `perspective: false`, producing a perspective view labeled as an elevation
- Setting `ortho_height` too small, cropping the top or bottom of the model
- Eye and target not aligned on the same X/Z plane, producing an angled view
- Tag visibility carrying over from a previous scene (tag bleed)

---

### Artifact 2.2: Side Elevation (Orthographic)

**What it looks like:** A straight-on side view (typically the right side). Shows depth and height relationships, joinery on the side, and structural members.

**How to create it:**

```
create_scene(
  name: "Side Elevation",
  eye: [W + 100, D/2, H/2],     # far right on X, centered on Y and Z
  target: [W, D/2, H/2],         # right face center
  up: [0, 0, 1],
  perspective: false,
  ortho_height: H * 1.15
)

take_screenshot(scene_name: "Side Elevation")
```

For a left-side elevation, mirror the X values:

```
eye: [-100, D/2, H/2]
target: [0, D/2, H/2]
```

**How to verify:**
- Same ortho checks as front elevation
- Eye is on the X axis (for right side) or negative X (for left side)
- Model depth is fully visible
- Side-specific features (stretchers, side panels, handles) are identifiable

**Common mistakes:**
- Choosing the wrong side (showing the back instead of the side)
- Eye/target misaligned, producing an off-axis view
- `ortho_height` set for front elevation height but side is taller due to overhang

---

### Artifact 2.3: Plan View (Top-Down Orthographic)

**What it looks like:** A bird's-eye view looking straight down. Shows the footprint, top surface layout, and spatial relationships between components.

**How to create it:**

```
create_scene(
  name: "Plan View",
  eye: [W/2, D/2, H + 100],     # centered above, looking down
  target: [W/2, D/2, H],         # top surface center
  up: [0, -1, 0],                # CRITICAL: up vector points toward back of model
  perspective: false,
  ortho_height: D * 1.15          # controls visible depth (Y axis fills frame height)
)

take_screenshot(scene_name: "Plan View")
```

**How to verify:**
- Camera looks straight down: eye and target share X and Y, differ only in Z
- Up vector is `[0, -1, 0]` (back of model toward top of image) or `[0, 1, 0]` depending on desired orientation
- `ortho_height` is based on depth (Y dimension), not height
- Footprint is fully visible

**Common mistakes:**
- Using default up vector `[0, 0, 1]` which is parallel to the viewing direction and produces an undefined/flipped view
- Setting `ortho_height` based on Z height instead of Y depth
- Not realizing that in top-down view, `ortho_height` controls how much of the Y axis is visible

---

### Artifact 2.4: Joinery Details (Zoomed Views)

**What it looks like:** Close-up views of each joint type used in the project, with section planes to reveal internal geometry. Typically 2-4 detail views per project. Shows the joint clearly enough that a builder can see what to cut.

**How to create it:**

For each joint, create a zoomed scene with a section plane to reveal the hidden geometry:

```
create_scene(
  name: "Detail - Dado Joint at Shelf",
  eye: [joint_x + 8, joint_y - 12, joint_z + 6],   # close, slightly above
  target: [joint_x, joint_y, joint_z],                # joint center
  perspective: true,                                    # perspective OK for details
  visible_tags: "Uprights,Shelves",                    # only relevant parts
  section_point: [joint_x, joint_y, joint_z],
  section_normal: [0, 1, 0]                            # cut through Y to reveal dado
)

take_screenshot(scene_name: "Detail - Dado Joint at Shelf")
```

Section plane placement: the `section_point` should be at the joint center, and `section_normal` should point in the direction that reveals the most internal geometry. For a dado joint, cut perpendicular to the shelf (normal along Y). For a mortise-tenon, cut along the length of the tenon.

**How to verify:**
- Section plane is active and positioned to reveal the joint
- The joint is clearly visible (dado channel, tenon inside mortise, etc.)
- Only relevant tags are visible (hide unrelated components that would obscure the view)
- Camera is close enough to see joint detail but far enough to show context
- Joint dimensions are readable (dado width matches shelf thickness, tenon fits mortise)

**Common mistakes:**
- Section plane in the wrong orientation (slicing along the joint instead of across it)
- Section plane too far from the joint, not cutting through anything useful
- Showing all tags, causing unrelated components to block the joint view
- Forgetting to deactivate the section plane for other scenes (verify with `verify_scenes`)
- Not creating enough detail views (one per joint type minimum)

---

### Artifact 2.5: Exploded View

**What it looks like:** All components pulled apart along the Z axis (or appropriate axis) so the assembly relationships are visible. Each part is recognizable and its position in the assembly is clear. Shown on a dedicated tag so the unexploded model is preserved.

**How to create it:**

First, plan Z offsets by structural role. Bottom-most parts get the smallest offset; top parts get the largest. Offsets should be proportional to assembly order.

```
create_exploded_view(
  offsets: '{"Base": 0, "Sides": 12, "Shelves": 24, "Top": 36, "Back Panel": 48}',
  tag_name: "Exploded"
)

create_scene(
  name: "Exploded View",
  eye: [W*2, -D*2, H*2.5],       # further back and higher than assembly overview
  target: [W/2, D/2, H*1.5],      # center of the exploded stack (higher than assembled)
  perspective: true,
  visible_tags: "Exploded"          # ONLY the exploded tag
)

take_screenshot(scene_name: "Exploded View")
```

**How to verify:**
- All components appear in the exploded view (count copies vs. original component count)
- Offsets produce clear separation (no overlapping parts)
- Exploded copies are on the dedicated tag, originals are untouched
- Scene only shows the exploded tag (not both exploded and original overlapping)
- Assembly order is readable from the spatial arrangement

**Common mistakes:**
- Offsets too small, parts still overlap visually
- Offsets too large, parts are so spread out the relationship is lost
- Showing both the "Exploded" tag and the original tags, producing a confusing double image
- Forgetting some tags in the offset map, leaving parts at their assembled position mixed with exploded parts
- Not adjusting the camera target upward to account for the increased vertical extent

---

### Artifact 2.6: Assembly Sequence

**What it looks like:** A numbered series of scenes, each showing a progressive step in the build. Step 1 shows the first sub-assembly. Each subsequent step adds components. The final step matches the assembly overview. Each scene has a descriptive name that serves as the instruction.

**How to create it:**

Create one scene per assembly step, controlling tag visibility to show only the parts assembled so far:

```
# Step 1: Build the base
create_scene(
  name: "Step 1 - Assemble Base Frame",
  eye: [W*1.5, -D*1.5, H*0.8],
  target: [W/2, D/2, base_H/2],
  perspective: true,
  visible_tags: "Base Rails,Base Stretchers"
)

# Step 2: Attach sides
create_scene(
  name: "Step 2 - Attach Side Panels",
  eye: [W*1.5, -D*1.5, H*1.0],
  target: [W/2, D/2, H*0.4],
  perspective: true,
  visible_tags: "Base Rails,Base Stretchers,Side Panels"
)

# Step 3: Install shelves
create_scene(
  name: "Step 3 - Install Shelves",
  ...
  visible_tags: "Base Rails,Base Stretchers,Side Panels,Shelves"
)
```

**Assembly sequence rules:**

1. **Inside out:** Internal joints and structure before enclosing panels. Attach shelf dados before the back panel traps them.
2. **Sub-assemblies before final assembly:** Build the side panel sub-assembly (uprights + cross-members) as a unit, then join side panels to each other.
3. **Dry-fit before glue-up:** Sequence should note where dry-fit checks happen (not a scene, but a step name like "Step 4 - Dry-fit shelf spacing").
4. **For knockdown builds:** Permanent joints first (glued dados, mortise-tenons), then test hardware fit (bolts, barrel nuts). Knockdown connections are the last assembly step.
5. **Gravity-friendly:** Wherever possible, arrange steps so the assembly rests stably. Avoid steps that require holding something in mid-air.

**How to verify:**
- Each step adds exactly one sub-assembly or component group (not too many at once)
- Tag visibility is cumulative (each step shows all previous tags plus new ones)
- The final step shows all tags (matches assembly overview)
- Scene names are descriptive enough to be instructions
- `verify_scenes` reports correct tag visibility for each step
- No step requires components that have not been introduced in a prior step

**Common mistakes:**
- Adding too many parts per step (overwhelming, not instructive)
- Non-cumulative tag visibility (a part visible in Step 2 disappears in Step 3)
- Assembly order that traps internal components (adding the back panel before shelves are installed)
- Not enough steps for complex joinery (a single "Step 3 - Add all shelves" when each shelf requires alignment and clamping)
- Scene names that are just numbers without descriptions

---

## Tier 3: Shop-Ready Plan

Adds section cuts, dimension callouts, hardware schedules, module breakdowns, and knockdown details. A Tier 3 package answers: "How do I build this in my shop, in what order, with what hardware, and how does it come apart?"

### Artifact 3.1: Section Cuts Through Critical Joints

**What it looks like:** Cross-section views through the most structurally important joints. Unlike the Tier 2 joinery details (which show joints from the outside with a section plane), these are true section cuts that show internal geometry clearly -- bolt paths through multiple layers, dado depths, tenon lengths inside mortises.

**How to create it:**

Create scenes with section planes positioned to cut through the joint's most informative cross-section:

```
# Section through a bolted knockdown joint
create_scene(
  name: "Section A-A: Bed Rail to Post",
  eye: [joint_x - 24, joint_y, joint_z],
  target: [joint_x, joint_y, joint_z],
  up: [0, 0, 1],
  perspective: false,
  ortho_height: 12,                            # tight zoom on the joint
  section_point: [joint_x, joint_y, joint_z],
  section_normal: [1, 0, 0]                    # cut perpendicular to rail
)
```

Use orthographic camera for section cuts so dimensions are measurable. Set `ortho_height` to show just the joint with a small margin (6-18 inches depending on joint size).

Name sections with architectural convention: "Section A-A", "Section B-B", etc. Reference these names in the assembly sequence.

**How to verify:**
- Section plane cuts through the most informative plane of the joint
- Camera is orthographic (measurable proportions)
- `ortho_height` is tight enough to show detail but includes full joint context
- Bolt paths, dado channels, or tenons are clearly visible in cross-section
- Each critical joint type has at least one section cut

**Common mistakes:**
- Section plane parallel to the joint instead of perpendicular (slices along it, revealing nothing)
- Orthographic zoom too wide, making the joint a tiny detail in a large view
- Not labeling sections consistently (mixing "Detail A" and "Section 1" naming)
- Cutting through the wrong location (missing the bolt centerline by half an inch)

---

### Artifact 3.2: Dimension Callouts on Model

**What it looks like:** Key dimensions displayed directly on the model as SketchUp dimension entities. Not every dimension -- only the ones a builder needs to measure and verify: overall dimensions, shelf spacing, joint locations, hardware positions.

**How to create it:**

Use `eval_ruby` to add dimension entities. SketchUp dimensions require two 3D points and an offset vector:

```
eval_ruby(code: '
  m = Sketchup.active_model
  e = m.active_entities
  m.start_operation("Add dimensions", true)

  # Overall width
  e.add_dimension_linear(
    [0, 0, 0],
    [48, 0, 0],
    [0, -3, 0]       # offset: 3 inches in front of the model
  )

  # Shelf height from floor
  e.add_dimension_linear(
    [0, 0, 0],
    [0, 0, 24],
    [-3, 0, 0]       # offset: 3 inches to the left
  )

  m.commit_operation
  "done"
')
```

Dimension placement strategy:
- Overall W, D, H on the assembly overview
- Internal spacing (shelf gaps, drawer openings) on front elevation
- Joint locations (dado positions, hole centers) on detail views
- Hardware positions (bolt centers, barrel nut offsets) on section cuts

**How to verify:**
- Dimensions are readable (not overlapping each other or model geometry)
- Dimension values match the design intent
- Offset vectors push dimensions away from the model face so they are clear
- Critical dimensions are present: overall size, repeating intervals, hardware locations
- No redundant dimensions (do not dimension the same measurement twice)

**Common mistakes:**
- Adding too many dimensions, creating visual clutter
- Dimensions overlapping each other because offset vectors point in the same direction
- Dimension endpoints not snapping to actual component geometry (measuring to empty space)
- Forgetting to add dimensions to section cut views where they matter most
- Adding dimensions in model space that are only relevant to one scene (use tags to control visibility)

---

### Artifact 3.3: Hardware Schedule

**What it looks like:** A table listing every piece of hardware in the project: type, specific size, quantity, and where each is used. Includes fasteners (screws, bolts), connectors (barrel nuts, corner brackets), and accessories (drawer slides, hinges, casters).

| Hardware | Size | Qty | Location |
|----------|------|-----|----------|
| Hex bolt | 3/8"-16 x 4" | 8 | Rail-to-post connections |
| Barrel nut | 3/8"-16, 15mm body | 8 | Inside posts, receives hex bolts |
| Pocket screw | 1-1/4" fine thread | 24 | Face frame assembly |
| Wood screw | #8 x 1-1/2" | 16 | Back panel to carcass |
| Shelf pin | 1/4" brass | 20 | Adjustable shelf positions |

**How to create it:**

Extract from model component attributes if hardware is modeled, or derive from the assembly specification. For knockdown projects, hardware is often not modeled as geometry but tracked as metadata:

```
eval_ruby(code: '
  m = Sketchup.active_model
  hardware = {}
  m.definitions.each do |d|
    d.instances.each do |i|
      hw = i.get_attribute("hardware", "type")
      next unless hw
      size = i.get_attribute("hardware", "size")
      loc = i.get_attribute("hardware", "location")
      key = "#{hw}|#{size}"
      hardware[key] ||= {type: hw, size: size, qty: 0, locations: []}
      hardware[key][:qty] += 1
      hardware[key][:locations] << loc unless hardware[key][:locations].include?(loc)
    end
  end
  hardware.values.to_json
')
```

If hardware is not modeled as components with attributes, build the schedule manually from the joint specification: count each joint type, multiply by fasteners per joint.

**How to verify:**
- Every knockdown joint has its hardware listed
- Bolt lengths account for the actual material stack-up (board thickness + barrel nut depth + washer)
- Quantities match the model (8 bolt holes = 8 bolts + 8 barrel nuts + 8 washers)
- No generic entries ("screws, various" -- specify exact type and size)
- Package quantities noted for purchasing (bolts sold individually, screws by the box)

**Common mistakes:**
- Forgetting washers (every bolt needs a washer, sometimes two)
- Wrong bolt length (too short to reach the barrel nut, or too long and protruding)
- Not specifying thread type (coarse for softwood, fine for hardwood/barrel nuts)
- Omitting alignment hardware (dowel pins for knockdown alignment are easy to forget)
- Listing hardware from an earlier design revision that no longer matches the model

---

### Artifact 3.4: Module Breakdown (Sub-Assembly Scenes)

**What it looks like:** For modular projects, each module gets its own scene showing only that module's components. The scene is zoomed to fit the module with clear tag isolation. Accompanied by module-specific cut lists and dimensions.

**How to create it:**

Each module should have its own tag (or tag folder). Create an isolated scene per module:

```
# Module 1: Core Frame
create_scene(
  name: "Module 1 - Core Frame",
  eye: [frame_W*1.5, -frame_D*1.5, frame_H*1.2],
  target: [frame_W/2, frame_D/2, frame_H/2],
  perspective: true,
  visible_tags: "Posts,Rails,Stretchers"
)

# Module 2: Storage Stairs
create_scene(
  name: "Module 2 - Storage Stairs",
  eye: [stair_W*1.5, -stair_D*1.5, stair_H*1.2],
  target: [stair_W/2, stair_D/2, stair_H/2],
  perspective: true,
  visible_tags: "Stair Stringers,Treads,Stair Shelves"
)
```

Generate a per-module cut list by temporarily hiding all other tags and running `generate_cutlist`, or by filtering the full cut list output by tag.

**How to verify:**
- Every component in the model belongs to exactly one module (no orphans, no double-assignment)
- Each module scene shows only that module's tags
- Module bounding boxes do not unexpectedly overlap (unless by design, like a desk that slides under a loft)
- Per-module cut lists sum to the full project cut list
- Modules are numbered in build order

**Common mistakes:**
- Components assigned to the wrong module's tag
- A "shared" component (like a connecting rail) that belongs to two modules -- assign it to the module where it is permanently attached
- Module scenes showing bleed from other tags (the most common scene bug; always run `verify_scenes`)
- Not providing module-specific dimensions (overall module size, connection point locations)

---

### Artifact 3.5: Knockdown Details

**What it looks like:** Focused views showing every knockdown connection: bolt hole location, barrel nut pocket position, alignment dowel placement, and the assembly/disassembly procedure. These are the details that make a project shippable and reassemblable.

**How to create it:**

For each knockdown connection, create a detail scene showing the hardware path:

```
# Knockdown detail: Rail-to-Post bolt connection
create_scene(
  name: "KD Detail - Rail to Post",
  eye: [post_x + 6, post_y - 10, joint_z],
  target: [post_x, post_y, joint_z],
  perspective: true,
  visible_tags: "Posts,Rails",
  section_point: [post_x, post_y, joint_z],
  section_normal: [0, 1, 0]         # cut through to show bolt path
)
```

Annotate or document alongside the scene:
- Bolt centerline height from floor or reference edge
- Barrel nut centerline distance from mating face
- Required clearance and tolerances
- Assembly order: insert barrel nut, align parts, thread bolt, tighten

**How to verify:**
- Every knockdown connection has a detail view
- Bolt holes align between mating parts (verify with `verify_bounds` on both components)
- Barrel nut pockets are accessible (not buried behind another component)
- Alignment dowels are present where needed (prevents racking during assembly)
- Tolerances are noted (bolt hole 1/16" oversize for adjustment)

**Common mistakes:**
- Barrel nut pocket on the wrong face (must be perpendicular to the bolt, accessible with an Allen wrench)
- Bolt hole and barrel nut hole not intersecting (misaligned centerlines)
- Forgetting alignment dowels (the bolt alone allows rotation; dowels prevent it)
- Not showing the insertion direction (which side does the bolt enter from?)
- Assuming the user knows how barrel nuts work (include a "how this joint works" note)

---

## Verification: The `verify_scenes` Checkpoint

After creating all scenes for any tier, always run:

```
verify_scenes()
```

This cycles through every scene and reports:
- Camera type (perspective vs. orthographic) per scene
- Visible tags per scene
- Whether section planes are active

**What to check in the output:**
1. **No perspective/ortho mismatch:** Elevations and sections must be ortho. Overview, exploded, and assembly steps should be perspective.
2. **No tag bleed:** Each scene should show exactly the tags intended. The most common bug is a tag that was made visible for Scene A remaining visible in Scene B.
3. **Section plane isolation:** Section planes should only be active in the scene that needs them. A section plane left active in the assembly overview is a critical error.
4. **Cumulative assembly steps:** Each assembly step scene should show all tags from previous steps plus the new ones.

---

## Concrete Examples

### Example A: Tier 1 -- Garage Shelf Plan Package

**Project:** A simple 48"W x 16"D x 72"H garage shelf with 4 shelves, built from 2x4 frame and 3/4" plywood shelves. Pocket screw joinery throughout.

**Artifacts produced:**

1. **Assembly Overview:** 3/4 perspective screenshot showing complete shelf unit with pine 2x4 frame and plywood shelves. Camera at `[72, -24, 86]` looking at `[24, 8, 36]`.

2. **Cut List:**

   | Part | Qty | Species | Nominal | Actual |
   |------|-----|---------|---------|--------|
   | Upright | 4 | Pine | 2x4 x 72" | 1.5" x 3.5" x 72" |
   | Front/Back Rail | 8 | Pine | 2x4 x 45" | 1.5" x 3.5" x 45" |
   | Side Rail | 8 | Pine | 2x4 x 13" | 1.5" x 3.5" x 13" |
   | Shelf | 4 | Plywood | 3/4" x 48" x 16" | 0.72" x 48" x 16" |

3. **Materials List:**
   - Pine 2x4: ~47 linear feet -- buy 6x 8ft 2x4
   - 3/4" plywood: 1 sheet (4x8), yields all 4 shelves
   - Pocket screws: 1-1/2" coarse thread, qty 64 (box of 100)
   - Wood glue: 8 oz

4. **Overall Dimensions:** 48"W x 16"D x 72"H

**Total artifacts: 4. Total tool calls: ~5** (create_scene, take_screenshot, generate_cutlist, verify_bounds, verify_scenes).

---

### Example B: Tier 2 -- Bookshelf Plan Package

**Project:** A 36"W x 11.25"D x 48"H bookshelf with 4 adjustable shelves, dado-joined fixed top/bottom, and a rabbeted back panel. Pine carcass, 1/4" plywood back.

**Artifacts produced:**

1. **Assembly Overview:** 3/4 perspective, all components visible.

2. **Cut List:** Uprights, top, bottom, shelves, back panel, shelf pins.

3. **Materials List:** Pine board feet, plywood panel, shelf pins (qty 20), wood glue, finish.

4. **Overall Dimensions:** 36"W x 11.25"D x 48"H.

5. **Front Elevation:** Ortho, `eye: [18, -100, 24]`, `target: [18, 0, 24]`, `ortho_height: 55`. Shows shelf spacing, overall proportions.

6. **Side Elevation:** Ortho, `eye: [136, 5.6, 24]`, `target: [36, 5.6, 24]`, `ortho_height: 55`. Shows depth, dado locations on upright.

7. **Plan View:** Ortho, top-down, `up: [0, -1, 0]`, `ortho_height: 13`. Shows shelf depth, back panel inset.

8. **Joinery Details:**
   - Detail A: Dado joint at fixed shelf (section plane through shelf, showing 3/8" deep dado in upright)
   - Detail B: Rabbet for back panel (section at back edge, showing 1/4" x 3/8" rabbet)
   - Detail C: Shelf pin holes (zoomed view of drilling pattern, 1.5" from edges, 2" spacing)

9. **Exploded View:** Components separated vertically -- base at 0, uprights at 8", fixed shelves at 16", adjustable shelves at 24", back panel at 32".

10. **Assembly Sequence:**
    - Step 1: Cut dados in uprights (both uprights, matching positions)
    - Step 2: Cut rabbets for back panel (uprights, top, bottom -- three edges)
    - Step 3: Dry-fit uprights + fixed shelves (check square)
    - Step 4: Glue and clamp carcass (uprights + top + bottom in dados)
    - Step 5: Attach back panel (1/4" ply in rabbets, pin nails + glue)
    - Step 6: Drill shelf pin holes (jig, 1/4" bit, tape depth stop)
    - Step 7: Sand and finish
    - Step 8: Install adjustable shelves on pins

**Total artifacts: 10. Total tool calls: ~20** (multiple create_scene, take_screenshot, generate_cutlist, verify_bounds, create_exploded_view, verify_scenes).

---

### Example C: Tier 3 -- Loft Bed Module Plan Package (Core Frame Module)

**Project:** Module 1 of a 7-module loft bed system. Core Frame: 45"x83" platform at 60" height, 4 posts (3.5"x3.5"x71.25"), 4 rails (1.5"x5.5"), knockdown bolt joints at all rail-to-post connections. Pine construction.

**Artifacts produced (for this one module):**

1. **Assembly Overview:** 3/4 perspective of Core Frame only (other modules hidden).

2. **Cut List (module-specific):**

   | Part | Qty | Species | Nominal | Actual |
   |------|-----|---------|---------|--------|
   | Post | 4 | Pine | 4x4 x 72" | 3.5" x 3.5" x 71.25" |
   | Long Rail | 2 | Pine | 2x6 x 83" | 1.5" x 5.5" x 83" |
   | Short Rail | 2 | Pine | 2x6 x 45" | 1.5" x 5.5" x 45" |
   | Cleat | 4 | Pine | 1x2 x 10" | 0.75" x 1.5" x 10" |
   | Slat | 8 | Pine | 1x4 x 45" | 0.75" x 3.5" x 45" |

3. **Materials List (module-specific):** Pine 4x4: 2x 8ft. Pine 2x6: 2x 8ft + 1x 4ft. Pine 1x4: 4x 8ft. Plus hardware.

4. **Overall Dimensions:** 48"W (post to post + overhang) x 86"D x 71.25"H.

5. **Front Elevation:** Ortho showing post spacing, rail height, platform level.

6. **Side Elevation:** Ortho showing rail depth, post profile, cleat position.

7. **Plan View:** Ortho top-down showing slat layout, post positions at corners.

8. **Joinery Details:**
   - Detail A: Bolt joint at rail-to-post (3/4 perspective with section plane)
   - Detail B: Cleat attachment to rail (pocket screws)
   - Detail C: Slat-to-cleat connection

9. **Exploded View:** Posts at 0, rails at 15", cleats at 25", slats at 35".

10. **Assembly Sequence:**
    - Step 1: Prepare posts (cut to length, drill bolt holes, drill barrel nut pockets)
    - Step 2: Prepare rails (cut to length, drill bolt holes, attach cleats with pocket screws)
    - Step 3: Dry-fit one short-rail sub-assembly (2 posts + 1 short rail, hand-tighten bolts)
    - Step 4: Attach long rails to form rectangular frame (all 4 bolts per rail)
    - Step 5: Check square (diagonal measurement, adjust before final tighten)
    - Step 6: Install platform slats on cleats
    - Step 7: Final torque all bolts

11. **Section Cuts:**
    - Section A-A: Through post at bolt joint height, showing 3/8" bolt path from rail face through to barrel nut in post
    - Section B-B: Through rail at cleat, showing pocket screw angle and penetration

12. **Dimension Callouts:** Overall frame size, bolt hole centerline height (54.5" from floor), barrel nut pocket depth (1.75" from post face), slat spacing (1.5" gaps).

13. **Hardware Schedule:**

    | Hardware | Size | Qty | Location |
    |----------|------|-----|----------|
    | Hex bolt | 3/8"-16 x 4" | 8 | Rail-to-post (2 per corner) |
    | Barrel nut | 3/8"-16, 15mm body | 8 | Inside posts |
    | Flat washer | 3/8" | 8 | Under bolt heads |
    | Pocket screw | 1-1/4" coarse | 8 | Cleats to rails (2 per cleat) |
    | Wood screw | #8 x 1-1/4" | 16 | Slats to cleats (2 per slat end) |

14. **Module Breakdown Scene:** Core Frame isolated, with connection points to adjacent modules (Railing, Stairs) annotated.

15. **Knockdown Details:**
    - KD Detail 1: Rail-to-post connection with bolt, washer, barrel nut cross-section
    - KD Detail 2: How to disassemble -- remove slats, unbolt rails from one end, fold frame flat
    - KD Detail 3: Alignment dowel locations (2 per post, 1/4" x 1" fluted dowels, prevent rail rotation)

**Total artifacts: 15. Total tool calls: ~40+** (extensive scene creation, multiple screenshots, section planes, cutlist, verify_bounds per sub-assembly, verify_scenes, eval_ruby for dimensions and hardware extraction).

---

## Eval Integration

### Layer 1 (Knowledge Test)

Ask the model: "What artifacts are needed for a [project type] plan?" The model should respond with the correct tier and list all required artifacts. Score:
- Lists correct tier: 1 point
- Lists all artifacts for that tier: 1 point per artifact
- Describes how to create each artifact (correct tool, correct camera type): 1 point per artifact
- Penalty: -1 point per artifact listed from a higher tier that is not needed (over-engineering)

### Layer 3 (End-to-End Test)

Give the model a complete project to plan. After it produces the plan package, verify:
- All required artifacts are present: pass/fail per artifact
- Camera types are correct (ortho where specified, perspective where specified): pass/fail per scene
- Tag visibility is correct (`verify_scenes` output matches spec): pass/fail
- Cut list is complete (all components represented): pass/fail
- Assembly sequence follows the rules (inside-out, sub-assembly first, cumulative tags): pass/fail
- Section planes are correctly positioned and isolated: pass/fail per section

### Scoring Rubric

| Tier | Perfect score | Passing score |
|------|--------------|---------------|
| Tier 1 | 4/4 artifacts, all verified | 3/4 artifacts (missing materials list OK if cut list present) |
| Tier 2 | 9+/9+ artifacts, all verified | 7/9+ (can skip plan view and one joinery detail) |
| Tier 3 | 14+/14+ artifacts, all verified | 11/14+ (can skip dimension callouts and one knockdown detail) |
