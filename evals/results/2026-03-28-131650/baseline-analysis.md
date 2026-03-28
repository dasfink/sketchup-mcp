# Layer 1 Baseline Results — 2026-03-28

## Summary

| Category | Pass | Total | Rate | Target | Status |
|----------|------|-------|------|--------|--------|
| Dimension reasoning | 12 | 13 | 92% | 90% | PASS |
| Joint selection | 24 | 32 | 75% | 90% | NEEDS WORK |
| Plan tier selection | 9 | 12 | 75% | 90% | NEEDS WORK |
| Material/tool/finish | 18 | 18 | 100% | 90% | PASS |
| **Overall** | **63** | **75** | **84%** | **90%** | **6pts short** |

## Analysis

**Material/tool/finish (100%):** The skill's materials-and-tools.md reference is working perfectly. Species, tool tier, and finish guidance are all correct.

**Dimension reasoning (92%):** Nearly perfect. One failure to investigate — likely an edge case in the dimension rules.

**Joint selection (75%):** 8 failures out of 32. Primary weakness. Failures likely in:
- Anti-pattern detection (recognizing wrong joint recommendations)
- Tool-constrained scenarios (recommending joints the builder can't make)
- Bail-out consistency (missing bail-out in some beginner contexts)

**Plan tier selection (75%):** 3 failures out of 12. Likely confusion at tier boundaries (e.g., when does a project cross from Tier 2 to Tier 3?).

## Next Steps

1. Analyze specific failure cases in joint-selection-results.json
2. Analyze specific failure cases in plan-tier-selection-results.json
3. Tighten joint-selection.md reference with clearer anti-pattern rules
4. Tighten plan-tiers.md reference with clearer tier boundary criteria
5. Re-run evals to verify improvement
