# Construction cost prediction comparison of 3 single boosting models

Used all 14,107 rows of the specified `github-main/data/train_predict_cost.csv`. Features and parameters were selected primarily by RMSE in original cost units, then tested using the specified four folds.

A total of 4,200 Optuna trials completed. Feature additions/removals were also assessed inside temporal validation. These are the best candidates found within a finite search, not guaranteed global optima.

## 4Fold simple average

| model | MAE | RMSE |
| --- | --- | --- |
| xgboost | 29,878.19 | 130,462.53 |
| catboost | 29,803.85 | 130,560.76 |
| lightgbm | 28,170.72 | 130,766.84 |

These average years equally. Pooled event-level metrics are retained separately in `pooled_metrics.csv` and are distinct from the requested annual means.

## Test value for each Fold

| model | fold | train_end | test_year | n_train | n_test | MAE | RMSE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | 1 | 2022 | 2023 | 5521 | 1824 | 36,022.35 | 163,663.83 |
| xgboost | 2 | 2023 | 2024 | 7345 | 1951 | 27,719.82 | 104,873.69 |
| xgboost | 3 | 2024 | 2025 | 9296 | 1773 | 28,803.12 | 120,522.83 |
| xgboost | 4 | 2025 | 2026 | 11069 | 3038 | 26,967.45 | 132,789.79 |
| catboost | 1 | 2022 | 2023 | 5521 | 1824 | 35,284.02 | 159,966.02 |
| catboost | 2 | 2023 | 2024 | 7345 | 1951 | 22,154.64 | 100,359.90 |
| catboost | 3 | 2024 | 2025 | 9296 | 1773 | 34,884.38 | 131,720.14 |
| catboost | 4 | 2025 | 2026 | 11069 | 3038 | 26,892.36 | 130,196.96 |
| lightgbm | 1 | 2022 | 2023 | 5521 | 1824 | 33,623.78 | 160,902.81 |
| lightgbm | 2 | 2023 | 2024 | 7345 | 1951 | 19,819.78 | 100,661.47 |
| lightgbm | 3 | 2024 | 2025 | 9296 | 1773 | 35,306.79 | 129,597.41 |
| lightgbm | 4 | 2025 | 2026 | 11069 | 3038 | 23,932.55 | 131,905.69 |

## Value on learning data (reference)

| model | fold | train_MAE | train_RMSE |
| --- | --- | --- | --- |
| xgboost | 1 | 34,537.68 | 168,196.05 |
| xgboost | 2 | 34,122.66 | 151,500.63 |
| xgboost | 3 | 27,667.30 | 143,171.31 |
| xgboost | 4 | 28,312.27 | 141,946.53 |
| catboost | 1 | 34,291.66 | 172,261.53 |
| catboost | 2 | 33,251.91 | 165,284.38 |
| catboost | 3 | 27,234.46 | 134,828.03 |
| catboost | 4 | 26,724.62 | 132,826.39 |
| lightgbm | 1 | 35,192.01 | 171,329.81 |
| lightgbm | 2 | 32,781.40 | 167,163.00 |
| lightgbm | 3 | 27,379.14 | 141,565.14 |
| lightgbm | 4 | 24,274.35 | 134,270.34 |

Training errors measure fit to the same data used to train the model; assess future performance using the test values above. Training periods overlap across folds.

## Selected features/settings

### xgboost — Test 2023

Features: `event_decimal_year`, `event_hour`, `event_month`, `event_weekday`, `event_weekend`, `event_year`, `hist_age_band_all_max`, `hist_age_band_last1_max`, `hist_age_band_last1_mean`, `hist_age_band_last1_median`, `hist_age_band_last1_n`, `hist_age_band_last1_std`, `hist_age_band_last1_tail_rate`, `hist_age_band_last2_max`, `hist_age_band_last2_mean`, `hist_age_band_last2_median`, `hist_age_band_last2_n`, `hist_age_band_last2_tail_rate`, `hist_grid1000_last1_max`, `hist_grid1000_last1_mean`, `hist_grid1000_last1_median`, `hist_grid1000_last1_n`, `hist_grid1000_last1_std`, `hist_grid1000_last1_tail_rate`, `hist_grid1000_last2_max`, `hist_grid1000_last2_mean`, `hist_grid1000_last2_median`, `hist_grid1000_last2_n`, `hist_grid1000_last2_std`, `hist_grid1000_last2_tail_rate`, `hist_grid250_last1_max_log1p`, `hist_grid250_last1_mean`, `hist_grid250_last1_median`, `hist_grid250_last1_n`, `hist_grid250_last1_std`, `hist_grid250_last1_tail_rate`, `hist_grid250_last2_max`, `hist_grid250_last2_max_log1p`, `hist_grid250_last2_mean`, `hist_grid250_last2_median`, `hist_grid250_last2_n`, `hist_grid250_last2_tail_rate`, `hist_grid500_last1_max`, `hist_grid500_last1_mean`, `hist_grid500_last1_median`, `hist_grid500_last1_n`, `hist_grid500_last1_std`, `hist_grid500_last1_tail_rate`, `hist_grid500_last2_max`, `hist_grid500_last2_mean`, `hist_grid500_last2_median`, `hist_grid500_last2_n`, `hist_grid500_last2_std`, `hist_grid500_last2_tail_rate`, `hist_length_band_last1_max`, `hist_length_band_last1_mean`, `hist_length_band_last1_median`, `hist_length_band_last1_n`, `hist_length_band_last1_std`, `hist_length_band_last1_tail_rate`, `hist_length_band_last2_max`, `hist_length_band_last2_mean`, `hist_length_band_last2_median`, `hist_length_band_last2_n`, `hist_length_band_last2_std`, `hist_length_band_last2_tail_rate`, `hist_material_last1_max`, `hist_material_last1_mean`, `hist_material_last1_median`, `hist_material_last1_n`, `hist_material_last1_std`, `hist_material_last1_tail_rate`, `hist_material_last2_max`, `hist_material_last2_mean`, `hist_material_last2_median`, `hist_material_last2_n`, `hist_material_last2_std`, `hist_material_last2_tail_rate`, `hist_material_surface_all_mean`, `hist_material_surface_last1_max`, `hist_material_surface_last1_mean`, `hist_material_surface_last1_median`, `hist_material_surface_last1_n`, `hist_material_surface_last1_std`, `hist_material_surface_last1_tail_rate`, `hist_material_surface_last2_max`, `hist_material_surface_last2_median`, `hist_material_surface_last2_n`, `hist_material_surface_last2_std`, `hist_material_surface_last2_tail_rate`, `hist_surface_last1_max`, `hist_surface_last1_mean`, `hist_surface_last1_median`, `hist_surface_last1_n`, `hist_surface_last1_std`, `hist_surface_last1_tail_rate`, `hist_surface_last2_max`, `hist_surface_last2_mean`, `hist_surface_last2_median`, `hist_surface_last2_n`, `hist_surface_last2_std`, `hist_surface_last2_tail_rate`, `hour_cos`, `hour_sin`, `inventory_50m_road_count`, `lay_month`, `lay_year`, `length_age`, `log1p_pipe_length`, `log_age`, `log_length`, `material`, `material_brass`, `material_cast_iron`, `material_code`, `material_copper`, `material_gray_iron`, `material_surface`, `material_wrought_iron`, `midpoint_x`, `midpoint_y`, `month_cos`, `month_sin`, `orientation_cos2`, `orientation_sin2`, `pipe_length`, `season_cos`, `season_sin`, `span_x`, `span_y`, `surface`, `surface_code`, `surface_farmland`, `surface_grassland`, `surface_road`, `surface_structure`, `surface_swamp`, `surface_water`, `weekday_cos`, `weekday_sin`, `x1`, `x2`, `y1`, `y2`, `years_used`, `years_used_at_leak`, `years_used_squared`.

Parameters:
```json
{
  "learning_rate": 0.13905014990269526,
  "max_depth": 6,
  "min_child_weight": 34.98462044400472,
  "subsample": 0.6264151106000365,
  "colsample_bytree": 0.6879771575181293,
  "reg_lambda": 0.022033633109930038,
  "reg_alpha": 0.05582770810800726,
  "gamma": 331.48938572459264,
  "max_bin": 256
}
```

Iteration limit: 5. Trees in final fit: 5. Inner mean RMSE: 228,164.92.

### xgboost — Test 2024

Features: `age_x_wet_proximity`, `event_decimal_year`, `hist_age_band_all_mean`, `hist_age_band_all_std`, `hist_grid1000_all_max`, `hist_grid1000_last1_std`, `hist_grid250_all_mean`, `hist_grid250_all_median`, `hist_grid250_last2_median`, `hist_material_surface_all_max`, `hist_material_surface_all_median`, `hist_material_surface_all_n`, `hist_material_surface_last1_mean`, `hist_material_surface_last1_median`, `hist_material_surface_last1_n`, `hist_nearest25_mean`, `hist_nearest5_mean`, `hist_radius100_max`, `hist_radius250_mean`, `hist_radius250_tail_rate`, `hist_radius500_median`, `hist_radius500_n`, `hist_radius50_max`, `hist_radius50_mean`, `hist_surface_all_mean`, `hist_surface_all_std`, `hist_surface_all_tail_rate`, `inventory_100m_road_count`, `inventory_10m_road_count`, `log1p_years_used`, `midpoint_y`, `orientation_cos2`, `surface`, `surface_road`, `x1`.

Parameters:
```json
{
  "learning_rate": 0.012647139215234684,
  "max_depth": 7,
  "min_child_weight": 1.6319104134943172,
  "subsample": 0.8251104371470617,
  "colsample_bytree": 0.9783371999781912,
  "reg_lambda": 0.0033111601738007807,
  "reg_alpha": 0.0037604097745400585,
  "gamma": 73.59419681731733,
  "max_bin": 64
}
```

Iteration limit: 29. Trees in final fit: 29. Inner mean RMSE: 159,419.88.

### xgboost — Test 2025

Features: `hist_grid1000_all_max`, `hist_grid1000_all_n`, `hist_grid1000_all_tail_rate`, `hist_grid250_all_max`, `hist_grid250_all_median`, `hist_grid250_all_n`, `hist_grid250_all_tail_rate`, `hist_grid250_last2_std`, `hist_grid500_all_mean`, `hist_grid500_all_std`, `hist_grid500_last1_median`, `hist_grid500_last1_std`, `hist_grid500_last2_n`, `hist_length_band_all_max`, `hist_length_band_all_std`, `hist_material_surface_all_median`, `hist_material_surface_all_std`, `hist_material_surface_all_tail_rate`, `hist_nearest10_median`, `hist_nearest25_max`, `hist_nearest25_median`, `hist_nearest5_max`, `hist_radius100_max`, `hist_radius250_max`, `hist_radius250_median`, `hist_radius250_n`, `hist_radius250_tail_rate`, `hist_radius500_median`, `hist_radius500_n`, `hist_surface_all_mean`, `hist_surface_all_median`, `hist_surface_all_tail_rate`, `hour_sin`, `inventory_250m_count`, `inventory_5m_length_sum`, `season_cos`.

Parameters:
```json
{
  "learning_rate": 0.08409193184055333,
  "max_depth": 3,
  "min_child_weight": 15.526510189285549,
  "subsample": 0.8357745931507727,
  "colsample_bytree": 0.9026079909263425,
  "reg_lambda": 0.14655058813806465,
  "reg_alpha": 18.210142788209243,
  "gamma": 0.018350106046247292,
  "max_bin": 256
}
```

Iteration limit: 31. Trees in final fit: 31. Inner mean RMSE: 121,440.48.

### xgboost — test 2026

Features: `event_decimal_year`, `event_month`, `hist_age_band_last1_std`, `hist_age_band_last2_mean`, `hist_grid1000_last1_std`, `hist_grid250_all_max`, `hist_grid250_last1_std`, `hist_grid250_last2_n`, `hist_grid500_last1_max`, `hist_grid500_last1_tail_rate`, `hist_grid500_last2_std`, `hist_length_band_all_max`, `hist_length_band_all_mean`, `hist_length_band_last1_mean`, `hist_length_band_last1_median`, `hist_length_band_last2_n`, `hist_material_last1_median`, `hist_material_surface_all_median`, `hist_material_surface_all_std`, `hist_material_surface_all_tail_rate`, `hist_material_surface_last1_median`, `hist_material_surface_last2_max`, `hist_nearest10_max`, `hist_radius250_median`, `hist_radius250_n`, `hist_radius250_tail_rate`, `hist_radius500_max`, `hist_radius500_median`, `hist_radius50_max`, `hist_surface_last1_max`, `hist_surface_last1_median`, `month_cos`, `orientation_cos2`, `season_sin`, `surface`, `x1`, `x2`.

Parameters:
```json
{
  "learning_rate": 0.0545530453904611,
  "max_depth": 3,
  "min_child_weight": 1.0133149800238779,
  "subsample": 0.960673751576149,
  "colsample_bytree": 0.5865653353486538,
  "reg_lambda": 2.449123018250732,
  "reg_alpha": 4.154093515050563,
  "gamma": 0.48726716844443607,
  "max_bin": 256
}
```

Iteration limit: 19. Trees in final fit: 19. Inner mean RMSE: 102,999.22.

### catboost — test 2023

Features: `hist_grid250_all_median`, `hist_material_surface_last2_median`, `hist_surface_all_mean`, `hist_surface_all_median_log1p`, `hist_surface_all_tail_rate`, `material`, `material_surface`, `surface`, `surface_road`, `y2`.

Parameters:
```json
{
  "learning_rate": 0.01951409473634728,
  "depth": 3,
  "l2_leaf_reg": 7.115991090600124,
  "random_strength": 18.658496689170093,
  "bootstrap_type": "Bernoulli",
  "subsample": 0.6128979677188174,
  "rsm": 0.9808188438425882,
  "border_count": 64
}
```

Iteration limit: 107. Trees in final fit: 107. Inner mean RMSE: 227,146.15.

### catboost — test 2024

Features: `hist_grid250_all_median`, `hist_grid500_all_mean`, `hist_material_all_mean`, `hist_material_surface_all_mean`, `hist_material_surface_all_median`, `hist_material_surface_all_std`, `hist_radius250_tail_rate`, `hist_radius500_median`, `hist_surface_all_median`, `hist_surface_all_n`, `hist_surface_all_std`, `hist_surface_all_tail_rate`, `hist_surface_last2_mean`, `surface_road`, `surface_structure`.

Parameters:
```json
{
  "learning_rate": 0.1086561515060856,
  "depth": 3,
  "l2_leaf_reg": 0.8820734944000431,
  "random_strength": 0.2883723562711601,
  "bootstrap_type": "Bernoulli",
  "subsample": 0.9029163001449033,
  "rsm": 0.6340304014592798,
  "border_count": 64,
  "one_hot_max_size": 2
}
```

Iteration limit: 11. Trees in final fit: 11. Inner mean RMSE: 160,252.83.

### catboost — test 2025

Features: `hist_age_band_all_max`, `hist_age_band_all_mean`, `hist_age_band_all_median`, `hist_age_band_all_n`, `hist_age_band_all_std`, `hist_age_band_all_tail_rate`, `hist_age_band_last1_max`, `hist_age_band_last1_mean`, `hist_age_band_last1_median`, `hist_age_band_last1_n`, `hist_age_band_last1_std`, `hist_age_band_last1_tail_rate`, `hist_age_band_last2_max`, `hist_age_band_last2_mean`, `hist_age_band_last2_median`, `hist_age_band_last2_n`, `hist_age_band_last2_std`, `hist_age_band_last2_tail_rate`, `hist_grid1000_all_max`, `hist_grid1000_all_mean`, `hist_grid1000_all_median`, `hist_grid1000_all_n`, `hist_grid1000_all_std`, `hist_grid1000_all_tail_rate`, `hist_grid1000_last1_max`, `hist_grid1000_last1_mean`, `hist_grid1000_last1_median`, `hist_grid1000_last1_n`, `hist_grid1000_last1_std`, `hist_grid1000_last1_tail_rate`, `hist_grid1000_last2_max`, `hist_grid1000_last2_mean`, `hist_grid1000_last2_median`, `hist_grid1000_last2_n`, `hist_grid1000_last2_std`, `hist_grid1000_last2_tail_rate`, `hist_grid250_all_max`, `hist_grid250_all_mean`, `hist_grid250_all_median`, `hist_grid250_all_n`, `hist_grid250_all_std`, `hist_grid250_all_tail_rate`, `hist_grid250_last1_max`, `hist_grid250_last1_mean`, `hist_grid250_last1_median`, `hist_grid250_last1_n`, `hist_grid250_last1_std`, `hist_grid250_last1_tail_rate`, `hist_grid250_last2_max`, `hist_grid250_last2_mean`, `hist_grid250_last2_median`, `hist_grid250_last2_n`, `hist_grid250_last2_std`, `hist_grid250_last2_tail_rate`, `hist_grid500_all_max`, `hist_grid500_all_mean`, `hist_grid500_all_median`, `hist_grid500_all_n`, `hist_grid500_all_std`, `hist_grid500_all_tail_rate`, `hist_grid500_last1_mean`, `hist_grid500_last1_median`, `hist_grid500_last1_n`, `hist_grid500_last1_std`, `hist_grid500_last1_std_log1p`, `hist_grid500_last1_tail_rate`, `hist_grid500_last2_max`, `hist_grid500_last2_mean`, `hist_grid500_last2_median`, `hist_grid500_last2_n`, `hist_grid500_last2_std`, `hist_grid500_last2_tail_rate`, `hist_length_band_all_max`, `hist_length_band_all_mean`, `hist_length_band_all_median`, `hist_length_band_all_n`, `hist_length_band_all_std`, `hist_length_band_all_tail_rate`, `hist_length_band_last1_max`, `hist_length_band_last1_mean`, `hist_length_band_last1_median`, `hist_length_band_last1_n`, `hist_length_band_last1_std`, `hist_length_band_last1_tail_rate`, `hist_length_band_last2_max`, `hist_length_band_last2_mean`, `hist_length_band_last2_median`, `hist_length_band_last2_n`, `hist_length_band_last2_std`, `hist_length_band_last2_tail_rate`, `hist_material_all_max`, `hist_material_all_mean`, `hist_material_all_median`, `hist_material_all_n`, `hist_material_all_std`, `hist_material_all_tail_rate`, `hist_material_last1_max`, `hist_material_last1_mean`, `hist_material_last1_median`, `hist_material_last1_n`, `hist_material_last1_std`, `hist_material_last1_tail_rate`, `hist_material_last2_max`, `hist_material_last2_mean`, `hist_material_last2_median`, `hist_material_last2_n`, `hist_material_last2_std`, `hist_material_last2_tail_rate`, `hist_material_surface_all_max`, `hist_material_surface_all_mean`, `hist_material_surface_all_median`, `hist_material_surface_all_n`, `hist_material_surface_all_std`, `hist_material_surface_all_tail_rate`, `hist_material_surface_last1_max`, `hist_material_surface_last1_mean`, `hist_material_surface_last1_median`, `hist_material_surface_last1_n`, `hist_material_surface_last1_std`, `hist_material_surface_last1_tail_rate`, `hist_material_surface_last2_max`, `hist_material_surface_last2_mean`, `hist_material_surface_last2_median`, `hist_material_surface_last2_n`, `hist_material_surface_last2_std`, `hist_material_surface_last2_tail_rate`, `hist_nearest10_max`, `hist_nearest10_mean`, `hist_nearest10_median`, `hist_nearest25_max`, `hist_nearest25_mean`, `hist_nearest25_median`, `hist_nearest5_max`, `hist_nearest5_mean`, `hist_nearest5_median`, `hist_radius100_max`, `hist_radius100_mean`, `hist_radius100_median`, `hist_radius100_n`, `hist_radius100_tail_rate`, `hist_radius250_max`, `hist_radius250_mean`, `hist_radius250_median`, `hist_radius250_n`, `hist_radius250_tail_rate`, `hist_radius500_max`, `hist_radius500_mean`, `hist_radius500_median`, `hist_radius500_n`, `hist_radius500_tail_rate`, `hist_radius50_max`, `hist_radius50_mean`, `hist_radius50_median`, `hist_radius50_n`, `hist_radius50_tail_rate`, `hist_surface_all_max`, `hist_surface_all_max_log1p`, `hist_surface_all_mean`, `hist_surface_all_median`, `hist_surface_all_n`, `hist_surface_all_std`, `hist_surface_all_tail_rate`, `hist_surface_last1_max`, `hist_surface_last1_mean`, `hist_surface_last1_median`, `hist_surface_last1_n`, `hist_surface_last1_std`, `hist_surface_last1_tail_rate`, `hist_surface_last2_mean`, `hist_surface_last2_median`, `hist_surface_last2_n`, `hist_surface_last2_std`, `hist_surface_last2_tail_rate`, `log1p_pipe_length`, `log1p_years_used`, `log_length`, `material`, `material_brass`, `material_cast_iron`, `material_code`, `material_copper`, `material_gray_iron`, `material_surface`, `material_wrought_iron`, `midpoint_x`, `midpoint_y`, `orientation_cos2`, `orientation_sin2`, `pipe_length`, `span_x`, `span_y`, `surface`, `surface_code`, `surface_farmland`, `surface_grassland`, `surface_road`, `surface_structure`, `surface_swamp`, `surface_water`, `weekday_cos`, `x1`, `x2`, `y1`, `y2`, `years_used_at_leak`.

Parameters:
```json
{
  "learning_rate": 0.03036174903365222,
  "depth": 3,
  "l2_leaf_reg": 0.6201847397621251,
  "random_strength": 0.0036169292499532543,
  "bootstrap_type": "Bernoulli",
  "subsample": 0.7277701133394161,
  "rsm": 0.914138704034685,
  "border_count": 128,
  "one_hot_max_size": 2
}
```

Iteration limit: 105. Trees in final fit: 105. Inner mean RMSE: 123,346.64.

### catboost — test 2026

Features: `event_hour`, `event_month`, `event_year`, `hist_grid1000_all_mean`, `hist_grid1000_all_n`, `hist_grid250_all_median`, `hist_grid250_all_tail_rate`, `hist_grid500_all_n`, `hist_grid500_all_std`, `hist_length_band_all_median`, `hist_length_band_all_tail_rate`, `hist_material_surface_all_median`, `hist_material_surface_last1_median`, `hist_radius500_median`, `hist_surface_all_max`, `hist_surface_all_mean`, `hist_surface_all_tail_rate`, `hist_surface_last1_std`, `hour_sin`, `inventory_10m_length_sum`, `inventory_50m_surface_diversity`, `midpoint_x`, `midpoint_y`, `orientation_cos2`, `orientation_sin2`, `season_cos`, `season_sin`, `surface`, `weekday_cos`, `weekday_sin`, `y2`.

Parameters:
```json
{
  "learning_rate": 0.07749586710478815,
  "depth": 6,
  "l2_leaf_reg": 5.692617395759746,
  "random_strength": 0.0010867950457761608,
  "bootstrap_type": "Bernoulli",
  "subsample": 0.8296272982086644,
  "rsm": 0.7847747510664507,
  "border_count": 254,
  "one_hot_max_size": 32
}
```

Iteration limit: 43. Trees in final fit: 43. Inner mean RMSE: 102,950.88.

### lightgbm — Test 2023

Features: `event_month`, `event_weekday`, `hist_grid250_all_max`, `hist_grid250_all_median`, `hist_grid250_last1_mean`, `hist_grid250_last1_median`, `hist_grid500_all_mean`, `hist_grid500_all_median`, `hist_grid500_last1_median`, `hist_material_all_max`, `hist_material_surface_all_mean`, `hist_material_surface_last1_median`, `hist_nearest25_max`, `hist_nearest5_mean`, `hist_radius100_mean`, `hist_radius500_tail_rate`, `hist_radius50_median`, `hour_sin`, `inventory_250m_count`, `inventory_distance_to_road`, `log1p_years_used`, `material_code`, `month_sin`, `orientation_cos2`, `surface_code`, `surface_road`, `surface_structure`, `weekday_cos`, `weekday_sin`, `x1`.

Parameters:
```json
{
  "learning_rate": 0.14776118540829655,
  "num_leaves": 61,
  "max_depth": 3,
  "min_child_samples": 43,
  "subsample": 0.683537514633538,
  "subsample_freq": 1,
  "colsample_bytree": 0.8297113874949713,
  "reg_lambda": 0.0029761217317507476,
  "reg_alpha": 1.3126489179268885,
  "max_bin": 127,
  "min_split_gain": 19700778.906826887
}
```

Iteration limit: 5. Trees in final fit: 5. Inner mean RMSE: 226,593.03.

### lightgbm — Test 2024

Features: `event_month`, `hist_age_band_all_max`, `hist_age_band_all_std`, `hist_grid1000_all_max`, `hist_grid1000_all_n`, `hist_grid1000_all_tail_rate`, `hist_grid250_all_max`, `hist_grid250_all_median`, `hist_grid500_all_max`, `hist_grid500_all_mean`, `hist_grid500_all_median`, `hist_length_band_all_max`, `hist_material_all_n`, `hist_material_surface_all_n`, `hist_material_surface_all_tail_rate`, `hist_material_surface_last1_median`, `hist_material_surface_last2_mean`, `hist_nearest25_median`, `hist_radius250_tail_rate`, `hist_surface_last1_std`, `hist_surface_last2_mean`, `hour_cos`, `lay_month`, `log1p_years_used`, `log_age`, `material_copper`, `midpoint_y`, `orientation_cos2`, `road_x_structure_exposure`, `season_cos`, `season_sin`, `surface_road`.

Parameters:
```json
{
  "learning_rate": 0.16801299589049618,
  "num_leaves": 10,
  "max_depth": 7,
  "min_child_samples": 63,
  "subsample": 0.7216937914576833,
  "subsample_freq": 1,
  "colsample_bytree": 0.5939078561191307,
  "reg_lambda": 2.50738968174609,
  "reg_alpha": 0.03439365605378452,
  "max_bin": 127,
  "min_split_gain": 64327.857575275346
}
```

Iteration limit: 6. Trees in final fit: 6. Inner mean RMSE: 162,772.31.

### lightgbm — Test 2025

Features: `hist_age_band_all_mean`, `hist_age_band_all_std`, `hist_grid1000_all_max`, `hist_grid1000_all_mean`, `hist_grid1000_all_median`, `hist_grid1000_all_n`, `hist_grid1000_all_std`, `hist_grid250_all_max`, `hist_grid250_all_mean`, `hist_grid250_all_median`, `hist_grid250_all_std`, `hist_grid250_all_tail_rate`, `hist_grid500_all_max`, `hist_grid500_all_mean`, `hist_grid500_all_median`, `hist_grid500_all_std`, `hist_length_band_all_std`, `hist_length_band_last2_std`, `hist_material_surface_all_median`, `hist_material_surface_all_tail_rate`, `hist_surface_all_max`, `hist_surface_all_mean`, `hist_surface_all_median`, `hist_surface_all_tail_rate`, `inventory_100m_parallel_count`.

Parameters:
```json
{
  "learning_rate": 0.0998750061997041,
  "num_leaves": 7,
  "max_depth": 6,
  "min_child_samples": 33,
  "subsample": 0.9003466355212323,
  "subsample_freq": 1,
  "colsample_bytree": 0.8847699781203096,
  "reg_lambda": 0.0036068778622544108,
  "reg_alpha": 2.2717342059203127,
  "max_bin": 127,
  "min_split_gain": 1929.5705562742053
}
```

Iteration limit: 55. Trees in final fit: 55. Inner mean RMSE: 124,011.21.

### lightgbm — test 2026

Features: `hist_age_band_all_max`, `hist_age_band_all_mean`, `hist_age_band_all_median`, `hist_age_band_all_n`, `hist_age_band_all_std`, `hist_age_band_all_tail_rate`, `hist_grid1000_all_max`, `hist_grid1000_all_mean`, `hist_grid1000_all_median`, `hist_grid1000_all_std`, `hist_grid1000_all_tail_rate`, `hist_grid1000_last2_mean`, `hist_grid250_all_max`, `hist_grid250_all_mean`, `hist_grid250_all_n`, `hist_grid250_all_std`, `hist_grid250_all_tail_rate`, `hist_grid500_all_max`, `hist_grid500_all_mean`, `hist_grid500_all_median`, `hist_grid500_all_n`, `hist_grid500_all_std`, `hist_grid500_all_tail_rate`, `hist_length_band_all_max`, `hist_length_band_all_mean`, `hist_length_band_all_median`, `hist_length_band_all_n`, `hist_length_band_all_std`, `hist_length_band_all_tail_rate`, `hist_material_all_max`, `hist_material_all_mean`, `hist_material_all_median`, `hist_material_all_n`, `hist_material_all_std`, `hist_material_all_tail_rate`, `hist_material_surface_all_max`, `hist_material_surface_all_mean`, `hist_material_surface_all_median_log1p`, `hist_material_surface_all_n`, `hist_material_surface_all_tail_rate`, `hist_material_surface_last2_std`, `hist_nearest10_max`, `hist_nearest10_mean`, `hist_nearest10_median`, `hist_nearest25_max`, `hist_nearest25_mean`, `hist_nearest25_median`, `hist_nearest5_max`, `hist_nearest5_mean`, `hist_nearest5_median`, `hist_radius100_mean`, `hist_radius100_median`, `hist_radius100_tail_rate`, `hist_radius250_max`, `hist_radius250_mean`, `hist_radius250_median`, `hist_radius250_n`, `hist_radius250_tail_rate`, `hist_radius500_max`, `hist_radius500_mean`, `hist_radius500_median`, `hist_radius500_n`, `hist_radius500_tail_rate`, `hist_radius50_max`, `hist_radius50_mean`, `hist_radius50_median`, `hist_radius50_n`, `hist_radius50_tail_rate`, `hist_surface_all_max`, `hist_surface_all_mean`, `hist_surface_all_median`, `hist_surface_all_n`, `hist_surface_all_std`, `hist_surface_all_tail_rate`, `inventory_100m_prior_repairs`, `inventory_10m_road_count`, `log1p_pipe_length`, `log1p_years_used`, `log_length`, `material`, `material_brass`, `material_cast_iron`, `material_code`, `material_copper`, `material_gray_iron`, `material_surface`, `material_wrought_iron`, `midpoint_x`, `midpoint_y`, `orientation_cos2`, `orientation_sin2`, `pipe_length`, `span_x`, `span_y`, `surface`, `surface_code`, `surface_farmland`, `surface_grassland`, `surface_road`, `surface_structure`, `surface_swamp`, `surface_water`, `x1`, `x2`, `y1`, `y2`, `years_used_at_leak`.

Parameters:
```json
{
  "learning_rate": 0.12907214194382882,
  "num_leaves": 12,
  "max_depth": 7,
  "min_child_samples": 16,
  "subsample": 0.7830482459013572,
  "subsample_freq": 1,
  "colsample_bytree": 0.9439828601929375,
  "reg_lambda": 47.79663467074333,
  "reg_alpha": 9.167377750356485,
  "max_bin": 255,
  "min_split_gain": 1261.5920384304368
}
```

Iteration limit: 28. Trees in final fit: 28. Inner mean RMSE: 101,491.09.

## Method and verification

For each fold, use its two latest training years as temporal validation and minimize their equal-weight mean RMSE. After early-stopping exploration, rerank up to five promising configurations using the same tree count in both years. CatBoost is refitted from scratch for each candidate tree count. All 12 configurations were fixed before outer testing. Historical cost features use only costs through the preceding year, assuming those costs are available at the next year-start.

No cost capping, outlier removal, logarithmic target, or model ensemble was used. Negative predictions were clipped to zero.

The original CSV SHA-256, actual costs, and target IDs were checked; historical statistics were independently checked on 42 records. MAE/RMSE for 12 folds and four-fold means were independently recomputed from event-level predictions. The history audit was a sample check, not an independent recomputation of every row.

For all four folds, multiply costs from the test year onward by 37 and add 1,234,567, then rerun cost-dependent preprocessing; features through the test year remained unchanged. There were 470 candidate columns. Cost-independent inventory features were checked structurally and through independent calculations on 24 records across six radii. Training MAE/RMSE were also independently recomputed from saved event-level training predictions.

The expanded search adds neighborhood inventory features and candidates from earlier experiment code. For each model/fold, compare individual additions, removal of selected features, substitutions with absolute training Spearman correlation at least 0.98, equivalent categorical/numeric encodings, and grouped additions/removals. After each improvement, update the baseline and repeat all comparisons. Retune parameters and a shared iteration count for 60 trials each, then repeat feature comparisons to convergence. Verify agreement between the feature set used during parameter search and the rechecked final set. High correlation alone does not exclude a feature; validation RMSE decides. Nearby-segment historical costs were also tested, without claiming actual repair locations or physical connections. Adoption paths and comparisons are saved in expanded_adoption_paths.csv and expanded_candidate_comparisons.csv; fold correlations are in expanded_correlations.csv. Earlier test outputs were archived and their errors were not used in the added search.

The supplied files include data through end-2026; this does not assert that all outcomes were known on the execution date. Earlier work already inspected 2026. Test costs were excluded from this search, but 2026 is not an untouched project-wide final holdout.

Neighborhood features exclude pipes installed after the event date and pipes with unknown lay dates. Inventory attributes are assumed valid at forecast time; removal and material/surface change histories are unavailable. Crossings and shared endpoints do not establish verified physical connections. Straight endpoint distance is not actual curved or excavated length.
