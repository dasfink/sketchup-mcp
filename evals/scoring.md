# Eval Scoring Guide

## Layer 1: Decision Evals
- **Method:** LLM-as-judge
- **Scoring:** Binary pass/fail. Aggregate = pass_count / total_count
- **Pass criteria:** Correct joint type, dimensions within 1/16", bail-out present for beginners
- **Target:** 90%

## Layer 2: Execution Evals
- **Method:** Automated MCP tool verification
- **Scoring:** Binary pass/fail. Bounds within 1/64". Solids check true.
- **Target:** 95%

## Layer 3: Integration Evals
- **Method:** Automated checks + human scorer
- **Scoring:** Weighted rubric (25% joints, 25% geometry, 25% artifacts, 15% cut list, 10% bail-out)
- **Target:** 80%
