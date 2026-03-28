# Furniture-Design-SketchUp Skill Improvement Design

## Problem Statement

The furniture-design-sketchup skill has working MCP tools (22 tools + WW library) and handles the loft bed project well, but lacks:

1. **Joint knowledge** -- no decision framework for when to use dado vs. rabbet vs. mortise-tenon. Tools exist but the skill doesn't know when to recommend each.
2. **Plan artifact completeness** -- can make scenes and screenshots but no systematic approach to producing a complete "build package" appropriate to project complexity.
3. **Project variety** -- tuned for one project (modular loft bed). Doesn't generalize to bookshelves, tables, workbenches, drawer boxes, or outdoor projects.
4. **Material/tool awareness** -- doesn't factor in beginner tool constraints, wood species properties, or finish type when making recommendations.

## Approach: Research-First, Skill-Second

Build a standalone research corpus, establish baseline eval scores, then surgically improve the skill based on where evals fail.

```
docs/corpus/           -- reusable research artifact
evals/                 -- test suite (3 layers)
skills/furniture-*/    -- improved iteratively based on eval failures
```

## Sources

| Source | What we extract | Status |
|--------|----------------|--------|
| Training data (Claude) | Joint taxonomy, SketchUp modeling techniques, woodworking fundamentals | Available now |
| Woodgears.ca plans (~40 free projects) | Project archetypes, modeling approaches, .skp reference models | 3 .skp models downloaded |
| Woodgears.ca tutorials (8 videos) | SketchUp modeling techniques for joints, scenes, layers | 4/8 transcripts extracted |
| Woodgears.ca construction articles | Joint decisions in real project context, dimensions, trade-offs | Scrapable via WebFetch |
| Ana White guides (3 PDFs) | Beginner tool constraints, material selection, dimensional lumber sizes, finish planning | Read and analyzed |
| Ana White plans (website) | Pocket-screw-first construction archetype, beginner project patterns | Future expansion |
| Instructables "20 Years of Woodworking" (133 projects) | Broad project variety, community build patterns | Future expansion (needs Chrome) |
| Your loft bed project | Gold-standard Tier 3 reference, modular/knockdown archetype | In current codebase |

---

## Section 1: Joint Taxonomy

For each joint type, we document:

| Field | Description |
|-------|-------------|
| Name | Joint name and aliases |
| What it is | Physical description |
| When to use | Connection types, load scenarios |
| When NOT to use | Contra-indications |
| Strength profile | Tension, compression, shear, racking resistance |
| Beginner-friendliness | Tool requirements, skill level, available bail-out |
| Minimum tools required | What Ana White's audience has vs. what Matthias Wandel's audience has |
| Bail-out alternative | Simpler joint that works for beginners |
| SketchUp modeling approach | Which MCP tool to use, parameters, verification |
| Wood species notes | Softwood vs. hardwood considerations |
| Typical dimensions | Rules of thumb (1/3 rule for tenons, depth rules for dados) |
| Finish implications | Visible vs. hidden, paint vs. stain, pocket hole plugs |

### Joints to catalog

**Channel joints (shelf-into-side):**
- **Dado** -- channel across the grain. Shelves into uprights, dividers. Router + straight bit or table saw + dado stack. Depth: 1/3 to 1/2 stock thickness. Width: actual thickness of mating board (23/32" for 3/4" plywood). MCP: `safe_cut_dado`.
- **Rabbet** -- L-shaped cut along an edge. Back panels, box corners. Same tools as dado. Depth: 1/2 to 2/3 stock thickness. MCP: `safe_cut_dado` at edge, or `boolean_subtract`.
- **Groove** -- channel with the grain. Panel capture in frame-and-panel doors, drawer bottoms. Same tools. MCP: `safe_cut_dado` rotated.

**Frame joints (apron-to-leg, rail-to-stile):**
- **Mortise & tenon** -- rectangular hole + matching tongue. The workhorse of frame joinery. Through (visible, can be wedged), blind (hidden), haunched (fills groove in frame-and-panel). Tenon: 1/3 stock thickness, at least 1" deep. Shoulder adds racking resistance. MCP: `create_mortise_tenon` or `boolean_subtract`.
- **Dowel joint** -- alignment-critical, at least 2 dowels to prevent rotation. Fluted dowels for glue escape. Jig essential. Decent strength, less forgiving than M&T. MCP: `safe_drill_hole` x2 per joint.
- **Pocket screw** -- Kreg jig, angled coarse-thread screw. Fast, no clamp time, reversible. Adequate for face frames, aprons, and non-chair applications. Does NOT accommodate wood movement -- bad for tabletop cross-grain attachment. Hidden by filler (paint) or plugs (stain). MCP: `safe_drill_hole` at angle.
- **Half-lap** -- each piece halved in thickness where they cross. Workbenches, face frames, stretchers. Easy to cut. Weak in tension, use where joint is in compression or add fasteners. MCP: `boolean_subtract`.

**Corner joints (box construction):**
- **Dovetail** -- mechanical interlock resists pull-apart in one direction. Through (visible both sides), half-blind (hidden from front, for drawer fronts). Angle: 1:6 softwood, 1:8 hardwood. MCP: `create_dovetail`.
- **Finger/box joint** -- equal-width interlocking fingers. Machine-friendly alternative to dovetails. Excellent glue surface. MCP: `create_finger_joint`.
- **Rabbet + pin** -- simple corner joint, L-shaped cut plus pin nails. Ana White beginner-level. MCP: `safe_cut_dado` + `safe_drill_hole`.
- **Butt + screw** -- simplest possible. Pocket screws or face screws. Hide with filler for paint projects. MCP: just position components.

**Panel joints (edge-to-edge, top attachment):**
- **Biscuit** -- alignment aid, not structural. Swelling biscuit + glue. Edge-joining boards, aligning miters. MCP: `boolean_subtract` for slot.
- **Tabletop buttons / Z-clips** -- NOT a wood joint, but critical knowledge. Allow seasonal wood movement. NEVER glue or pocket-screw a solid top across grain. MCP: model as hardware components.

**Knockdown joints (disassembly/reassembly):**
- **Bolt + barrel nut** -- bed rails, modular furniture. MCP: `safe_drill_hole` for bolt and cross-bore.
- **Bed rail hardware** -- specialty bracket. Invisible when assembled.
- **Cam lock + dowel** -- IKEA-style. Rarely hand-built but good for production.

---

## Section 2: Plan Artifact Spec

What "a complete plan" means, tiered by project complexity.

### Tier 1: Minimum Viable Plan
Every project, no exceptions.

| Artifact | Description | SketchUp tool |
|----------|-------------|---------------|
| Assembly overview | 3/4 perspective, whole piece | `create_scene` + `take_screenshot` |
| Cut list | Every part: name, qty, species, nominal/actual dims | `generate_cutlist` |
| Materials list | Board feet by species, hardware count | Derived from cut list |
| Overall dimensions | W x D x H of finished piece | `verify_bounds` |

### Tier 2: Buildable Plan
Furniture and structural projects.

| Artifact | Description | SketchUp tool |
|----------|-------------|---------------|
| Front elevation | Orthographic front view with key dims | `create_scene` (ortho) |
| Side elevation | Orthographic side view | `create_scene` (ortho) |
| Plan view | Top-down orthographic | `create_scene` (ortho) |
| Joinery details | Zoomed views of each joint type used | `create_scene` + section plane |
| Exploded view | Parts separated to show assembly order | `create_exploded_view` |
| Assembly sequence | Numbered steps with scene per stage | Skill-generated text + scenes |

### Tier 3: Shop-Ready Plan
Complex and modular projects.

| Artifact | Description | SketchUp tool |
|----------|-------------|---------------|
| Section cuts | Cross-sections through critical joints | Section planes + scenes |
| Dimension callouts | On-model dimensions at every measurement | `eval_ruby` (dimension entities) |
| Hardware schedule | Every bolt, screw, barrel nut -- type, size, qty, location | From model attributes |
| Module breakdown | Sub-assembly groupings for phased building | Per-module scenes + tag visibility |
| Knockdown details | Bolt locations, alignment dowels, hardware | Detail scenes |

### Project type to tier mapping

| Project type | Min tier | Examples |
|-------------|----------|----------|
| Simple box/shelf | Tier 1 | Garage shelf, planter box |
| Furniture | Tier 2 | Bookshelf, table, bed frame |
| Complex/modular | Tier 3 | Loft bed, built-in cabinets |
| Outdoor/structural | Tier 2+ | Shed, pergola, workbench |

---

## Section 3: Project Archetypes

### Archetype 1: Flat-Pack / Panel Assembly
- **Examples:** Garage shelf, storage shelf, bookcase, drawer box
- **Structure:** Uprights + horizontal shelves/dividers, typically rectangular
- **Typical joints:** Dado (shelves into sides), rabbet (back panel), butt + screws (simplest)
- **Beginner version (Ana White style):** Pocket screws + shelf pins, 1/4" plywood back for squareness
- **Key challenge:** Squareness, back panel keeping it racked
- **Material notes:** 3/4" plywood or 1x12 common boards. 1/4" plywood back.

### Archetype 2: Frame & Panel
- **Examples:** Table, desk, workbench, bed frame
- **Structure:** Legs + aprons/rails + top surface
- **Typical joints:** Mortise & tenon (apron to leg), tabletop buttons/z-clips (top attachment)
- **Beginner version:** Pocket screws for apron-to-leg, elongated screw holes for top
- **Key challenge:** Wood movement in solid top, leg-to-apron racking resistance
- **Material notes:** Legs from 4x4 or laminated 2x stock. Aprons from 1x4/1x6.

### Archetype 3: Chair / Complex Angles
- **Examples:** Kitchen chair, stool, lawn chair
- **Structure:** Legs at angles, curved/shaped components, compound joinery
- **Typical joints:** Angled mortise & tenon, wedged tenons, turned spindles
- **Beginner version:** Simplified square stool with straight legs and pocket screws
- **Key challenge:** Compound angles, consistency across 4 legs, racking loads
- **Material notes:** Hardwood strongly recommended for strength.

### Archetype 4: Box / Drawer
- **Examples:** Drawer, jewelry box, tool tote, storage box
- **Structure:** 4 sides + bottom, sometimes a lid
- **Typical joints:** Dovetail (traditional), finger/box joint (machine-friendly), rabbet + pin (simple)
- **Beginner version:** Rabbet joint + glue + pin nails, 1/4" plywood bottom in groove
- **Key challenge:** Squareness, bottom panel fitting, SketchUp small-face problem
- **Material notes:** 1/2" to 3/4" stock for sides, 1/4" plywood or hardboard for bottom.

### Archetype 5: Modular / Knockdown
- **Examples:** Loft bed, knockdown table, bunk bed, modular shelving
- **Structure:** Independent sub-assemblies connected with hardware
- **Typical joints:** Bolt + barrel nut between modules, M&T or dado within modules
- **Beginner version:** More bolts, fewer permanent joints
- **Key challenge:** Alignment across modules, structural rigidity, assembly sequence
- **Material notes:** Mix of construction lumber (structure) and 3/4" plywood (panels).

### Archetype 6: Outdoor / Structural
- **Examples:** Patio bench, planter, sawhorse, shed framing
- **Structure:** Overbuilt for weather and load, typically softwood
- **Typical joints:** Half-lap, carriage bolt, lag screw, notch
- **Beginner version:** Deck screws + construction adhesive
- **Key challenge:** Wood movement from weather, drainage, rot resistance
- **Material notes:** Red-toned 2x lumber (dense, holds fasteners). Avoid yellow-toned. Cedar for decking/non-structural. Bark side up.

---

## Section 4: Material & Tool Awareness

### Dimensional Lumber Reference

The skill must convert between nominal and actual dimensions:

| Nominal | Actual |
|---------|--------|
| 1x2 | 3/4" x 1-1/2" |
| 1x3 | 3/4" x 2-1/2" |
| 1x4 | 3/4" x 3-1/2" |
| 1x6 | 3/4" x 5-1/2" |
| 1x8 | 3/4" x 7-1/4" |
| 1x10 | 3/4" x 9-1/4" |
| 1x12 | 3/4" x 11-1/4" |
| 2x2 | 1-1/2" x 1-1/2" |
| 2x4 | 1-1/2" x 3-1/2" |
| 2x6 | 1-1/2" x 5-1/2" |
| 2x8 | 1-1/2" x 7-1/4" |
| 2x10 | 1-1/2" x 9-1/4" |
| 2x12 | 1-1/2" x 11-1/4" |

### Beginner Tool Tiers

**Tier 0 (Ana White minimum):** Tape measure, speed square, clamps, pencil, drill/driver, circular saw.
- Available joints: Butt + screw, pocket screw (with Kreg jig add-on)
- Cannot cut: dados, rabbets, mortises, dovetails

**Tier 1 (+ router):** Add router + straight bit + edge guide.
- Available joints: + Dado, rabbet, groove, roundover, chamfer
- Still cannot: mortise & tenon (without jig), dovetails

**Tier 2 (+ table saw):** Add table saw, dado stack, miter gauge.
- Available joints: + Finger/box joint (with jig), half-lap, precise miters
- Approaching: mortise (with router) + tenon (with table saw)

**Tier 3 (full shop):** Add bandsaw, drill press, planer, jointer.
- All joints available including hand-cut dovetails, compound angles

The skill should ask about available tools when the user's tool tier isn't already known, and constrain joint recommendations accordingly.

### Finish Implications for Joint Selection

| Finish type | Joint implications |
|-------------|-------------------|
| Paint | Pocket holes can be filled. Butt joints hidden. Precision matters MORE (mistakes visible on flat painted surfaces). |
| Stain | Pocket holes need plugs or hidden placement. Wood filler won't take stain evenly. Choose joints that are hidden or decorative. |
| Natural/oil | Cleanest joints required. Dovetails, M&T become decorative features. No filler. |
| Outdoor | Hardware-based joints preferred (bolts, screws). Glue joints may fail from moisture cycling. |

---

## Section 5: Eval Structure

### Layer 1: Decision Evals (50-100 cases, no SketchUp needed)

Test the skill's reasoning. Prompt-to-expected-answer pairs.

**Categories:**
- Joint selection (connection type + material + skill level -> recommended joint)
- Plan tier selection (project type + complexity -> required artifacts)
- Dimension/proportion reasoning (stock dimensions -> joint dimensions)
- Material selection (project type + environment -> wood recommendation)
- Tool constraint awareness (available tools -> feasible joints)
- Wood movement awareness (cross-grain attachment -> correct method)

**Example cases:**

| Category | Prompt | Expected |
|----------|--------|----------|
| Joint selection | "Joining 3/4" shelf into 3/4" pine upright" | Dado, 3/8" deep. Bail-out: cleat + pocket screws |
| Joint selection | "Attaching table apron to leg, white oak" | Mortise & tenon, blind, tenon 1/4" thick |
| Joint selection | "Drawer front to side, hardwood" | Half-blind dovetail. Bail-out: rabbet + pin nails |
| Wood movement | "Attaching solid tabletop to apron" | Buttons, z-clips, or elongated holes. NOT glue across grain |
| Tool constraint | "Beginner with circular saw + drill only" | Butt + screw, pocket screw (if they get a Kreg jig) |
| Plan tier | "Simple garage shelf from 2x4 and plywood" | Tier 1 |
| Plan tier | "Dining table, walnut, M&T" | Tier 2 |
| Dimensions | "Tenon for 3/4" rail into 1-1/2" leg" | 1/4" thick, centered, 1" deep min |
| Dimensions | "Dado for 3/4" plywood" | Width: 23/32" (actual plywood), depth: 3/8" |
| Material | "Indoor bookshelf, painted" | Common boards (pine/spruce) or 3/4" plywood |
| Material | "Outdoor bench frame" | Red-toned 2x lumber. Avoid yellow-toned. |
| Finish | "Pocket screw bookshelf, stained" | Plugged pocket holes or hidden placement |

**Scoring:** Exact match on joint/material type, within tolerance on dimensions, bail-out must be present for beginner contexts. Binary pass/fail per case.

### Layer 2: Tool Execution Evals (20-30 cases, requires SketchUp)

Test individual MCP operations.

**Joinery modeling:**

| Test | Setup | Operation | Verify |
|------|-------|-----------|--------|
| Cut dado | 3/4"x11-1/4"x36" board | `safe_cut_dado` 23/32" wide, 3/8" deep, 8" offset | `verify_bounds` |
| Drill bolt hole | 1-1/2"x3-1/2"x60" board | `safe_drill_hole` 5/16" radius, 1-1/2" depth | `verify_bounds` + solid check |
| Boolean mortise | 1-1/2"x3-1/2"x30" leg | `boolean_subtract` 1/4" x 1" x 3" cutter | `verify_bounds` -- void at location |
| Mortise & tenon pair | Leg + rail components | `create_mortise_tenon` | Both modified, interlocking |
| Finger joint | Two boards at corner | `create_finger_joint` | Both modified, interlocking |
| Dovetail | Drawer front + side | `create_dovetail` | Geometry valid |

**Scene/plan creation:**

| Test | Operation | Verify |
|------|-----------|--------|
| Front elevation | `create_scene` ortho camera | `verify_scenes` -- ortho, correct position |
| Section through dado | Scene + section plane | `take_screenshot` + visual |
| Exploded view | `create_exploded_view` | `verify_bounds` -- parts separated |
| Cut list accuracy | 5-part assembly | `generate_cutlist` -- 5 parts, correct dims |
| Multi-scene plan | Tier 2 scene set | `verify_scenes` -- all 6 required scenes |

**Scoring:** `verify_bounds` within 1/64" tolerance, `verify_scenes` for scene correctness, `generate_cutlist` matches expected BOM. Fully automated.

### Layer 3: Integration Evals (5-8 cases, requires SketchUp)

End-to-end project builds from natural language prompt to complete model + plan.

| Project | Archetype | Tier | Key joints | Tests |
|---------|-----------|------|------------|-------|
| Simple bookshelf (36x12x48, pine, 3 shelves) | Flat-pack | 2 | Dado, rabbet | Common beginner project |
| Kitchen table (30x48x30, oak) | Frame & panel | 2 | M&T, buttons | Wood movement awareness |
| Knockdown workbench (24x60x34, 2x lumber) | Knockdown | 2 | Half-lap, bolt | Structural + knockdown |
| Drawer box (for dresser) | Box | 2 | Dovetail/finger, groove | Small-face problem |
| Storage stair module (loft bed) | Modular | 3 | Dado, pocket, bolt | Complex multi-component |
| Pocket-screw bookshelf (Ana White style) | Flat-pack | 1 | Pocket screw, butt | Beginner tool constraints |

**Scoring rubric:**

| Criterion | Weight |
|-----------|--------|
| Joint selection appropriate | 25% |
| Geometry valid (all solids, correct dims) | 25% |
| Plan artifacts complete for tier | 25% |
| Cut list accurate | 15% |
| Beginner bail-out offered (when applicable) | 10% |

---

## Section 6: Corpus Structure

```
docs/corpus/
  joint-taxonomy.md              -- joint types, decision criteria, SketchUp modeling
  plan-artifact-spec.md          -- what a complete plan needs per tier
  project-archetypes.md          -- common project types and their patterns
  material-reference.md          -- dimensional lumber sizes, plywood, species properties
  tool-tiers.md                  -- beginner to full shop, joint feasibility per tier
  finish-guide.md                -- paint vs stain vs natural implications
  woodgears-ca/
    models/
      table.skp                  -- joint reference model (downloaded)
      table_with_scenes.skp      -- scenes/layers reference (downloaded)
      objects.skp                -- nested objects reference (downloaded)
    transcripts/
      tutorial2-drawing-objects.en-CA.vtt   -- measurements, pushpull
      tutorial5-scenes-layers.en-CA.vtt     -- layer/scene workflow
      tutorial7-svg-export.en.vtt
      tutorial8-clock-faces.en.vtt
    articles/                    -- scraped construction article summaries
  ana-white/
    building-quickstart.md       -- safety, workspace, tools, workflow
    wood-choosing-guide.md       -- species, sizes, plywood, indoor/outdoor
    painting-guide.md            -- finish steps, product recs, terminology
evals/
  layer1-decisions/
    joint-selection.json         -- 30+ decision test cases
    plan-tier-selection.json     -- 10+ tier selection cases
    dimension-reasoning.json     -- 10+ dimension calculation cases
    material-tool-finish.json    -- 15+ material/tool/finish cases
  layer2-execution/
    joinery-modeling.json        -- 10+ MCP tool operation tests
    scene-creation.json          -- 10+ scene/plan tests
  layer3-integration/
    bookshelf.json               -- end-to-end project spec
    kitchen-table.json
    workbench.json
    drawer-box.json
    loft-bed-module.json
    pocket-screw-bookshelf.json
  scoring.md                     -- how to score each layer
  eval-runner.sh                 -- automation script
```

---

## Section 7: Skill Improvement Strategy

After building the corpus and eval infrastructure:

1. **Establish baseline** -- run all evals against current skill. Record scores per layer and category.
2. **Identify weakest areas** -- which eval categories have lowest pass rates?
3. **Targeted skill updates** -- for each weak area:
   - Add the minimum knowledge to the skill's reference files
   - Re-run that eval category
   - Confirm improvement without regression
4. **Integration validation** -- run Layer 3 after each batch of skill changes
5. **Iterate** -- repeat until target scores are met

**Target scores:**
- Layer 1: 90% pass rate (decision quality)
- Layer 2: 95% pass rate (tool execution reliability)
- Layer 3: 80% weighted score (integration quality)

### What gets added to the skill vs. stays in corpus

| In the skill | In the corpus |
|-------------|---------------|
| Joint selection decision tree (compact) | Full joint taxonomy with history and rationale |
| Plan tier rules | Complete artifact spec with examples |
| Archetype templates (compact) | Detailed project analysis |
| Tool tier awareness prompts | Ana White / woodgears.ca source material |
| Dimensional lumber lookup | Construction article summaries |
| Finish-aware joint guidance | Raw transcripts and .skp models |

The skill stays lean. The corpus is the reference library.

---

## Implementation Order

1. Write corpus reference documents (joint-taxonomy.md through finish-guide.md)
2. Scrape remaining woodgears.ca construction articles
3. Summarize Ana White PDFs into corpus markdown
4. Build Layer 1 eval cases (JSON)
5. Run Layer 1 baseline against current skill
6. Build Layer 2 eval cases
7. Build Layer 3 eval cases
8. First skill improvement pass (joint selection + plan tiers)
9. Second pass (material/tool/finish awareness)
10. Third pass (archetype templates)
11. Final integration validation
