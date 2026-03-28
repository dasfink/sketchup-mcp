#!/usr/bin/env python3
"""Layer 1 eval runner: decision quality via LLM-as-judge."""
import json, sys, os
from anthropic import Anthropic


def run_case(client, case):
    skill_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="You are a furniture design assistant using the furniture-design-sketchup skill.",
        messages=[{"role": "user", "content": case["prompt"]}],
    )
    judge_prompt = f"""Score this furniture design response.
PROMPT: {case['prompt']}
CONTEXT: {json.dumps(case.get('context', {}))}
EXPECTED: {json.dumps(case['expected'])}
ACTUAL: {skill_response.content[0].text}

Return JSON: {{"pass": true/false, "reasoning": "..."}}
Check: correct joint type, dimensions within 1/16", bail-out present if beginner."""

    verdict = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    return {
        "id": case["id"],
        "response": skill_response.content[0].text,
        "verdict": verdict.content[0].text,
    }


if __name__ == "__main__":
    cases_file, results_dir = sys.argv[1], sys.argv[2]
    client = Anthropic()
    cases = json.load(open(cases_file))
    results = [run_case(client, c) for c in cases]
    out = os.path.join(
        results_dir, os.path.basename(cases_file).replace(".json", "-results.json")
    )
    json.dump(results, open(out, "w"), indent=2)
    passed = sum(
        1 for r in results if '"pass": true' in r.get("verdict", "").lower()
    )
    print(f"  {passed}/{len(results)} passed")
