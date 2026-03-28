# Project Archetypes for Furniture Design

Every furniture project fits one of six structural archetypes. Identifying the archetype early determines component naming, modeling order, joint selection, and plan complexity. When a user describes a project, match it to an archetype before doing anything else.

---

## 1. Flat-Pack / Panel Assembly

**Examples:** Bookcase, garage shelf, storage shelf, media console, mudroom cubby, pantry shelving unit

**Structural pattern:** Vertical uprights support horizontal shelves. A back panel squares the carcass. All parts are flat panels — no turned legs, no curves, no angles. The simplest archetype structurally and the most common first project.

**Typical joints:**
- Dado (shelf into upright) — the defining joint of this archetype
- Rabbet (back panel into carcass)
- Butt + screws (Tier 0 fallback)
- Shelf pin holes for adjustable shelves
- Edge banding on plywood edges (optional, cosmetic)

**Beginner version:** Pocket screws join shelves to uprights. Shelf pins replace fixed dado shelves (more forgiving — no dado cuts required). 1/4" plywood back nailed into a rabbet or simply stapled flush to the back edges. Paint-grade pine or birch plywood.

**Key challenge:** Squareness. A carcass with no back panel racks immediately. The back panel is structural — it holds the box square. Attach the back before removing clamps. Check diagonals: if both diagonals are equal, the carcass is square.

**Material notes:**
- Uprights and shelves: 3/4" plywood (cabinet-grade birch for paint, hardwood veneer ply for stain) or solid 1x12 boards
- Back panel: 1/4" plywood or 1/4" hardboard (Masonite)
- Face frame (optional): 1x2 or 1x3 solid wood, pocket-screwed or glued to front edges
- Edging: Iron-on veneer edge banding or solid wood strips for exposed plywood edges

**Typical dimensions:**
- Width: 30-48" (single section), wider units built as multiples
- Depth: 10-14" (books and media need 10-12", pantry shelves 14-16")
- Height: 36" (counter height), 48" (mid-height), 72" (floor-to-ceiling)
- Shelf spacing: 10-12" for books, 14-16" for binders, adjustable is better than fixed

**Component naming conventions:**
- `Left_Side`, `Right_Side` — vertical uprights
- `Top`, `Bottom_Shelf` — horizontal members forming the box
- `Shelf_1`, `Shelf_2`, ... — interior shelves (numbered bottom to top)
- `Back_Panel` — 1/4" back
- `Face_Frame_Left_Stile`, `Face_Frame_Top_Rail` — face frame members (if present)
- `Trim_Base_Front`, `Trim_Crown` — decorative trim (if present)

**Tag organization:**
- `Sides` — left and right uprights
- `Shelves` — all horizontal shelf members including top and bottom
- `Back` — back panel
- `Trim` — face frame, base molding, crown, edge banding
- `Hardware` — shelf pins, cam locks (if knockdown)

**Modeling order:**
1. Left and right sides (define the carcass height and depth)
2. Top and bottom shelf (define the width, complete the box)
3. Interior shelves (position within the box)
4. Back panel (flush to rear edges)
5. Face frame and trim (applied to front)
6. Hardware (shelf pins, hinges if doors added)

**Default plan tier:** Tier 2 (dado + rabbet require router or table saw). Tier 0 version uses pocket screws and shelf pins.

---

## 2. Frame & Panel

**Examples:** Dining table, desk, workbench, coffee table, nightstand, bed frame, console table

**Structural pattern:** Four legs connected by horizontal aprons form a rigid frame. A top sits on the frame but is not glued to it — it must float to accommodate wood movement. Stretchers between legs add rigidity when aprons alone are not enough. This is the workhorse archetype for any piece with legs.

**Typical joints:**
- Mortise and tenon (apron into leg) — the defining joint of this archetype
- Buttons or Z-clips (top attachment, allows cross-grain movement)
- Drawbore pin (locks M&T without clamps)
- Pocket screws (Tier 0 substitute for M&T)
- Half-lap (stretcher intersections)
- Dowel joint (simpler alternative to M&T)

**Beginner version:** Pocket screws join aprons to legs (drill into apron, screw into leg). Elongated screw holes or store-bought figure-8 fasteners attach the top. Add a lower stretcher shelf (flat panel between the legs near the floor) to prevent racking — it compensates for the weaker pocket-screw joint. Paint-grade.

**Key challenge:** Two problems dominate this archetype. First, wood movement: a solid-wood top expands and contracts across its width (not length) with humidity changes. If the top is glued or screwed tightly to the aprons, it will crack. Buttons, Z-clips, or elongated holes solve this. Second, racking: the frame must resist side-to-side force. Deep aprons (4-6") and tight M&T joints provide racking resistance. Pocket screws alone may not — add stretchers or a shelf.

**Material notes:**
- Legs: 2.5-3.5" square. Use 4x4 (actual 3.5" square) for rustic/farmhouse, or laminate two 8/4 boards for fine furniture. Tapered legs milled from 8/4 stock for MCM/Danish Modern style.
- Aprons: 3/4" thick, 4-6" wide. Solid hardwood. Wider aprons resist racking better but reduce legroom.
- Top: 3/4"-1" solid wood (edge-glued panels), or 3/4" plywood with solid-wood edge banding for a budget build. Desk tops can be 3/4" ply with laminate.
- Stretchers: Same dimensions as aprons or smaller. H-stretcher or box stretcher configurations.

**Typical dimensions:**
- Dining table: 60-72"L x 36-40"W x 30"H (seats 6-8)
- Desk: 48-60"W x 24-30"D x 30"H
- Coffee table: 48"L x 24"W x 16-18"H
- Nightstand: 20-24"W x 16-20"D x 24-26"H
- Workbench: 60-96"L x 24-30"D x 34-36"H (user's elbow height minus ~4")

**Component naming conventions:**
- `Leg_FL`, `Leg_FR`, `Leg_BL`, `Leg_BR` — front-left, front-right, back-left, back-right
- `Apron_Front`, `Apron_Back`, `Apron_Left`, `Apron_Right`
- `Top` — the tabletop (single component even if edge-glued from multiple boards)
- `Stretcher_Front`, `Stretcher_Side_L`, `Stretcher_Cross` — lower frame members
- `Cleat_Front`, `Cleat_Side` — top-attachment cleats (if used instead of buttons)
- `Drawer_Box` — nested Box archetype (if drawers are included)

**Tag organization:**
- `Legs` — all four legs
- `Aprons` — all apron members
- `Top` — tabletop
- `Stretchers` — lower frame members (if present)
- `Hardware` — buttons, Z-clips, bolts, drawer slides
- `Drawers` — drawer boxes and fronts (if present)

**Modeling order:**
1. Legs (establish the four corners and height)
2. Aprons (connect legs, define the frame footprint)
3. Stretchers (if used, add lower rigidity)
4. Top (rest on frame, overhang 1-2" per side typical)
5. Drawers and hardware (last — they fit within the frame)

**Default plan tier:** Tier 2 (M&T requires router + table saw, or dedicated mortiser). Tier 0 version uses pocket screws + stretcher shelf.

---

## 3. Chair / Complex Angles

**Examples:** Kitchen chair, dining chair, bar stool, step stool, Adirondack chair, rocking chair, lawn chair

**Structural pattern:** Angled legs splay outward for stability. Rear legs often extend upward to form the back. Seat may be flat, scooped, or woven. Compound angles (simultaneously angled in two planes) are common. This is the most difficult archetype — chairs endure more racking force per joint than any other furniture type because humans lean, shift, and push back.

**Typical joints:**
- Angled mortise and tenon (leg to seat rail, leg to stretcher)
- Wedged through-tenon (visible, decorative, and mechanically strong)
- Dowel joint (simpler alternative to angled M&T)
- Bridle joint (back to seat junction)
- Half-lap (stretcher intersections)
- Pocket screws (Tier 0 only — weak under chair loads; reinforce with glue blocks)

**Beginner version:** Square stool with straight legs (no angles). Four legs, four aprons, a flat seat. Pocket screws with corner glue blocks for racking resistance. Keep all angles at 90 degrees. This is a Frame & Panel build mechanically — the "chair" archetype only applies when angles are introduced.

**Key challenge:** Compound angles. A leg that splays 5 degrees to the side AND rakes 5 degrees front-to-back requires a compound-angle mortise in the seat rail. This is hard to lay out, hard to cut, and hard to model in SketchUp. The SketchUp small-face problem also surfaces when modeling tenons at angles on thin stock. Scale up the model (10x) when cutting joinery at compound angles.

**Material notes:**
- Hardwood only. Chairs take enormous stress relative to their size. Softwood will fail at the joints.
- Legs: 1.5-2" square, hardwood (oak, maple, walnut, ash). Ash is traditional for Windsor chairs (steam-bends well).
- Seat: 1-1.5" thick hardwood slab (scooped for comfort), or woven (rush, Danish cord, webbing).
- Back: Steam-bent or lamination-bent spindles/slats, or straight slats with angled joinery at the ends.
- Stretchers: 3/4"-1" round or square stock. Turned stretchers are common on traditional chairs.

**Typical dimensions:**
- Dining chair: Seat 16-18" off floor, seat depth 15-17", seat width 16-18", total height 32-36"
- Bar stool: Seat 28-30" off floor (for 40-42" counter), add footrest at 12-14" from floor
- Step stool: 8-12" height per step, 12-14" deep, 16-20" wide
- Adirondack: Seat 14" off ground, reclined 25-30 degrees, armrests at 24"

**Component naming conventions:**
- `Leg_FL`, `Leg_FR`, `Leg_BL`, `Leg_BR` — splayed legs
- `Back_Leg_L`, `Back_Leg_R` — when rear legs extend to form the back
- `Seat_Rail_Front`, `Seat_Rail_Back`, `Seat_Rail_Left`, `Seat_Rail_Right`
- `Seat` or `Seat_Slab` — the seat itself
- `Back_Rail_Top`, `Back_Rail_Bottom` — horizontal back frame
- `Back_Slat_1`, `Back_Slat_2`, ... — vertical back members
- `Stretcher_Front`, `Stretcher_Side_L`, `Stretcher_Side_R`, `Stretcher_Back`
- `Armrest_L`, `Armrest_R` — armrests (if present)

**Tag organization:**
- `Legs` — all legs
- `Seat` — seat slab or woven seat frame
- `Back` — back rails, slats, and spindles
- `Stretchers` — lower bracing between legs
- `Arms` — armrests and arm supports (if present)
- `Hardware` — bolts, wedges, pins

**Modeling order:**
1. Legs (establish splay angles and overall footprint)
2. Seat rails (connect legs at seat height, define angles)
3. Seat (rest on or join to rails)
4. Back assembly (back legs extending up, or separate back posts + rails + slats)
5. Stretchers (brace legs near the floor)
6. Armrests (if present, connect back legs to front legs at arm height)

**Default plan tier:** Tier 2-3 (angled M&T requires Tier 3 tools; straight-leg stool version is Tier 2). Beginner square stool is Tier 0.

---

## 4. Box / Drawer

**Examples:** Drawer, jewelry box, keepsake box, tool tote, wine crate, desk organizer, blanket chest

**Structural pattern:** Four sides joined at the corners surround a bottom panel captured in a groove. The simplest closed form in woodworking. Drawers are boxes that slide; chests are boxes with lids. Complexity comes from the corner joints (dovetails, finger joints) and interior divisions.

**Typical joints:**
- Dovetail (through or half-blind) — the prestige joint for this archetype
- Finger/box joint — easier than dovetails, still attractive
- Rabbet + pin nails (fast, hidden by paint or a drawer front)
- Lock rabbet (interlocking, machine-cut on table saw)
- Miter + spline (seamless corners for decorative boxes)
- Groove (bottom panel captured in a groove on all four sides)

**Beginner version:** Rabbet joint at corners, glued and reinforced with 23-gauge pin nails or small brads. 1/4" plywood bottom captured in a groove (cut the groove before assembly) or nailed to the bottom face. If no router or table saw for grooves, nail the bottom flush and add a thin trim strip to hide the edge. Paint-grade.

**Key challenge:** Squareness and the SketchUp small-face problem. A box that is 0.5 degrees out of square will never close properly with a fitted lid, and drawers will bind. Clamp across both diagonals during glue-up — adjust until diagonals are equal. In SketchUp, thin stock (1/4" bottom, 1/2" sides) creates tiny faces at joints that SketchUp may refuse to form. Work at 10x scale (model in inches but multiply all dimensions by 10), then scale down when complete.

**Material notes:**
- Sides: 1/2" to 3/4" solid wood (hardwood for dovetail boxes, pine or poplar for painted drawers)
- Bottom: 1/4" plywood or hardboard, captured in a 1/4" groove routed 1/4" up from the bottom edge
- Drawer front (if separate from box): 3/4" hardwood, sized to overlay or inset into the face frame
- Lid (for boxes): 1/2"-3/4" solid wood, grain-matched to the box front
- Dividers: 1/4" plywood or 1/2" solid wood, captured in dadoes

**Typical dimensions:**
- Kitchen drawer: 4-6"H x 20-22"D x width varies (face frame opening minus 1" for slides)
- Jewelry box: 3-5"H x 8-12"W x 6-8"D
- Blanket chest: 18-20"H x 36-48"W x 18-20"D
- Tool tote: 6-8"H x 16-24"L x 8-10"W, open top with center handle
- Desk organizer: 4-6"H x 12-16"W x 8-10"D, multiple compartments

**Component naming conventions:**
- `Side_Left`, `Side_Right` — long sides (or use `Side_Front`, `Side_Back` for drawers where front/back are the long dimension)
- `Side_Front`, `Side_Back` — short sides (or `End_Left`, `End_Right` for boxes)
- `Bottom` — the bottom panel
- `Front` — applied drawer front (if different from box front)
- `Lid`, `Lid_Frame`, `Lid_Panel` — lid components (for boxes)
- `Divider_1`, `Divider_2` — interior partitions
- `Handle` or `Pull` — hardware or integral handle

**Tag organization:**
- `Sides` — all four sides of the box
- `Bottom` — bottom panel
- `Front` — applied front (drawers) or decorative face (boxes)
- `Dividers` — interior partitions and organizer grids
- `Lid` — lid and lid hardware (boxes with lids)
- `Hardware` — pulls, hinges, slides, catches

**Modeling order:**
1. Sides (define box dimensions, include joinery profiles at corners)
2. Bottom (sized to fit grooves in all four sides)
3. Applied front (if drawer — overlays the box front)
4. Dividers (fit inside the assembled box)
5. Lid (if box — hinged or sliding)
6. Hardware (pulls, slides, hinges)

**Default plan tier:** Tier 2 (finger joints and grooves require table saw; dovetails require Tier 3). Tier 0 version uses rabbet + pin nails.

---

## 5. Modular / Knockdown

**Examples:** Loft bed, bunk bed, modular shelving system, sectional storage cubes, knockdown workbench, bed frame with bolt-together rails

**Structural pattern:** Independent sub-assemblies (modules) are built separately, then bolted together on site. Each module is self-contained and can use any of the other archetypes internally (a loft bed module might be Frame & Panel for the posts-and-rails, and Flat-Pack for the stair storage). The defining feature is the connection between modules: mechanical fasteners (bolts, barrel nuts, bed rail hardware, cam locks) that can be disassembled and reassembled.

**Typical joints:**
- Bolt + barrel nut (between modules) — the defining joint of this archetype
- Bed rail fastener / hook hardware (bed-specific module connections)
- Cam lock + dowel pin (flat-pack furniture hardware, IKEA-style)
- Mortise and tenon (within a module)
- Dado and rabbet (within a module, especially storage modules)
- Pocket screws (within modules at Tier 0)
- Half-lap (within frame modules)

**Beginner version:** More bolts, fewer permanent joints. Use 3/8" hex bolts with barrel nuts or T-nuts at every module-to-module connection. Within each module, use pocket screws. Pre-drill everything with a drill press or drilling jig for alignment. Make alignment marks (triangle marks across joints) during dry assembly so modules go back together the same way.

**Key challenge:** Alignment between modules and assembly sequence. Bolt holes must line up perfectly across modules that were built at different times. Use a drilling template (a piece of hardboard with precisely located holes) shared across all modules. Plan the assembly sequence — some bolts become inaccessible after other modules are attached. Document the sequence and include it with the plans.

**Material notes:**
- Posts/frame: 4x4 construction lumber (SPF or Douglas fir) for bed frames, or 2x stock laminated for custom dimensions
- Panels: 3/4" plywood (cabinet-grade for visible surfaces, CDX for hidden structure)
- Rails and stretchers: 2x6 or 2x8 for beds, 1x4/1x6 for shelving
- Hardware: 3/8" hex bolts (3-4" long), barrel nuts, T-nuts, bed rail brackets, washer on every bolt
- Slats: 1x4 or 2x4 spaced for mattress support (beds), no more than 3" gaps

**Typical dimensions:**
- Loft bed: 42-80"W x 76-82"L (mattress + 2"), 65-72" clearance under loft, total height depends on ceiling
- Bunk bed: Same footprint, 36" between mattress tops minimum
- Modular cube shelving: 15-16" cubes (fits vinyl records and standard storage bins)
- Knockdown workbench: 48-96"L x 24-30"D x 34-36"H, bolt-together trestle base

**Component naming conventions:**
Name by module first, then by part:
- `Stair_Module_Post_FL`, `Stair_Module_Shelf_1` — stair module parts
- `Loft_Module_Post_FL`, `Loft_Module_Rail_Front` — loft/bed module parts
- `Desk_Module_Panel_Top`, `Desk_Module_Panel_Side_L` — desk module parts
- For bed-specific: `Headboard`, `Footboard`, `Side_Rail_L`, `Side_Rail_R`, `Slat_1`...`Slat_N`
- Connection hardware: `Barrel_Nut_1`, `Bolt_1`, or group as `Hardware_Loft_to_Stair`

**Tag organization:**
Tags organized per module:
- `Module_Loft_Posts` — vertical members of loft module
- `Module_Loft_Rails` — horizontal members of loft module
- `Module_Loft_Panels` — panel members of loft module
- `Module_Stair_Posts`, `Module_Stair_Shelves`, `Module_Stair_Panels`
- `Module_Desk_Frame`, `Module_Desk_Panels`
- `Hardware` — all bolts, barrel nuts, bed rail brackets across all modules
- `Slats` — mattress support slats (beds)

**Modeling order:**
1. Design each module independently as its own group
2. Model the first module completely (posts, rails, panels, internal joinery)
3. Model connection points (bolt holes, barrel nut recesses) on the first module
4. Model the second module, starting from the shared connection face
5. Mirror connection points exactly between modules (use the drilling template concept — copy the hole pattern)
6. Position modules relative to each other in the final assembly
7. Verify clearances: door swings, stair headroom, mattress fit, bolt access with a wrench

**Default plan tier:** Tier 3 (multiple joint types across modules, precise alignment required). Individual modules may be Tier 0-2 internally.

---

## 6. Outdoor / Structural

**Examples:** Patio bench, garden planter, Adirondack chair, sawhorse, potting bench, pergola, shed framing, deck furniture, picnic table

**Structural pattern:** Overbuilt for weather, impact, and ground contact. Joints are mechanical (bolts, screws, lag screws) rather than glue-dependent because moisture cycling weakens glue bonds over time. Structure prioritizes drainage — no flat surfaces where water pools, no end grain touching the ground, no trapped moisture between mating surfaces. Everything slopes, drains, or is spaced for airflow.

**Typical joints:**
- Half-lap (strong, simple, allows water to drain through the joint)
- Carriage bolt (draws joint tight, resists pullout)
- Lag screw (heavy structural connections)
- Notch / bird's mouth (rafter to beam connections, structural)
- Deck screw (general-purpose, coated for corrosion resistance)
- Construction adhesive (outdoor-rated polyurethane, supplements screws)
- Through-bolt with washer (for legs and stretchers under load)

**Beginner version:** Deck screws everywhere + exterior-rated construction adhesive (Liquid Nails Heavy Duty or PL Premium). Pre-drill every hole — outdoor lumber splits easily. Counter-bore and plug screw holes if cosmetic appearance matters, or leave exposed (they weather to match). Use Simpson Strong-Tie connectors for structural connections instead of cutting complex joints.

**Key challenge:** Weather, drainage, and rot. Water is the enemy. Design every surface to shed water. Space slats 1/8"-1/4" apart so water drains and wood dries. Never trap water between two mating surfaces — if two boards touch, one should be able to dry. Slope flat surfaces 1-2 degrees so water runs off. Keep end grain off the ground (use plastic or metal feet). Choose rot-resistant species or pressure-treated lumber for ground contact.

**Material notes:**
- Primary structure: Pressure-treated (PT) lumber for ground contact and hidden structure, or naturally rot-resistant species (cedar, white oak, redwood, cypress)
- Visible surfaces: Western red cedar (lightweight, naturally rot-resistant, weathers to silver-gray) or redwood. Orient boards bark-side up — this resists cupping as the board dries.
- Fasteners: Stainless steel or coated (ACQ-compatible) hardware only. Untreated steel corrodes in contact with PT lumber and cedar (tannin reaction). Galvanized minimum, stainless preferred.
- Adhesive: Exterior-rated only. Titebond III (water-resistant, not waterproof) or polyurethane glue (Gorilla Glue) for joints that will see weather.
- Finish: Penetrating exterior stain/sealer, reapply every 1-2 years. No film-forming finishes outdoors (they trap moisture and peel).

**Typical dimensions:**
- Patio bench: 48-60"L x 16-18"D seat x 18" seat height, back to 34-36" total height
- Garden planter: 24-48"L x 12-18"W x 12-18"H, line with plastic or landscape fabric
- Sawhorse: 24-36"L top beam, 24-32" height, legs splay 15-20 degrees
- Picnic table: 72"L x 28-30"W tabletop, 30" table height, attached benches at 18"
- Adirondack chair: See Chair archetype for dimensions, add 2x material thickness for outdoor stock

**Component naming conventions:**
- `Frame_Post_FL`, `Frame_Post_FR` — structural uprights
- `Frame_Beam_Front`, `Frame_Beam_Back` — horizontal structural members
- `Frame_Brace_L`, `Frame_Brace_R` — diagonal bracing
- `Slat_1`, `Slat_2`, ... — seat slats, back slats, or deck boards (numbered in order)
- `Stretcher_Front`, `Stretcher_Cross` — lower frame members
- `Leg_FL`, `Leg_FR`, `Leg_BL`, `Leg_BR` — legs (if not integrated into frame posts)
- `Cap_Rail`, `Trim_Fascia` — decorative or protective top pieces

**Tag organization:**
- `Frame` — all structural members (posts, beams, braces, stretchers)
- `Slats` — all repeated surface members (seat, back, deck boards)
- `Hardware` — bolts, lag screws, Simpson ties, hinges
- `Trim` — cap rails, fascia, decorative elements
- `Feet` — ground-contact pads or levelers

**Modeling order:**
1. Frame (posts, beams, structural connections — this is the skeleton)
2. Bracing (diagonal or cross bracing for racking resistance)
3. Slats and cladding (seat slats, back slats, side panels — applied to frame)
4. Trim and caps (top rails, fascia, decorative pieces)
5. Hardware (model bolt heads and lag screw locations for the plan drawings)
6. Feet and ground-contact details (pads, spacers, concrete footings)

**Default plan tier:** Tier 2 (half-laps and notches require table saw or circular saw + chisel; basic screw-together version is Tier 0). Structural outdoor projects (pergola, shed framing) may require Tier 2-3 for precision cuts.

---

## How to Use This Document

### Matching a project to an archetype

When a user describes a project, identify the archetype by asking: what is the primary structural pattern?

| If the user says... | Archetype |
|---|---|
| "bookshelf," "shelving unit," "cabinet" (no legs) | Flat-Pack / Panel Assembly |
| "table," "desk," "bench with legs," "bed frame" | Frame & Panel |
| "chair," "stool with angled legs," "rocker" | Chair / Complex Angles |
| "drawer," "box," "chest," "tote" | Box / Drawer |
| "loft bed," "bunk bed," "has to come apart," "modular" | Modular / Knockdown |
| "patio," "outdoor," "planter," "sawhorse," "garden" | Outdoor / Structural |

### When archetypes combine

Real projects often combine archetypes. A desk with drawers is Frame & Panel (desk frame) + Box (drawer). A loft bed with storage stairs is Modular (overall) + Frame & Panel (bed module) + Flat-Pack (stair storage modules). Identify the primary archetype for the overall structure, then note sub-archetypes for nested components.

### Archetype drives the modeling order

Always follow the archetype's modeling order. Building the structure inside-out (starting with the defining structural members) prevents the most common beginner mistake: modeling decorative details before the structure is sound, then discovering that joints do not align.

### Archetype drives joint selection

Cross-reference the archetype's typical joints with the user's tool tier (see tool-tiers.md). If the archetype calls for M&T but the user is at Tier 0, substitute the beginner version's joints. Never recommend a joint the user cannot cut with their current tools without first explaining the tool requirement.
