# Stricter skip conditions — public display $77.22M

**This edition is based on the original $77.22M exploration expansion. It is not a stack of three editions in order.**

Require empty-circle bounds of 10% per circle and 15% for any member, plus conservative fixed savings of at least $25, under two models and three hazard levels. Exclude 19 candidates and accept nine groups. No-leak savings were $3,171.74; the public display matched the baseline, without confirmed improvement.

[Submitted CSV](outputs/submission_skip_guard.csv) / [Official display source and CSV hash](official_results.json)

The predictors, repair-cost estimates, and cost formula are unchanged. Endpoint containment, surface types, and incidental replacement costs were recalculated.
Cost model: `2026-10-26-area-exponent`. Inputs match repository data; raw data are not duplicated.

## Saved evidence and execution results

- [Score image](outputs/official_score.png)
- [Yearly Breakdown Image](outputs/official_annual_table.png)
- [Original experiment summary](outputs/SUMMARY.md)
- [Validation and input/output hash](outputs/report.json)
- [Estimate by condition](outputs/comparison.csv)
- [Reconfirmation during integration](outputs/integration_validation.json)

The Public value is based on checking the correspondence between user-provided images and submitted files. Click here for evaluation site
These were not independently fetched; displayed precision is 0.01M. Private scores are unknown.
The official value of `report.json` is null and the unevaluated description in the summary is saved as a record before submission.
Post-submission values are maintained in `official_results.json`.

Original target coverage and zero replacement delays were confirmed under the no-leak schedule. Future leaks can advance construction,
so replacement years are not guaranteed across all possible futures.
The baseline's geometric-coverage limitation for historically replaced original iron remains.
Shared validation explicitly targets active iron; it does not claim full original-iron coverage.

## Rerun

Use the repository dependencies. In `submissions/2026-10-28_ryota_early3/`,
Uses frozen prediction/geometry helpers and `data/`. Integration changes were limited to input paths.

```sh
python -m unittest discover -s submissions/2026-10-28_ryota_skip_guard -v
python submissions/2026-10-28_ryota_skip_guard/merge_skip_guard.py --sims 30
```

Rerunning overwrites this folder's outputs. Save new experiments in a newly dated/named folder.
