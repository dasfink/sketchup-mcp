#!/usr/bin/env python3
"""Layer 1 eval runner: decision quality via LLM-as-judge.

Uses the `claude` CLI (which handles OAuth auth) instead of the Anthropic SDK directly.
"""
import json, sys, os, subprocess, tempfile


def claude_prompt(prompt, system=None):
    """Run a prompt through the claude CLI and return the response text."""
    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if system:
        cmd.extend(["--system-prompt", system])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        return f"ERROR: {result.stderr[:200]}"
    return result.stdout.strip()


def run_case(case):
    """Prompt the skill, then judge the response."""
    # Step 1: Get skill response
    skill_response = claude_prompt(
        case["prompt"],
        system="You are a furniture design assistant. When recommending joints, consider the builder's tool tier, finish type, wood species, and skill level. Always provide a beginner bail-out alternative when appropriate."
    )

    # Step 2: Judge the response
    judge_prompt = f"""Score this furniture design response. Return ONLY valid JSON.

PROMPT: {case['prompt']}
CONTEXT: {json.dumps(case.get('context', {}))}
EXPECTED: {json.dumps(case['expected'])}
ACTUAL RESPONSE: {skill_response}

Return JSON: {{"pass": true, "reasoning": "..."}} or {{"pass": false, "reasoning": "..."}}
Pass criteria: correct joint type, dimensions within 1/16" tolerance, bail-out present if context has skill_level=beginner."""

    verdict = claude_prompt(judge_prompt)

    return {
        "id": case["id"],
        "category": case.get("category", "unknown"),
        "prompt": case["prompt"][:100],
        "response": skill_response[:500],
        "verdict": verdict,
    }


if __name__ == "__main__":
    cases_file = sys.argv[1]
    results_dir = sys.argv[2]

    cases = json.load(open(cases_file))
    print(f"  Running {len(cases)} cases from {os.path.basename(cases_file)}...")

    results = []
    for i, case in enumerate(cases):
        print(f"    [{i+1}/{len(cases)}] {case['id']}...", end=" ", flush=True)
        r = run_case(case)
        results.append(r)
        passed = '"pass": true' in r.get("verdict", "").lower() or '"pass":true' in r.get("verdict", "").lower()
        print("PASS" if passed else "FAIL")

    out = os.path.join(
        results_dir, os.path.basename(cases_file).replace(".json", "-results.json")
    )
    json.dump(results, open(out, "w"), indent=2)

    passed = sum(
        1 for r in results
        if '"pass": true' in r.get("verdict", "").lower()
        or '"pass":true' in r.get("verdict", "").lower()
    )
    print(f"  Result: {passed}/{len(results)} passed ({100*passed//max(len(results),1)}%)")
