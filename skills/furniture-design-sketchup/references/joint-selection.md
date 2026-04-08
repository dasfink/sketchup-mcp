# Joint Selection Guide

Decision framework for choosing joints. Cross-reference connection type, tool tier, finish, and load.

## Decision Tree

### Step 1: What are the boards doing?

| Connection type | Joint family |
|---|---|
| Shelf into case side | **Channel** — Dado, Rabbet |
| Frame (leg-to-apron, rail-to-post) | **Frame** — M&T, Dowel, Pocket Screw, Half-Lap |
| Box or drawer corner | **Corner** — Dovetail, Finger, Rabbet+Pin, Butt+Screw |
| Wide panel glue-up or top attachment | **Panel** — Biscuit, Buttons/Z-Clips |
| Must disassemble without damage | **Knockdown** — Bolt+Barrel Nut, Bed Rail HW, Cam Lock |

### Step 2: Tool tier?

| Tier | Tools |
|---|---|
| 0 | Circular saw + drill/driver (+Kreg jig) |
| 1 | Tier 0 + router (straight bit, rabbeting bit) |
| 2 | Tier 1 + table saw (dado stack, miter gauge) |
| 3 | Tier 2 + full shop (drill press, mortiser, bandsaw) |

### Step 3: Finish?

| Finish | Constraint |
|---|---|
| Paint | Fastener holes fillable; simplest joints fine |
| Stain | Joints must be clean; end-grain absorption differs |
| Natural/oil | Cleanest joints; avoid cross-grain plugs |
| Outdoor | Mechanical fasteners, not glue-only; stainless hardware |

### Step 4: Load?

| Load | Description |
|---|---|
| Light | Books, clothes, decorative (< 50 lbs/shelf) |
| Moderate | Kitchen items, heavy books, drawers (50–150 lbs) |
| Structural | Body weight, bed frames, workbenches (> 150 lbs) |

## Lookup Tables

### Shelf-into-Side

| Tools | Finish | Load | Recommended | Bail-out |
|---|---|---|---|---|
| T0 | Paint | Light | Butt + screw + cleat | Butt + screw |
| T0 | Paint | Moderate | Butt + screw + cleat | Pocket screw to side |
| T0 | Stain | Light | Shelf pins (no joint) | Shelf pins |
| T0 | Stain | Moderate | Shelf pins + dado (hire out) | Shelf pins |
| T1 | Paint | Light | Rabbet on shelf end | Butt + screw |
| T1 | Paint | Moderate | Dado | Rabbet + screw |
| T1 | Stain | Light | Stopped dado | Shelf pins |
| T1 | Stain | Moderate | Dado + face frame | Rabbet + face frame |
| T2 | Paint | Any | Dado | Rabbet |
| T2 | Stain | Any | Stopped dado or dado + face frame | Dado + edge band |
| T3 | Stain | Structural | Dado + glue + face frame | Dado + screws from back |

### Frame Connection (Leg-to-Apron, Rail-to-Post)

| Tools | Finish | Load | Recommended | Bail-out |
|---|---|---|---|---|
| T0 | Paint | Light | Pocket screw | Butt + screw |
| T0 | Paint | Moderate | Pocket screw (2 per) | Corner brace + screw |
| T0 | Stain | Light | Dowel joint | Pocket screw (hidden face) |
| T0 | Stain | Moderate | Dowel joint (3 per) | Dowel joint (2 per) |
| T1 | Paint | Moderate | Loose tenon (router) | Pocket screw |
| T1 | Stain | Moderate | Loose tenon | Dowel joint |
| T1 | Any | Structural | Loose tenon | Dowel + corner brace |
| T2 | Any | Moderate | M&T (integral) | Loose tenon |
| T2 | Any | Structural | M&T (integral) | Loose tenon |
| T3 | Stain | Any | M&T (blind or through) | Loose tenon |
| T3 | Stain | Structural | Through wedged M&T | Blind M&T |

### Box / Drawer Corner

| Tools | Finish | Load | Recommended | Bail-out |
|---|---|---|---|---|
| T0 | Paint | Light | Butt + screw/nail | Butt + screw |
| T0 | Paint | Moderate | Rabbet + pin | Butt + screw |
| T0 | Stain | Light | Rabbet + pin | Butt + pin (hidden) |
| T1 | Paint | Moderate | Rabbet + pin (routed) | Rabbet + pin (saw-cut) |
| T1 | Stain | Moderate | Lock rabbet (router) | Rabbet + pin |
| T2 | Paint | Any | Rabbet + pin | Finger joint |
| T2 | Stain | Light | Finger joint | Rabbet + pin |
| T2 | Stain | Moderate | Finger joint | Rabbet + pin |
| T3 | Stain | Light | Half-blind dovetail | Finger joint |
| T3 | Stain | Moderate | Half-blind dovetail | Finger joint |
| T3 | Stain | Structural | Through dovetail | Half-blind dovetail |

### Panel Glue-Up / Top Attachment

| Tools | Finish | Load | Recommended | Bail-out |
|---|---|---|---|---|
| T0 | Any | Any | Edge glue + cauls | Edge glue + dowels |
| T1 | Any | Any | Biscuit or dowel | Edge glue + cauls |
| T0 | Any | Top attachment | Z-clips | Slotted screw holes |
| T1+ | Any | Top attachment | Tabletop buttons | Z-clips |

### Knockdown (Must Disassemble)

| Tools | Finish | Load | Recommended | Bail-out |
|---|---|---|---|---|
| T0 | Paint | Light | Cam lock + dowel | Bolt + T-nut |
| T0 | Paint | Moderate | Bolt + barrel nut | Bolt + T-nut |
| T0 | Paint | Structural | Bolt + barrel nut | Bed rail brackets |
| T0 | Stain | Light | Bolt + barrel nut (plugged) | Cam lock (capped) |
| T0 | Stain | Structural | Bolt + barrel nut (plugged) | Bed rail brackets |
| T3 | Stain | Structural | Tusked through M&T | Bolt + barrel nut |

## Anti-Patterns

| Don't do this | Why | Do this instead |
|---|---|---|
| Dovetails on a painted box | Invisible under paint — wasted effort | Rabbet + pin or butt + screw |
| Pocket screws on oil-finished walnut | Visible holes ruin the finish | M&T or dowel joint |
| Glue-only joints outdoors | Moisture cycling breaks glue bonds | Mechanical fasteners (bolts, screws) |
| M&T at Tier 0 | No tools to cut it | Pocket screw or dowel joint |
| Dado in stock < 1/2" thick | Channel weakens the board too much | Rabbet or cleat |

## MCP Tool Quick Index

| Joint | Primary MCP Tool | WW Library Call |
|---|---|---|
| Dado | `safe_cut_dado` | `WW.dado` |
| Rabbet | `boolean_subtract` | `WW.rabbet` |
| Groove | `safe_cut_dado` (rotated) | `WW.groove` |
| Mortise & Tenon | `create_mortise_tenon` | `WW.mortise` + `WW.tenon` |
| Dowel | `safe_drill_hole` | `WW.bolt_hole` |
| Half-Lap | `boolean_subtract` | `WW.half_lap` |
| Dovetail | `create_dovetail` | (use MCP tool) |
| Finger Joint | `create_finger_joint` | (use MCP tool) |
| Bolt + Barrel Nut | `safe_drill_hole` | `WW.bolt_hole` + `WW.barrel_nut_hole` |
| Tabletop Buttons | `safe_cut_dado` (groove) | `WW.groove` |
