# Execution results of the initial 3-year focused version

## Official display score after submission (user report)

The current `early3_adaptive.csv` scored **$76.91M**, while the previous `multi_pipe.csv` scored
The display result of **$71.40M** was shared in a screenshot.
The displayed difference is **+$5.51M (approximately 7.72%)**.
Keep this separate from local simulation results, and record the images and CSV hashes in
Recorded in `official_results.json`. Click here to access the evaluation site
These are user-provided submission results, not results independently fetched and matched to submissions.

## Main candidate to submit

**`early3_adaptive.csv`**. The previous CSV submission of $71.40M remains saved.
Circle combinations and order were reselected to match expected leak losses in the first three years.
Group risky pipes where efficient; replace pipes individually when grouping is inefficient.
Later-stage design groups contain at most three pipes.

## Actual history verification

Settings were selected from six candidates for time-series verification in 2024 and 2025, and verification was conducted without using them for setting selection in 2026.
Selected settings: half-year age bands, 0.5-year smoothing bandwidth, and history weight 0.85 for each additional past year.

| 2026 verification | Previous model | Current model |
|---|---:|---:|
| Leak capture rate by top 10% risk | 28.28% | 49.57% |
| Brier score (lower is better) | 0.08057 | 0.07937 |
| Log loss (lower is better) | 0.26437 | 0.27219 |
| Predicted average annual leak probability | 6.15% | 4.66% |
| Actual annual leak rate | 10.03% | 10.03% |

**Although the ranking has improved, the calibration of the absolute value of the leak probability cannot be said to have improved.**
The top capture rate in 2026 does not guarantee accuracy from 2027 to 2029.

## Comparative calculation of the initial 3 years and the entire period

Compare three plans under two leak models, hazard multipliers 0.5/1/2, and 30 paired repetitions per setting.
There were 540 full-period evaluations. Additional calculations using the same full-period leak times
First-three-year repair costs were also recorded separately. Every case completed by 2051.

The following paired comparison uses hazard multiplier 1. Amounts are in millions.

| Leak evaluation model | Previous first-three-year repair cost | Current first-three-year repair cost | Reduction | Full-period score difference (current minus previous) |
|---|---:|---:|---:|---:|
| Old model | 30.490 | 29.507 | 3.23% | +1.209 |
| New model | 37.906 | 34.780 | 8.25% | +2.538 |

Approximate 95% Monte Carlo intervals for full-period score differences were [-0.136, +2.554] for the old model,
and [+0.874, +4.203] million for the new model. These are not prediction intervals incorporating model error.
First-three-year repair costs were lower than the previous plan in all six settings examined.
The full-period score was higher in five of six settings; for the old model at hazard multiplier 0.5,
was $0.574M lower on average. The candidate therefore did not dominate every setting.

The comparison `early3_reorder_only.csv` retains the previous circle geometry and changes only order.
Not selected as the main candidate because standard-setting full-period scores were lower under both old and new models.
This CSV is also retained for reproducing the experiment.

## Budget and circle size

Assuming no future leaks:

| Indicators | Previous | This time |
|---|---:|---:|
| Number of circles | 15,328 | 19,838 |
| Total construction cost | $175,986,889.96 | $180,664,606.53 |
| Completion year | 2044 | 2045 |
| Remaining unreplaced iron pipes | 0 | 0 |

Construction costs increase by approximately $4.68M. This reflects early separation of high-risk pipes and
smaller later-stage groups increased costs; first-three-year repair savings alone are insufficient for judging the plan.

First-three-year results under the current execution order, assuming no future leaks:

| Year | Number of circles constructed | Number of newly replaced steel pipes | Median circle radius | Average circle radius |
|---|---:|---:|---:|---:|
| 2027 | 2,534 | 3,221 | 3.86 | 5.25 |
| 2028 | 2,250 | 2,572 | 5.24 | 5.97 |
| 2029 | 1,200 | 1,424 | 6.43 | 8.67 |

**The actual radius is not getting smaller every year.** In the early stages, it is better to protect the dangerous and short pipes alone.
was often more efficient. Rather than imposing a descending-radius order,
risk and cost efficiency were prioritized. The later-phase maximum of three pipes refers to design targets;
It is not a radius limit. Incidental pipes can also enter the circle, so pipe count and radius are not simply proportional.

## Execution confirmation

- Passed 8 unit tests. Efficient separation of multiple pipe groups and isolated pipes was also confirmed.
- Reload the CSV after output and confirm that all unreplaced iron pipes are covered and completed within the 25-year budget.
- Extracted 200 cost units (100 cost units each) from the 2 new CSV plans and passed round-robin confirmation of inclusion in all 43,039 pipes.
- Confirm that the SHA-256 of the last CSV matches the previous execution result and has not been overwritten.
- Details saved in `report.json`, `comparison.csv`, `holdout_2026.csv`, `spot_audit.json`.

Budget, cost, and leak-timing assumptions match the earlier experiment, including its reservations about the unavailable official specification.
Later user-provided official displays showed $76.91M for this version and $71.40M for the previous version.
This single submission result does not guarantee improvement on other future data.
