# Shana Nursoo — Week 1 cost prediction

My runs of the three models assigned to me: **Linear Regression** (with Anthony),**XGBoost** (with Takito)
and **CatBoost** (with Takito). Data: `data/train_predict_cost.csv` (14,107 leaks, 2019–2026). Seed 440.
The leak year (`event_year`) is always a feature so the models can follow cost changes over time.

## Results for the team table

Each model was trained twice, on `y_train` (raw dollars) and on `y_log_train = log1p(cost)` (converted back
with `np.expm1`). The row to report is whichever has the lower mean RMSE; the two are never mixed.
Means are equal-weight averages of the four years.

**RMSE ($)**

| Model | Target reported | 2023 | 2024 | 2025 | 2026 | Mean |
|---|---|---:|---:|---:|---:|---:|
| Linear Regression | log | 142,861 | 88,158 | 115,236 | 135,520 | **120,444** |
| XGBoost | log + smearing | 160,409 | 100,341 | 113,616 | 131,796 | **126,540** |
| CatBoost | raw | 163,078 | 99,183 | 115,578 | 130,288 | **127,032** |**MAE ($)** for the same rows

| Model | Target reported | 2023 | 2024 | 2025 | 2026 | Mean |
|---|---|---:|---:|---:|---:|---:|
| Linear Regression | log | 25,529 | 14,105 | 20,282 | 19,782 | **19,925** |
| XGBoost | log + smearing | 24,153 | 13,723 | 23,684 | 21,667 | **20,807** |
| CatBoost | raw | 33,717 | 19,694 | 29,525 | 27,928 | **27,716** |

The other target for each model, for comparison:

| Model | Target | RMSE 2023 | 2024 | 2025 | 2026 | Mean RMSE | Mean MAE |
|---|---|---:|---:|---:|---:|---:|---:|
| Linear Regression | raw | 158,615 | 99,159 | 114,090 | 128,796 | 125,165 | 25,637 |
| XGBoost | raw | 164,504 | 105,006 | 114,550 | 139,337 | 130,849 | 29,365 |
| CatBoost | log + smearing | 160,751 | 103,771 | 114,910 | 130,126 | 127,390 | 20,512 |

For reference, always predicting the training-set mean scores a mean RMSE of 136,356.

**Caveat on 2026.** All choices (features, feature sets, targets) were made on 2023–2025 only, then 2026
was scored once. The best 2026 RMSEs among my runs are the raw-dollar Linear Regression variants
(128,635–128,796), not the log one reported above (135,520). Linear Regression's lower mean comes from
2023–2025, the years used to pick its features, so it is partly fitted to those years.

## Files

| File | What it is |
|---|---|
| `folds.py` | Step 1: loads the shared CSV and splits it into the four year folds (`X`, `y`, `y_log`). |
| `linear_regression.py` | Linear Regression experiments (OLS and Ridge, feature-block selection). |
| `boosting.py` | XGBoost and CatBoost experiments (`boosting.py xgboost`, `boosting.py catboost`). |
| `output_<model>_<target>.csv` | Held-out predictions for 2023–2026: 8,586 rows, `pipe_id,predicted_cost`. |
| `results/linear_regression/` | Metrics per year and mean, every feature trial (`experiments.csv`), selected features. |
| `results/xgboost/`, `results/catboost/` | Metrics per year and mean, chosen depth and tree count per fold, feature sets. |

`<target>` is `raw`, `log` or `log_smear`. Negative predictions are clipped to 0.

| Fold | Training years | Test year | Test rows |
|---|---|---|---:|
| 1 | 2019–2022 | 2023 | 1,824 |
| 2 | 2019–2023 | 2024 | 1,951 |
| 3 | 2019–2024 | 2025 | 1,773 |
| 4 | 2019–2025 | 2026 | 3,038 |

## Shared setup

**Starting features:** `event_year`, `pipe_length`, `years_used_at_leak`, `midpoint_x`, `midpoint_y`,
`season_sin`, `season_cos`, and one-hot material and surface flags (wrought iron and water are the dropped
reference levels, being the most common).

**Targets, kept separate:**

- `raw`: fit on cost in dollars.
- `log`: fit on `log1p(cost)`, predictions back-transformed with `np.expm1`.
- `log_smear`: the `log` fit multiplied by Duan's smearing factor (mean of `exp(residual)` on the training
  rows). Plain `expm1` predicts closer to the median than the mean, which under-predicts the rare very
  expensive leaks that dominate RMSE; this corrects for it. It is still a model trained on `y_log_train`.

Time-of-day and weekday columns were excluded because a future leak scenario has no known time;
`route_id`, `straight_section_id` and the `material_surface` string are IDs, not numeric predictors.

## Linear Regression

**Preprocessing (fit on each fold's training years only):** median imputation with missing-value indicators
(history columns are blank in 2019), then standardization.

**Feature experiments:** 108 candidate feature blocks: log length/age, material×length and surface×length
interactions, material–surface pairs, and every family of the columns Takito added on 2026-10-05 (prior-year
cost history, nearby inventory, repair history, routes, topology, geometry). Starting from the base set, each
round tries adding every unused block and removing every current block (event year stays), and keeps the
single change that lowers the mean 2023–2025 RMSE by more than $50. It stops when nothing helps.
All trials are logged in `results/linear_regression/experiments.csv`.

**Ridge:** also fitted on the selected features, with alpha chosen inside each fold by training on all
but the last training year and validating on that year. It did not beat OLS on mean RMSE.

| Model | Target | 2023 | 2024 | 2025 | 2026 | Mean 2023–25 | Mean 2023–26 |
|---|---|---:|---:|---:|---:|---:|---:|
| OLS, selected features | log | 142,861 | 88,158 | 115,236 | 135,520 | 115,418 | 120,444 |
| OLS, selected features | log_smear | 150,429 | 87,532 | 113,658 | 133,258 | 117,206 | 121,219 |
| Ridge, selected features | log_smear | 152,893 | 89,058 | 113,675 | 133,258 | 118,542 | 122,221 |
| Ridge, selected features | log | 162,678 | 88,170 | 115,239 | 135,521 | 122,029 | 125,402 |
| OLS, selected features | raw | 158,615 | 99,159 | 114,090 | 128,796 | 123,955 | 125,165 |
| OLS, starting features | raw | 159,850 | 99,746 | 114,579 | 128,667 | 124,725 | 125,711 |
| Ridge, selected features | raw | 161,925 | 99,159 | 114,090 | 128,635 | 125,058 | 125,952 |
| OLS, starting features | log_smear | 159,915 | 103,094 | 116,678 | 131,528 | 126,562 | 127,804 |
| OLS, starting features | log | 164,971 | 107,557 | 121,567 | 136,260 | 131,365 | 132,589 |
| Training-mean constant | raw | 169,549 | 111,782 | 124,485 | 139,608 | 135,272 | 136,356 |

- **Log vs raw.** With the starting features, raw dollars give lower RMSE (125,711 vs 132,589) while log
  gives much lower MAE: the log model predicts typical leaks well and misses the expensive ones.
- **Smearing** closes most of that gap for the starting features (132,589 → 127,804).
- **Prior-year cost history** around the pipe (same material/surface, nearby radius, grid cell, segment) is
  what helped the log model most. The raw model barely benefits: it kept only a 250 m segment history block
  and `current_pu_fraction`, and dropped `season_sin`, `years_used_at_leak`, `midpoint_y` and `pipe_length`.

## XGBoost and CatBoost

No imputation or scaling; both libraries handle missing values directly.

**Tuning, inside each fold's training years only:** fit on every training year except the last, score dollar
RMSE on that last year for tree depth 3 or 6 and 25 to 1,500 trees (learning rate 0.05, checked every 25
trees), then refit on all training years with the best setting. Raw, log and log_smear are tuned separately.
XGBoost also uses 80% row and column subsampling.

**Feature-set experiments**, compared on mean 2023–2025 RMSE:

- `starting`: the 16 starting features.
- `starting+history`: plus all prior-year cost-history columns (`hist_*`).
- `starting+all_new`: plus every usable column Takito added on 2026-10-05.

| Model | Feature set | Target | 2023 | 2024 | 2025 | 2026 | Mean 2023–25 | Mean 2023–26 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| XGBoost | all_new | log_smear | 160,409 | 100,341 | 113,616 | 131,796 | 124,788 | 126,540 |
| XGBoost | starting | log_smear | 161,472 | 102,619 | 115,109 | 129,688 | 126,400 | 127,222 |
| XGBoost | starting | raw | 164,504 | 105,006 | 114,550 | 139,337 | 128,020 | 130,849 |
| XGBoost | history | log_smear | 161,455 | 102,221 | 122,021 | 132,625 | 128,566 | 129,580 |
| XGBoost | history | raw | 167,161 | 96,866 | 123,949 | 132,980 | 129,325 | 130,239 |
| XGBoost | starting | log | 164,150 | 105,226 | 118,858 | 135,443 | 129,411 | 130,919 |
| XGBoost | all_new | log | 164,622 | 106,056 | 118,823 | 135,591 | 129,833 | 131,273 |
| XGBoost | history | log | 165,683 | 107,295 | 119,233 | 135,753 | 130,737 | 131,991 |
| XGBoost | all_new | raw | 169,772 | 93,243 | 137,215 | 133,130 | 133,410 | 133,340 |
| CatBoost | all_new | raw | 163,078 | 99,183 | 115,578 | 130,288 | 125,947 | 127,032 |
| CatBoost | starting | raw | 163,513 | 101,253 | 114,058 | 129,055 | 126,275 | 126,970 |
| CatBoost | starting | log_smear | 160,751 | 103,771 | 114,910 | 130,126 | 126,478 | 127,390 |
| CatBoost | history | log_smear | 163,322 | 102,830 | 113,734 | 131,732 | 126,629 | 127,904 |
| CatBoost | all_new | log_smear | 166,849 | 102,870 | 114,157 | 130,135 | 127,959 | 128,503 |
| CatBoost | history | raw | 162,029 | 95,094 | 130,368 | 130,252 | 129,163 | 129,436 |
| CatBoost | starting | log | 164,027 | 106,791 | 120,844 | 134,962 | 130,554 | 131,656 |
| CatBoost | history | log | 169,196 | 106,886 | 118,227 | 135,950 | 131,436 | 132,565 |
| CatBoost | all_new | log | 168,808 | 106,068 | 119,613 | 134,870 | 131,496 | 132,340 |

- **Raw-dollar boosting stops almost immediately.** Inner validation picked only 25–50 trees for every raw
  model: after that, extra trees chase a few $1M+ leaks in the training years and get worse on the next year.
- **Smearing improved every log model**, by 2,200–5,000 of mean 2023–2025 RMSE.
- **The extra columns help little.** The best feature set beats `starting` by about 1,600 (XGBoost) and 300
  (CatBoost) of mean 2023–2025 RMSE, and both are worse than `starting` in 2026.
- **The models are similar.** My XGBoost (126,540) and CatBoost (127,032) are a bit better than Takito's
  runs in the team sheet (130,463 and 130,561), but none of the boosted models beat Linear Regression.

## Reproduce

From the repository root:

```bash
python -m venv .venv
.venv/bin/pip install -r notebooks/Shana_Nursoo/requirements.txt
.venv/bin/python notebooks/Shana_Nursoo/linear_regression.py   # about 15 minutes
.venv/bin/python notebooks/Shana_Nursoo/boosting.py xgboost     # about 16 minutes
.venv/bin/python notebooks/Shana_Nursoo/boosting.py catboost    # about 15 minutes
```

`python notebooks/Shana_Nursoo/folds.py` prints the fold sizes as a quick check of Step 1.
XGBoost and CatBoost use 4 threads; results can differ slightly on another machine or library version.
