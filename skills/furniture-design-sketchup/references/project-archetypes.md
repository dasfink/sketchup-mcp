# Project Archetypes

Every furniture project fits one of six structural archetypes. Identify the archetype before doing anything else — it determines components, modeling order, joints, and plan complexity.

## Quick Match

| User says... | Archetype |
|---|---|
| "bookshelf," "shelving unit," "cabinet" (no legs) | Flat-Pack / Panel Assembly |
| "table," "desk," "bench with legs," "bed frame" | Frame & Panel |
| "chair," "stool with angled legs," "rocker" | Chair / Complex Angles |
| "drawer," "box," "chest," "tote" | Box / Drawer |
| "loft bed," "bunk bed," "has to come apart," "modular" | Modular / Knockdown |
| "patio," "outdoor," "planter," "sawhorse," "garden" | Outdoor / Structural |

Real projects often combine archetypes. A desk with drawers = Frame & Panel + Box. A loft bed with storage stairs = Modular + Frame & Panel + Flat-Pack.

---

## 1. Flat-Pack / Panel Assembly

**Pattern:** Vertical uprights support horizontal shelves. Back panel squares the carcass.

**Defining joint:** Dado (shelf into upright). Bail-out: pocket screws + shelf pins.

**Tags:** `Sides`, `Shelves`, `Back`, `Trim`, `Hardware`

**Modeling order:** Sides → Top/bottom → Interior shelves → Back panel → Face frame/trim → Hardware

**Components:** `Left_Side`, `Right_Side`, `Top`, `Bottom_Shelf`, `Shelf_1`…`Shelf_N`, `Back_Panel`, `Face_Frame_*`

**Typical dims:** W 30–48", D 10–14", H 36/48/72". Shelf spacing 10–12" (books).

**Default tier:** Tier 2 (dado + rabbet). Tier 0 with pocket screws + shelf pins.

---

## 2. Frame & Panel

**Pattern:** Four legs connected by horizontal aprons form a rigid frame. Top floats on the frame.

**Defining joint:** Mortise and tenon (apron into leg). Bail-out: pocket screws + stretcher shelf.

**Tags:** `Legs`, `Aprons`, `Top`, `Stretchers`, `Hardware`, `Drawers`

**Modeling order:** Legs → Aprons → Stretchers → Top → Drawers/hardware

**Components:** `Leg_FL/FR/BL/BR`, `Apron_Front/Back/Left/Right`, `Top`, `Stretcher_*`

**Typical dims:** Dining 60–72"L × 36–40"W × 30"H. Desk 48–60"W × 24–30"D × 30"H. Coffee 48"L × 24"W × 16–18"H.

**Key challenge:** Wood movement — solid top must float (buttons/Z-clips). Racking — deep aprons + tight M&T.

**Default tier:** Tier 2. Tier 0 with pocket screws + stretcher.

---

## 3. Chair / Complex Angles

**Pattern:** Angled legs splay for stability. Rear legs often extend to form back. Compound angles common.

**Defining joint:** Angled M&T. Bail-out: straight-leg stool with pocket screws.

**Tags:** `Legs`, `Seat`, `Back`, `Stretchers`, `Arms`, `Hardware`

**Modeling order:** Legs → Seat rails → Seat → Back assembly → Stretchers → Armrests

**Components:** `Leg_FL/FR/BL/BR`, `Seat_Rail_*`, `Seat`, `Back_Rail_*`, `Back_Slat_*`, `Stretcher_*`

**Key challenge:** Compound angles. Use 10x scale in SketchUp for thin stock joinery.

**Material:** Hardwood only — chairs take enormous stress relative to size.

**Default tier:** Tier 2–3. Beginner square stool = Tier 0.

---

## 4. Box / Drawer

**Pattern:** Four sides joined at corners surround a bottom panel captured in a groove.

**Defining joint:** Dovetail (prestige) or finger joint. Bail-out: rabbet + pin nails.

**Tags:** `Sides`, `Bottom`, `Front`, `Dividers`, `Lid`, `Hardware`

**Modeling order:** Sides → Bottom → Applied front → Dividers → Lid → Hardware

**Components:** `Side_Left/Right`, `Side_Front/Back`, `Bottom`, `Front`, `Divider_*`, `Lid`

**Typical dims:** Kitchen drawer 4–6"H × 20–22"D. Jewelry box 3–5"H × 8–12"W. Blanket chest 18–20"H × 36–48"W.

**Key challenge:** Squareness. SketchUp small-face problem on thin stock — work at 10x scale.

**Default tier:** Tier 2 (finger joints). Tier 0 with rabbet + pin nails.

---

## 5. Modular / Knockdown

**Pattern:** Independent sub-assemblies bolted together on site. Each module may use any other archetype internally.

**Defining joint:** Bolt + barrel nut (between modules). Internal joints vary by module.

**Tags:** Per-module: `Module_X_Posts`, `Module_X_Rails`, `Module_X_Panels`. Plus `Hardware`, `Slats`.

**Modeling order:** Design each module independently → Model connection points → Position modules relative → Verify clearances

**Components:** Named by module: `Stair_Module_Post_FL`, `Loft_Module_Rail_Front`, etc.

**Key challenge:** Alignment between modules. Use a shared drilling template. Plan assembly sequence — some bolts become inaccessible.

**Default tier:** Tier 3 overall. Individual modules may be Tier 0–2.

---

## 6. Outdoor / Structural

**Pattern:** Overbuilt for weather. Mechanical joints (bolts, screws, lag screws). Everything slopes, drains, or is spaced for airflow.

**Defining joint:** Half-lap or carriage bolt. Bail-out: deck screws + construction adhesive.

**Tags:** `Frame`, `Slats`, `Hardware`, `Trim`, `Feet`

**Modeling order:** Frame → Bracing → Slats/cladding → Trim/caps → Hardware → Feet

**Components:** `Frame_Post_*`, `Frame_Beam_*`, `Frame_Brace_*`, `Slat_1`…`Slat_N`, `Cap_Rail`

**Key challenges:** Drainage (space slats 1/8–1/4"), end grain off ground, rot-resistant species or PT lumber, stainless/HDG fasteners.

**Default tier:** Tier 2. Screw-together version = Tier 0.

---

## Using Archetypes

1. **Match project → archetype** before modeling
2. **Follow the archetype's modeling order** — builds structure inside-out
3. **Cross-reference joints with tool tier** — if archetype calls for M&T but user is Tier 0, use the bail-out joints
4. **Combined archetypes:** identify primary archetype for overall structure, note sub-archetypes for nested components
