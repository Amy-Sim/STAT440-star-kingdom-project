# Ryota: $76.91M → $77.07M in construction cost reduction with fixed forecast

The user-provided submission screenshot confirms a **displayed public score of $77.07M**.
Improvement over the previous $76.91M best: **+$0.16M ($160,000 at displayed precision)**.
Displays are rounded to 0.01M; differences are not exact differences between underlying scores.

## What have you changed since your previous high point?

**Leak forecast and repair cost forecast were fixed, and 260 neighboring circles with the same scheduled construction year were integrated.**

- Reduced original 19,838 circles to 19,578 circles.
- The integrated circle covers all target pipes of the original 2 circles, and recalculates the ground surface and replacement cost of all included pipes.
- Place the integrated circle in its original earlier position and delete the later one. The relative order of other circles is preserved.
- Risk weights, prediction models, and target pipes are unchanged.
- If the newly included unreplaced pipes are scheduled for the same year or later, that candidate will not be adopted.

Same year refers to the scheduled year when replaying the best-scoring CSV without future leaks.
This does not guarantee identical replacement years in every future scenario.

| Comparison | Previous best | Construction savings version |
|---|---:|---:|
| Public display score | $76.91M | **$77.07M** |
| Circle count | 19,838 | **19,578** |
| Construction cost, no future leaks | $180,664,606.53 | **$180,425,969.20** |
| Completion year and same conditions | 2045 | 2045 |

Construction savings under the same conditions were **$238,637.33**. No pipe was delayed relative to the original schedule,
189 pipes were advanced. This does not measure the official public evaluation's construction-cost difference.
Public score is also affected by repair costs and actual construction time.

## Saved artifacts

- [This submission CSV](../submissions/2026-10-28_ryota_construction_savings/outputs/submission_construction_savings.csv)
- [Previous highest point CSV](../submissions/2026-10-28_ryota_early3/outputs_early3/early3_adaptive.csv)
- [Methods/Restrictions/Re-execution steps](../submissions/2026-10-28_ryota_construction_savings/README.md)
- [List of 260 merged pairs](../submissions/2026-10-28_ryota_construction_savings/outputs/merges.csv)
- [Input/output hash and verification result](../submissions/2026-10-28_ryota_construction_savings/outputs/report.json)
- [public display source/corresponding CSV hash](../submissions/2026-10-28_ryota_construction_savings/official_results.json)
- [Submission screen](../submissions/2026-10-28_ryota_construction_savings/outputs/official_score_77_07m.png)

Two leak models, hazard 0.5/1/2 times, common random number comparison 30 times each, average construction cost and
Mean scores improved by approximately +$0.131M to +$0.299M.
Keep model-conditional simulations separate from the public results reported here.
Private score is not confirmed.

The inherited geometric-coverage limitation for historically replaced iron pipes is documented in the method README and
This is explicit in the shared validation JSON. It verifies unreplaced-iron coverage and budget-feasible completion;
Do not record a pass on strict coverage of every original iron pipe.
