# Shrink trailing circle — public display $77.29M

**This edition is based on the original $77.22M exploration expansion. It is not a stack of three editions in order.**

Shrink 81 later circles after excluding pipes covered earlier. Preserve each row's replacement targets and cumulative coverage without adding unintended unreplaced pipes. The 19,352-circle count and order remain unchanged. No-leak construction savings were $84,298.09; this achieved the highest displayed public score at that stage.

[Submitted CSV](outputs/submission_shrink_after_work.csv) / [Official display source and CSV hash](official_results.json)

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
python -m unittest discover -s submissions/2026-10-28_ryota_shrink_after_work -v
python submissions/2026-10-28_ryota_shrink_after_work/shrink_after_work.py --sims 30
```

Rerunning overwrites this folder's outputs. Save new experiments in a newly dated/named folder.
