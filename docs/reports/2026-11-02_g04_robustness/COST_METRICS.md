# Check the RMSE and MAE of the repair amount and the cover circle at the end

Historical comparison, dated 2026-11-02. The current final selection is [G17](../2026-11-02_regional_optimization/G17/README.md).


[Text](README.md) / [Editable Word](G04_comparison_detailed.docx)

## Target of RMSE and MAE

Both measure prediction error in dollar repair costs conditional on a leak.
These are not RMSE/MAE values for construction costs, public scores, leak timing, circle locations, or work order.
Report each model's errors directly, without subtracting a comparator's errors.

```text
RMSE = sqrt(mean((predicted repair cost - actual repair cost)^2))
MAE = mean(abs(estimated repair cost - actual repair cost))
```

Using the same 6,766 repairs from 2024 to 2026 (1,955 in 2024, 1,773 in 2025, and 3,038 in 2026).
All models were matched on the same event IDs and actual costs.
Metrics pool residuals from all 6,766 events rather than averaging annual RMSE/MAE values.
Differences from earlier annual-mean RMSE values arise from this different aggregation method.

|Plan author|Repair-cost predictor|RMSE ($)|MAE ($)|
|---|---|---:|---:|
|Shana|Existing stable ensemble|116,861.56|22,947.17|
|Ryota|Historical material/surface mean|117,750.96|25,341.67|
|Amy|Historical material/surface mean|117,750.96|25,341.67|
|Takito|CMS001 Conditional cost stack|115,810.35|23,579.27|

RMSE strongly reflects large errors. MAE is the average absolute error per case.
Lower is better for both metrics, but the same model need not be best on both.
Since Amy and Ryota use the same amount prediction method, their prediction errors will be the same.
Their public-score difference cannot be attributed to these identical RMSE/MAE values.

## Three metrics added

|Metric|Calculation and meaning|Interpretation|
|---|---|---|
|Worst-year RMSE|Maximum annual RMSE across 2024/2025/2026; 2026 for every model here|Lower indicates smaller large errors in that validation year, although the year's actual-cost difficulty also matters.|
|Total prediction bias|100 × (total predicted cost − total actual cost) / total actual cost|Closer to zero is better; positive means overprediction and negative means underprediction.|
|Top-10% cost capture|Actual costs of the top 677 predicted-cost events / actual costs of all 6,766 events × 100|Higher means better identification of events contributing most actual repair costs.|

Round the top 10% upward to 677 events; break predicted-cost ties by ascending event ID.
The metrics assess multi-year conditional-cost error, calibration, and high-cost capture;
These metrics alone do not determine whether circle placement overfits.

|Author|Worst-year RMSE ($)|Total bias (%)|Cost capture (%)|
|---|---:|---:|---:|
|Shana|128,632.64|+1.58|73.22|
|Ryota|129,206.19|+19.51|71.43|
|Amy|129,206.19|+19.51|71.43|
|Takito|126,966.13|+10.78|75.51|

See [absolute_metrics_summary.csv](evidence/absolute_metrics_summary.csv) for all metrics.
See [G04 formulas and settings](ALGORITHM_DETAILS.md) for implementation and the [main report](README.md) for an accessible explanation.

## Handling validation predictions

- Shana: Saved historical OOF predictions corresponding to `ensemble_stable` used by 20a.
  [I confirmed the amount prediction input using the 20a series input code](https://github.com/reinesana/STAT440-star-kingdom-project/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/src/build_candidate_16.py).
- Amy Ryota: Using only repair records up to the previous year of each evaluation year, from existing `risk_model(pr, cutoff=year-1)`
  Recalculate historical mean repair costs by material/surface, falling back to surface means and then the global mean for unsupported groups.
- Takito: Saved validation forecasts created only in the past for each year of CMS001.
  The final weights learned from all periods for 2027 are not used retrospectively for 2024-2026.
  Recompute annual metrics from raw residuals and
  [Verified with published annual records](https://github.com/reinesana/STAT440-star-kingdom-project/blob/takito/latest-model-articles-2026-10-28/notebooks/ensemble_for_cost_prediction/latest_conditional_stack/evidence/selected_annual_metrics.csv).

Predictions for each year use earlier training data, but model and recipe selection involved
previously inspected validation years influenced selection. This is not an untouched test, and
These RMSE/MAE values alone cannot prove the absence of overfitting.
Repair-cost prediction errors also cannot establish whether the geometry improvements overfit the plan.

## Public score and final submission

Public is the score of the entire plan that is officially evaluated, and its target is different from the repair cost prediction described above.
Shana's 74.03M is a reference value based on the old evaluation rules, so it is not used for ranking comparison with the current Public.
Ryota's 77.29M is rounded, and the lack of geometric coverage in the original plan should also be noted.

G04 has the best current Public at 78.99096825M, and the predicted amount RMSE is also the lowest in this comparison.
It also meets full iron coverage and budget requirements, supporting its selection as the final submission at that stage.
Shana's model has lower MAE, and RMSE/MAE alone do not determine overall plan superiority.
We do not guarantee that G04 is the best Private.

## The cover circle at the end is not an unrepaired pipe left behind.

I reloaded the G04 CSV and re-inspected the construction part and the end part of the containment pipe.

|Check|Result|
|---|---:|
|Construction circles in prefix|22,154 circles|
|Coverage-only suffix circles|37,314 circles|
|Newly replaced pipes in suffix|0 pipes|
|Suffix construction cost|0 dollars|
|Original iron pipes not geometrically covered by the construction prefix|10,826 pipes|
|Of these, pipes already replaced at project start|10,826 (all)|

Every pipe contained in a suffix circle is either PU at project start or contained in a construction-prefix circle.
After the construction prefix finishes, every suffix circle therefore contains only PU pipes.
Future leaks only add PU pipes, so this containment relationship remains valid.

Merging this suffix cannot save construction costs because its original cost is zero.
Enlarging merged suffix circles to include copper or other pipes not replaced by the prefix can
Additional construction costs can instead arise.
Optimize centers, radii, splitting, and merging of the actual construction circles in the prefix.

See the [containment-set check](evidence/coverage_suffix_check.json).
This does not infer each circle's state from the official annual table;
verified using the submitted CSV, initial pipe states, and containment sets of the construction prefix.

## Recalculate

```powershell
python docs/reports/2026-11-02_g04_robustness/recompute_cost_errors.py
```

Required libraries: numpy and pandas.

- [Common target verification prediction/actual cost](evidence/cost_predictions_common_2024_2026.csv)
- [Aggregation method/input hash](evidence/cost_rmse_mae_protocol.json)
- [RMSE/MAE main table](evidence/cost_rmse_mae_summary.csv)
- [Error by year and all items](evidence/cost_prediction_errors_by_year.csv)
- [Details of sensitivity analysis that changed previous future assumptions](SENSITIVITY.md)

The earlier sensitivity analysis is retained, but its metrics differ from the RMSE/MAE in the current report.
