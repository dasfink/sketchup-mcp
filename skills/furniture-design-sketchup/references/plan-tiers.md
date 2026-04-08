# Plan Tiers

What constitutes a complete plan at each complexity level. Each tier includes all artifacts from the tier below.

## Project-to-Tier Mapping

| Project type | Tier | Examples |
|---|---|---|
| Simple box/shelf | Tier 1 | Garage shelf, planter box, tool tote, spice rack |
| Furniture | Tier 2 | Bookshelf, table, bed frame, nightstand, dresser |
| Complex/modular | Tier 3 | Loft bed, built-in cabinets, Murphy bed, entertainment center |
| Outdoor/structural | Tier 2 (Tier 3 if multi-structure) | Shed, pergola, workbench, deck railing |

**Decision rule:** Sub-assemblies that ship as independent units or knockdown hardware → Tier 3. Joinery beyond pocket screws and butt joints → at least Tier 2.

## Tier 1: Minimum Viable Plan (4 artifacts)

Every project produces these. Answers: "What am I building, what do I need to buy, how big is it?"

| # | Artifact | Camera | Key checks |
|---|---|---|---|
| 1.1 | Assembly Overview | Perspective 3/4 | All components visible, materials applied, fills 60%+ of frame |
| 1.2 | Cut List | — | Every component listed, actual dimensions (not nominal), species assigned, parts folded |
| 1.3 | Materials List | — | Board feet with waste factor, hardware counted per joint, purchase quantities |
| 1.4 | Overall Dimensions | — | W × D × H matches design intent |

### Tool calls for Tier 1

```
create_scene(name: "Assembly Overview", eye: [W*1.5, -D*1.5, H*1.2], target: [W/2, D/2, H/2], perspective: true)
take_screenshot(scene_name: "Assembly Overview")
generate_cutlist(auto_orient: true, part_folding: true)
verify_bounds(expected: '{"<Project>": {"x": [0, W], "y": [0, D], "z": [0, H]}}')
verify_scenes()
```

## Tier 2: Buildable Plan (9+ artifacts)

Adds views, joinery details, exploded view, assembly sequence. Answers: "How do I actually build this?"

| # | Artifact | Camera | Key checks |
|---|---|---|---|
| 2.1 | Front Elevation | Ortho | `perspective: false`, eye/target same X/Z, parallel lines stay parallel |
| 2.2 | Side Elevation | Ortho | Eye on X axis (right) or −X (left), model depth visible |
| 2.3 | Plan View | Ortho top-down | `up: [0, -1, 0]`, `ortho_height` based on Y depth |
| 2.4 | Joinery Details (2–4) | Perspective or section | Section plane reveals internal geometry, only relevant tags visible |
| 2.5 | Exploded View | Perspective | Parts on dedicated "Exploded" tag, clear separation, assembly order readable |
| 2.6 | Assembly Sequence | Perspective per step | Cumulative tag visibility, inside-out order, descriptive scene names |

### Camera recipes

```
# Front elevation
create_scene(name: "Front Elevation", eye: [W/2, -100, H/2], target: [W/2, 0, H/2], perspective: false, ortho_height: H*1.15)

# Side elevation (right)
create_scene(name: "Side Elevation", eye: [W+100, D/2, H/2], target: [W, D/2, H/2], perspective: false, ortho_height: H*1.15)

# Plan view
create_scene(name: "Plan View", eye: [W/2, D/2, H+100], target: [W/2, D/2, H], up: [0, -1, 0], perspective: false, ortho_height: D*1.15)

# Exploded view
create_exploded_view(offsets: '{"Base": 0, "Sides": 12, "Shelves": 24, "Top": 36}', tag_name: "Exploded")
create_scene(name: "Exploded View", eye: [W*2, -D*2, H*2.5], target: [W/2, D/2, H*1.5], perspective: true, visible_tags: "Exploded")
```

### Assembly sequence rules

1. **Inside out** — internal joints before enclosing panels
2. **Sub-assemblies first** — build units, then join units
3. **Dry-fit before glue-up** — note dry-fit steps in sequence
4. **Knockdown last** — permanent joints first, then hardware
5. **Gravity-friendly** — each step rests stably

## Tier 3: Shop-Ready Plan (14+ artifacts)

Adds section cuts, dimensions, hardware schedule, module breakdown, knockdown details. Answers: "How do I build this in my shop, in what order, with what hardware, how does it come apart?"

| # | Artifact | Camera | Key checks |
|---|---|---|---|
| 3.1 | Section Cuts | Ortho | Perpendicular to joint, tight zoom, labeled A-A/B-B |
| 3.2 | Dimension Callouts | On model | Key dims only (overall, spacing, hardware positions), no clutter |
| 3.3 | Hardware Schedule | Table | Type, size, qty, location. Every bolt has a washer. |
| 3.4 | Module Breakdown | Per-module scenes | Each module isolated, per-module cut list, numbered in build order |
| 3.5 | Knockdown Details | Section + perspective | Bolt path, barrel nut pocket, alignment dowels, insertion direction |

### Section cut recipe

```
create_scene(
  name: "Section A-A: Rail to Post",
  eye: [joint_x - 24, joint_y, joint_z],
  target: [joint_x, joint_y, joint_z],
  perspective: false,
  ortho_height: 12,
  section_point: [joint_x, joint_y, joint_z],
  section_normal: [1, 0, 0]
)
```

## Verification Checkpoint

After creating all scenes at any tier, always run `verify_scenes()` and check:

1. **Camera types** — Elevations/sections = ortho. Overview/exploded/assembly = perspective.
2. **Tag bleed** — Each scene shows exactly the intended tags.
3. **Section plane isolation** — Active only in the scene that needs it.
4. **Cumulative assembly steps** — Each step shows all previous tags plus new ones.

## Scoring (for eval reference)

| Tier | Perfect | Passing |
|---|---|---|
| 1 | 4/4 verified | 3/4 (materials list can be skipped if cut list present) |
| 2 | 9+/9+ verified | 7/9+ (can skip plan view and one joinery detail) |
| 3 | 14+/14+ verified | 11/14+ (can skip dimension callouts and one KD detail) |
