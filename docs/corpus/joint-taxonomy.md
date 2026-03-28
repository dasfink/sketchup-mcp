# Joint Taxonomy — Decision Framework for Furniture Joinery

This document catalogs every joint type used in furniture design, with a 12-field schema
per joint and a decision tree at the end. It is the primary reference for joint selection
in the furniture-design-sketchup skill.

All dimensions are in inches unless noted. "Beginner" means someone with a circular saw
and a drill; "Intermediate" adds a router and/or table saw; "Advanced" assumes a full shop.

---

## Table of Contents

1. [Channel Joints](#channel-joints) — Dado, Rabbet, Groove
2. [Frame Joints](#frame-joints) — Mortise & Tenon (variants), Dowel, Pocket Screw, Half-Lap
3. [Corner Joints](#corner-joints) — Dovetail (variants), Finger/Box, Rabbet + Pin, Butt + Screw
4. [Panel Joints](#panel-joints) — Biscuit, Tabletop Buttons/Z-Clips
5. [Knockdown Joints](#knockdown-joints) — Bolt + Barrel Nut, Bed Rail Hardware, Cam Lock + Dowel
6. [Decision Tree](#decision-tree)
7. [Lookup Table](#lookup-table)

---

## Channel Joints

These joints house one board inside a channel cut into another. They excel at
shelf-into-side and back-panel-into-case connections.

---

### Dado

**1. Name & aliases:** Dado (US), housing joint (UK), trench joint.

**2. What it is:** A flat-bottomed channel cut across the grain of a board (perpendicular
to the long axis). The mating board slides into the channel for a flush or recessed fit.

**3. When to use:**
- Shelves into case sides (bookcase, cabinet, storage stairs).
- Dividers into a carcase.
- Any board-into-side connection where the shelf runs the full width.

**4. When NOT to use:**
- When the dado end will be visible on the front edge (use stopped/blind dado or
  face-frame to hide it).
- On boards thinner than 1/2" (the channel weakens them too much).
- When the joint must be disassembled (permanent once glued).

**5. Strength profile:**
| Load      | Rating    | Notes                                      |
|-----------|-----------|--------------------------------------------|
| Tension   | Low       | Shelf can pull out if not glued/pinned      |
| Compression | Excellent | Full-width bearing surface                |
| Shear     | Good      | Channel walls resist lateral movement       |
| Racking   | Moderate  | Helps stiffen a case, especially with back panel |

**6. Beginner-friendliness:** Intermediate. Requires a router with a straight bit or a
table saw with a dado stack. A circular saw + chisel is possible but slow and imprecise.

**7. Minimum tools required:**
- Tier 1: Router + straight bit + edge guide (or router table)
- Tier 2: Table saw + dado stack
- DIY option: Circular saw + chisel (not recommended for precision)

**8. Bail-out alternative:** Butt joint with shelf pins or cleats screwed to the side.
For painted pieces, pocket screws from the underside of the shelf into the side.

**9. SketchUp modeling approach:**

*MCP tool — `safe_cut_dado`:*
```
safe_cut_dado(
  component_name="Left Side",
  face="x+",           # inner face of left side
  z_start=10.0,        # bottom of dado (distance from bottom of board)
  z_end=10.75,         # top of dado (z_start + shelf thickness)
  depth=0.375           # 3/8" deep, half of 3/4" side
)
```

*WW library — `eval_ruby`:*
```ruby
WW.dado("Left Side", face: :inner, at: 10.0, width: 0.75, depth: 0.375)
```

*Verification:* After cutting, use `verify_bounds` to confirm the side board's bounding
box is unchanged (the dado is internal geometry, not a dimensional change).

**10. Wood species notes:**
- Softwood (pine, cedar): Use 1/3 depth rule — dado depth = 1/3 board thickness.
  Pine is soft enough that a snug fit matters; too loose and the shelf wobbles.
- Hardwood (oak, maple, walnut): Can go to 1/2 depth. Hardwood holds the channel
  walls well. Test-fit is critical — hardwood does not compress like pine.

**11. Typical dimensions (rules of thumb):**
- Width = exact thickness of the mating board (measure, do not assume nominal).
  For 3/4" plywood, width = 23/32" (0.719"), not 0.75".
- Depth = 1/4 to 1/2 of the board thickness. For a 3/4" side, depth = 1/4" to 3/8".
- Standard: 3/8" depth in 3/4" material (the most common case).

**12. Finish implications:**
- Hidden: The joint is fully hidden when the shelf is inserted.
- Through dado is visible on the front edge. If staining, consider a stopped dado
  or add a face frame.
- Paint: Through dado is acceptable — wood filler covers the visible end.

---

### Rabbet

**1. Name & aliases:** Rabbet (US), rebate (UK), step joint.

**2. What it is:** An L-shaped step cut along the edge or end of a board. Unlike a dado
(which is a channel in the middle), a rabbet removes material from the edge. The mating
board sits in the step.

**3. When to use:**
- Back panels into a case (the classic 1/4" plywood back).
- Joining two boards at a corner (e.g., drawer sides to drawer front).
- Reducing visible end grain at corners.

**4. When NOT to use:**
- As the sole joint on a heavy, load-bearing corner (not strong enough alone).
- On very thin stock (< 3/8") where the remaining wall is fragile.
- When the corner must resist racking without reinforcement.

**5. Strength profile:**
| Load      | Rating    | Notes                                      |
|-----------|-----------|--------------------------------------------|
| Tension   | Low       | Pulls apart easily without fasteners        |
| Compression | Good    | Step provides bearing surface                |
| Shear     | Moderate  | Step resists sliding in one direction        |
| Racking   | Low       | Needs back panel or fasteners for racking   |

**6. Beginner-friendliness:** Beginner-friendly with a router; straightforward on a
table saw. One of the first joints a new woodworker should learn.

**7. Minimum tools required:**
- Tier 1: Router + rabbeting bit (or straight bit with fence)
- Tier 2: Table saw (two passes)
- Tier 0: Circular saw + fence (for simple back-panel rabbets)

**8. Bail-out alternative:** Butt the back panel against the case back and nail/screw it.
Loses 1/4" of interior depth but requires no special cuts.

**9. SketchUp modeling approach:**

*WW library — `eval_ruby`:*
```ruby
WW.rabbet("Left Side", edge: :back_inner, width: 0.375, depth: 0.25)
```
Edge options: `:back_inner`, `:back`, `:front`, `:top_back`, `:bottom_back`.

*MCP tool — `boolean_subtract` (alternative):*
```
boolean_subtract(
  target="Left Side",
  cutter_type="box",
  position=[0, 11.0, 0],        # at back edge
  dimensions=[48.0, 0.375, 0.25] # full length, width, depth
)
```

*Verification:* Use `verify_bounds` — the bounding box will shrink by the rabbet
depth on the relevant axis.

**10. Wood species notes:**
- Works in all species. Softwood rabbets can split if nailed too close to the edge —
  pre-drill or use brads.
- Plywood: Standard for back-panel rabbets. Match the rabbet width to the plywood
  thickness (measure the actual sheet).

**11. Typical dimensions:**
- Back-panel rabbet: width = plywood thickness (typically 1/4"), depth = 3/8".
- Corner rabbet: width = mating board thickness, depth = 1/2 to 2/3 of the rabbeted
  board's thickness.

**12. Finish implications:**
- Back-panel rabbet: Hidden (back of case faces the wall).
- Corner rabbet: Partially visible. Pinning or nailing the corner leaves small holes.
  Paint hides easily; stain-grade benefits from a dovetail or finger joint instead.

---

### Groove

**1. Name & aliases:** Groove, plough (UK), slot. Sometimes confused with dado — the
difference is grain direction: a groove runs with the grain, a dado runs across it.

**2. What it is:** A flat-bottomed channel cut along the grain (parallel to the board's
long axis). Used to capture a panel (drawer bottom, frame-and-panel door panel) so it
can float without being glued.

**3. When to use:**
- Drawer bottoms into drawer sides and front.
- Frame-and-panel door construction (panel floats in grooves).
- Sliding mechanisms (e.g., sliding trays).

**4. When NOT to use:**
- When the channel must run across the grain (that is a dado, not a groove).
- On boards narrower than 2" (too fragile after the groove).
- When the panel must be removable (the groove is continuous, trapping the panel unless
  the back is left open).

**5. Strength profile:**
| Load      | Rating    | Notes                                      |
|-----------|-----------|--------------------------------------------|
| Tension   | Low       | Panel can slide out the open end             |
| Compression | Moderate | Panel bears on the groove bottom             |
| Shear     | Moderate  | Groove walls resist lateral panel movement   |
| Racking   | Low       | Groove alone does not prevent racking        |

**6. Beginner-friendliness:** Intermediate. Same tooling as a dado.

**7. Minimum tools required:**
- Tier 2: Table saw (single blade, multiple passes, or dado stack)
- Tier 1: Router + straight bit + fence (more setup, same result)

**8. Bail-out alternative:** For drawer bottoms, use a 1/4" panel stapled/nailed to the
bottom of the drawer box (flush bottom). Less elegant but functional.

**9. SketchUp modeling approach:**

*WW library — `eval_ruby`:*
```ruby
WW.groove("Drawer Front", face: :inside, from_edge: 0.25, width: 0.25, depth: 0.25)
```
Face options: `:inside` / `:bottom`, `:top`.

*MCP tool — `safe_cut_dado` can also be used for grooves* (the underlying geometry is
identical — a rectangular channel). Orient the component so the groove runs along the
face axis, then call:
```
safe_cut_dado(
  component_name="Drawer Front",
  face="y-",
  z_start=0.25,
  z_end=0.5,
  depth=0.25
)
```

**10. Wood species notes:**
- Softwood: Groove walls can compress under heavy drawer loads. Keep depth <= 1/3 thickness.
- Hardwood: Full 1/4" groove in 3/4" stock is standard. Clean cuts with sharp bits.
- Plywood: Measure actual panel thickness. Baltic birch 1/4" is often 6mm (0.236").

**11. Typical dimensions:**
- Drawer bottom groove: 1/4" wide x 1/4" deep, positioned 1/4" up from the bottom edge.
- Frame-and-panel groove: 1/4" wide x 3/8" deep, centered on the frame stock width.

**12. Finish implications:**
- Hidden by design: The groove is interior to the joint, covered by the captured panel.
- Drawer bottoms: Unfinished plywood is standard; finish the visible face if the drawer
  will be seen from below (open shelving).

---

## Frame Joints

Frame joints connect end-grain to face-grain or face-grain to face-grain in structural
frames (table legs to aprons, bed rails to posts, chair frames).

---

### Mortise and Tenon

**1. Name & aliases:** Mortise and tenon (M&T). Variants: through M&T, blind (stub) M&T,
haunched M&T, loose (floating) tenon, tusked tenon, wedged tenon.

**2. What it is:** A projecting tongue (tenon) on one board fits into a matching
rectangular pocket (mortise) in the other board. The fundamental frame joint of
furniture-making for thousands of years.

**3. When to use:**
- Table leg to apron.
- Bed rail to post.
- Chair frame connections.
- Door stile to rail.
- Any frame connection bearing structural load.

**4. When NOT to use:**
- Plywood or MDF (end-grain glue surface is poor; use dowels or biscuits instead).
- When disassembly is needed (use knockdown hardware instead, unless tusked/wedged).
- When the builder has no way to cut a mortise (requires router, drill press, or chisels).

**5. Strength profile:**
| Load      | Rating      | Notes                                        |
|-----------|-------------|----------------------------------------------|
| Tension   | Very Good   | Long-grain glue surface + mechanical interlock |
| Compression | Excellent | Shoulder bears directly                        |
| Shear     | Excellent   | Tenon walls resist shear in both directions    |
| Racking   | Excellent   | Gold standard for anti-racking in frames       |

**6. Beginner-friendliness:** Intermediate to advanced. Blind M&T requires precise mortise
cutting and tenon fitting. Loose tenon is more beginner-friendly (both parts get a mortise,
joined by a dowel-like loose tenon).

**7. Minimum tools required:**
- Tier 1 (blind/through): Router + mortising jig + straight bit; or drill + chisel
- Tier 2 (tenon cheeks): Table saw with miter gauge; or router table
- Tier 3 (advanced): Hollow-chisel mortiser, Festool Domino (loose tenon)
- Absolute minimum: Drill press + chisel for the mortise, hand saw for the tenon

**8. Bail-out alternative:**
- Loose tenon (easier than integral tenon — both parts get a mortise, connected by a
  separate floating tenon).
- Dowel joint (2-3 dowels provide ~70% of M&T strength with simpler tooling).
- Pocket screw (for paint-grade only; quick but weak in tension).

**9. SketchUp modeling approach:**

*MCP tool — `create_mortise_tenon`:*
```
create_mortise_tenon(
  mortise_id="<entity_id of leg>",
  tenon_id="<entity_id of apron>",
  width=1.5,
  height=3.0,
  depth=1.5,
  offset_x=0, offset_y=0, offset_z=0
)
```
The tool auto-detects which faces are closest and cuts the mortise pocket + shapes
the tenon projection.

*WW library — separate mortise + tenon calls via `eval_ruby`:*
```ruby
# Cut mortise in the leg
WW.mortise("Front Left Leg",
  face: :inner,        # Y=0 face
  at: [1.75, 2.0],     # [x, z] center on face
  size: [1.5, 3.0],    # [width, height] of opening
  depth: 1.5,          # blind mortise depth
  through: false
)

# Shape tenon on the apron
WW.tenon("Front Apron",
  end_face: :left,
  size: [1.5, 3.0],     # matches mortise opening
  length: 1.375         # slightly less than mortise depth for glue room
)
```

*Through tenon variant:* Set `through: true` in `WW.mortise`. The tenon extends past the
mortise board. Model the wedge kerfs with `kerf: 0.0625` on `WW.tenon`.

*Haunched tenon variant:* Model as a standard tenon with an additional shallow dado at the
top of the mortise board to house the haunch. Useful where the mortise is at the top of a
leg (prevents the mortise from opening up).

*Loose tenon variant:* Cut matching mortises in both boards; model the loose tenon as a
separate small component (e.g., `WW.board("Loose Tenon", [0.375, 1.5, 3.0])`).

*Verification:* Use `verify_bounds` on the mortise board — its bounding box should be
unchanged (internal pocket). The tenon board's length or width will be reduced by the
shoulder depth on the tenoned end.

**10. Wood species notes:**
- Softwood: Tenon should be snug but not forced — softwood crushes if the fit is too
  tight. Use 1/16" less than the mortise width for a glue-fit.
- Hardwood: Aim for a "firm hand-press" fit. Piston fit is the goal for oak/maple.
- Avoid M&T in plywood — the end grain layers delaminate under stress. Use dowels instead.

**11. Typical dimensions:**
- Tenon thickness = 1/3 of the mortise board's thickness. For a 1.5" leg, tenon = 1/2".
  For a 3/4" frame, tenon = 1/4".
- Tenon width = apron width minus 1/4" top and bottom (leave 1/8" shoulders, or 1/4"
  at top for a haunch).
- Tenon length = 2/3 to 3/4 of the mortise board's width. For a 3.5" leg, tenon = 2.5".
- Mortise depth = tenon length + 1/16" glue room.

**12. Finish implications:**
- Blind M&T: Completely hidden. No finish concerns.
- Through M&T: End grain of tenon is visible on the opposite face. This is a design
  feature in Arts & Crafts / MCM styles. Stain the end grain first (it absorbs more),
  or use contrasting wood for the tenon as a decorative element.
- Wedged through tenon: Highly decorative. Show the wedges in contrasting wood for effect.

---

### Dowel Joint

**1. Name & aliases:** Dowel joint, doweled joint, pin joint.

**2. What it is:** Two or more cylindrical wooden dowels inserted into mating holes in
both boards to create alignment and a glue surface. Functionally similar to a loose tenon
but using round pins instead of rectangular ones.

**3. When to use:**
- Frame joints where M&T is overkill or the builder lacks M&T tooling.
- Edge-to-edge panel glue-ups (alignment aid).
- Plywood or MDF joints where M&T does not work (dowels glue well in core material).
- IKEA-style knockdown when combined with cam locks.

**4. When NOT to use:**
- High-stress frame joints in hardwood furniture (M&T is stronger).
- Where precise alignment is critical and a doweling jig is unavailable (misalignment
  is common without a jig).
- Outdoor furniture (dowels can swell/shrink cyclically and loosen).

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Good      | Dowels resist pullout well with glue           |
| Compression | Good    | Bears on dowel + bottom of hole                |
| Shear     | Good      | Multiple dowels resist shear collectively      |
| Racking   | Moderate  | ~70% of M&T; adding a third dowel helps        |

**6. Beginner-friendliness:** Beginner-friendly with a doweling jig. Without a jig,
alignment is difficult and misdrilled holes are hard to fix.

**7. Minimum tools required:**
- Tier 0: Drill + doweling jig (Dowelmax, Jessem, or budget jig)
- Self-centering dowel jig + drill is the simplest setup

**8. Bail-out alternative:** Pocket screws (faster, no jig needed, but visible on one side).

**9. SketchUp modeling approach:**

*WW library via `eval_ruby`:*
```ruby
# Drill dowel holes in both boards
WW.bolt_hole("Leg", face: :inner, at: [1.75, 2.5], hole: 0.375, depth: 1.0)
WW.bolt_hole("Leg", face: :inner, at: [1.75, 5.5], hole: 0.375, depth: 1.0)
WW.bolt_hole("Apron", face: :left, at: [1.75, 2.5], hole: 0.375, depth: 1.0)
WW.bolt_hole("Apron", face: :left, at: [1.75, 5.5], hole: 0.375, depth: 1.0)
```

*MCP tool — `safe_drill_hole`:*
```
safe_drill_hole(
  component_name="Front Left Leg",
  center=[1.75, 0, 2.5],
  normal=[0, 1, 0],
  radius=0.1875,        # 3/8" dowel
  depth=1.0
)
```

**10. Wood species notes:**
- Use fluted or spiral-grooved dowels for glue distribution.
- Softwood: Dowels hold well but the surrounding wood can split — do not over-tighten
  clamps. Use 3/8" dowels in 3/4" stock.
- Hardwood: 3/8" or 1/2" dowels. Pre-drill slightly oversized for easy insertion with
  glue (drill 25/64" for 3/8" dowel in hardwood).

**11. Typical dimensions:**
- Dowel diameter = 1/3 to 1/2 of the thinner board's thickness.
  3/4" stock: 3/8" dowels. 1.5" stock: 1/2" dowels.
- Dowel length = 1.5" to 2" (split between the two boards).
- Hole depth = dowel length / 2 + 1/16" (room for glue and air).
- Spacing: 2" to 3" on center; at least 2 dowels per joint.

**12. Finish implications:**
- Hidden: Dowels are fully buried inside both boards. No visibility.
- If a dowel is exposed (through-dowel as a decorative pin), use contrasting wood
  and sand flush. This is a design feature in Shaker and MCM styles.

---

### Pocket Screw

**1. Name & aliases:** Pocket screw, pocket-hole joint, Kreg joint (brand name often
used generically).

**2. What it is:** A self-tapping screw driven at a 15-degree angle through a pocket hole
in one board and into the face grain of the mating board. The pocket hole is drilled with
a stepped bit in a jig.

**3. When to use:**
- Face frames.
- Quick cabinet assembly (paint-grade).
- Tabletop attachment (with elongated pocket holes for wood movement).
- Beginner projects where speed matters more than elegance.
- Joining plywood panels.

**4. When NOT to use:**
- Stain-grade or exposed fine furniture (pocket holes are visible and ugly).
- Joints under high tension (the screw can pull out of face grain).
- End-grain to end-grain (no holding power).
- Outdoor (screws corrode; joints loosen with wood movement).

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Low       | Screw in face grain can pull out under load    |
| Compression | Good    | Board shoulders bear directly                  |
| Shear     | Moderate  | Screw resists shear, but one screw is a pivot  |
| Racking   | Low       | Single pivot point; use 2+ screws per joint    |

**6. Beginner-friendliness:** Excellent. The most beginner-friendly structural joint.
A Kreg jig, drill, and driver are all that is needed.

**7. Minimum tools required:**
- Tier 0: Pocket-hole jig + drill/driver + pocket screws
- No table saw, router, or chisels required.

**8. Bail-out alternative:** This IS the bail-out for most joints. If pocket screws are
unacceptable, step up to dowels or a simple M&T.

**9. SketchUp modeling approach:**

Pocket screws are typically modeled as annotation rather than geometry in SketchUp.
The joint appears as a simple butt joint in the model.

*Modeling the butt joint:*
```ruby
# Just position the boards in contact — no cut geometry needed
WW.board("Face Frame Stile", "1x2", 30)
WW.board("Face Frame Rail", "1x2", 14.5)
WW.place("Face Frame Rail", [0.75, 0, 12.0])
```

*If pocket holes must be shown:*
```ruby
# Drill angled pocket holes (visual only)
WW.pilot_hole("Face Frame Rail", face: :back, at: [0.375, 0.75], dia: 0.375, depth: 1.0)
```

**10. Wood species notes:**
- Works in all species. Use fine-thread screws for hardwood, coarse-thread for softwood.
- Plywood and MDF: Use coarse-thread screws; fine-thread strips out in particleboard core.
- Softwood: Screws hold well but can split near edges — keep the pocket hole 3/4"+ from
  the board end.

**11. Typical dimensions:**
- 3/4" stock: Use 1-1/4" pocket screws, drill depth setting = 3/4".
- 1-1/2" stock: Use 2-1/2" pocket screws, drill depth setting = 1-1/2".
- Pocket hole spacing: 6" to 8" on center for panels, one per joint for frames.

**12. Finish implications:**
- Pocket holes are visible on one side. Always orient pockets toward the hidden face
  (back of a face frame, underside of a tabletop).
- Paint: Fill pocket holes with plugs or wood filler; sands flat.
- Stain: Pocket-hole plugs never match well. Avoid pocket screws on stain-grade work.

---

### Half-Lap

**1. Name & aliases:** Half-lap, halving joint, cross-lap, end-lap, T-lap, corner lap.

**2. What it is:** Each board has half its thickness removed at the joint area so the two
boards interlock and sit flush. Variants include cross-lap (boards cross in the middle),
end-lap (boards meet at the ends), and T-lap (one board meets the middle of another).

**3. When to use:**
- Stretcher-to-stretcher connections (e.g., X-shaped base on a trestle table).
- Light frame construction (workbench bases, shelf frames).
- Face frames (alternative to pocket screws).
- Where a flat, flush intersection is needed and the cross-section is visible.

**4. When NOT to use:**
- Where maximum joint strength is needed (half the wood is removed, halving the
  cross-section at the joint).
- Structural connections under high racking loads (use M&T instead).
- On thin stock (< 1/2") where removing half leaves too little material.

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Low       | Glue-only is weak; pin or screw to improve     |
| Compression | Good    | Large face-grain glue area                     |
| Shear     | Good      | Interlock resists shear in the lap plane        |
| Racking   | Moderate  | Better than butt, worse than M&T               |

**6. Beginner-friendliness:** Good. One of the easier joints to visualize and cut. Can
be done with basic tools.

**7. Minimum tools required:**
- Tier 0: Circular saw + chisel (make multiple kerf cuts, chisel out waste)
- Tier 1: Router + straight bit + template
- Tier 2: Table saw + dado stack (fastest method)

**8. Bail-out alternative:** Butt joint with screws or a lap joint without halving
(one board sits on top of the other, screwed from below).

**9. SketchUp modeling approach:**

*WW library — `eval_ruby`:*
```ruby
# Cross-lap: cut both boards at their intersection
WW.half_lap("Stretcher A", face: :top, at: 20.0, width: 3.5, depth: 0.75)
WW.half_lap("Stretcher B", face: :bottom, at: 20.0, width: 3.5, depth: 0.75)
```
Note: `WW.half_lap` is a convenience wrapper around `WW.dado`. The `at` parameter is
the center of the notch (not the edge), and `width` matches the mating board's width.

*MCP tool — `boolean_subtract`:*
```
boolean_subtract(
  target="Stretcher A",
  cutter_type="box",
  position=[18.25, 0, 0.75],     # notch position (at - width/2, 0, half thickness)
  dimensions=[3.5, 3.5, 0.75]     # width, depth, height of notch
)
```

**10. Wood species notes:**
- Softwood: Glue-only half-laps tend to creep under load. Add a screw or pin.
- Hardwood: Excellent glue joint due to the large face-grain surface area.
- Plywood: Works well. The cross-grain layers in plywood actually strengthen the lap.

**11. Typical dimensions:**
- Notch depth = exactly half the board thickness. For 3/4" stock, depth = 3/8".
  For 1.5" stock, depth = 3/4".
- Notch width = exact width of the mating board (measure, do not assume).
- End-lap: Remove half the thickness for a distance equal to the mating board's width.

**12. Finish implications:**
- The joint line is visible as a straight seam. In cross-laps, the top surface is flush.
- Stain: Glue squeeze-out at the joint line will show. Clean up carefully.
- Paint: Fills easily. Half-laps are an excellent paint-grade joint.
- Decorative option: Use contrasting woods so the interlocking pattern is a feature.

---

## Corner Joints

Corner joints connect two boards at 90 degrees, typically at the corners of boxes, drawers,
and cases.

---

### Dovetail

**1. Name & aliases:** Dovetail. Variants: through dovetail, half-blind dovetail,
sliding dovetail, single-shoulder dovetail. The "tails" are the fan-shaped projections;
the "pins" are the narrower pieces between them.

**2. What it is:** Interlocking fan-shaped tails and pins that resist being pulled apart
mechanically. The strongest corner joint for solid-wood boxes and drawers. Hand-cut
dovetails are a hallmark of fine craftsmanship.

**3. When to use:**
- Drawer construction (the classic application — front-to-side).
- Blanket chests, tool chests, jewelry boxes.
- Any box corner where the joint will be seen and is a design feature.
- Heirloom / fine furniture where maximum corner strength matters.

**4. When NOT to use:**
- Plywood or MDF (layers delaminate when cutting tails/pins).
- When the corner will be hidden (overkill if painted or behind a face frame).
- Beginner projects under time pressure (high skill requirement).
- Where disassembly is needed (permanent once glued).

**5. Strength profile:**
| Load      | Rating      | Notes                                        |
|-----------|-------------|----------------------------------------------|
| Tension   | Excellent   | Mechanical interlock prevents pullout          |
| Compression | Excellent | Broad bearing surface                          |
| Shear     | Very Good   | Tails resist shear along the joint             |
| Racking   | Excellent   | Interlocking geometry resists racking in all directions |

**6. Beginner-friendliness:** Advanced. Hand-cut dovetails require marking, sawing, and
chiseling skills. Router-cut dovetails require a dovetail jig and careful setup.

**7. Minimum tools required:**
- Hand-cut: Dovetail saw + marking gauge + chisels + dovetail marker (Tier 0 tools, but
  advanced skill)
- Router-cut: Router + dovetail jig (e.g., Leigh, Porter-Cable, Keller) + dovetail bit
  (Tier 1-2)
- Through dovetails: Simpler jig setup. Half-blind: Requires a jig with offset.

**8. Bail-out alternative:**
- Finger/box joint (same strength concept but perpendicular cuts, much easier to cut).
- Rabbet + pin (simple corner with nails/brads; acceptable for painted work).
- Lock rabbet (router-table joint that approximates half-blind dovetail strength).

**9. SketchUp modeling approach:**

*MCP tool — `create_dovetail`:*
```
create_dovetail(
  tail_id="<entity_id of drawer side>",
  pin_id="<entity_id of drawer front>",
  width=4.5,          # board width (height of the dovetailed corner)
  height=0.5,         # stock thickness
  depth=0.5,          # how deep the tails/pins engage
  angle=15.0,         # dovetail angle (14 for hardwood, 18 for softwood)
  num_tails=3
)
```

*Half-blind variant:* Set `depth` to less than the full thickness of the pin board (e.g.,
3/8" depth in a 3/4" drawer front). The tails do not pass through.

*Verification:* Use `verify_bounds` — both boards' bounding boxes should remain the same
size, but the corner geometry will interlock.

**10. Wood species notes:**
- Softwood: Use an 18-degree (1:5) angle. Softer wood needs a wider angle for the tails
  to maintain strength.
- Hardwood: Use a 14-degree (1:7) or 15-degree angle. Narrower tails look more refined
  and hardwood is strong enough to hold them.
- Avoid: MDF, particleboard, plywood (layers split during cutting).

**11. Typical dimensions:**
- Tail angle: 14-15 degrees (hardwood) to 18 degrees (softwood). The `angle` parameter
  in `create_dovetail` specifies this.
- Pin width (narrow part): 1/2 the stock thickness minimum.
- Half-pin at top and bottom: Always include half-pins at the edges to prevent the
  corner from splitting.
- Spacing: Tails are typically wider than pins (2:1 to 3:1 ratio).

**12. Finish implications:**
- Through dovetails: Fully visible on both faces. This is the point — they are decorative.
  End grain absorbs stain differently; pre-seal or sand to higher grit.
- Half-blind dovetails: Hidden on the drawer front, visible on the side. Standard for
  drawer construction where the front is a show face.
- Contrasting woods (walnut tails in maple pins) are a design statement in MCM and
  Arts & Crafts styles.

---

### Finger Joint (Box Joint)

**1. Name & aliases:** Finger joint, box joint, comb joint.

**2. What it is:** Interlocking rectangular fingers at a corner. Similar in concept to
dovetails but with straight-sided (90-degree) fingers instead of angled tails. Easier to
cut, nearly as strong.

**3. When to use:**
- Box and drawer construction where dovetails are too time-consuming.
- Visible corners that benefit from a decorative pattern.
- Jigs, shop fixtures, and utility boxes.
- Any application where dovetails would be appropriate but simpler tooling is available.

**4. When NOT to use:**
- Where the joint must resist direct pullout (dovetails are mechanically superior for
  tension).
- Plywood (works only if the fingers are wide enough to avoid delaminating the layers).
- Where an invisible joint is needed (finger joints are always visible).

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Good      | Glue area is enormous but no mechanical lock   |
| Compression | Excellent | Large bearing surface                        |
| Shear     | Very Good | Fingers resist shear in the joint plane         |
| Racking   | Good      | Better than butt or rabbet, slightly less than dovetail |

**6. Beginner-friendliness:** Intermediate. Requires a table-saw jig or a router table
with a box-joint jig. The jig does the hard work once set up.

**7. Minimum tools required:**
- Tier 2: Table saw + box-joint jig (shop-made or commercial) + dado stack
- Tier 1: Router table + straight bit + indexing jig

**8. Bail-out alternative:** Rabbet + pin. A simple rabbet at the corner with brads or
screws. Much less decorative but quick.

**9. SketchUp modeling approach:**

*MCP tool — `create_finger_joint`:*
```
create_finger_joint(
  board1_id="<entity_id of side A>",
  board2_id="<entity_id of side B>",
  width=4.5,
  height=0.5,
  depth=0.5,
  num_fingers=5
)
```

*Verification:* Both boards maintain their bounding box but now have interlocking
rectangular geometry at the corner.

**10. Wood species notes:**
- Works in all solid wood species. Finger width should be at least 1/4" in softwood
  (narrower fingers break).
- Plywood: Use wide fingers (1/2"+) to avoid delamination at the finger tips.
- Hardwood: Can use narrow fingers (3/16" to 1/4") for a refined look.

**11. Typical dimensions:**
- Finger width = stock thickness (classic square fingers in 3/4" stock: 3/4" fingers).
- For finer work: finger width = 1/4" to 3/8" in 1/2" to 3/4" stock.
- Finger depth = full stock thickness (through joint).
- Always an odd number of fingers so the same board starts and ends with a finger.

**12. Finish implications:**
- Always visible. The alternating end-grain / face-grain pattern is the aesthetic.
- End grain absorbs more stain — pre-seal or use a conditioner for uniform color.
- Contrasting woods make finger joints pop as a design element.
- Paint: fills cleanly but hides the decorative purpose of the joint.

---

### Rabbet + Pin

**1. Name & aliases:** Rabbet and nail, rabbet and brad, rabbet and pin, nailed rabbet
corner.

**2. What it is:** A rabbet is cut on the end of one board, the mating board sits in the
step, and nails or brads pin the joint. The simplest corner joint that hides end grain
on one face.

**3. When to use:**
- Simple boxes, utility cabinets, painted casework.
- Drawer construction (paint-grade or lined drawers).
- Any corner where speed matters more than visible elegance.
- Plywood boxes (rabbets work well in plywood).

**4. When NOT to use:**
- Stain-grade fine furniture (nails/brads are visible).
- Joints under high tension (nails pull out).
- Heavy load-bearing corners (upgrade to finger joint or dovetail).

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Low       | Nails resist pullout poorly                    |
| Compression | Moderate | Rabbet step provides some bearing              |
| Shear     | Moderate  | Step + nails resist shear better than butt     |
| Racking   | Low       | Better than butt joint but not by much         |

**6. Beginner-friendliness:** Excellent. One of the simplest joints to cut and assemble.

**7. Minimum tools required:**
- Tier 0: Circular saw or table saw (for the rabbet) + hammer/brad nailer
- Tier 1: Router + rabbeting bit (cleaner cut)

**8. Bail-out alternative:** Butt joint + screws (no rabbet needed, just butt the boards
and screw through). Even simpler but weaker and shows fastener holes.

**9. SketchUp modeling approach:**

*WW library — `eval_ruby`:*
```ruby
WW.rabbet("Drawer Side", edge: :front, width: 0.5, depth: 0.375)
```
The pins (nails) are not typically modeled in SketchUp.

*MCP tool — `boolean_subtract`:*
```
boolean_subtract(
  target="Drawer Side",
  cutter_type="box",
  position=[0, 0, 0],
  dimensions=[0.375, 0.5, 4.5]
)
```

**10. Wood species notes:**
- Softwood: Pre-drill for nails near the edge to prevent splitting.
- Hardwood: Always pre-drill. Brads may bend in hard maple — use a brad nailer or
  switch to pin nails.
- Plywood: Excellent. The rabbet creates a mechanical stop that prevents the plywood
  from sliding during assembly.

**11. Typical dimensions:**
- Rabbet width = mating board thickness (e.g., 1/2" for 1/2" plywood drawer sides).
- Rabbet depth = 1/2 to 2/3 of the rabbeted board's thickness.
- Pin spacing: 18-gauge brads every 3" to 4".

**12. Finish implications:**
- Pin holes visible on one face. Acceptable for painted work.
- Stain: Fill pin holes with color-matched putty. Never looks perfect.
- One face hides end grain (the rabbet side); the other face shows the joint line.

---

### Butt Joint + Screw

**1. Name & aliases:** Butt joint, screw joint, face-screw joint, through-screw joint.

**2. What it is:** The simplest joint: one board butts against the face or edge of another
and screws hold them together. No interlocking geometry, no material removal beyond
screw holes.

**3. When to use:**
- Shop fixtures, jigs, utility shelving.
- Construction-grade work (deck framing, wall framing).
- Painted built-ins where speed is paramount.
- As the internal structure under veneered or face-framed casework.

**4. When NOT to use:**
- Any visible fine-furniture application.
- Joints under tension (screws into end grain pull out easily).
- Anywhere glue strength matters (end-grain glue bonds are weak).

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Poor      | Screws into end grain pull out; face grain is better |
| Compression | Moderate | Contact surfaces bear, screw prevents sliding |
| Shear     | Low       | Screws resist shear but are the sole connection |
| Racking   | Poor      | No mechanical interlock; add gussets or bracing |

**6. Beginner-friendliness:** Excellent. The absolute simplest joint. Requires only a
drill and screws.

**7. Minimum tools required:**
- Tier 0: Drill/driver + screws. That is it.

**8. Bail-out alternative:** This IS the simplest joint. No bail-out needed. For stronger
alternatives, step up to rabbet + pin or pocket screws.

**9. SketchUp modeling approach:**

No joint geometry to model. Position the boards in contact:
```ruby
WW.board("Shelf", "1x12", 36)
WW.board("Side", "1x12", 24)
WW.place("Shelf", [0.75, 0, 10.0])
```

If screw holes must be shown for drill-guide purposes:
```ruby
WW.pilot_hole("Side", face: :outer, at: [18.0, 10.375], dia: 0.125, depth: 0.75)
```

Or with the MCP tool:
```
safe_drill_hole(
  component_name="Side",
  center=[18.0, 0, 10.375],
  normal=[0, 1, 0],
  radius=0.0625,
  depth=0.75
)
```

**10. Wood species notes:**
- Softwood: Use coarse-thread screws. Pre-drill pilot holes to prevent splitting.
  #8 x 1-5/8" for 3/4" stock into 3/4" stock.
- Hardwood: Always pre-drill. Use fine-thread screws or dedicated hardwood screws.
  Hardwood can split aggressively without pilot holes.
- Plywood edge: Screws into plywood edges hold poorly. Use pocket screws into the face
  or add a cleat.

**11. Typical dimensions:**
- Screw length = thickness of the first board + 2/3 of the second board. For two 3/4"
  boards: 1-1/4" to 1-5/8" screws.
- Pilot hole: Match to the screw root diameter (see screw packaging).
- Countersink or counterbore: 3/8" plug for concealed screws.

**12. Finish implications:**
- Screw heads or filled holes are visible on one face.
- Paint: Fill with wood filler, sands flat.
- Stain: Plug the counterbored holes with matching wood plugs. Cross-grain plugs always
  show under stain.
- Best practice: Hide the screw face (back of a cabinet, underside of a shelf).

---

## Panel Joints

Panel joints connect boards edge-to-edge to create wider panels, or attach solid-wood
tops to bases while allowing for seasonal wood movement.

---

### Biscuit Joint

**1. Name & aliases:** Biscuit joint, plate joint (the biscuit is a compressed beech
wafer, #0, #10, or #20 size).

**2. What it is:** An oval slot is cut into the edge of each board with a biscuit joiner
(plate joiner). A compressed-wood biscuit is glued into the mating slots. The biscuit
swells with moisture from the glue, locking the joint.

**3. When to use:**
- Edge-to-edge panel glue-ups (alignment aid).
- Miter joints (adds alignment and some strength to mitered corners).
- Face-frame to case attachment.
- Where alignment is more important than added strength (glue is the primary bond in
  edge-to-edge joints; the biscuit just keeps things flush).

**4. When NOT to use:**
- Structural frame joints (biscuits add minimal strength).
- Narrow boards (< 2.5" wide — there is not enough material for the slot).
- End-grain joints.
- Where a dowel or loose tenon would be more appropriate for strength.

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Low       | Biscuit adds minimal tension resistance         |
| Compression | N/A     | Edge-glue joint handles compression natively   |
| Shear     | Moderate  | Biscuit prevents boards from sliding during clamp-up |
| Racking   | Low       | Not a structural joint                         |

**6. Beginner-friendliness:** Good with a biscuit joiner. The tool is simple to use but
is a single-purpose purchase.

**7. Minimum tools required:**
- Tier 1: Biscuit joiner (plate joiner) — no other tool cuts the slot reliably.
- Optionally: Router + slot-cutting bit (less common, harder to control).

**8. Bail-out alternative:** Dowels (serve the same alignment purpose and are cheaper to
start — just need a drill and doweling jig). Or simply edge-glue without alignment aids
(use cauls to keep the panel flat during glue-up).

**9. SketchUp modeling approach:**

Biscuit joints are **annotation-only** in SketchUp models. The biscuit slots are too small
and numerous to model usefully. Instead:

```ruby
# Model the panel as a single glued-up board
WW.board("Tabletop", [0.75, 24, 48], material: "White Oak")

# Add annotation via attribute to indicate biscuit joinery
top = WW.resolve("Tabletop")  # internal - use eval_ruby
top.set_attribute("WW", "joinery", "biscuit #20, 8\" spacing")
```

No MCP geometry tools are needed for biscuits.

**10. Wood species notes:**
- Works in all species. The biscuit is compressed beech — softer than hardwood, harder
  than softwood.
- Plywood: Biscuits work in plywood edges but the slot weakens the thin face veneer.
  Position slots away from the edges.

**11. Typical dimensions:**
- #0 biscuit: 1-5/8" x 3/4" (for narrow stock, ~1.5" wide).
- #10 biscuit: 2-1/8" x 3/4" (general purpose).
- #20 biscuit: 2-3/8" x 1" (for wide stock, most common for panel glue-ups).
- Slot depth: ~1/2" per side (set by the biscuit joiner).
- Spacing: 6" to 8" on center for panel glue-ups.

**12. Finish implications:**
- Completely hidden. No visible trace of the biscuit after glue-up.
- If a biscuit ghost shows through thin veneer, it means the slot was too close to the
  surface. Keep slots centered in the board edge.

---

### Tabletop Buttons / Z-Clips

**1. Name & aliases:** Tabletop buttons, Z-clips, figure-8 fasteners, tabletop fasteners,
expansion cleats.

**2. What it is:** Small hardware pieces that attach a solid-wood top to a base frame while
allowing the top to expand and contract with humidity changes. Buttons fit into a groove
in the apron; Z-clips screw to the apron and the top. Figure-8 fasteners sit in a
recessed hole on the apron and screw to the top.

**3. When to use:**
- Any solid-wood tabletop attached to a frame or apron.
- Dresser tops, desk tops, workbench tops.
- Any situation where a wide solid-wood panel must be attached to a rigid base.

**4. When NOT to use:**
- Plywood tops (plywood is dimensionally stable; simple screws through slotted holes
  are fine).
- Tops narrower than 8" (minimal wood movement).
- Where the top is integral to the structure and cannot float.

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Good      | Holds the top down securely against uplift     |
| Compression | N/A     | Top sits on the frame under gravity            |
| Shear     | Moderate  | Resists lateral sliding but allows seasonal movement |
| Racking   | N/A       | Top attachment does not contribute to racking resistance |

**6. Beginner-friendliness:** Excellent. Z-clips require only a drill/driver. Buttons
require a groove in the apron (router or table saw).

**7. Minimum tools required:**
- Z-clips: Tier 0 — drill/driver only.
- Buttons: Tier 1 — router or table saw (to cut the groove in the apron).
- Figure-8 fasteners: Tier 0 — drill + Forstner bit.

**8. Bail-out alternative:** Screw through slotted holes in the apron (elongated holes
along the grain direction allow movement). Requires only a drill.

**9. SketchUp modeling approach:**

Model as hardware components:
```ruby
# Z-clip as a small L-shaped block (representative, not exact)
clip = WW.board("Z-Clip", [0.125, 0.75, 1.0])
WW.place("Z-Clip", [6.0, 0, -0.125])  # positioned at the apron top edge

# Or add a groove in the apron for traditional buttons
WW.groove("Front Apron", face: :top, from_edge: 0.25, width: 0.25, depth: 0.375)
```

For most models, tabletop attachment is **annotation-only**:
```ruby
apron = WW.resolve("Front Apron")
apron.set_attribute("WW", "hardware", "Z-clips, 12\" spacing")
```

**10. Wood species notes:**
- Species does not affect the hardware choice. What matters is the width of the top:
  - < 12" wide: Minimal movement, figure-8s are fine.
  - 12-24" wide: Z-clips or buttons.
  - > 24" wide: Buttons preferred (more movement allowance than Z-clips).
- Rule of thumb: solid wood moves ~1/8" per 12" of width per 4% moisture change
  across the grain. A 36" top can move 3/8" seasonally.

**11. Typical dimensions:**
- Z-clips: #8 screw, 1" wide, installed every 12" along each apron.
- Buttons: 1" x 2" hardwood block with a 1/4" tongue, groove is 1/4" x 3/8" deep
  in the apron, buttons every 12".
- Figure-8 fasteners: 5/8" recess, installed every 12"-16".

**12. Finish implications:**
- Completely hidden. The hardware is between the top and the apron.
- No effect on the finish of the top or the base.

---

## Knockdown Joints

Knockdown (KD) joints allow furniture to be assembled and disassembled without glue.
Essential for pieces that must move through doorways or ship flat-packed.

---

### Bolt + Barrel Nut

**1. Name & aliases:** Bolt and barrel nut, cross-dowel and bolt, connector bolt,
furniture bolt, bed bolt.

**2. What it is:** A machine bolt passes through one board and threads into a barrel nut
(a cylinder with a threaded cross-hole) embedded in the mating board. Tightening the bolt
pulls the two boards together. The barrel nut sits in a hole drilled perpendicular to
the bolt.

**3. When to use:**
- Bed frame: rail to post connections (the classic application).
- Modular furniture that must be disassembled for moving.
- Desk or table trestle-to-stretcher connections.
- Any joint that must be strong AND removable.

**4. When NOT to use:**
- Visible fine furniture where hardware would be aesthetically objectionable (though
  cap nuts or plug covers can hide them).
- Joints under vibration (bolts can loosen — use thread-lock or a lock nut).
- Very thin stock (< 1" — not enough material for the barrel nut hole).

**5. Strength profile:**
| Load      | Rating      | Notes                                        |
|-----------|-------------|----------------------------------------------|
| Tension   | Excellent   | Steel bolt resists pullout indefinitely        |
| Compression | Excellent | Bolt head / washer bears on wide area          |
| Shear     | Very Good   | Bolt shank resists shear directly               |
| Racking   | Good        | Pair of bolts (top + bottom) resists racking well |

**6. Beginner-friendliness:** Good. Requires precise drilling but no joinery skill
beyond making holes. A drill press or doweling jig ensures accuracy.

**7. Minimum tools required:**
- Tier 0: Drill + appropriately sized bits (Forstner for barrel nut, twist bit for bolt)
- A drill guide or drill press is strongly recommended for the perpendicular barrel nut
  hole.

**8. Bail-out alternative:** Bed rail brackets (surface-mounted, no precision drilling
needed but are visible). Or pocket screws (semi-permanent but fast).

**9. SketchUp modeling approach:**

*WW library — `eval_ruby`:*
```ruby
# Bolt hole through the post
WW.bolt_hole("Bed Post",
  face: :front,
  at: [1.75, 2.0],           # center of bolt on the face
  hole: 0.375,                # 3/8" bolt hole
  cbore: 0.75,                # 3/4" counterbore for bolt head
  cbore_depth: 0.375          # recess bolt head 3/8"
)

# Barrel nut hole in the rail (perpendicular cross-hole)
WW.barrel_nut_hole("Side Rail",
  face: :right,
  at: [3.625, 2.0],           # [y, z] center on the end face
  hole: 0.625,                # 5/8" barrel nut hole
  depth: 2.5,                 # how deep into the end grain
  cross_hole: 0.375,          # 3/8" cross-hole for the bolt
  cross_at: 1.5               # 1.5" from the end to the cross-hole center
)
```

*MCP tool — `safe_drill_hole`:*
```
# Bolt hole
safe_drill_hole(
  component_name="Bed Post",
  center=[1.75, 0, 2.0],
  normal=[0, 1, 0],
  radius=0.1875,
  depth=3.5
)

# Barrel nut hole
safe_drill_hole(
  component_name="Side Rail",
  center=[83.0, 3.625, 2.0],
  normal=[1, 0, 0],
  radius=0.3125,
  depth=2.5
)
```

**10. Wood species notes:**
- Hardwood preferred for the barrel nut hole — the walls must resist compression from
  the nut. Oak, maple, walnut are ideal.
- Softwood: Works, but the barrel nut can crush the surrounding wood over repeated
  assembly/disassembly. Use a larger barrel nut (wider bearing surface).
- Plywood: Cross-dowels work well in plywood due to the alternating grain layers
  providing consistent holding power.

**11. Typical dimensions:**
- Bolt: 1/4-20 (light duty) or 5/16-18 (standard) or 3/8-16 (heavy duty / bed frames).
- Barrel nut: 10mm or 5/8" diameter is standard for furniture; 1" long.
- Bolt length: Through the first board + into the second board to reach the barrel nut.
- Counterbore: 3/4" diameter, 3/8" deep (fits a washer + bolt head, covered with a plug).
- Cross-hole center: 1" to 2" from the end of the mating board.

**12. Finish implications:**
- Bolt heads can be hidden with wood plugs in counterbored holes. Match the plug species
  and grain direction.
- Allen-head (hex socket) bolts look cleaner than hex-head bolts.
- Cap nuts (acorn nuts) on through-bolts provide a finished look without plugs.
- For paint: Fill the counterbore with filler over the bolt head (semi-permanent).

---

### Bed Rail Hardware (Brackets)

**1. Name & aliases:** Bed rail brackets, bed rail fasteners, hook plates, surface-mount
bed hardware.

**2. What it is:** A two-piece interlocking metal bracket. One plate screws to the inside
of the bed post; the other hooks onto it from the rail. Gravity and the weight of the
mattress keep the joint engaged. A pin or locking tab prevents the hook from lifting off.

**3. When to use:**
- Bed rail to post connections (the primary application).
- Heavy furniture that must be disassembled without tools.
- Where bolt + barrel nut is too complex or requires too-precise drilling.

**4. When NOT to use:**
- Visible joints in fine furniture (surface-mount brackets are industrial-looking).
- Non-bed furniture (designed specifically for the bed rail use case).
- Lightweight frames (overkill for anything that does not bear body weight).

**5. Strength profile:**
| Load      | Rating      | Notes                                        |
|-----------|-------------|----------------------------------------------|
| Tension   | Good        | Hook resists horizontal pullout                |
| Compression | Excellent | Weight bears on the bracket hook               |
| Shear     | Very Good   | Interlocking hook resists vertical shear       |
| Racking   | Good        | Better than a single bolt; the plate distributes load |

**6. Beginner-friendliness:** Excellent. Surface-mount, requires only a drill/driver
and screws.

**7. Minimum tools required:**
- Tier 0: Drill/driver + screws (provided with the hardware).
- Optionally: Chisel to mortise the plates flush into the wood (for a cleaner look).

**8. Bail-out alternative:** Bolt + barrel nut (stronger, more hidden, but requires
precision drilling). Or simply screw the rail to the post with lag screws (non-removable).

**9. SketchUp modeling approach:**

Bed rail hardware is **annotation-only** in SketchUp for most models. The brackets are
small relative to the furniture and the exact shape is manufacturer-specific.

```ruby
# Annotate the bed post
post = WW.resolve("Bed Post")
post.set_attribute("WW", "hardware", "bed rail bracket, post plate, inside face")
post.set_attribute("WW", "hardware_position", "centered, 6\" from top and bottom")

# Annotate the side rail
rail = WW.resolve("Side Rail")
rail.set_attribute("WW", "hardware", "bed rail bracket, hook plate, end face")
```

If a visual representation is needed, model as a simple rectangular plate:
```ruby
WW.board("Bracket Plate", [0.125, 1.0, 4.0])
WW.place("Bracket Plate", [inside_face_x, y_center - 0.5, z_center - 2.0])
```

**10. Wood species notes:**
- Screws must bite into solid wood (not end grain). Mount the post plate into face grain.
- Softwood (pine bed): Use longer screws and add a hardwood reinforcement block behind
  the bracket if the post is narrow.
- Hardwood: Standard screws are fine. Pre-drill in hard maple.

**11. Typical dimensions:**
- Standard bracket: 4" to 6" tall, 1" to 1.5" wide.
- Screw holes: #12 or #14 screws, typically 4-6 per plate.
- Post plate mounts centered vertically on the inside face of the post.
- Rail plate mounts flush on the end or inside face of the rail.

**12. Finish implications:**
- Hidden between the post and rail. Not visible in normal use.
- Mortising the brackets flush (recessing into the wood) provides a cleaner gap-free
  joint. Requires chiseling a shallow mortise.
- No effect on the finish of the surrounding wood.

---

### Cam Lock + Dowel

**1. Name & aliases:** Cam lock, cam fitting, minifix, confirmat fitting, flat-pack
fastener. Specific brands: Hafele Minifix, Titus cam lock.

**2. What it is:** A two-part system: a threaded stud (or dowel with a threaded insert)
is screwed into one board, and a cam disc in the mating board rotates to capture the
stud and pull the joint tight. The cam sits in a 15mm bored hole and rotates 90-180
degrees to lock. Often paired with a wooden or plastic alignment dowel.

**3. When to use:**
- Flat-pack furniture (designed for tool-free or Allen-key assembly).
- Retail / commercial furniture that ships disassembled.
- Modular systems where panels must be reconfigured.
- Anywhere end-user assembly is required.

**4. When NOT to use:**
- Fine furniture (the cam housing is visible as a 15mm circle on one face).
- Joints under high racking loads (cam locks are weaker than bolt + barrel nut).
- Solid wood (designed for particleboard and MDF with consistent density;
  solid wood can crack around the cam housing with repeated use).
- Outdoor furniture (metal cams corrode; plastic cams degrade in UV).

**5. Strength profile:**
| Load      | Rating    | Notes                                        |
|-----------|-----------|----------------------------------------------|
| Tension   | Moderate  | Cam lock holds firmly but can strip in soft material |
| Compression | Good    | Boards pull together when cam is locked          |
| Shear     | Low       | Alignment dowel provides shear resistance, not the cam |
| Racking   | Low       | Multiple cam + dowel pairs needed for adequate racking resistance |

**6. Beginner-friendliness:** Good for assembly; complex for fabrication. Drilling the
15mm cam housing and the stud hole requires precision (a drill press is recommended).
End-user assembly is trivial (just turn the cam with a screwdriver).

**7. Minimum tools required:**
- Fabrication: Drill press + 15mm Forstner bit + 5mm or 8mm twist bit
- Assembly: Flat-head screwdriver or Allen key (Tier 0)

**8. Bail-out alternative:** Bolt + barrel nut (more forgiving of drilling inaccuracies,
stronger, but requires a wrench for assembly).

**9. SketchUp modeling approach:**

Cam lock joints are **annotation-only** in SketchUp. The cam disc and stud are too small
to model usefully and are manufacturer-specific.

```ruby
# Annotate panels with cam lock joinery
side = WW.resolve("Side Panel")
side.set_attribute("WW", "joinery", "cam lock + dowel")
side.set_attribute("WW", "cam_positions", "3 per shelf, 15mm housing, 34mm from edge")

shelf = WW.resolve("Shelf")
shelf.set_attribute("WW", "joinery", "cam stud + alignment dowel in end grain")
```

If drill points must be shown for fabrication guidance:
```ruby
WW.pilot_hole("Side Panel", face: :inner, at: [6.0, 10.0], dia: 0.59, depth: 0.5)  # 15mm cam housing
WW.pilot_hole("Shelf", face: :left, at: [6.0, 0.375], dia: 0.315, depth: 1.0)  # 8mm stud hole
```

**10. Wood species notes:**
- Designed for particleboard and MDF (consistent, non-directional grain).
- Plywood: Works but the cam housing must not fall on a void in the core.
- Solid wood: The 15mm hole weakens the board near edges. Keep the cam at least 34mm
  (1-3/8") from the board edge. Works better in hardwood than softwood.

**11. Typical dimensions:**
- Cam housing: 15mm diameter, 12.5mm deep (standard Minifix size).
- Stud: 8mm diameter, threaded portion into the mating board.
- Alignment dowel: 8mm x 30mm, positioned 32mm from the cam on center.
- Edge distance: 34mm from the board edge to the cam center (European 32mm system).

**12. Finish implications:**
- The 15mm cam housing is visible as a circle on one face. Cover with a press-in
  plastic cap (available in dozens of colors to match melamine/veneer).
- On painted surfaces: Fill with wood filler if permanent assembly is acceptable.
- On stained solid wood: Not recommended — the hole and cap are always visible.

---

## Decision Tree

Use this decision tree to select the right joint for a connection.

### Step 1: What are the boards doing?

| Connection type          | Go to section         |
|-------------------------|-----------------------|
| Shelf into a case side  | **Channel joints** (Dado, Rabbet) |
| Frame connection (leg-to-apron, rail-to-post) | **Frame joints** (M&T, Dowel, Pocket Screw, Half-Lap) |
| Box or drawer corner    | **Corner joints** (Dovetail, Finger, Rabbet+Pin, Butt+Screw) |
| Wide panel glue-up or top attachment | **Panel joints** (Biscuit, Buttons/Z-Clips) |
| Must disassemble without damage | **Knockdown joints** (Bolt+Barrel Nut, Bed Rail HW, Cam Lock) |

### Step 2: What tools does the builder have?

| Tier | Tools available                                      |
|------|------------------------------------------------------|
| 0    | Circular saw + drill/driver                           |
| 1    | Tier 0 + router (with straight bit, rabbeting bit)    |
| 2    | Tier 1 + table saw (with dado stack or miter gauge)   |
| 3    | Tier 2 + full shop (drill press, mortiser, dovetail jig, bandsaw) |

### Step 3: What is the finish?

| Finish   | Joint visibility constraint                          |
|----------|------------------------------------------------------|
| Paint    | Fastener holes and joint lines can be filled          |
| Stain    | Joints must be clean; end-grain absorption differs    |
| Natural  | Same as stain; also avoid cross-grain plugs           |
| Outdoor  | Use mechanical fasteners (not glue-only); stainless steel hardware |

### Step 4: What is the load?

| Load       | Description                                        |
|------------|----------------------------------------------------|
| Light      | Books, clothes, decorative items (< 50 lbs/shelf)  |
| Moderate   | Kitchen items, heavy books, drawers (50-150 lbs)    |
| Structural | Body weight, bed frames, workbenches (> 150 lbs)    |

---

## Lookup Table

Cross-reference the 4 decision inputs to find the recommended joint and bail-out.

### Shelf-into-Side

| Tools | Finish | Load       | Recommended Joint    | Bail-out              |
|-------|--------|------------|----------------------|-----------------------|
| T0    | Paint  | Light      | Butt + screw + cleat | Butt + screw          |
| T0    | Paint  | Moderate   | Butt + screw + cleat | Pocket screw to side  |
| T0    | Stain  | Light      | Shelf pins (no joint)| Shelf pins            |
| T0    | Stain  | Moderate   | Shelf pins + dado (hire out) | Shelf pins    |
| T1    | Paint  | Light      | Rabbet on shelf end  | Butt + screw          |
| T1    | Paint  | Moderate   | Dado                 | Rabbet + screw        |
| T1    | Stain  | Light      | Stopped dado         | Shelf pins            |
| T1    | Stain  | Moderate   | Dado + face frame    | Rabbet + face frame   |
| T2    | Paint  | Any        | Dado                 | Rabbet                |
| T2    | Stain  | Any        | Stopped dado or dado + face frame | Dado + edge band |
| T3    | Stain  | Structural | Dado + glue + face frame | Dado + screws from back |

### Frame Connection (Leg-to-Apron, Rail-to-Post)

| Tools | Finish | Load       | Recommended Joint    | Bail-out              |
|-------|--------|------------|----------------------|-----------------------|
| T0    | Paint  | Light      | Pocket screw         | Butt + screw          |
| T0    | Paint  | Moderate   | Pocket screw (2 per) | Corner brace + screw  |
| T0    | Stain  | Light      | Dowel joint          | Pocket screw (hidden face) |
| T0    | Stain  | Moderate   | Dowel joint (3 per)  | Dowel joint (2 per)   |
| T1    | Paint  | Moderate   | Loose tenon (router) | Pocket screw          |
| T1    | Stain  | Moderate   | Loose tenon          | Dowel joint           |
| T1    | Any    | Structural | Loose tenon          | Dowel + corner brace  |
| T2    | Any    | Moderate   | M&T (integral)       | Loose tenon           |
| T2    | Any    | Structural | M&T (integral)       | Loose tenon           |
| T3    | Stain  | Any        | M&T (blind or through)| Loose tenon          |
| T3    | Stain  | Structural | Through wedged M&T   | Blind M&T             |

### Box / Drawer Corner

| Tools | Finish | Load       | Recommended Joint    | Bail-out              |
|-------|--------|------------|----------------------|-----------------------|
| T0    | Paint  | Light      | Butt + screw/nail    | Butt + screw          |
| T0    | Paint  | Moderate   | Rabbet + pin         | Butt + screw          |
| T0    | Stain  | Light      | Rabbet + pin         | Butt + pin (hidden)   |
| T1    | Paint  | Moderate   | Rabbet + pin (routed)| Rabbet + pin (saw-cut)|
| T1    | Stain  | Moderate   | Lock rabbet (router) | Rabbet + pin          |
| T2    | Paint  | Any        | Rabbet + pin         | Finger joint          |
| T2    | Stain  | Light      | Finger joint         | Rabbet + pin          |
| T2    | Stain  | Moderate   | Finger joint         | Rabbet + pin          |
| T3    | Stain  | Light      | Half-blind dovetail  | Finger joint          |
| T3    | Stain  | Moderate   | Half-blind dovetail  | Finger joint          |
| T3    | Stain  | Structural | Through dovetail     | Half-blind dovetail   |

### Panel Glue-Up / Top Attachment

| Tools | Finish | Load       | Recommended Joint    | Bail-out              |
|-------|--------|------------|----------------------|-----------------------|
| T0    | Any    | Any        | Edge glue + cauls    | Edge glue + dowels    |
| T1    | Any    | Any        | Biscuit or dowel     | Edge glue + cauls     |
| T0    | Any    | Top attachment | Z-clips           | Slotted screw holes   |
| T1+   | Any    | Top attachment | Tabletop buttons   | Z-clips               |

### Knockdown (Must Disassemble)

| Tools | Finish | Load       | Recommended Joint    | Bail-out              |
|-------|--------|------------|----------------------|-----------------------|
| T0    | Paint  | Light      | Cam lock + dowel     | Bolt + T-nut          |
| T0    | Paint  | Moderate   | Bolt + barrel nut    | Bolt + T-nut          |
| T0    | Paint  | Structural | Bolt + barrel nut    | Bed rail brackets     |
| T0    | Stain  | Light      | Bolt + barrel nut (plugged) | Cam lock (capped) |
| T0    | Stain  | Structural | Bolt + barrel nut (plugged) | Bed rail brackets |
| T3    | Stain  | Structural | Tusked through M&T   | Bolt + barrel nut     |

---

## MCP Tool Reference (Quick Index)

| Joint                 | Primary MCP Tool            | WW Library Call              |
|-----------------------|-----------------------------|-----------------------------|
| Dado                  | `safe_cut_dado`             | `WW.dado`                   |
| Rabbet                | `boolean_subtract`          | `WW.rabbet`                 |
| Groove                | `safe_cut_dado` (rotated)   | `WW.groove`                 |
| Mortise & Tenon       | `create_mortise_tenon`      | `WW.mortise` + `WW.tenon`   |
| Dowel                 | `safe_drill_hole`           | `WW.bolt_hole`              |
| Pocket Screw          | (annotation only)           | `WW.pilot_hole` (optional)  |
| Half-Lap              | `boolean_subtract`          | `WW.half_lap`               |
| Dovetail              | `create_dovetail`           | (use MCP tool)              |
| Finger Joint          | `create_finger_joint`       | (use MCP tool)              |
| Rabbet + Pin          | `boolean_subtract`          | `WW.rabbet`                 |
| Butt + Screw          | (position only)             | `WW.pilot_hole` (optional)  |
| Biscuit               | (annotation only)           | (annotation only)           |
| Tabletop Buttons      | `safe_cut_dado` (groove)    | `WW.groove`                 |
| Bolt + Barrel Nut     | `safe_drill_hole`           | `WW.bolt_hole` + `WW.barrel_nut_hole` |
| Bed Rail Hardware     | (annotation only)           | (annotation only)           |
| Cam Lock + Dowel      | (annotation only)           | (annotation only)           |
