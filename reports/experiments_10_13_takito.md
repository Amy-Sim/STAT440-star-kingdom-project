# Experiments on October 13 by Takito

10/13 By Takito · 2026

### Purpose and main finding

We compared six ways to order pipe replacement work in the Star Kingdom project. Candidate 06 was best: −$15.61 million, about $9.97 million better than the oldest-first baseline. All candidates retained the same circles; only their order changed.

The project replaces original iron pipes during 2027–2051, with $10 million added to the construction budget each year. Score = $250 million − construction costs − leak repair costs over the project period. Higher scores are better. A negative score means combined costs exceeded the allocation used in the score; it does not alone imply a violation of construction-budget constraints.

Each CSV row gives a circular work area’s center and radius; row order determines construction order. A pipe is replaced only when both endpoints are inside the circle. We kept one circle per original iron pipe, centered at its midpoint with half its endpoint length plus a 0.000001 m radius margin. Coordinates and radii are metres.

## What we compared and the results

01–04 compare four repair-cost forecasts using the same leak probabilities. Expected repair cost means predicted repair cost if a leak occurs multiplied by the probability of a leak in 2027–2028. Circle priorities sum the contributions of fully contained, unreplaced pipes. 05 uses repair cost alone. 06 divides the expected repair cost by each circle’s initial construction cost.

| Candidate | Priority rule | Score M$ | Change vs baseline M$ |
| --- | --- | --- | --- |
| Baseline | Oldest first | -25.58 | — |
| 01 | CatBoost × leak probability | -27.54 | -1.96 |
| 02 | Shrinkage ensemble × leak probability | -25.70 | -0.12 |
| 03 | Equal-weight ensemble × leak probability | -25.58 | +0.00 |
| 04 | RMSE-weighted ensemble × leak probability | -27.16 | -1.58 |
| 05 | CatBoost repair cost only | -35.45 | -9.87 |
| 06 | Shrinkage expected repair cost ÷ construction cost | -15.61 | +9.97 |

M$ means million dollars. Positive changes mean improvement. Scores and differences are approximate because the evaluator displays rounded values. Candidate 03 tied with the baseline at the displayed precision.

## What we learned

01–04 did not beat the baseline; 03 tied at the displayed precision. Cost alone performed worst: 05 scored −$35.45 million. Adding leak probability improved the same CatBoost approach by $7.91 million (01 versus 05).

Including construction cost gave the largest gain: 06 beat 02 by $10.09 million and the baseline by $9.97 million. This supports choosing work by expected benefit per construction dollar. Total scores alone cannot separate construction savings from avoided leak repairs.


## Candidate 06 explained simply

Candidate 06 is a way to decide **which circle to work on first**. It does not learn or optimize circle sizes. The cost ensemble predicts repair costs; a separate model predicts leak probabilities; a final rule turns these predictions into a construction order.

### Step 1 Draw a circle around each original iron pipe

The center is halfway between the pipe’s two endpoints. The radius is half the distance between those endpoints, plus a tiny 0.000001 m margin to prevent rounding from leaving an endpoint outside. For example, endpoints 40 m apart give a radius of approximately 20 m. This is endpoint geometry, not a measured curved pipe length.

We kept all 38,455 baseline circles. Their centers and radii are the same in all six files. A circle can also contain other pipes; any fully contained, currently unreplaced pipe is included in its work cost. **Candidate 06 changes the order, not the size, of the circles.**

### Step 2 Predict repair cost using the 2027 scenario

Yes: **every repair-cost forecast used here assumes the year is 2027**. The model inputs use scenario year 2027, pipe age on 1 January 2027, and observed repair history through the end of 2026. No actual future leak month or day is supplied.

The forecast asks, “If this pipe leaks in the 2027 scenario, how much might the repair cost?” It does not predict the preventive construction bill. Even pipes whose work is delayed until 2028 or later keep their 2027 repair-cost estimate in this experiment; costs are not re-predicted for their eventual work year.

### Step 3 Multiply by the chance of a leak

The separate risk model estimates leak probabilities for 2027 and 2028, updating pipe age for each year. These are combined into a two-year probability. **Repair cost uses 2027; leak probability covers 2027–2028.**

For example, a $100,000 predicted repair cost and a 10% two-year leak probability give $10,000 of expected repair cost. We sum these amounts for all fully contained, unreplaced pipes in each circle.

### Step 4 Put the circles with more expected benefit per construction dollar first

**Priority = expected repair cost inside the circle ÷ initial construction cost of the circle.**

| Illustrative circle | Expected repair cost | Construction cost | Priority |
| --- | --- | --- | --- |
| A | $100,000 | $50,000 | 2 |
| B | $150,000 | $150,000 | 1 |

These are teaching examples, not actual circles from the submissions. Candidate 06 puts A first: although B has a larger expected repair cost, A offers more expected benefit for each construction dollar.

The result is one fixed ordered list. Annual budgets determine when the evaluator can execute each circle. **The plan does not update predictions or reorder circles each year, and it does not optimize the full 25-year schedule.** The initial construction-cost estimate also stays fixed during ranking; actual costs can change when preceding work or leaks replace pipes.


## How Candidate 06 Was Built

Candidate 06 combined three quantities: the cost of a leak, the probability of a leak, and the cost of preventive replacement. The repair-cost estimate came from the team’s optimized ensemble. A separate model supplied leak probabilities. We then used these predictions to order the same construction circles as the baseline.

### 1. Training data and features

We joined train.csv with pipes.csv by Pipe ID and retained all 14,113 repair records from 2019–2026. Records with missing installation dates were retained, and unusually expensive repairs were not removed or capped.

The cost models used information available before the prediction year, including pipe material, surface type, age, endpoint length, location, nearby pipes, endpoint-route features, and historical repair-cost summaries. Different models selected different feature groups. Actual future leak dates, hours, and weekdays were not used.

The target was repair cost conditional on a leak occurring. This is different from preventive construction cost and does not, by itself, predict whether a pipe will leak.

### 2. Component models and model selection

The ensemble contained nine models developed from Takito’s, Anthony’s, and Rion’s work, plus a surface-based reference forecast.

| Component | Main approach | Final weight |
| --- | --- | --- |
| Surface reference | Historical surface-specific mean, smoothed toward the overall mean | 19.61% |
| Anthony linear | Linear regression predicting cost directly | 9.86% |
| Anthony Gamma | Gamma regression for positive costs | 11.08% |
| Anthony Random Forest | Predict log cost, then convert back to cost | 10.39% |
| Takito XGBoost | Boosted trees predicting cost directly | 6.05% |
| Takito CatBoost | Boosted trees predicting cost directly | 9.97% |
| Takito LightGBM | Boosted trees predicting cost directly | 5.00% |
| Rion Gamma | Gamma regression with a different feature specification | 5.32% |
| Rion Random Forest | Predict cost directly | 7.36% |
| Rion LightGBM | Predict log cost, then convert back to cost | 15.35% |

Weights are rounded; the calculation used the saved full-precision values.

Model selection followed time order. For each prediction year, models were trained and tuned using only earlier years. Optuna searched 30 configurations per component and prediction year for 2021–2027, comparing feature groups and model settings. The objective was average annual RMSE on the two most recent available earlier validation years, or one year when only one was available. RMSE measures prediction error and gives larger errors more weight.

The search included regularization for regression and boosting models, and settings such as tree count, depth, leaf size, learning rate, and sampling. For log-cost models, the method used to convert predictions back to expected cost was also selected using past data. For example, the final CatBoost used 49 features, depth 2, and 150 iterations.

Existing Shana prediction files were excluded because evaluation-year outcomes had already influenced their feature or model selection. Models requiring actual future failure times were also excluded. Therefore, the ensemble used the ten eligible components, rather than every existing team prediction file.

### 3. How the shrinkage ensemble was constructed

We compared equal weights, weights optimized for RMSE, shrinkage weights, and a constrained balance ensemble.

Candidate 06 used the shrinkage ensemble. First, we fitted nonnegative weights that summed to one using historical predictions made without training on their target year. These are called out-of-fold, or OOF, predictions. The optimization minimized average annual RMSE and included a penalty discouraging large departures from equal weights.

We then mixed those optimized weights with equal weights:

Final weight = 50% × regularized optimized weight + 50% × 10%.

This gives every component at least a 5% weight. “Shrinkage” here means moving the weights toward equal weighting, reducing dependence on a small number of models.

For each historical evaluation year, weights were learned only from earlier OOF years. The final 2027 weights used 13,035 OOF predictions from 2020–2026. The 2019 records could not have past-only OOF predictions because no earlier training history was available, but they were included in the final component-model training.

We selected the deployment ensemble among diversified candidates whose average annual RMSE was within 1% of the best diversified ensemble. We then preferred smaller worst-year total-cost bias, followed by smaller average absolute bias and lower relative variation in annual RMSE.

The shrinkage ensemble was selected because it offered a useful balance between individual prediction error and total-cost bias:

| Historical metric, evaluated on 2023–2026 repairs | CatBoost alone | Shrinkage ensemble |
| --- | --- | --- |
| Average annual RMSE | 124,569.85 | 125,230.52 |
| Mean absolute annual total-cost bias | 20.50% | 4.61% |
| Worst absolute annual total-cost bias | 34.45% | 10.02% |

Its average annual RMSE was about 0.53% higher than CatBoost’s, but its annual predicted totals were closer to the observed totals. This does not establish better performance in every year. The deployment choice was made after reviewing historical results, so those results are not an untouched final test.

### 4. Full-data refitting and prediction

After selecting the settings, each component was refitted on all 14,113 records through the end of 2026. The saved ensemble weights were then applied to the component predictions.

We generated 2027 cost predictions for 28,926 pipes in pipes.csv that had no recorded historical leak. Historical-leak pipes were treated as already replaced. Of the prediction targets, 27,240 had materials represented in the cost training data; 1,678 polyurethane pipes and eight pipes with missing material required extrapolation.

For construction priorities, polyurethane and historically replaced pipes received zero contribution. Predictions for missing-material pipes remained uncertain. The same full-data ensemble predictions were used by candidates 02 and 06.

### 5. Leak probability and construction priority

Leak probability came from a separate LightGBM classifier, not the repair-cost ensemble. It used material, surface, length, age, and midpoint coordinates. Two configurations were compared using 2025 and 2026 validation log loss, a measure of probability-prediction error. The selected model was refitted on the historical pipe-year observations and used to estimate annual leak probabilities.

The two-year probability was calculated as:

Probability of a leak in 2027–2028 = 1 − (1 − p2027) × (1 − p2028).

We multiplied this probability by the ensemble’s 2027 repair-cost prediction. For each circle, we summed these expected repair costs across all fully contained, unreplaced pipes, including copper and brass.

Candidate 06 then calculated:

Circle priority = summed expected repair cost ÷ initial circle construction cost.

The construction-cost estimate included the fixed work-unit charge, surface excavation cost, and replacement length. Surface types were counted once each, including those associated with already replaced pipes. Only unreplaced pipes contributed replacement length.

We ordered circles from highest to lowest priority. The baseline’s 38,455 circles were retained, with no changes to their centers or radii. Thus, candidate 06 tested a different ordering rule rather than a new circle design.

### 6. Validation and interpretation

The exported CSV was checked for complete iron-pipe coverage and construction-budget feasibility. Under a no-future-leak simulation, candidate 06 finished in 2042 with construction costs of approximately $152.12 million. These are local validation results, not the evaluator’s realized construction costs or completion year.

The submitted score was −$15.61 million, approximately $9.97 million better than the baseline. Compared with candidate 02, which used the same ensemble and leak probabilities without dividing by construction cost, candidate 06 improved by $10.09 million.

This supports the construction-cost denominator in this experiment. However, the priority is a heuristic: it uses a fixed two-year risk window, overlapping circles can share benefits, and the initial construction-cost denominator is not updated for preceding work or future leaks. It does not represent a full optimization of the 25-year project.

### Scope of this experiment

These six files use the separate LightGBM risk model described above. They do not use the newer leak-probability ensemble now present in notebooks/leak_model_comparison. Cost-ensemble selection and leak-risk-model selection are separate processes.

Each candidate has one submitted evaluation, with no uncertainty estimate. All scores remain negative, and candidate 06 is not proven optimal. Its two-year expected repair cost is a ranking proxy rather than a validated estimate of total avoided cost over 25 years.

All six exported CSVs passed full original-iron coverage and no-future-leak budget checks. Their simulated completion year was 2042 and construction costs ranged from $151.39 million to $152.12 million. Validation includes full endpoint containment, surface-type costs, historical replacements, overlaps, zero-cost skips, annual carryover, and stopping at the first unaffordable unit.

Use 06 as the reference for future tests of circle grouping and longer-term replacement scheduling.

## Sources

Submitted scores come from the user-supplied [submission screenshot](assets/experiments_10_13_takito_scores.png). Rows are mapped bottom to top as baseline, then 01–06. The CSV files contain construction circles, not evaluation scores.

The baseline CSV is [2026-10-05_baseline_v1.csv](../submissions/2026-10-05_baseline_v1.csv). The six original submission files are:

- [01_catboost_risk.csv](https://github.com/reinesana/STAT440-star-kingdom-project/blob/e9650d54e2f89c1724442154e6504184f8d62f59/submissions/2026-10-13_cost_candidates/01_catboost_risk.csv)
- [02_stable_risk.csv](https://github.com/reinesana/STAT440-star-kingdom-project/blob/e9650d54e2f89c1724442154e6504184f8d62f59/submissions/2026-10-13_cost_candidates/02_stable_risk.csv)
- [03_equal_risk.csv](https://github.com/reinesana/STAT440-star-kingdom-project/blob/e9650d54e2f89c1724442154e6504184f8d62f59/submissions/2026-10-13_cost_candidates/03_equal_risk.csv)
- [04_rmse_weighted_risk.csv](https://github.com/reinesana/STAT440-star-kingdom-project/blob/e9650d54e2f89c1724442154e6504184f8d62f59/submissions/2026-10-13_cost_candidates/04_rmse_weighted_risk.csv)
- [05_catboost_cost_only.csv](https://github.com/reinesana/STAT440-star-kingdom-project/blob/e9650d54e2f89c1724442154e6504184f8d62f59/submissions/2026-10-13_cost_candidates/05_catboost_cost_only.csv)
- [06_stable_risk_per_work_cost.csv](https://github.com/reinesana/STAT440-star-kingdom-project/blob/e9650d54e2f89c1724442154e6504184f8d62f59/submissions/2026-10-13_cost_candidates/06_stable_risk_per_work_cost.csv)

Model and implementation records: [cost-model report](../notebooks/ensemble_for_cost_prediction/report_en.md), [training contract](../notebooks/ensemble_for_cost_prediction/evidence/training_contract.json), [ensemble weights](../notebooks/ensemble_for_cost_prediction/evidence/ensemble_weights.json), [final model settings](../notebooks/ensemble_for_cost_prediction/evidence/final_model_settings.csv), [submission generator](../src/build_cost_submissions.py), [risk-model training](../src/risk_priority.py), and [local validation and provenance](../submissions/2026-10-13_cost_candidates/README.md).

# Experiment done by Takito on October 13th

October 13, 2026 · Takito
