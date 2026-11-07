# Rion Oyama — Week 1 cost prediction (R)

STAT 440: predict the monetary repair cost conditional on a pipe leaking.
This folder follows the archive layout of `notebooks/Takito_Kobayashi`, while preserving Rion's own R models, features, and results. It does not reproduce Takito's tuning or feature search.

## Original code

[`executed_code/Project_codeW1.Rmd`](executed_code/Project_codeW1.Rmd) preserves Rion's model calculations and exploratory chunks. The English cleanup translates its comments, headings, and display text. `executed_code_sha256.json` records the original pre-translation archive hash; that version remains in Git history.

Current English-source SHA-256: `879179e43fa2c359f6e0392f7a4d542ba41b745d5f8c5ab6d50ade7a5035933c`.

## Data

The shared input is [`../../data/train_predict_cost.csv`](../../data/train_predict_cost.csv): 14,107 historical leak events, prepared by joining pipe attributes and leak costs. The existing shared data is not duplicated or modified. `source_hashes.json` identifies the exact input used. No high-cost observations were removed or capped.

## Prediction CSVs

- [`output_randomforest.csv`](output_randomforest.csv): original-cost Random Forest, 2023–2026.
- [`output_gamma.csv`](output_gamma.csv): Gamma regression with log link, 2023–2026.
- [`output_lightgbm.csv`](output_lightgbm.csv): log1p-target LightGBM, 2023–2026.

Each has **8,586 held-out predictions** and exactly two columns: `pipe_id,predicted_cost`, matching Takito's output format. These are predictions for historical test events, not all inventory pipes and not a 2027–2051 forecast. Dates and observed costs are available in `results/per_fold/` and can also be joined from the shared input.

Additional RF log1p and LightGBM raw predictions for 2023–2025 remain in `results/per_fold/`. RF log1p and LightGBM raw were not evaluated for 2026 in the original notebook; no missing predictions or results are fabricated.

| Fold | Training years | Evaluation year | Test rows |
|---|---|---|---:|
| 1 | 2019–2022 | 2023 | 1,824 |
| 2 | 2019–2023 | 2024 | 1,951 |
| 3 | 2019–2024 | 2025 | 1,773 |
| 4 | 2019–2025 | 2026 | 3,038 |

## Results

| Model | Target | Years | Mean MAE | Mean RMSE |
|---|---|---|---:|---:|
| Gamma | log link | 2023,2024,2025,2026 (4 years) | 23,661.71 | 125,590.37 |
| LightGBM | log1p | 2023,2024,2025,2026 (4 years) | 18,303.73 | 130,910.84 |
| Random Forest | log1p | 2023,2024,2025 (3 years) | 17,602.74 | 129,280.57 |
| LightGBM | raw | 2023,2024,2025 (3 years) | 41,958.59 | 156,989.69 |
| Random Forest | raw | 2023,2024,2025,2026 (4 years) | 35,062.51 | 142,666.84 |

Means above are descriptive, equally weighted averages of the listed annual metrics, not pooled errors. **Three-year and four-year averages must not be compared directly.** Full-precision recomputation can differ by a cent from averages calculated from screenshot-rounded values.

For the documented 2025-selection/2026-evaluation procedure, report those years separately. In the RF comparison, raw had lower 2025 RMSE; in the LightGBM comparison, log1p had lower 2025 RMSE. Gamma's 2025 RMSE was 114,040.92 and its 2026 RMSE was 129,651.09. This is a record of already-inspected project results, not a claim that 2026 remains a fresh independent holdout for subsequent experiments.

See [`results/fold_metrics.csv`](results/fold_metrics.csv), [`results/average_metrics.csv`](results/average_metrics.csv), and the [Japanese report](results/results.md).

## Reproduce

Install dependencies once in R:

```r
source("notebooks/Rion_Oyama/requirements.R")
```

Then, from the repository root:

```sh
Rscript notebooks/Rion_Oyama/reproduce.R rion_reproduction
```

The output directory must be new or empty. An optional second argument supplies a local copy of the input CSV. The runner checks its SHA-256 hash before fitting.

The runner executes all 19 archived R chunks in order in a fresh environment. Only file handling changes: GitHub CSV reads use the verified local input, `View()` is suppressed for non-interactive execution, and CSV writes go into the chosen output directory. RF 2024 predictions, which were computed but not exported in the notebook, are exported from its existing prediction vectors. Model formulas, parameters, transformations, and seeds are unchanged. It does not tune models or add new 2026 variants.

The runner recomputes MAE/RMSE from exported predictions, checks uniqueness and observed costs against the input, and exports the three two-column prediction files. The supplied notebook is an original archive; use the runner for portable batch execution rather than knitting it directly.

`selected_configs/configurations.json` documents model settings; `results/sessionInfo.txt` and `results/versions.json` record R/package versions. Results can vary across package versions/platforms. The seed is 440; Gamma fitting is deterministic.

## Interpretation

All models use material, surface, length, age at the event, midpoint coordinates, and event year. Dates/ages describe a specified leak event; future deployment needs a scenario date from the leak model. Tree models do not automatically extrapolate an inflation trend. Gamma uses original costs with a log link, not a log-transformed target. Log-target RF/LightGBM use `expm1()` without a mean-retransformation correction, and can underestimate expected aggregate cost. LightGBM negative predictions are clipped to zero before evaluation, as specified in the original code.
