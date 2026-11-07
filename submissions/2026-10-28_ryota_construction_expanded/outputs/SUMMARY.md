# Exploration expansion version that adds same year integration from $77.07M version

Submission candidate: **`submission_construction_expanded.csv`**

The baseline is `submission_construction_savings.csv`, which achieved the then-best $77.07M.
After submission, the user-provided screenshot confirmed **$77.22M**, a displayed gain of**+$0.15M** over $77.07M. The baseline CSV is preserved; sources are recorded in `../official_results.json`.

## Changes from last time

The predictors, prioritization approach, cost formula, and merge acceptance rules are unchanged;
Expanded the search for circles sharing a scheduled year under no future leaks.

| Search items | Previous | This time |
|---|---:|---:|
| Neighboring circles examined | 12 | 24 |
| Maximum center distance | 80m | 120m |
| Maximum CSV row gap | 160 | 320 |

Retain the neighbor-distance/original-radius filter and the limit of 12 pipes in the union of the original pair's containment sets.
Expanding the limits above therefore does not send every candidate to geometric evaluation.
Cover every pipe covered by the original pair. Reject newly included unreplaced pipes scheduled for the same year or later.
Choose pairs with positive expected cost savings after accounting for the chance that a circle becomes empty.
Place the merged circle at the earlier position and preserve all other relative ordering.

We evaluated 9,118 pairs and selected 226 unique pairs from 254 positive candidates.
Reduced from 19,578 circles to **19,352 circles**.

## Verification with zero leak

| Metric | $77.07MVersion | Current |
|---|---:|---:|
| Construction cost | $180,425,969.20 | **$180,290,222.26** |
| Completion year | 2045 | 2045 |
| Circle count | 19,578 | **19,352** |

Additional construction savings: **$135,746.94**.
Preserved coverage of all baseline-contained pipes; no pipe was delayed and 155 were advanced.
Relative to the original $76.91M plan, 486 groups were merged in total, saving $374,384.27 in construction under the same conditions.

Same-year execution and zero delay describe this no-leak schedule; they do not imply that every future leak scenario
This does not guarantee unchanged replacement years for every pipe.

## Comparison trial calculation of common random numbers (30 times for each condition)

All comparisons are against the $77.07M version, not differences from actual public scores.

| Evaluation model | Hazard multiplier | Mean construction savings | Mean score difference |
|---|---:|---:|---:|
| Fine age bands | 0.5 | $96,122 | +$173,558 |
| Fine age bands | 1 | $62,929 | +$161,139 |
| Fine age bands | 2 | $43,354 | +$135,794 |
| Old 5-year age | 0.5 | $101,348 | +$125,887 |
| Old 5-year age bands | 1 | $78,333 | +$169,142 |
| Old 5-year age | 2 | $41,514 | +$110,139 |

The average construction cost, average repair cost, and average score improved in all six conditions.
Approximate 95% Monte Carlo intervals for all score differences were also above zero. These are conditional on the predictors,
intervals exclude model error and uncertainty in private evaluation.
This does not mean every individual trial improved.

Both added tests passed. Reloaded the CSV and rechecked coverage, replacement years, and costs.
Shared validation checks budget-feasible completion for the explicitly defined unreplaced-iron target set.
The inherited geometric-coverage limitation for historically replaced original iron remains.
No coverage circles were added in this round; do not report a pass on full original-iron coverage.

Details: `report.json`, `merges.csv`, `comparison.csv`, and `simulations.csv`.
Input, baseline, and submission SHA-256 hashes are recorded. Cost model: `2026-10-26-area-exponent`.
**Keep the $77.07M version and compare it with the official evaluation as a new candidate.**
