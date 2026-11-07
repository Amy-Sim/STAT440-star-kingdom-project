> User provided results after submission: Public display **$77.29M**. The standard for all three editions is the original $77.22M edition. Source: `../official_results.json`. ``Not acquired'' in the trial calculation records below is the status as of before submission.

# Version that shrinks the subsequent circle excluding pipes covered by previous construction

Submission candidate: **`submission_shrink_after_work.csv`**.
The baseline is the best-scoring $77.22M version. Shrink 81 circles without changing predictions, circle count, or order.
No official score was obtained.

## Method and safety conditions

Process the CSV sequentially from the beginning and record the pipes already covered by the previous circle.
For each circle, calculate a smaller circle covering every pipe not already covered by an earlier row.
Confirm that no unintended unreplaced pipes enter the new circle and that its scheduled replacement targets exactly match the original.
Accept only if the radius decreases and costs fall by at least $1.

Do not automatically discard a historically replaced pipe if no earlier circle has geometrically covered it.
At every row, the new CSV consequently preserves the set of pipes covered by the original CSV up to that row.
The circle center may move to cover the required pipes.
Recalculate surfaces and costs for each circle; do not exclude surfaces merely because their pipes are already replaced.

## Verification with zero leak

| Indicator | $77.22M version | This time |
|---|---:|---:|
| Circle count | 19,352 | 19,352 |
| Smaller circle | — | **81** |
| Construction cost | $180,290,222.26 | **$180,205,924.17** |
| Completion year | 2045 | 2045 |

Construction savings: **$84,298.09**. No pipe was delayed relative to the original schedule; 102 were advanced.
Confirmed identical per-row replacement targets and preserved cumulative containment coverage through every row.
Future leaks can change either plan's timing; replacement years are not guaranteed to remain unchanged across all futures.

## Common random number comparison (30 times for each condition)

| Evaluation model | Hazard multiplier | Mean construction savings | Mean score difference |
|---|---:|---:|---:|
| Fine age bands | 0.5 | $67,050 | +$96,054 |
| Fine age bands | 1 | $53,827 | +$66,631 |
| Fine age bands | 2 | $35,981 | +$68,365 |
| Old 5-year age bands | 0.5 | $66,161 | +$71,870 |
| Old 5-year age bands | 1 | $58,645 | +$77,210 |
| Old 5-year age | 2 | $30,723 | +$54,717 |

Mean construction costs, repair costs, and scores improved in all six settings.
Approximate 95% Monte Carlo intervals for mean score differences were above zero in each setting, but they exclude model error and are not
This is not a prediction interval and does not guarantee a higher public or private score.

Passed 2 tests. An example of shrinking a circle by excluding the pipe that was replaced in the previous circle,
Confirmed that geometric coverage of pipes replaced before project start was not discarded.
Shared validation checks budget-feasible completion for an explicitly defined unreplaced-iron target set.
The baseline's coverage limitation for historically replaced original iron is retained,
Do not record a pass on full original-iron coverage. Original coverage was not worsened.

Details: `shrinks.csv`, `report.json`, `comparison.csv`, `simulations.csv`, and validation JSON.
Cost model: `2026-10-26-area-exponent`. Retain the best-scoring version unchanged for comparison.
