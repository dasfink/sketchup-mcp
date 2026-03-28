# Sauna Building Reference for SketchUp Modeling

A sauna is not furniture — it is a small building with extreme thermal and moisture demands. This document synthesizes Finnish sauna building principles (Trumpkin/localmile.org), the Auerbach 8x12 blueprint (SaunaTimes), and real material cost data into a single reference for modeling saunas in SketchUp.

---

## 1. Project Overview

A proper sauna installation has four zones:

1. **Hot room** — the sauna itself. Insulated enclosure with heater, benches, and controlled ventilation.
2. **Changing room** — adjacent to hot room. Hooks, bench, towel storage. Transition space.
3. **Shower / wash area** — cold rinse between rounds. Can be outdoor hose, indoor shower, or lake.
4. **Cooling area** — porch, deck, or outdoor bench. Essential for the sauna cycle (heat, cool, repeat).

### Why sauna construction is different from regular building

- **Temperature range:** Interior air reaches 80-100 C (176-212 F). Materials must tolerate sustained heat without off-gassing, warping, or degrading.
- **Moisture cycling:** Each session dumps liters of water onto hot stones, creating massive steam bursts. The envelope must handle repeated wet-dry cycles without trapping moisture in the wall assembly.
- **Ventilation physics:** The entire experience depends on convective airflow. Fresh air must enter above the heater, rise across the ceiling, descend over bathers as gentle heat, and exhaust below the foot bench. Get this wrong and the sauna is stuffy, stratified, and unpleasant.
- **Vapor control:** Exactly ONE vapor barrier (foil-faced PIR), on the warm side of insulation. Never two vapor barriers — the wall assembly must dry to the outside. Trapped moisture rots framing.

### Key rules summary

| Rule | Value |
|------|-------|
| First Law of Lolyly | Feet above the stones — foot bench top must be at least 20 cm (8") above the top of the heater stones |
| Minimum hot room size | 250 x 250 x 260 cm (8'2" x 8'2" x 8'6" h) interior |
| Absolute minimum | 180 x 160 cm (6' x 5'3") — marginal, avoid if possible |
| Volume per person | 3-6 m3 |
| Ventilation rate | 9-12 L/sec (20-25 CFM) per person |
| Target CO2 | Below 700 ppm |
| Door swing | Outward, no latch (safety) |
| Ceiling shape | Flat preferred. Barrel vault OK if peak parallels bench wall. Slope higher over benches, lower over heater. |

---

## 2. Critical Measurements Table

All dimensions are from Trumpkin's guidelines unless noted. Imperial conversions are approximate.

### Room Dimensions

| Measurement | Metric | Imperial | Notes |
|-------------|--------|----------|-------|
| Minimum interior W x D | 250 x 250 cm | 8'2" x 8'2" | Square plan, simplest to build |
| Minimum interior height | 260 cm | 8'6" | Critical — 7' ceilings are the #1 North American mistake |
| Absolute minimum W x D | 180 x 160 cm | 6' x 5'3" | Marginal for one person, not recommended |
| Volume per bather | 3-6 m3 | 106-212 ft3 | Plan for peak occupancy |

### Bench Heights (measured from ceiling DOWN)

| Bench Level | Distance Below Ceiling | Height from Floor (in 8'6" room) | Purpose |
|-------------|----------------------|----------------------------------|---------|
| Sitting bench (top) | 110-120 cm (44-48") | ~152-157 cm (60-62") | Primary bathing position |
| Foot bench (middle) | 150-165 cm (60-65") | ~97-112 cm (38-44") | Feet rest here while sitting above |
| Step bench (bottom) | ~215 cm (85") from ceiling | ~45 cm (18") | Entry/exit step only |

### Bench Dimensions

| Measurement | Value | Notes |
|-------------|-------|-------|
| Bench depth (sitting) | 60-71 cm (24-28") minimum | 102 cm (40") ideal for lying down |
| Width per person | 60 cm (24") minimum | 66-76 cm (26-30") for comfort |
| Slat width | 22 x 83 mm (7/8" x 3-1/4") | 1x4 nominal |
| Slat gap | 10-22 mm (3/8" to 7/8") | Minimum 1/6 surface area open |
| Bench-to-wall gap | 5-7 cm (2-3") | Critical for steam circulation |
| Bench slat material | Abachi, Alder, Aspen, Linden | Lower thermal conductivity — cooler to touch |

### Heater Placement

| Measurement | Value | Notes |
|-------------|-------|-------|
| Distance from foot bench | 100-150 cm (40-60") minimum | Heater on opposite wall from benches |
| Foot bench above stones | 20 cm (8") minimum | First Law of Lolyly |
| Fresh air intake | Ceiling directly above heater | Mechanical downdraft for electric heaters |
| Exhaust vent | Below foot platform, bench wall | Mechanical powered extraction |

### Door

| Measurement | Value | Notes |
|-------------|-------|-------|
| Standard height | 193 cm (6'4") | Shorter doors (168 cm / 5'6") create larger heat cavity above |
| Rough opening (Auerbach) | 97 x 206 cm (38-1/4" x 81") | Actual blueprint dimension |
| Swing direction | Outward only | Safety — must never trap a person |
| Latch | None | Safety — occupant must always be able to exit |
| Seal | Tight weatherstripping | Minimize heat loss |

### Windows

| Measurement | Value | Notes |
|-------------|-------|-------|
| Rough opening (Auerbach) | 77 x 105 cm (30-1/8" x 41-3/8") | Changing room window |
| Hot room window | 76 x 46 cm (30" x 18") fixed transom | Recommended over full window in hot room |
| Center from end walls | 91 cm (36") | Auerbach blueprint |

---

## 3. Component Breakdown for SketchUp

This is a **framing project**, not furniture. The primary tool is `create_component_box` used to place individual studs, plates, joists, and rafters at actual lumber dimensions.

### Foundation / Floor Frame

| Component | Lumber | Qty (8x12 plan) | Notes |
|-----------|--------|-----------------|-------|
| Sill plates | 2x6 PT (1.5" x 5.5") | 2 @ 12', 2 @ 8' | Pressure-treated, contact with concrete/grade |
| Floor joists | 2x6 (1.5" x 5.5") | ~9 @ 8' | 16" OC spanning 8' direction |
| Rim joists | 2x6 (1.5" x 5.5") | 2 @ 12' | Close off joist ends |
| Subfloor | 3/4" plywood | 3 sheets (4x8) | T&G plywood, glued and screwed |

Hot room floor options (best to worst):
1. Heated concrete/tile with hydronic radiant heat (best — warm feet, easy to clean)
2. Wood frame + wood floor + linear drain (good — 5-10 C warmer at foot bench vs. concrete)
3. Unheated concrete (bad — sucks heat, increases stratification)

### Wall Framing

| Component | Lumber | Notes |
|-----------|--------|-------|
| Bottom plate | 2x4 KD (1.5" x 3.5") | Single plate on subfloor |
| Top plates | 2x4 KD (1.5" x 3.5") | Double top plate |
| Studs | 2x4 KD 84" (1.5" x 3.5" x 7') | 16" OC, precut length |
| Headers | 2x6 or 2x8 | Over door and window openings |
| Jack studs | 2x4 KD | Support headers at openings |
| King studs | 2x4 KD | Full-height studs flanking openings |
| Cripple studs | 2x4 KD | Above headers, below sills |

Auerbach blueprint: 7' studs yielding 7'4-1/2" subfloor-to-ceiling. Note: Trumpkin recommends minimum 8'6" ceiling. To reach 8'6", use 96" (8') studs with double top plate = approximately 8'5" to ceiling, or 10' studs cut to length.

### Wall Assembly (inside to outside)

This is the Finnish standard layup. Model each layer as a separate tag group.

| Layer | Material | Thickness | Tag |
|-------|----------|-----------|-----|
| Interior cladding | 1x4 T&G spruce (3/4" x 3-1/2") | 19 mm (3/4") | InteriorCladding |
| Air gap | Furring strips (1x2 or similar) | 10-20 mm (3/8"-3/4") | InteriorCladding |
| Vapor barrier | Foil-faced PIR (FinnFoam FF-PIR, Kingspan Sauna-Satu, Johns Manville AP) | Varies | WallFraming |
| Insulation | R-13 fiberglass or mineral wool in stud cavities | 3.5" (full stud depth) | WallFraming |
| Studs | 2x4 KD 16" OC | 3.5" | WallFraming |
| Sheathing | OSB or plywood | 7/16" - 1/2" | WallFraming |
| Rain screen | Furring strips | 3/4" | ExteriorCladding |
| Exterior cladding | WRC bevel siding (11/16" x 8") | 11/16" | ExteriorCladding |

**Critical rules:**
- NEVER two vapor barriers. The foil-faced PIR is the single vapor barrier (perm rating 0.1 or less). Structure dries to the outside.
- Air gap between foil and interior cladding is mandatory. It prevents thermal bridging, allows residual moisture to evaporate, and enables the foil to reflect radiant heat.
- T&G interior cladding: tongue UP, groove DOWN (prevents moisture pooling in groove). Horizontal orientation preferred over vertical. Pin one side only to allow wood movement.

### Roof Framing

| Component | Lumber | Notes |
|-----------|--------|-------|
| Rafters | 2x6 (1.5" x 5.5") | 16" or 24" OC |
| Ridge board | 2x8 (1.5" x 7.25") | Or structural ridge beam for cathedral ceiling |
| Collar ties | 2x4 | If needed for span |
| Fascia | 2x6 or 2x8 | Covers rafter tails |
| Soffit | Plywood or vented panel | Ventilated for roof drying |

Auerbach uses a reverse gable (ridge along the 8' side). Minimum 1' overhangs all around.

### Bench Structure

Three-level bench system. All bench components use the Benches tag.

| Component | Material | Dimensions | Notes |
|-----------|----------|------------|-------|
| Bench frame uprights | 2x4 softwood | Custom cut to height | Vertical supports screwed to wall blocking |
| Bench frame rails | 2x4 softwood | Span between uprights | Front and back rails at each level |
| Bench slats | Abachi, Alder, or Aspen | 7/8" x 3-1/4" (1x4 nominal) | Spaced with 3/8"-7/8" gaps |
| Backrest slats | Same as bench slats | Same dimensions | Angled 10-15 degrees, mounted on brackets |

**Bench rules:**
- No skirts (they block airflow). If skirts are used for aesthetics, recess 2-3" from front edge and make at least 30% permeable.
- 2-3" gap between bench slats and wall on all sides.
- Minimum 1/6 of bench surface area must be open air (1:5 gap-to-wood ratio).
- Build benches to be removable for annual deep cleaning.
- Bench depth: 24-28" minimum for sitting, 40" ideal for lying down.

### Heater Zone

| Component | Notes |
|-----------|-------|
| Heater | Model as simple box at manufacturer dimensions. Place on opposite wall from benches. |
| Heater guard rail | Wood railing 10-15 cm from heater on exposed sides |
| Cement board | 1/2" Durock behind and beneath heater. 6 sheets in Auerbach plan. |
| Stone mass | Heater stones fill the top basket. Top of stones defines the "Feet Above Stones" reference line. |

### Ventilation Ducts

| Component | Location | Notes |
|-----------|----------|-------|
| Fresh air intake | Ceiling directly above heater | Ducted with damper. Mechanical downdraft for electric heaters. |
| Exhaust vent | Below foot bench platform, on bench wall | Mechanical powered fan. This is where stale air exits. |
| Convective loop | Not a physical component | Air rises from heater, crosses ceiling, descends over bathers, returns to heater. Bathers should feel only descending convective heat. |

### Door and Windows

- Hot room door: solid core, well-sealed, opens outward, no latch. Model with weatherstripping detail.
- Changing room door: standard exterior man door, 38-1/4" x 81" RO.
- Windows: fixed transom in hot room (18" tall x 30" wide), operable window in changing room.

---

## 4. Construction Sequence

Order of operations for building (and for modeling — follow the same sequence in SketchUp for logical layer buildup):

1. **Foundation** — Concrete slab, piers, or skid frame. PT sill plates. Floor joists. Subfloor.
2. **Wall framing** — Bottom plates, studs at 16" OC, double top plates. Frame door and window rough openings with headers, jacks, kings, cripples.
3. **Roof framing** — Rafters, ridge, collar ties if needed. Sheathe roof.
4. **Sheathing** — OSB or plywood on exterior walls.
5. **Roofing** — Underlayment, shingles or metal roofing.
6. **Windows and exterior door** — Install in rough openings with flashing.
7. **Exterior rain screen and cladding** — Furring strips over sheathing, then WRC bevel siding.
8. **Electrical rough-in** — Heater circuit (240V, dedicated), lighting circuit, ventilation fan wiring. All wiring behind vapor barrier.
9. **Insulation** — R-13 fiberglass or mineral wool in stud cavities.
10. **Vapor barrier** — Foil-faced PIR over studs/insulation. Tape all seams. This is the ONLY vapor barrier.
11. **Furring strips** — Over foil-faced PIR, creating 10-20mm air gap.
12. **Interior cladding** — 1x4 T&G spruce, horizontal, tongue up. Pin one side only.
13. **Cement board** — Behind and below heater location.
14. **Bench framing** — Install wall blocking first, then bench uprights and rails.
15. **Bench slats** — Removable slats on rails. Verify gaps (1:5 ratio minimum).
16. **Heater installation** — Mount heater, connect electrical, load stones.
17. **Ventilation** — Install intake duct above heater, exhaust fan below foot bench. Test airflow.
18. **Hot room door** — Hang door, outward swing, no latch, weatherstrip.
19. **Floor finish** — Tile, sealed concrete, or wood floor with drain in hot room.
20. **Changing room finish** — Standard interior finish, hooks, bench.

---

## 5. Material Specifications

Based on the 2013 Home Depot quote for the Auerbach 8x12 plan ("PRIEM SAUNA," Minneapolis), updated with Trumpkin's material recommendations.

### Framing

| Material | Qty | 2013 Cost | Notes |
|----------|-----|-----------|-------|
| 2x4 x 84" KD whitewood studs | 20 | $45 | Wall framing |
| 2x6 x 12' PT weathershield | 2 | Part of $39 | Sill plates, long walls |
| 2x6 x 8' PT weathershield | 4 | Part of $39 | Sill plates, short walls + extras |

### Insulation and Vapor Control

| Material | Qty | 2013 Cost | Notes |
|----------|-----|-----------|-------|
| R-13 kraft-faced 15" x 32' rolls | 10 | $79 | Stud cavity insulation |
| Reflectix 48" x 25' rolls | 3 | $99 | Radiant barrier — modern guidance prefers foil-faced PIR (FinnFoam, Kingspan Sauna-Satu, Johns Manville AP) |

### Exterior Cladding

| Material | Qty | 2013 Cost | Notes |
|----------|-----|-----------|-------|
| 11/16" x 8" x 8' WRC KD bevel cedar siding | 22 | $143 | Short wall runs |
| 11/16" x 8" x 12' WRC KD bevel cedar siding | 28 | $272 | Long wall runs |

### Interior Cladding

| Material | Qty | 2013 Cost | Notes |
|----------|-----|-----------|-------|
| 1x6 T&G cedar | 968 board feet | $1,045 | From Weekes Forest Products. **Modern guidance: use Nordic White Spruce or North American Spruce instead of cedar.** |

### Other Materials

| Material | Qty | 2013 Cost | Notes |
|----------|-----|-----------|-------|
| 1/2" x 3' x 5' Durock cement board | 6 sheets | $54 | Behind and below heater |
| Electrical (outlets, dimmers, wire, GFCI, boxes) | Lot | ~$150 est. | 240V heater circuit + lighting + fan |
| Windows and door | Per plan | Included | See Auerbach RO dimensions |

### 2013 Total: ~$2,415 (including tax and delivery to Minneapolis)

**Wood selection — what to use and what to avoid:**

| Use | Species | Why |
|-----|---------|-----|
| Interior cladding (best) | Nordic White Spruce | Low resin, pleasant scent, stable in heat |
| Interior cladding (good) | North American Spruce, Monterey Pine | Available, affordable, good performance |
| Interior cladding (acceptable) | Alder, Aspen | Low density, minimal resin |
| Bench slats | Abachi (Obeche), Alder, Aspen, Linden | Low thermal conductivity — stays cooler to touch |
| Exterior cladding | Western Red Cedar | Fine for EXTERIOR (no heat/steam exposure) |

| Avoid | Species | Why |
|-------|---------|-----|
| Interior — NEVER | Western Red Cedar | Contains Thujone (neurotoxin), respiratory irritant, overpowering odor. Not used in Finnish saunas. Acceptable only for exterior cladding. |
| Interior — NEVER | Pressure-treated lumber | Toxic chemicals release at sauna temperatures |
| Interior — Avoid | Pine with heavy resin | Resin bleeds at high temperatures, causes burns |

Board specification: 1x4 nominal (3/4" x 3-1/2" actual) tongue-and-groove. 90%+ of interior should be soft wood. Horizontal orientation. Tongue UP, groove DOWN. Pin one side only for wood movement.

---

## 6. SketchUp Modeling Approach

### Project Classification

- **Archetype:** Small building / framing project (not furniture)
- **Plan tier:** Tier 3 — full construction documentation with section cuts through wall assembly, bench detail views, ventilation path diagrams
- **Primary tool:** `create_component_box` for all framing members
- **Lumber dimensions:** Always use actual dimensions (2x4 = 1.5" x 3.5", 2x6 = 1.5" x 5.5", 1x4 = 0.75" x 3.5")

### Tag Structure

| Tag | Contents |
|-----|----------|
| Foundation | Sill plates, floor joists, rim joists, subfloor |
| WallFraming | Studs, plates, headers, jacks, kings, cripples, sheathing, insulation, vapor barrier |
| RoofFraming | Rafters, ridge board, collar ties, roof sheathing |
| InteriorCladding | Furring strips (air gap), T&G boards |
| ExteriorCladding | Rain screen furring, bevel siding |
| Benches | All three bench levels — uprights, rails, slats, backrests |
| Heater | Heater unit, guard rail, cement board |
| Ventilation | Intake duct, exhaust duct, fan unit, dampers |
| Door | Hot room door, changing room door, weatherstripping |
| Windows | All window units, trim |

### Component Naming Convention

Follow the pattern: `[Zone]_[Element]_[Qualifier]`

Examples:
- `HotRoom_Stud_Wall_North_01`
- `HotRoom_TopPlate_Wall_East`
- `HotRoom_Bench_Top_Slat_01`
- `HotRoom_Bench_Foot_Rail_Front`
- `ChangingRoom_Stud_Wall_South_01`
- `Foundation_Joist_01`
- `Roof_Rafter_01`

### Modeling Sequence

1. **Model the floor frame first.** Sill plates as boxes, then joists at 16" OC, then subfloor as a single thin box.
2. **Frame walls one at a time.** Bottom plate, studs, top plates. Frame openings with proper headers. Each wall can be a group or nested components.
3. **Frame the roof.** Rafters from wall plate to ridge.
4. **Add sheathing.** Thin boxes representing OSB on exterior walls and roof.
5. **Add interior layers.** Vapor barrier (thin plane or box), furring strips, T&G cladding (can be simplified as a single panel or modeled board-by-board for detail views).
6. **Add exterior layers.** Rain screen furring, then siding.
7. **Build benches.** Frame uprights and rails, then place slats with proper gaps.
8. **Place heater.** Simple box at manufacturer dimensions with cement board behind.
9. **Add ventilation components.** Duct runs, fan, damper.
10. **Create scenes.** Exterior view, interior hot room view, wall section cut, bench detail, ventilation diagram.

### Section Cut Scenes (Tier 3)

Essential section cuts for construction documentation:

| Scene | What it shows |
|-------|---------------|
| Wall Section | All layers from exterior cladding through air gap, sheathing, studs with insulation, foil-faced PIR, furring/air gap, interior T&G |
| Bench Section | Three bench levels with heights dimensioned from ceiling down, slat gaps, wall gaps, backrest angle |
| Ventilation Diagram | Intake above heater, convective loop path, exhaust below foot bench. Arrows showing airflow direction. |
| Floor-to-Ceiling Section | Full height showing floor assembly, wall-to-floor connection, wall-to-roof connection, ceiling height |
| Plan View (hot room) | Heater placement relative to benches, door swing, ventilation locations, bench footprint |

---

## 7. Common Mistakes

These are the reasons most North American saunas fail, per Trumpkin's analysis. Each one is a modeling and design decision.

### 1. Ceiling too low (7' or less)
- **Problem:** Benches end up in the cold stratified zone. Steam rises and pools in a thin layer at the ceiling with no room for bathers.
- **Fix:** Minimum 8'6" (260 cm) interior ceiling height. Use 8' or taller studs.

### 2. Benches too low
- **Problem:** Feet are below the heater stones. Cold feet, poor steam distribution, bathers sit in cool stratified air.
- **Fix:** Apply the First Law of Lolyly — foot bench top must be at least 8" above the top of the heater stones. Sitting bench 44-48" below ceiling.

### 3. No ventilation or wrong ventilation
- **Problem:** CO2 builds up, air goes stale, bathers feel headaches and fatigue. Blamed on "the sauna" when it is actually oxygen deprivation.
- **Fix:** Mechanical ventilation. Fresh air intake at ceiling above heater. Exhaust below foot bench on bench wall. 20-25 CFM per person.

### 4. Wrong heater type
- **Problem:** Heavy steel stoves produce too much radiant heat and weak convective loops. The air does not circulate properly.
- **Fix:** Use a stove with adequate stone mass for the room volume. Kuuma (wood-burning) or quality electric heaters sized to the room.

### 5. Using cedar for interior
- **Problem:** Western Red Cedar contains Thujone, a neurotoxin. At sauna temperatures it off-gasses, causing respiratory irritation and headaches. The strong odor overwhelms the sauna experience. It is not used in Finland.
- **Fix:** Nordic White Spruce (ideal), North American Spruce, Alder, or Aspen for interior cladding.

### 6. Two vapor barriers
- **Problem:** Moisture gets trapped between barriers, rotting the wall framing. Invisible damage that destroys the structure.
- **Fix:** Exactly one vapor barrier (foil-faced PIR on the warm side of insulation). Wall dries to the outside through vapor-permeable sheathing and rain screen.

### 7. No air gap behind interior cladding
- **Problem:** Interior T&G cladding pressed directly against foil creates thermal bridging and prevents the foil from reflecting radiant heat. Moisture behind cladding cannot evaporate.
- **Fix:** 10-20mm furring strips between foil and T&G cladding. This air gap is not optional.

### 8. No vestibule or changing room
- **Problem:** Heat dumps directly outside every time the door opens. No transition space for cooling. Clothes in the hot room.
- **Fix:** Adjacent changing room shares a wall with the hot room. Minimum space for bench, hooks, towel storage.

### 9. No cooling options
- **Problem:** The sauna cycle is heat-cool-repeat. Without cooling (cold plunge, shower, outdoor air), bathers cannot do multiple rounds.
- **Fix:** Plan for cooling from the start — outdoor shower, cold plunge tub, or at minimum proximity to cool outdoor air.

### 10. T&G installed wrong
- **Problem:** Tongue down / groove up collects moisture in the groove channel. Vertical orientation can trap water behind boards.
- **Fix:** Tongue UP, groove DOWN. Horizontal orientation. Pin one side only for movement.

---

## 8. Reference Links

- **Trumpkin's Notes on Building a Sauna** — localmile.org/trumpkins-notes-on-building-a-sauna/ — The most comprehensive single-document guide to Finnish sauna design principles. Covers physics, ventilation, bench geometry, materials, and common mistakes.
- **SaunaTimes.com** — saunatimes.com — Glenn Auerbach's site. Source of the 8x12 blueprint. Blog, community, and the "Sauna Build: From Start to Finnish" eBook.
- **Auerbach Pro Ranch Sauna Blueprint** — 8'x12' plan with two bench layout options (Option A: 7'4" bench area for 3 adults; Option B: 6' bench area with window view). Available through SaunaTimes.
- **Kuuma Stoves** — kuumastoves.com — Wood-burning sauna stoves recommended by Auerbach and the SaunaTimes community.
