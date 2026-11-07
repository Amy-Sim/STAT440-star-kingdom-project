# Takito latest model and replacement plan — 26 October 2026

## Result and evidence

The user-supplied evaluator screenshot shows **Takito: $74.78M at 15:42 on 26 October 2026**, the highest value among the visible rows. Other visible Takito results are $74.25M and $74.00M at 15:34 and $74.16M at 15:25. The screenshot does not show uploaded filenames. The user subsequently confirmed that this is the result of**21a_20a_catboost6863_logrf3137.csv**. The filename association is user-confirmed. The screenshot is user-provided evidence, not a fresh evaluator query or proof of a global leaderboard rank. Times are copied from the screenshot without timezone conversion.

The latest locally prepared candidate is **21a_20a_catboost6863_logrf3137.csv**. Its code, frozen predictions, audit tables and existing validation outputs are published together in [the submission folder](../submissions/2026-10-26_best20a_catboost_logrf/). No further evaluator submission was made for this report.

## Process

The task is to replace all original iron pipes during 2027–2051 and maximize the $250M allocation remaining after construction and leak repairs. Candidate 21a builds on the team's 20a plan, preserving its 36,375 circles and p17b leak probabilities. It changes only conditional repair-cost predictions and the resulting execution order. This is a team-derived plan: it reuses earlier circle grouping and geometry work, Rion's dynamic overlap ordering, the cohort probability refinements, Takito's CatBoost and Anthony's corrected log Random Forest.

For each pipe, the 2027 repair-cost forecast conditional on a leak is:

```text
severity = 0.6862701169749837 × Takito CatBoost
         + 0.3137298830250163 × Anthony corrected log RF
value = max(leak_probability × (severity − 200 × pipe_length_m), 0)
```

The $200/m subtraction accounts for the replacement charge no longer paid after a leaking pipe has been repaired as polyurethane. Eight active pipes with unknown material have no supported stack forecast and retain the control's stable severity forecast. Historically leaked and originally polyurethane pipes have zero active severity.

The priority for a circle is the sum of values of its still-unreplaced, wholly contained pipes divided by its current construction cost. After selecting a circle, overlapping circles lose the value and replacement cost of pipes already replaced. This simulation produces a fixed CSV before submission; it cannot respond to actual future leaks. p17b retains cohort-stage probabilities, including 1963: 0.12, 1964: 0.55, 1965: 0.70 and 1966: 0.30 for active pipes, with the existing team probabilities elsewhere.

## Testing: repair-cost model

The stack considered 15 prediction columns and used nonnegative weights summing to one, without an intercept, minimizing pooled MSE on earlier out-of-time predictions. Deterministic SLSQP used uniform and vertex starts; seed 440 is recorded. Only CatBoost and corrected log RF receive nonzero weights in the final 2027 fit. Historical tests used their own past-only weights, not these final coefficients.

For test year 2024 weights use 2023 predictions; for 2025 they use 2023–2024; for 2026 they use 2023–2025. Final 2027 weights use 8,592 out-of-time observations from 2023–2026. The comparison below uses the same 6,766 events in 2024–2026 and arithmetic means of annual metrics; 2023 is N/A for stack evaluation.

| Method | Mean MAE ($) | Mean RMSE ($) |
| --- | ---: | ---: |
| All-candidate optimized stack | 23,507.16 | 113,605.17 |
| Existing stable ensemble | 22,667.17 | 113,822.99 |
| Takito CatBoost | 25,246.75 | 113,185.40 |
| Corrected log RF | 21,169.98 | 113,599.40 |
| Previous six-candidate optimized stack | 23,471.65 | 113,346.55 |

The new stack slightly reduces RMSE versus stable while increasing MAE, and it does not beat CatBoost's RMSE. A higher planning score therefore must not be described as universal predictive superiority. These historical years have been inspected in earlier experiments and are not an untouched final holdout. See the published annual metrics, historical weights, OOF predictions and verification record in the submission folder.

## Testing: exported replacement plan

| Item | 20a control | 21a |
| --- | ---: | ---: |
| Circles | 36,375 | 36,375 |
| Changed rank positions vs. 20a | — | 25,389 |
| Uncovered original iron pipes | 0 | 0 |
| Construction cost, historical local formula, no future leaks | $148,081,592.66 | $148,028,948.98 |
| Completion year in that local scenario | 2041 | 2041 |
| Zero-cost skipped units in that local scenario | 13,138 | 13,248 |
| Official score assigned to this exact file | historical 74.03M record, earlier evaluator version | **$74.78M (user-confirmed screenshot result)** |

The local construction difference is $52,643.68. It is not the difference in official scores. Original 20a order was reproduced with its original costs; 21a has exactly the same circle multiset. The published frozen inputs reproduce the 21a CSV exactly after newline normalization, including forecast recomputation, the fallback join, full iron coverage, budget carryover and completion under the historical local cost function.

## Evaluator changes and limitations

The shared experiment Google Doc, read on 26 October 2026, records evaluator bug fixes and a newly noted formula:

```text
100 + surface_rate × area^0.85 + 200 × length
```

The existing local ordering and validator used to generate these files instead use:

```text
100 + (surface_rate × area)^0.85 + 200 × length
```

The plan is preserved exactly as prepared. The local cost and completion values above are explicitly historical-formula checks; they are **not revalidation under the revised formula**. The published reproduction intentionally retains that formula to reproduce the submitted artifact. Scores recorded before and after evaluator changes should not be used to claim a controlled improvement. In particular, subtracting the historical 20a score of 74.03M from the screenshot's 74.78M would not establish a clean model-only gain. Re-evaluate control and candidate under the same evaluator version for that comparison. Public performance does not establish private performance or identify which component caused an improvement.

## Reproduction

From a clone containing this branch, install `numpy pandas scipy lightgbm`, then run from the repository root:

```powershell
python submissions/2026-10-26_best20a_catboost_logrf/reproduce.py
```

This rebuilds the plan using frozen predictions and pipe probabilities and verifies the checked-in ordering. It does not retrain base models or recreate the upstream search. `build_submission_workspace_original.py` preserves the original workspace-dependent build for provenance; `reproduce.py` is the portable entry point. The original manifest preserves original Windows-file hashes; `publication_manifest.json` additionally records LF-normalized hashes so Git checkout newline conversion is transparent. Only the candidate CSV is an evaluator submission; audit and model-prediction CSVs are supporting evidence.

## Sources

- [Shared experiment record](https://docs.google.com/document/d/1N32Z_DC6Frw1OYwSNA9mIlXjgDPuKiOQXH4nJV2RZcQ/edit), current relevant contents read 26 October 2026: historical method/results and evaluator change note.
- [20a at reviewed main commit 668a598](https://github.com/reinesana/STAT440-star-kingdom-project/tree/668a598ba8efd478d1c5bf569b39fc7fb93162e2/submissions/2026-10-22_candidate_20_sameyear_merge): frozen geometry and reference plan.
- [Published candidate and evidence](../submissions/2026-10-26_best20a_catboost_logrf/): exact coefficients, forecasts, OOF tables, validation, manifest and audits.
- User-provided evaluator screenshot: visible Takito results dated 26 October 2026; filename association confirmed by the user. Browser chrome and unrelated screen contents are not republished.
