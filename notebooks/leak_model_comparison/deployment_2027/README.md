# 2027 ensemble leak probabilities

Predictions generated for **28,909** pipes from**43,039** inventory pipes.
Training uses **305,391** pipe-year observations from 2019–2026.

Ensemble expected first leaks in 2027: **3,113.3**, before planned replacements.

Each pipe probability is the equal-weight mean of raw XGBoost, CatBoost, and unweighted baseline LightGBM. Configurations are frozen; no calibration or tuning is added.

## Scope and validation

Historical leaks imply replacement and exclusion from this first-leak model. Missing required features also cause exclusion. See inventory_scope_audit.csv for every inventory ID and reason. Excluded pipes have unknown/out-of-scope probabilities, not zero risk.
28,909 eligible feature records were checked against the 2026 master: material, surface, length, and age advanced by 365/365.25 years.
IDs, probability bounds, ensemble arithmetic, and CSV round-trip contents were validated.

## Files

- ensemble_2027_probabilities.csv : three component probabilities and final leak_probability.
- ensemble_2027_for_cost_join.csv : pipe_id, year, leak_probability.
- prediction_features_2027.csv : inputs for eligible pipes.
- inventory_scope_audit.csv : full inventory eligibility and exclusion reasons.
- ensemble_models.joblib : fitted models, encoding columns, and weights; load only trusted model files.
- manifest.json : training settings, versions, input hashes, scope, and expected counts.

## Interpretation

Component expected leak counts: XGBoost 6,209.3; CatBoost 1,625.8; LightGBM 1,504.8. Substantial disagreement is an uncertainty signal. The agreed weights were not changed.
These are forecasts with no known 2027 labels, not verified future accuracy. Different package versions may affect results. The prior ensemble underestimated 2026 leak counts by 19.12%; this forecast has not been mechanically adjusted to match 2026.
For repair-cost integration join pipe_id to the cost model ID and check year, population overlap, and conditional-cost meaning. Probability times conditional repair cost is an expected-loss estimate, not scheduled construction cost.
Previously leaked polyurethane pipes and inventory with missing attributes still need separate handling in full-network planning. Probabilities for original polyurethane pipes with no historical leak remain in this first-recorded-leak population.
Long-horizon 2027–2051 predictions and replacement scheduling are not included. Planned replacements alter the risk set; do not apply this pre-work forecast unchanged afterward.

## Pipe-count discrepancy with the repair-cost team

The repair-cost team exported predictions for 28,926 inventory pipes without recorded historical leaks.
This leakage model exported probabilities for 28,909 pipes.
There is a **difference of 17 pipes** with missing required inputs.

| Missing input                                | Count | Pipe IDs                      |
| -------------------------------------------- | ----: | ----------------------------- |
| Installation date (age cannot be calculated) |     9 | P10869, P12275–P12282         |
| Material                                     |     8 | P09986, P09987, P42036–P42041 |

The nine pipes missing installation dates are wrought iron. None of the 17 appears in the historical leak records, so this exclusion is not evidence of leak-related replacement. **Their leak probabilities are unknown, not zero**.**NOTE**

- All 28,909 predicted leakage IDs match the repair-cost prediction population. Joining from the cost table should preserve all 28,926 IDs and flag the 17 missing probabilities. An inner join would silently drop them. Do not fill their probabilities or expected losses with zero.

- These pipes need an explicit missing-data policy before full-network loss estimation and replacement planning; known wrought-iron pipes remain replacement targets. Material-unknown pipes require separate review.

- See missing_input_17_pipes.csv for the reviewed ID list and inventory_scope_audit.csv for the complete eligibility audit.
