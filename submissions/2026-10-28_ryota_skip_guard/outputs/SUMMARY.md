> User provided results after submission: public display **$77.22M**. The standard for all three editions is the original $77.22M edition. Source: `../official_results.json`. ``Not acquired'' in the trial calculation records below is the status as of before submission.

# Version that strictly excludes circles that are likely to be skipped in the future

Candidate: **`submission_skip_guard.csv`**.
The baseline is the best-scoring $77.22M version. Only triple-merge acceptance conditions were tightened; predictors and ordering policy are unchanged.
No official score was obtained for this candidate.

## Added condition

Evaluate all six settings: fine-age and old five-year-age models, each at hazard multipliers 0.5/1/2.
Calculate an upper bound on the probability that every unreplaced pipe in a circle leaks before its scheduled year.
Do not assume independent leaks within a circle; use the minimum individual cumulative leak probability as an upper bound.

- The upper limit of the probability of each original circle becoming an empty circle is **10% or less**.
- The upper limit of the probability that one of the combinations will be empty (sum of each upper limit) is **15% or less**.
- Even if you estimate the case where the original circle is skipped unfavorably and assume that the integrated circle will always be constructed for a fee,
  At least **$25** in predicted fixed construction savings remains.
- All conditions are required to be met in all six leak scenarios.

Probability bounds are conditional on predicted per-pipe probabilities, not guarantees of true future probabilities or total construction costs.
Earlier replacement can prevent leak repairs while increasing replacement-length costs.
Probability calibration error also remains.

## Results

Of 32 candidates passing the original savings rules, 19 were excluded by the additional conditions.
From 13 remaining candidates, accept **nine disjoint triple merges**. Circle count falls from 19,352 to**19,334**.
The 3rd set was a combination in which there was no fixed cost savings for any 2 circles, but 3 circles if savings.

No-leak construction costs: $180,290,222.26 → **$180,287,050.52**.
Savings were small: **$3,171.74**. Completion was in 2045, with no delayed pipes and 10 advanced pipes.
Check coverage of all originally contained pipes and verify that the baseline file is unchanged.
Five tests passed, including high-skip rejection, aggregation of small skip probabilities, and zero-risk acceptance.

## Common random number comparison (30 times for each condition)

| Evaluation model | Hazard multiplier | Mean construction savings | Mean score difference |
|---|---:|---:|---:|
| Fine age bands | 0.5 | $1,383 | +$22,165 |
| Fine age bands | 1 | $2,308 | +$2,710 |
| Fine age bands | 2 | $1,526 | +$3,634 |
| Old 5-year age | 0.5 | $1,906 | +$2,548 |
| Old 5-year age | 1 | $1,855 | +$2,612 |
| Old 5-year age | 2 | $397 | +$1,210 |

Mean construction costs decreased and mean scores improved in all six settings, although the effects were small.
Approximate 95% Monte Carlo intervals for score differences include zero for fine-age hazard 0.5 and old-age hazard 2.
The larger fine-age hazard-0.5 mean gain is driven by repair costs; do not treat it as a robust $20,000 improvement.
Not every trial improved; these results do not guarantee model accuracy or private performance.

Displayed scores use 0.01M ($10,000) increments, larger than the no-leak savings here.
Retain the best-scoring version and treat this as a fine-tuning candidate.

Shared validation checks budget and completion for unreplaced iron. For historically replaced original iron,
The best-scoring baseline's geometric-coverage limitation remains; no supplementary circles were added.
Same-year execution and zero delay were checked only against the no-future-leak schedule.
Cost model: `2026-10-26-area-exponent`. See `merges.csv`, `report.json`, and `comparison.csv`.
