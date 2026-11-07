> User provided results after submission: public display **$77.21M**. The standard for all three editions is the original $77.22M edition. Source: `../official_results.json`. ``Not acquired'' in the trial calculation records below is the status as of before submission.

# Candidate to integrate 3 circles from $77.22M version at the same time

Submission candidate: **`submission_circle_triples.csv`**. No official score was obtained at that stage.
Retain the best $77.22M CSV as baseline and improve geometry without changing predictors or the cost formula.

## Change and explore

For a common no-future-leak scheduled year, examine 10 neighbors within 100 m and a 320-row CSV gap for
Consider a combination of 3 circles. The union of all pipes completely included in the original 3 circles is up to 16.
Build a new circle covering every target pipe, then recheck incidental pipes and surfaces.
Reject newly included unreplaced pipes scheduled for the same year or later.
Require at least $25 in fixed savings and $10 in estimated savings after allowing for empty-circle skipping.
Choose disjoint groups, place each merged circle at the earliest original row, and remove the other two rows.
Preserve the relative order of all other circles.

Geometric evaluation was performed on 2,570 pairs, and **3-circle integration of 24 pairs** was adopted from 32 positive candidates.
Of these, **five groups saved fixed costs only when all three circles were merged; no two-circle subset saved fixed costs**.
This merges three circles, each potentially covering multiple pipes, rather than three individual pipes.

## Verification with zero leak

| Indicator | $77.22M version | This time |
|---|---:|---:|
| Circle count | 19,352 | **19,304** |
| Construction cost | $180,290,222.26 | **$180,258,947.56** |
| Completion year | 2045 | 2045 |

Construction savings: **$31,274.70**.
Preserved coverage of all originally contained pipes. Under the same conditions, no pipes were delayed and 16 were advanced.
Shared validation also confirmed budget-feasible completion for unreplaced iron pipes.
The baseline's geometric-coverage limitation for historically replaced original iron remains.
No supplementary coverage circles were added; do not report a pass on full original-iron coverage.

Passed 2 tests. With 2 circles, there is no fixed cost savings, but if there are 3 circles, there is a savings arrangement,
Confirmed that circles from different scheduled years were not merged.

## Comparison trial calculation of common random numbers (30 times for each condition)

| Evaluation model | Hazard multiplier | Mean construction savings | Mean score difference |
|---|---:|---:|---:|
| Fine age bands | 0.5 | $21,528 | +$43,328 |
| Fine age bands | 1 | $15,097 | +$20,497 |
| Fine age bands | 2 | −$1,461 | +$4,254 |
| Old 5-year age bands | 0.5 | $20,592 | +$22,349 |
| Old 5-year age | 1 | $16,440 | +$20,960 |
| Old 5-year age bands | 2 | −$3,213 | +$2,190 |

Mean scores were higher in all six settings, but gains were small.
At twice the hazard, changes in empty-circle skipping and related effects increased mean construction costs, and the score-difference
approximate 95% Monte Carlo interval also included zero. Robust improvement across all settings was not established.
Intervals for the score differences in the other four settings were above zero, but they exclude model uncertainty.

Same-year execution and no delay were checked against the no-future-leak schedule; they do not guarantee the same timing in
identical timing is not guaranteed. Compare while retaining the best existing submission.

Details: `merges.csv`, `report.json`, `comparison.csv`, `simulations.csv`, and validation JSON.
Cost model: `2026-10-26-area-exponent`. Input, baseline, and submission SHA-256 hashes are recorded.
