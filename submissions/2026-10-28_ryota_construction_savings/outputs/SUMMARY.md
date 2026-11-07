# Construction cost reduction version — Changes from the $76.91M version

Submission candidate: **`submission_construction_savings.csv`**

Merge neighboring circles from the best $76.91M plan to reduce construction costs without changing leak forecasts.
After submission, the user-provided screenshot confirmed **$77.07M**, a displayed gain of**+$0.16M** over $76.91M. Sources and CSV mapping are recorded in `../official_results.json`.

## Method

Replay the original CSV without future leaks to obtain each circle's construction year and each pipe's replacement year.
Examine pairs among 12 neighboring circles in the same scheduled year, within 80 m and a 160-row CSV gap.
Build a circle covering the entire union of pipes wholly contained in the two original circles; use all wholly contained pipes and surfaces to
recalculate costs. If the new circle includes an unreplaced pipe scheduled for the same or a later year,
reject such candidates. The combined original containment set may contain at most 12 pipes.

Require at least $25 in fixed construction savings, while accounting for future empty-circle skipping under the previous leak forecast,
retain candidates with at least $10 in estimated savings after this adjustment. Choose disjoint pairs in descending savings order.
Place the merged circle at the earlier row and remove the later row, preserving other relative ordering.

We evaluated 7,237 pairs and selected 260 pairs from 289 positive candidates.
Confirm that the enlarged circle covers both original target sets, then read back and revalidate the exported CSV.

## Confirm execution with zero leak in the future

| Index | $76.91M version | Construction cost reduction version |
|---|---:|---:|
| Number of circles | 19,838 | 19,578 |
| Construction cost | $180,664,606.53 | $180,425,969.20 |
| Completion year | 2045 | 2045 |

**Construction cost difference reduced by $238,637.33.**
Confirmed continued coverage of every pipe covered by the original CSV.
Under the same conditions, no pipe was delayed relative to the original schedule and 189 were advanced.
Passed 2 tests. An example of reducing costs by combining parallel pipes of the same year, and circles constructed in different years.
were confirmed not to be merged.

The previous full-original-iron coverage limitation remains. Every unreplaced iron pipe is covered, but
No circles were added for historically leaked/replaced iron pipes in this round.

## Comparison trial calculation of common random numbers (30 times for each condition)

| Leak evaluation model | Hazard multiplier | Mean construction savings | Mean repair savings | Mean score difference |
|---|---:|---:|---:|---:|
| Fine age bands | 0.5 | $171,953 | $100,453 | +$272,406 |
| Fine age bands | 1 | $118,387 | $39,265 | +$157,651 |
| Fine age bands | 2 | $70,989 | $65,463 | +$136,452 |
| Old 5-year age | 0.5 | $176,506 | $122,885 | +$299,391 |
| Old 5-year age | 1 | $132,776 | $55,516 | +$188,291 |
| Old 5-year age bands | 2 | $73,535 | $57,870 | +$131,405 |

Mean scores improved in all six settings; approximate 95% Monte Carlo intervals for score differences were also above zero.
However, this comparison is conditional on the models and simulations; future forecast errors and
It is not an interval that includes the uncertainty of private evaluation. Nor does it mean that every single trial improved.

**“Same year” and “0 replacement delays” are confirmations of the original future leak-free construction schedule.**
Realized future leaks can advance construction in both the original and new CSV, so across all futures
This does not guarantee that every pipe's replacement year remains the same or moves earlier.
Retain the original $76.91M version and compare the new candidate through official evaluation.

## File

- `merges.csv`: Original two rows combined, construction year, radius, estimated savings.
- `report.json`: Input/submission hash, cover/planned year/cost/estimate results.
- `comparison.csv`/`simulations.csv`: summary by condition and each trial.
- `*.validation.json`: Confirmation of budget and completion of unreplaced iron pipes through shared verification.

Cost model: `2026-10-26-area-exponent`. Surface costs include distinct surfaces of every wholly contained pipe, including
Calculate using distinct surfaces of every wholly contained pipe. The raw data and predictors remain unchanged.
