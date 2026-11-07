# XGBoost Leak Prediction Model

## Final Model and Probability Calibration

This document summarizes the finalized XGBoost leak-prediction workflow up to probability calibration. The purpose of this stage is to prepare a calibrated leak-risk model that can later be applied to the 2027 first-leak risk set.

The 2027 leak probabilities are **not generated at this stage**. The team should first confirm the final 2027 prediction population and risk-set construction.

---

## 1. Modeling Objective

The leak model predicts the probability that a pipe experiences its **first recorded leak** during a given year.

One observation represents one pipe-year while the pipe remains at risk of its first leak. After a pipe experiences its first leak, it is removed from later risk-set observations.

The final output required from this model is a probability:

\[
P(\text{leak during year})
\]

rather than only a binary leak / no-leak classification.

---

## 2. Final Model Selection

After model development and final comparison, **XGBoost was selected as the final leak-prediction model**.

The final model uses four predictors:

- `material`
- `surface`
- `pipe_length`
- `pipe_age`

`pipe_id` is not used as a predictor because it is an identifier. `year` is used for temporal splitting rather than as a baseline model feature.

Categorical variables (`material` and `surface`) are encoded using one-hot encoding with:

```python
OneHotEncoder(handle_unknown="ignore")
```

The preprocessing step is fit only on the model-training period so that later-year information does not influence training.

---

## 3. Selected XGBoost Configuration

The selected XGBoost configuration is:

```python
XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    scale_pos_weight=10,
    max_depth=4,
    learning_rate=0.10,
    n_estimators=100,
    random_state=440
)
```

### Role of `scale_pos_weight`

The leak outcome is imbalanced, so `scale_pos_weight=10` gives greater importance to the positive leak class during model fitting.

This parameter is a **training hyperparameter**, not a probability-calibration coefficient.

Because class weighting can affect the numerical interpretation of the raw XGBoost probabilities, probability calibration is performed separately after fitting the model.

---

## 4. Calibration Method Selection

Before final deployment, sigmoid probability calibration was evaluated using temporal validation.

The earlier rolling temporal calibration analysis showed that sigmoid calibration improved probability reliability. Across the held-out temporal predictions, the Brier score improved from approximately:

- Raw XGBoost: **0.0584**
- Calibrated XGBoost: **0.0508**

Based on this evaluation, **sigmoid calibration** was retained for the final model.

Calibration is performed using:

```python
CalibratedClassifierCV(
    FrozenEstimator(model),
    method="sigmoid"
)
```

`FrozenEstimator` keeps the already-fitted XGBoost model fixed while the calibrator learns the mapping from raw XGBoost scores to calibrated probabilities.

---

## 5. Final Temporal Deployment Structure

The final deployment model uses the following temporal structure:

| Stage            | Years     | Purpose                                                                     |
| ---------------- | --------- | --------------------------------------------------------------------------- |
| XGBoost training | 2019–2025 | Fit preprocessing and final XGBoost model                                   |
| Calibration      | 2026      | Fit sigmoid probability calibrator                                          |
| Prediction       | 2027      | Generate final leak-risk probabilities after the 2027 risk set is confirmed |

This preserves chronological order:

```text
2019 ---------------- 2025 | 2026 | 2027
        TRAIN                CAL     PREDICT
```

The 2027 observations are not used for either XGBoost fitting or calibration.

---

## 6. Final Training and Calibration Data

The final temporal split produced:

### XGBoost training set: 2019–2025

- Observations: **273,444**
- Leaks: **11,069**
- Leak rate: **0.040480** (~4.05%)

### Calibration set: 2026

- Observations: **31,947**
- Leaks: **3,038**
- Leak rate: **0.095095** (~9.51%)

After preprocessing, the four original predictors produced **14 transformed features**.

The preprocessing model and XGBoost classifier are fit using only the 2019–2025 observations. The 2026 observations are transformed using the already-fitted preprocessor and are reserved for sigmoid calibration.

---

## 7. Final 2026 Calibration Results

The final XGBoost model produced the following probability diagnostics on the 2026 calibration data:

| Metric                     | Raw XGBoost | Sigmoid Calibrated |
| -------------------------- | ----------: | -----------------: |
| Mean predicted probability |    0.144066 |       **0.095090** |
| Brier score                |    0.088302 |       **0.078056** |
| Log loss                   |    0.305532 |       **0.282353** |
| Minimum probability        |    0.000389 |           0.051632 |
| Maximum probability        |    0.926564 |           0.539670 |

The actual 2026 leak rate was:

\[
0.095095
\]

The raw XGBoost model assigned an average leak probability of approximately **14.41%**, substantially above the observed 2026 leak rate of approximately**9.51%**.

After sigmoid calibration, the average predicted probability became approximately **9.51%**.

Both probability-quality metrics also decreased:

\[
\text{Brier: } 0.088302 \rightarrow 0.078056
\]

\[
\text{Log Loss: } 0.305532 \rightarrow 0.282353
\]

Lower values are better for both metrics.

The calibrated probabilities were also less extreme than the raw XGBoost probabilities, with the probability range changing from approximately:

```text
Raw:        0.0004 – 0.9266
Calibrated: 0.0516 – 0.5397
```

This is consistent with the calibration step correcting the overly extreme raw probabilities produced by the weighted classifier.

### Important interpretation note

The 2026 observations are used to **fit the final calibrator itself**. Therefore, the 2026 calibration metrics should not be interpreted as an independent test of model generalization.

The justification for using sigmoid calibration comes from the earlier rolling temporal calibration analysis, where calibration was evaluated on future held-out years.

The 2026 analysis here is the final **deployment calibration** used to prepare the model for 2027 prediction.

---

## 8. Current Final Pipeline

The finalized leak-model pipeline is:

```text
Pipe-year features
        |
        v
One-hot encoding / preprocessing
        |
        v
Final XGBoost
scale_pos_weight = 10
max_depth = 4
learning_rate = 0.10
n_estimators = 100
        |
        v
Raw XGBoost probability
        |
        v
Sigmoid calibration
        |
        v
Calibrated P(leak)
```

No classification threshold is required for the final optimization input because the downstream task needs the **probability itself**, not a 0/1 classification.

---

## 9. Current Status

Completed:

- First-leak risk-set modeling definition
- Feature selection
- Categorical preprocessing
- XGBoost development and tuning
- Class-imbalance weighting
- Temporal model evaluation
- Final model comparison
- XGBoost selection
- Temporal calibration evaluation
- Final XGBoost training on 2019–2025
- Final sigmoid calibration using 2026
- Calibration diagnostics
- Reproducible `.py` implementation

The final model is therefore ready for 2027 prediction.

---

## 10. Next Step

The next step is intentionally left outside the current final-model script.

Before generating probabilities, the team should confirm the **2027 first-leak risk set**. In particular, pipes that have already experienced their first leak should not incorrectly remain in the prediction population.

After the 2027 risk set is confirmed:

```text
2027 eligible pipe features
        |
        v
fitted preprocessor
        |
        v
fitted XGBoost
        |
        v
fitted sigmoid calibrator
        |
        v
2027 calibrated leak probabilities
```

The expected final leak-team output will contain a pipe identifier and its calibrated leak probability, for example:

```text
pipe_id,leak_probability
...
```

These probabilities can then be combined with the cost model outputs for the replacement optimization stage.
