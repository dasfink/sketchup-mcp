# Furniture Skill Improvement Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a woodworking knowledge corpus, eval infrastructure, and iteratively improve the furniture-design-sketchup skill based on eval results.

**Architecture:** Research-first approach. Six corpus reference documents provide the knowledge base. Three-layer eval pyramid (decision evals, execution evals, integration evals) measures skill quality. Skill improvements are targeted at eval failures, keeping the skill lean while the corpus holds the full reference material.

**Tech Stack:** Markdown (corpus), JSON (eval cases), Bash/Python (eval runner), Ruby (SketchUp MCP tools), Claude Code skills infrastructure.

**Spec:** `docs/superpowers/specs/2026-03-28-furniture-skill-improvement-design.md`

---

## Chunk 1: Corpus Reference Documents

Tasks 1-6 are independent and can be parallelized. Each writes one or more corpus markdown files from the spec's content plus Claude's training data knowledge.

### Task 1: Write Joint Taxonomy

**Files:**
- Create: `docs/corpus/joint-taxonomy.md`

The most important corpus document. Contains the full decision framework for joint selection. Source: spec Section 1 + Claude training data on woodworking joinery and SketchUp modeling.

- [ ] **Step 1: Write channel joints section**

Write the dado, rabbet, and groove entries using the 12-field schema from the spec (name, what it is, when to use, when NOT to use, strength profile, beginner-friendliness, minimum tools, bail-out, SketchUp modeling, species notes, dimensions, finish implications). Each joint entry should be 15-25 lines.

```markdown
# Joint Taxonomy

## Channel Joints (shelf-into-side)

### Dado
- **What it is:** A channel cut across the grain of one board to receive the edge of another
- **When to use:** Shelves into uprights, dividers, fixed shelf positions
- **When NOT to use:** Adjustable shelving (use shelf pins instead), end-grain connections
- **Strength profile:** Good shear resistance perpendicular to channel. Poor pull-out resistance alone — needs glue, screws, or a captured back panel
- **Beginner-friendliness:** Moderate (Tier 1 tools: router + straight bit + edge guide)
- **Minimum tools:** Router + straight bit OR table saw + dado stack
- **Bail-out:** Cleat strip (1x2 screwed to upright) + pocket screws through shelf into cleat
- **SketchUp modeling:** MCP `safe_cut_dado` — params: component, face, width, depth, offset. Also available as `WW.dado` via eval_ruby for scripted multi-dado operations
- **Wood species notes:** Cut slightly tight in softwood (compresses under clamp pressure). Exact fit in hardwood
- **Typical dimensions:** Width = actual thickness of mating board (23/32" for standard 3/4" plywood, 3/4" for Baltic birch). Depth = 1/3 to 1/2 host board thickness (e.g., 1/4" to 3/8" in 3/4" stock)
- **Finish implications:** Hidden joint — no finish concern. But dado depth affects visible face thickness from outside

### Rabbet
[similar entry...]

### Groove
[similar entry...]
```

- [ ] **Step 2: Write frame joints section**

Write mortise & tenon (with through, blind, haunched, loose variants), dowel, pocket screw, and half-lap entries. M&T is the largest entry — include sub-variants.

- [ ] **Step 3: Write corner joints section**

Write dovetail (through, half-blind), finger/box joint, rabbet + pin, butt + screw entries.

- [ ] **Step 4: Write panel and knockdown joints sections**

Write biscuit (annotation-only), tabletop buttons/z-clips, bolt + barrel nut, bed rail hardware (annotation-only), cam lock (annotation-only).

- [ ] **Step 5: Write joint selection decision tree**

Add a compact decision tree at the end of the file — this is what gets extracted into the skill later:

```markdown
## Joint Selection Decision Tree

1. What are the boards doing? (shelf-into-side / frame connection / corner / panel / knockdown)
2. What tools does the builder have? (Tier 0-3)
3. What's the finish? (paint / stain / natural / outdoor)
4. What's the load? (light / moderate / structural)

→ Lookup table mapping these 4 inputs to recommended joint + bail-out
```

- [ ] **Step 6: Commit**

```bash
git add docs/corpus/joint-taxonomy.md
git commit -m "feat(corpus): add joint taxonomy with decision tree"
```

---

### Task 2: Write Material Reference

**Files:**
- Create: `docs/corpus/material-reference.md`

Combines dimensional lumber, plywood, and wood species data from spec Section 4, enriched with additional detail from Ana White guides and Claude training data.

- [ ] **Step 1: Write dimensional lumber section**

Include the full nominal-to-actual table from the spec, plus notes on:
- Common board (whitewood/SPF) vs. select pine vs. construction grade
- Board feet calculation formula
- Standard lengths available (6', 8', 10', 12')
- How to check for straightness (Ana White: sight down length like an arrow)
- Acclimation (bring indoors 1-2 weeks before building)

- [ ] **Step 2: Write plywood section**

Include the nominal-to-actual table from the spec, plus:
- Standard sheet sizes (4x8 standard, 5x5 Baltic birch)
- Grades (A, B, C, D faces — AC plywood has one good side)
- Cabinet-grade vs. construction-grade
- Edge treatment options (banding, roundover, paint fill)
- Grain direction matters for strength and appearance

- [ ] **Step 3: Write wood species guide**

Expand the spec's quick reference into a full guide:
- Indoor species: pine, poplar, oak, maple, walnut, cherry — with hardness, workability, cost, stain acceptance
- Outdoor species: Southern Yellow Pine, Douglas Fir, pressure-treated SPF, cedar, redwood — with rot resistance, fastener holding, maintenance
- The red-toned vs. yellow-toned 2x distinction (Ana White)
- When to use hardwood vs. softwood (furniture type, expected use, finish)

- [ ] **Step 4: Commit**

```bash
git add docs/corpus/material-reference.md
git commit -m "feat(corpus): add material reference (lumber, plywood, species)"
```

---

### Task 3: Write Plan Artifact Spec

**Files:**
- Create: `docs/corpus/plan-artifact-spec.md`

Documents the three plan tiers and what each artifact requires. Source: spec Section 2.

- [ ] **Step 1: Write tier definitions and artifact details**

For each artifact in each tier, document:
- What it looks like (description + example)
- How to create it in SketchUp (specific tool calls, camera positions)
- How to verify it (what to check before including in the plan)
- Common mistakes (wrong camera type, missing section plane, tag bleed)

Include assembly sequence derivation rules:
- Build from inside out (internal joints before enclosing)
- Sub-assemblies before final assembly
- Dry-fit before glue-up
- For knockdown: permanent joints first, then test hardware fit

- [ ] **Step 2: Write project-to-tier mapping with examples**

For each project type, show a concrete example of what the plan package looks like:
- Tier 1 example: garage shelf — overview, cut list, dims (3 artifacts)
- Tier 2 example: bookshelf — overview + elevations + exploded + assembly (9 artifacts)
- Tier 3 example: loft bed module — all of Tier 2 + sections + hardware + modules (14+ artifacts)

- [ ] **Step 3: Commit**

```bash
git add docs/corpus/plan-artifact-spec.md
git commit -m "feat(corpus): add plan artifact spec with tier examples"
```

---

### Task 4: Write Project Archetypes

**Files:**
- Create: `docs/corpus/project-archetypes.md`

Detailed version of spec Section 3's six archetypes. Source: spec + woodgears.ca project catalog + Ana White patterns.

- [ ] **Step 1: Write archetypes 1-3 (flat-pack, frame & panel, chair)**

For each archetype, expand beyond the spec to include:
- Typical dimensions and proportions (bookshelf: 30-48" wide, 10-14" deep, 36-72" tall)
- Component naming conventions (for SketchUp model consistency)
- Tag/layer organization pattern
- Example projects from woodgears.ca catalog that match this archetype
- SketchUp modeling order (which components to create first)

- [ ] **Step 2: Write archetypes 4-6 (box/drawer, modular, outdoor)**

Same depth as step 1. For modular archetype, include the assembly sequence methodology from the loft bed project as the reference pattern.

- [ ] **Step 3: Commit**

```bash
git add docs/corpus/project-archetypes.md
git commit -m "feat(corpus): add project archetypes with modeling patterns"
```

---

### Task 5: Write Tool Tiers and Finish Guide

**Files:**
- Create: `docs/corpus/tool-tiers.md`
- Create: `docs/corpus/finish-guide.md`

- [ ] **Step 1: Write tool tiers document**

Expand spec Section 4's tool tiers. For each tier, include:
- Tools in this tier (with approximate cost)
- Joints achievable
- Joints NOT achievable (and why)
- Recommended first project at this tier
- Upgrade path to next tier (what to buy next and why)
- Joint-to-tool feasibility matrix (rows: joints, columns: tiers, cells: yes/no/with-jig)

- [ ] **Step 2: Write finish guide**

Expand spec Section 4's finish implications. Include:
- Paint workflow (Ana White's 6-step: fill, sand, clean, prime, paint, build color)
- Stain workflow (test on scrap first, apply with foam, wipe excess)
- Natural/oil workflow (sand to 220, apply, wait, wipe, repeat)
- Outdoor finish (exterior stain/sealer, reapply schedule)
- How finish choice affects joint selection (table from spec, expanded)
- How finish choice affects material selection (painted = pine is fine, stained = need consistent grain)

- [ ] **Step 3: Commit**

```bash
git add docs/corpus/tool-tiers.md docs/corpus/finish-guide.md
git commit -m "feat(corpus): add tool tiers and finish guide"
```

---

### Task 6: Summarize Ana White PDFs

**Files:**
- Create: `docs/corpus/ana-white/building-quickstart.md`
- Create: `docs/corpus/ana-white/wood-choosing-guide.md`
- Create: `docs/corpus/ana-white/painting-guide.md`

Source: the three PDFs at `/Users/michaelfinkler/claude co-working/Umas-Loft-bed/AnaWhite*.pdf` and `buildingquickstartguidebetter.pdf`.

- [ ] **Step 1: Summarize building quickstart guide**

Read the PDF and extract into structured markdown:
- Safety checklist (PPE, tool manuals, workspace)
- Workspace setup (flat surface, lighting, ventilation)
- Essential starter tools (the Tier 0 list)
- Before-you-build checklist (study plan, gather materials, visualize)
- During-build principles (check square, clamp, go slow)
- After-build steps (sand, finish, clean up)

- [ ] **Step 2: Summarize wood choosing guide**

Extract:
- Common boards section (features, picking tips, acclimation)
- Dimensional lumber table
- Plywood section (1/4" and 3/4" uses, edge treatment, grades)
- Outdoor wood section (red vs yellow 2x, cedar, bark side up)
- Hardwood advisory (save for experienced builders)

- [ ] **Step 3: Summarize painting guide**

Extract:
- 6-step painting process
- Product recommendations
- Painting tips (precision matters, primer always, test stain color)
- Terminology (water-based stain, oil-based stain, polyurethane, wood filler)

- [ ] **Step 4: Commit**

```bash
git add docs/corpus/ana-white/
git commit -m "feat(corpus): add Ana White guide summaries"
```

---

### Task 7: Scrape Woodgears.ca Construction Articles

**Files:**
- Create: `docs/corpus/woodgears-ca/articles/` (multiple markdown files)

Scrape 5-10 key construction articles from woodgears.ca that show joint decisions in real projects. Use WebFetch.

- [ ] **Step 1: Identify target articles**

Prioritize articles that show joint selection rationale. Good candidates from the plans catalog:
- Kitchen chair (mortise & tenon): `https://woodgears.ca/kitchen_chairs/`
- Student desk (frame & panel): `https://woodgears.ca/student-desk/`
- Bed frame (knockdown): `https://woodgears.ca/bed/`
- Storage shelf (dados): `https://woodgears.ca/storage/`
- Workbench (half-lap, bolts): `https://woodgears.ca/workbench/`
- Patio table (outdoor joints): `https://woodgears.ca/table/patio_table.html`
- Shelving with dowels: `https://woodgears.ca/shelves/doweled.html`

- [ ] **Step 2: Scrape and summarize each article**

For each article, use WebFetch and extract:
- Project type and archetype
- Joints used and why
- Material choices
- Assembly sequence
- Problems encountered and solutions
- How it maps to our taxonomy

Save as `docs/corpus/woodgears-ca/articles/{project-name}.md`

- [ ] **Step 3: Commit**

```bash
git add docs/corpus/woodgears-ca/articles/
git commit -m "feat(corpus): add woodgears.ca article summaries"
```

---

## Chunk 2: Eval Infrastructure

Tasks 8-11 build the three-layer eval suite. They can be parallelized but depend on Chunk 1 being done (corpus provides the ground truth for eval expected values).

### Task 8: Build Layer 1 Eval Cases

**Files:**
- Create: `evals/layer1-decisions/joint-selection.json`
- Create: `evals/layer1-decisions/plan-tier-selection.json`
- Create: `evals/layer1-decisions/dimension-reasoning.json`
- Create: `evals/layer1-decisions/material-tool-finish.json`

- [ ] **Step 1: Write joint selection cases (30+ cases)**

Use the JSON schema from the spec. Cover all joint types from the taxonomy. Include cases that test:
- Basic joint selection (10 cases: one per major joint type)
- Skill-level constraints (5 cases: same connection at different tool tiers)
- Species-dependent decisions (5 cases: softwood vs hardwood changes recommendation)
- Anti-patterns (5 cases: scenarios where common mistakes are made — e.g., pocket screws across grain for tabletop)
- Bail-out presence (5+ cases: every case with beginner context must include bail-out)

Example case structure:
```json
[
  {
    "id": "joint-sel-001",
    "category": "joint-selection",
    "prompt": "I need to join a 3/4\" pine shelf into a 3/4\" pine upright for a bookshelf",
    "expected": {
      "joint_type": "dado",
      "dimensions": {"width": "0.75\"", "depth": "0.375\""},
      "bail_out": "cleat strip + pocket screws",
      "notes": "Use actual plywood thickness (23/32\") if plywood shelf"
    },
    "context": {"skill_level": "beginner", "tools": "tier_1", "finish": "paint"}
  }
]
```

- [ ] **Step 2: Write plan tier selection cases (10+ cases)**

Cover each project type from the archetype list. Include edge cases:
- Simple project that could be Tier 1 or Tier 2 depending on detail
- Modular project that requires Tier 3
- Outdoor project (Tier 2 vs Tier 3 based on complexity)

- [ ] **Step 3: Write dimension reasoning cases (10+ cases)**

Test the 1/3 rule, plywood actual thickness, dado depth rules, tenon sizing. Include:
- Standard scenarios (3/4" rail into 1-1/2" leg)
- Plywood thickness gotcha (23/32" vs 3/4")
- Dovetail angles (1:6 vs 1:8 by species)
- Minimum mortise depth
- Dado depth limits

- [ ] **Step 4: Write material/tool/finish cases (15+ cases)**

Combine material, tool constraint, and finish awareness tests:
- Indoor painted bookshelf → pine + pocket screws acceptable
- Outdoor bench → red-toned 2x, hardware joints, exterior finish
- Stained dresser → hidden pocket holes or decorative dovetails
- Beginner with only drill + circular saw → what joints are feasible?
- Wood movement scenario → tabletop attachment method

- [ ] **Step 5: Commit**

```bash
git add evals/layer1-decisions/
git commit -m "feat(evals): add Layer 1 decision eval cases (65+ cases)"
```

---

### Task 9: Build Layer 2 Eval Cases

**Files:**
- Create: `evals/layer2-execution/joinery-modeling.json`
- Create: `evals/layer2-execution/scene-creation.json`

- [ ] **Step 1: Write joinery modeling cases (10+ cases)**

Use the JSON schema from the spec. Each case defines setup geometry, the operation to test, and verification checks. Cover:
- `safe_cut_dado` — standard dado, edge rabbet, through groove
- `boolean_subtract` — mortise creation, half-lap cut
- `create_mortise_tenon` — paired mortise and tenon
- `create_finger_joint` — two boards at corner
- `create_dovetail` — drawer front + side
- `safe_drill_hole` — bolt hole, barrel nut cross-bore
- `WW.dado` via `eval_ruby` — same as safe_cut_dado but via WW library
- `WW.rabbet` via `eval_ruby` — edge variants

**Note:** Use actual MCP tool parameter names. `create_component_box` takes `name`, `position` (array), `dimensions` (array). `safe_cut_dado` takes `component_name`, `face`, `z_start`, `z_end`, `depth`. Check tool schemas before writing cases.

Example case:
```json
[
  {
    "id": "dado-001",
    "category": "joinery-modeling",
    "description": "Cut a standard 3/4\" dado in a bookshelf upright",
    "setup": [
      {"tool": "create_component_box", "params": {"name": "Upright", "position": [0, 0, 0], "dimensions": [0.75, 11.25, 36], "material": "Pine"}}
    ],
    "operation": {
      "tool": "safe_cut_dado",
      "params": {"component_name": "Upright", "face": "y+", "z_start": 8, "z_end": 8.72, "depth": 0.375}
    },
    "verify": [
      {"tool": "verify_bounds", "component": "Upright", "expected": {"width": [0.74, 0.76], "height": [35.9, 36.1], "depth": [11.2, 11.3]}},
      {"tool": "eval_ruby", "script": "WW.check_solids('Upright')", "expected": true}
    ]
  }
]
```

- [ ] **Step 2: Write scene creation cases (10+ cases)**

Test all plan artifact types:
- Assembly overview (3/4 perspective)
- Front/side/plan orthographic views (correct camera type + position)
- Section plane through a joint
- Exploded view (parts separated by tag offset)
- Multi-scene setup (Tier 2 complete set — verify all 6 scenes)
- Cut list generation (verify part count, dimensions, species)
- Tag visibility per scene (no tag bleed)

- [ ] **Step 3: Commit**

```bash
git add evals/layer2-execution/
git commit -m "feat(evals): add Layer 2 execution eval cases (20+ cases)"
```

---

### Task 10: Build Layer 3 Eval Cases

**Files:**
- Create: `evals/layer3-integration/bookshelf.json`
- Create: `evals/layer3-integration/kitchen-table.json`
- Create: `evals/layer3-integration/workbench.json`
- Create: `evals/layer3-integration/drawer-box.json`
- Create: `evals/layer3-integration/loft-bed-module.json`
- Create: `evals/layer3-integration/pocket-screw-bookshelf.json`

- [ ] **Step 1: Write 3 core integration cases**

Start with the most important three (one per tier):
- **Pocket-screw bookshelf** (Tier 1, flat-pack, beginner) — simplest
- **Simple bookshelf** (Tier 2, flat-pack, dado + rabbet) — most common
- **Storage stair module** (Tier 3, modular, complex) — most challenging

Each case includes:
```json
{
  "id": "int-bookshelf-001",
  "archetype": "flat-pack",
  "tier": 2,
  "prompt": "Design a simple bookshelf: 36\" wide, 12\" deep, 48\" tall, pine, 3 fixed shelves, painted white",
  "expected_joints": ["dado", "rabbet"],
  "expected_artifacts": ["assembly_overview", "front_elevation", "side_elevation", "plan_view", "joinery_details", "exploded_view", "assembly_sequence"],
  "expected_parts": [
    {"name": "Side", "qty": 2, "width": 0.75, "height": 48, "depth": 11.25},
    {"name": "Top", "qty": 1, "width": 0.75, "height": 34.5, "depth": 11.25},
    {"name": "Bottom", "qty": 1, "width": 0.75, "height": 34.5, "depth": 11.25},
    {"name": "Shelf", "qty": 3, "width": 0.75, "height": 34.5, "depth": 10.75},
    {"name": "Back", "qty": 1, "width": 0.25, "height": 47.25, "depth": 35.25}
  ],
  "scoring_rubric": {
    "joint_selection": 0.25,
    "geometry_valid": 0.25,
    "plan_artifacts_complete": 0.25,
    "cut_list_accurate": 0.15,
    "bail_out_offered": 0.10
  },
  "context": {"skill_level": "beginner", "tools": "tier_1", "finish": "paint"}
}
```

- [ ] **Step 2: Write 3 additional integration cases**

- **Kitchen table** (Tier 2, frame & panel, M&T + wood movement)
- **Knockdown workbench** (Tier 2, knockdown, half-lap + bolts)
- **Drawer box** (Tier 2, box, dovetail/finger + groove)

- [ ] **Step 3: Commit**

```bash
git add evals/layer3-integration/
git commit -m "feat(evals): add Layer 3 integration eval cases (6 cases)"
```

---

### Task 11: Write Eval Runner and Scoring Guide

**Files:**
- Create: `evals/scoring.md`
- Create: `evals/eval-runner.sh`

- [ ] **Step 1: Write scoring.md**

Document how each layer is scored:

```markdown
# Eval Scoring Guide

## Layer 1: Decision Evals
- **Method:** LLM-as-judge. A separate Claude instance receives the skill's response + expected answer, returns {pass, reasoning}.
- **Scoring:** Binary pass/fail per case. Aggregate = pass_count / total_count.
- **Pass criteria:** Correct joint type, dimensions within 1/16" tolerance, bail-out present when context.skill_level == "beginner".
- **Target:** 90% pass rate.

## Layer 2: Execution Evals
- **Method:** Automated. Setup geometry via MCP tools, run operation, verify via verify_bounds + eval_ruby solid checks.
- **Scoring:** Binary pass/fail per case. Bounds must be within 1/64" tolerance. Solids check must return true.
- **Target:** 95% pass rate.

## Layer 3: Integration Evals
- **Method:** Hybrid. Automated checks (verify_bounds, verify_scenes, generate_cutlist) + human scorer for joint appropriateness.
- **Scoring:** Weighted rubric (25% joint selection, 25% geometry, 25% artifacts, 15% cut list, 10% bail-out).
- **Target:** 80% weighted score.
```

- [ ] **Step 2: Write eval-runner.sh**

Shell script that orchestrates eval execution. For Layer 1, it iterates through JSON cases, prompts Claude, and calls the judge. For Layer 2, it requires SketchUp running and calls MCP tools. Layer 3 is manual.

```bash
#!/usr/bin/env bash
# Furniture Skill Eval Runner
# Usage: ./eval-runner.sh [layer1|layer2|layer3|all]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results/$(date +%Y-%m-%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

layer=$1

case "$layer" in
  layer1)
    echo "Running Layer 1: Decision Evals..."
    for f in "$SCRIPT_DIR"/layer1-decisions/*.json; do
      echo "  Processing $(basename "$f")..."
      # Each case: prompt skill, collect response, judge against expected
      # Output: results JSON with pass/fail per case
      python3 "$SCRIPT_DIR/run_layer1.py" "$f" "$RESULTS_DIR"
    done
    # Score: count pass/fail from results files
    passed=$(grep -l '"pass": true' "$RESULTS_DIR"/*-results.json 2>/dev/null | wc -l || echo 0)
    total=$(ls "$RESULTS_DIR"/*-results.json 2>/dev/null | wc -l || echo 0)
    echo "Layer 1 results: $passed/$total passed"
    ;;
  layer2)
    echo "Layer 2: Execution Evals (requires SketchUp running)"
    echo "Run each case manually via Claude Code with SketchUp MCP connected."
    echo "Cases: evals/layer2-execution/*.json"
    echo "Verify each with verify_bounds + eval_ruby WW.check_solids()"
    ;;
  layer3)
    echo "Layer 3: Integration Evals (manual)"
    echo "Run each project prompt via Claude Code with the furniture-design-sketchup skill."
    echo "Cases: evals/layer3-integration/*.json"
    echo "Score using the rubric in evals/scoring.md"
    ;;
  all)
    $0 layer1
    $0 layer2
    $0 layer3
    ;;
esac

echo "Results saved to $RESULTS_DIR"
```

- [ ] **Step 3: Write run_layer1.py helper**

Python script that reads a Layer 1 JSON file, prompts Claude via the Anthropic SDK, and uses a judge prompt to score each case. Requires `uv add anthropic` (or `pip install anthropic`).

```python
#!/usr/bin/env python3
"""Layer 1 eval runner: decision quality testing via LLM-as-judge."""
import json, sys, os
from anthropic import Anthropic

def run_case(client, case):
    """Prompt the skill, then judge the response."""
    # Step 1: Get skill response
    skill_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="You are a furniture design assistant using the furniture-design-sketchup skill.",
        messages=[{"role": "user", "content": case["prompt"]}]
    )

    # Step 2: Judge the response
    judge_prompt = f"""Score this furniture design response.

PROMPT: {case['prompt']}
CONTEXT: {json.dumps(case.get('context', {}))}
EXPECTED: {json.dumps(case['expected'])}
ACTUAL RESPONSE: {skill_response.content[0].text}

Return JSON: {{"pass": true/false, "reasoning": "..."}}
Check: correct joint type, dimensions within 1/16" tolerance, bail-out present if beginner context."""

    verdict = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": judge_prompt}]
    )
    return {
        "id": case["id"],
        "response": skill_response.content[0].text,
        "verdict": verdict.content[0].text
    }

if __name__ == "__main__":
    cases_file, results_dir = sys.argv[1], sys.argv[2]
    client = Anthropic()
    cases = json.load(open(cases_file))
    results = [run_case(client, c) for c in cases]
    out_path = os.path.join(results_dir, os.path.basename(cases_file).replace('.json', '-results.json'))
    json.dump(results, open(out_path, 'w'), indent=2)
    passed = sum(1 for r in results if '"pass": true' in r.get('verdict', '').lower())
    print(f"  {passed}/{len(results)} passed")
```

- [ ] **Step 4: Commit**

```bash
git add evals/scoring.md evals/eval-runner.sh evals/run_layer1.py
chmod +x evals/eval-runner.sh
git commit -m "feat(evals): add eval runner, scoring guide, and Layer 1 harness"
```

---

## Chunk 3: Skill Improvement

Tasks 12-16 are sequential. Each improvement pass targets specific eval failures.

### Task 12: Run Layer 1 Baseline

**Files:**
- Read: all Layer 1 JSON eval cases
- Create: `evals/results/` (baseline results)

**Prerequisite:** Tasks 1-11 complete.

- [ ] **Step 1: Run Layer 1 evals against current skill**

```bash
cd /Users/michaelfinkler/Dev/sketchup-mcp
./evals/eval-runner.sh layer1
```

- [ ] **Step 2: Analyze results**

Review the results JSON. Identify:
- Overall pass rate (target: 90%)
- Weakest category (joint selection? dimensions? material? tool constraints?)
- Specific failure patterns (does it always miss bail-outs? wrong plywood thickness?)

Document findings in `evals/results/baseline-analysis.md`.

- [ ] **Step 3: Commit baseline**

```bash
git add evals/results/
git commit -m "feat(evals): Layer 1 baseline results"
```

---

### Task 13: First Skill Improvement Pass — Joint Selection + Plan Tiers

**Files:**
- Modify: `~/.claude/skills/furniture-design-sketchup/SKILL.md`
- Create: `~/.claude/skills/furniture-design-sketchup/references/joint-selection.md`
- Create: `~/.claude/skills/furniture-design-sketchup/references/plan-tiers.md`

**Note on skill file location:** The active skill lives at `~/.claude/skills/furniture-design-sketchup/` (outside the git repo). Edit files there directly — they are the runtime copy Claude Code reads. These files are NOT tracked in the repo's git history; the corpus and evals are the tracked artifacts.

Target the weakest areas from the baseline. Extract the minimum knowledge from the corpus into new skill reference files.

- [ ] **Step 1: Create joint-selection.md reference**

Extract the compact decision tree from `docs/corpus/joint-taxonomy.md`. Include:
- The 4-input decision framework (connection type, tool tier, finish, load)
- Lookup table (not the full taxonomy — just the decision outputs)
- Bail-out rules (always present for beginner context)
- Common anti-patterns (pocket screws across grain, glue-only dado, etc.)

Keep under 100 lines. The corpus has the full detail; the skill gets the decision logic.

- [ ] **Step 2: Create plan-tiers.md reference**

Extract from `docs/corpus/plan-artifact-spec.md`:
- Tier 1/2/3 artifact checklists (compact)
- Project-to-tier mapping table
- Assembly sequence derivation rules (3 sentences)

Keep under 60 lines.

- [ ] **Step 3: Update SKILL.md to reference new files**

Add import references to the skill's main file so it loads the new reference documents.

- [ ] **Step 4: Re-run Layer 1 joint selection + plan tier evals**

```bash
cd /Users/michaelfinkler/Dev/sketchup-mcp
./evals/eval-runner.sh layer1
```

Compare against baseline. Target: 90%+ on joint selection and plan tier categories.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(skill): add joint selection and plan tier references" --allow-empty
# Skill files live at ~/.claude/skills/ (outside repo). This commit marks the milestone.
# The actual skill changes are in the ~/.claude/skills/ directory.
```

---

### Task 14: Second Pass — Material, Tool, and Finish Awareness

**Files:**
- Create: `~/.claude/skills/furniture-design-sketchup/references/materials-and-tools.md`
- Modify: `~/.claude/skills/furniture-design-sketchup/SKILL.md`

- [ ] **Step 1: Create materials-and-tools.md reference**

Extract from corpus:
- Dimensional lumber nominal-to-actual table (compact)
- Plywood actual thickness gotcha (23/32" for standard 3/4")
- Tool tier summary (Tier 0-3, one line each with available joints)
- Finish implications table (4 rows from spec)
- Wood species quick reference (6 rows from spec)
- "Ask about available tools" prompt pattern

Keep under 80 lines.

- [ ] **Step 2: Update SKILL.md**

Add reference to new file. Add a "Before recommending joints, check:" checklist:
1. What tools does the builder have?
2. What's the finish?
3. Is this indoor or outdoor?
4. What species?

- [ ] **Step 3: Re-run Layer 1 material/tool/finish evals**

Compare against baseline. Target: 90%+ on material, tool constraint, and finish categories.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(skill): add material, tool tier, and finish awareness" --allow-empty
# Skill files live at ~/.claude/skills/ (outside repo).
```

---

### Task 15: Third Pass — Archetype Templates

**Files:**
- Create: `~/.claude/skills/furniture-design-sketchup/references/project-archetypes.md`
- Modify: `~/.claude/skills/furniture-design-sketchup/SKILL.md`

- [ ] **Step 1: Create project-archetypes.md reference**

Extract from corpus — one compact template per archetype:
- Archetype name + trigger keywords
- Default component list (what parts to create)
- Default joints + bail-outs
- Default tag organization
- Default plan tier
- SketchUp modeling order

Keep under 100 lines (6 archetypes x ~15 lines each).

- [ ] **Step 2: Update SKILL.md**

Add archetype recognition to the skill's workflow:
1. User describes project → skill identifies archetype
2. Archetype provides defaults → skill confirms with user
3. Skill proceeds with archetype-informed decisions

- [ ] **Step 3: Re-run all Layer 1 evals**

Full regression check. All categories should be at 90%+.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(skill): add project archetype templates" --allow-empty
# Skill files live at ~/.claude/skills/ (outside repo).
```

---

### Task 16: Final Integration Validation

**Files:**
- Read: all eval results
- Create: `evals/results/final-report.md`

- [ ] **Step 1: Run Layer 2 evals (requires SketchUp)**

```bash
cd /Users/michaelfinkler/Dev/sketchup-mcp
./evals/eval-runner.sh layer2
```

Target: 95%+ pass rate on tool execution.

- [ ] **Step 2: Run Layer 3 evals (3 core cases)**

Run the pocket-screw bookshelf, simple bookshelf, and storage stair module integration tests manually. Score each with the rubric.

Target: 80%+ weighted score.

- [ ] **Step 3: Write final report**

```markdown
# Eval Results Report

## Layer 1: Decision Quality
- Baseline: X%
- Final: Y%
- Weakest category: ...
- Remaining failures: ...

## Layer 2: Tool Execution
- Pass rate: Z%
- Failures: ...

## Layer 3: Integration
- Bookshelf: X/100
- Table: X/100
- Loft bed module: X/100

## Recommendations
- Areas for future improvement
- Corpus expansion priorities (Instructables, more woodgears articles)
```

- [ ] **Step 4: Commit**

```bash
git add evals/results/
git commit -m "feat(evals): final integration validation report"
```
