# Rion Oyama: Week 1 cost prediction results

These are rerun results from Rion's original `Project_codeW1 .Rmd`. The package follows Takito's structure of executable code, prediction CSVs, results, and reproduction instructions. The models remain Rion's original models; this cleanup translates explanatory text.

The shared input is `data/train_predict_cost.csv`. Predictions estimate costs conditional on a leak. Raw data and expensive observations were preserved.

## Results by year

| Model | Target | Year | MAE | RMSE | Total bias (%) |
|---|---|---:|---:|---:|---:|
| Gamma | log link | 2023 | 30,116.21 | 157,549.34 | 10.23 |
| Gamma | log link | 2024 | 16,257.05 | 101,120.15 | -9.25 |
| Gamma | log link | 2025 | 24,111.92 | 114,040.92 | -9.78 |
| Gamma | log link | 2026 | 24,161.66 | 129,651.09 | -16.26 |
| LightGBM | log1p | 2023 | 20,405.70 | 164,614.59 | -67.60 |
| LightGBM | log1p | 2024 | 12,199.15 | 105,398.50 | -67.06 |
| LightGBM | log1p | 2025 | 19,889.19 | 117,606.50 | -58.78 |
| LightGBM | log1p | 2026 | 20,720.89 | 136,023.78 | -64.86 |
| LightGBM | raw | 2023 | 55,108.89 | 218,222.87 | 105.67 |
| LightGBM | raw | 2024 | 36,093.64 | 127,838.62 | 115.23 |
| LightGBM | raw | 2025 | 34,673.26 | 124,907.58 | 41.71 |
| Random Forest | log1p | 2023 | 20,706.18 | 165,696.30 | -66.32 |
| Random Forest | log1p | 2024 | 12,443.76 | 104,102.70 | -61.54 |
| Random Forest | log1p | 2025 | 19,658.27 | 118,042.70 | -60.00 |
| Random Forest | raw | 2023 | 44,530.58 | 170,941.13 | 80.47 |
| Random Forest | raw | 2024 | 37,041.38 | 147,154.02 | 164.85 |
| Random Forest | raw | 2025 | 29,468.14 | 116,908.26 | 32.87 |
| Random Forest | raw | 2026 | 29,209.95 | 135,663.94 | 23.09 |

## Average (reference value)

| Model | Target | Years | Mean MAE | Mean RMSE |
|---|---|---|---:|---:|
| Gamma | log link | 2023,2024,2025,2026 (4 years) | 23,661.71 | 125,590.37 |
| LightGBM | log1p | 2023,2024,2025,2026 (4 years) | 18,303.73 | 130,910.84 |
| Random Forest | log1p | 2023,2024,2025 (3 years) | 17,602.74 | 129,280.57 |
| LightGBM | raw | 2023,2024,2025 (3 years) | 41,958.59 | 156,989.69 |
| Random Forest | raw | 2023,2024,2025,2026 (4 years) | 35,062.51 | 142,666.84 |

These reference means weight the displayed years equally. Do not directly compare three-year and four-year means. Report 2025 validation and 2026 final evaluation separately. Values were recomputed from predictions rather than rounded screenshots.

## Reproduction and confirmation

- Executed 19 chunks of the original R Markdown in order.
- Matched the hash of the input CSV with the same file on GitHub.
- All 18 pairs of MAE and RMSE were recalculated from the saved predicted values.
- `output_randomforest.csv`, `output_gamma.csv`, `output_lightgbm.csv` each have 8,586 rows and columns `pipe_id,predicted_cost`.
- Random Forest log version/LightGBM raw version has not been implemented in 2026. Missing data are not set to 0.
- The RF 2024 forecast CSV that was not saved in the original was added and saved from the calculated vector in the original.
- Since the results of each year have been viewed in the past, 2026 cannot be treated as unused test data for future model adjustments.

The difference of a few cents in the average on GitHub is because it was calculated from the unrounded value. Raw and log data for all years are not swapped and mixed into one forecast file.
