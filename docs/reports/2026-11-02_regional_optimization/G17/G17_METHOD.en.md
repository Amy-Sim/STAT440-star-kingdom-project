# G17: how the $79.17M replacement plan was built

[日本語](G17_METHOD.ja.md) · [Submission CSV](G17_single_merge.csv) · [Official annual results](evidence/official_G17.csv)

This document explains the exact **G17** version, with Public score **$79,168,928.88**. It is the plan referred to as the 79.17M best model at that stage; it does not describe subsequent candidates. Its pipeline is:

**Pipe records → F168 leak timing + CMS001 conditional repair cost → cost-aware work order → circle movement/splitting/merging → fixed submission CSV.**

The two predictors answer different questions. F168 asks “when might this pipe leak?” CMS001 asks “if it leaks, how expensive will the repair be?” The geometry optimizer then asks “which pipes should one work circle replace, and where should that circle be?”

## 1. Prepare the data

1. Join the pipe inventory and historical leak records by pipe ID. The inventory contains 43,039 pipes; the cost deployment training set contains 14,113 recorded leak events from 2019–2026.
2. Calculate straight endpoint-to-endpoint length and spatial features from coordinates in **meters**. A planar crossing alone does not establish physical connectivity.
3. At each forecast origin, construct features using information available before that year. Historical leak/replacement status is reflected in the remaining at-risk inventory. Native polyurethane (PU) and previously replaced pipes do not receive replacement-priority value.
4. Keep leak severity and planned construction cost separate. The observed repair-cost target in `train.csv` is not the formula used to price a scheduled replacement circle.

## 2. Predictor A: CMS001 conditional repair cost

### Step A1 — train three complementary regressors

| Base | Target / purpose |
|---|---|
| CatBoost | Predict repair dollars directly; captures nonlinear and categorical interactions. |
| Random Forest | Predict `log(cost)`, then apply its saved mean-retransformation correction. |
| LightGBM | Predict `log(1 + cost)`, then apply its saved mean-retransformation correction. |

Each retains its own selected features and preprocessing. The underlying features describe pipe characteristics, surface, age/geometry and available historical summaries; the stack itself receives the three dollar predictions plus the material–surface group. Log retransformation needs correction because simply exponentiating an average log prediction does not recover the mean dollar cost.

### Step A2 — obtain predictions on later years

Train bases on earlier years and predict the next evaluation year. These temporal out-of-fold (OOF) predictions let the mixing stage observe errors on events that were not used to fit the corresponding base prediction. For example, the 2025 mixing weights use saved OOF events from 2023–2024, not 2025 outcomes.

### Step A3 — fit global and material–surface weights

Fit nonnegative weights summing to one to minimize squared dollar error on earlier OOF events. First fit a global vector. For each material × surface group with at least 50 earlier events, also fit a local vector, then shrink it toward the global vector:

```text
effective_weights = n/(n + tau) × local_weights
                  + tau/(n + tau) × global_weights
predicted repair cost = sum(effective_weights × base dollar predictions)
```

Sparse/unseen groups use the global vector. Select `tau` from `0, 50, 200, 1000, 1e9` using earlier forward validations; use the predefined fallback when there is insufficient earlier validation.

**Final 2027 deployment:** refit bases on 2019–2026 events; fit weights using 8,592 OOF events from 2023–2026. There are 18 eligible local groups and `tau = 50`. Global weights are **68.6270% CatBoost, 31.3730% corrected log RF, 0% corrected log LightGBM**. Local groups can use LightGBM, so the global percentages do not describe every pipe.

**Illustration:** with 100 earlier events and `tau = 50`, a group's effective vector is two-thirds local and one-third global. This avoids relying entirely on a small group's fitted weights. These are illustrative group counts, not a particular recorded pipe.

## 3. Predictor B: F168 leak timing

### Step B1 — model time to first leak

Build yearly risk sets: a pipe remains at risk until its first leak or the observation cutoff. A pipe that has not leaked by the cutoff is censored, rather than labeled as permanently safe. Fit the following ten bases:

| Base family | What it contributes |
|---|---|
| Elastic-net Cox | Regularized proportional-hazards model |
| Weibull AFT; lognormal AFT | Two parametric lifetime distributions |
| Spline survival | Flexible age/time effects |
| Random survival forest | Tree-based survival relationships |
| XGBoost AFT | Boosted lifetime model |
| CatBoost hazard | Boosted annual leak hazard |
| MTLR; DeepHit | Neural discrete-time survival alternatives |
| Hierarchical hazard | Shared and cohort-level hazard effects |

Selected feature sets differ by base. They include material, surface, length, age, installation year/decade, material–installation cohort, spatial/neighborhood composition, and **past-only** local/cohort leak history. Neighborhood summaries use 50 m, 100 m and 250 m radii where selected. Not every model receives every feature.

### Step B2 — learn the combination from historical forward predictions

F168 uses the `optuna_base` recipes and **StandardScaler → Ridge**, rather than equal weighting. For 2027, the meta-training observations are base next-year predictions and realized leak indicators from 2020–2026. Tune the Ridge penalty by training on earlier meta-years and validating on the latest available meta-year; refit on all available meta-years afterward. The final penalty is **alpha = 7308.877234445037**.

Ridge coefficients are not constrained to be positive or sum to one. This is different from CMS001's convex weights. F168 does not apply the old manual installation-year probability overrides.

### Step B3 — create a 25-year curve

Convert each base survival curve to annual conditional hazards. Apply the same learned Ridge mapping to the ten hazards at each forecast horizon, clip the resulting hazard to `[0, 1]`, then reconstruct survival:

```text
h(t) = predicted chance of a leak in year t, conditional on survival until t
S(t) = product over years 1…t of (1 − h(year))
F(t) = 1 − S(t)
```

Beyond a base's empirical time support, its final supported hazard is held constant, capped at 0.95. This is an extrapolation assumption. For illustration, hazards of 0.10 and 0.20 give two-year survival `0.9 × 0.8 = 0.72` and two-year leak probability `0.28`.

## 4. Mix the two predictions into a work order

The starting order is the saved **CMS001 + F168 / 02_OVERLAP_CREDIT** order. It is not simply descending leak probability or descending repair cost.

### Step C1 — assign a replacement value to each live pipe

For length `L`, CMS001 repair forecast `C_raw`, and F168 cumulative probabilities:

```text
F2  = 1 − S(2)
F25 = 1 − S(25)
R   = (1 − 0.3227327995) × F2 + 0.3227327995 × F25
C   = C_raw / (max(L, 0.1) / median_live_length)^0.0030795309
V   = R^0.8300158668 × max(C − 0.9780439932 × 200 × L, 0)^0.8780168139
```

This balances near-term and longer-term risk, repair severity, and replacement length cost. `V` is a heuristic priority value, **not expected dollars**. The constants are saved planning parameters, separate from the learned prediction-model weights. PU/already replaced pipes get zero value.

For intuition, a high-risk pipe with a very costly potential repair tends to move earlier, while a long pipe with little avoided repair cost can move later. Although `leak probability × conditional repair cost` explains the basic expected-loss idea, the actual saved order uses the formula above.

### Step C2 — extract what each candidate circle newly replaces

For every candidate, find all pipes whose **both endpoints** lie inside it. Subtract native/historically replaced PU and pipes already replaced by earlier selected works. The remaining set is this work's new replacement target. For example, if a circle contains A, B and C, but A is already PU and B was replaced earlier, this work contributes only C's value and unreplaced length.

### Step C3 — select and update circles

```text
priority = (sum of V for new targets + 0.01 × overlap credit)
           / current construction cost^0.8490093179
```

The overlap credit is the fixed charge saved when doing this work makes another remaining circle PU-only. Select a high-priority circle, mark its targets replaced, and update overlapping circles and their neighboring dependency scores. The saved recipe also applies local and block order moves. Its final overlap-credit stage processes earlier planned-year groups first and compares priorities within each group.

### Step C4 — replay the annual budget

Add $10M per year plus unused carryover. If the next circle cannot be afforded, it waits at the front for the next year. The forecast-based order is built offline; the submitted CSV is fixed and does not run a new online model after each realized leak. Geometry changes can change costs and therefore budget-year boundaries, so replay the whole plan after modifications.

## 5. Choose circle centers and radii

G17 does **not** predict one radius per pipe with a radius regression model. It searches feasible circle geometries and compares their construction economics.

### Step D1 — use the actual cost rule

For a circle requiring replacement:

```text
area = pi × radius²
surface_rate = sum of rates for DISTINCT surface classes represented
               by ALL fully contained physical pipes
cost = round_to_cents(100 + surface_rate × area^0.85
                     + 200 × total unreplaced pipe length)
```

| Surface | Rate |
|---|---:|
| Grassland | 3 |
| Farmland | 7 |
| Swamp | 12 |
| Road | 17 |
| Structure | 50 |
| Water | 32 |

Only area is raised to `0.85`. Already replaced pipes still contribute their surface class if the circle requires any replacement. A completely PU-only circle is skipped for free.

**Illustration:** a circle covering grassland and road uses rate `3 + 17 = 20`, even if its road pipe was previously replaced. Moving the circle to exclude that road pipe while retaining all target endpoints can reduce the rate to 3. Conversely, a larger merged circle may save one mobilization charge yet become much more expensive by including a new surface class.

### Step D2 — shrink, move and split

1. Replay the inherited order without future leaks and record each row's new target set and planned year. Preserve the intended targets while changing geometry; reject candidates that accidentally include unrelated live targets.
2. For one target pipe, start with the midpoint circle of radius half its length plus a small tolerance. Search center positions on its perpendicular bisector, including boundaries where other pipes enter or leave.
3. For multiple targets, use all target endpoints. Try a minimum enclosing circle, endpoint mean, bounding-box center and old center. For each center, set radius to the maximum target-endpoint distance plus `1e-6 m`.
4. Search surrounding centers in 24 directions at multiple scales, then refine locally. Round exported coordinates to nine decimals and check endpoint containment again.
5. For sets of 2–12 targets, compare separate single-pipe works and candidate two-way splits based on x/y order. Accept a split only when its priced total saves more than $1. Splitting is not forced merely because a circle is large.

### Step D3 — merge neighboring works when beneficial

The development chain progressively broadened the search:

| Stage | Search used in this lineage |
|---|---|
| G04 | Same planned year; nearby pairs/triples; at most 10 target pipes |
| R01 | Further two-dimensional center refinement |
| G05 | Regional search over groups up to 6 circles; at most 16 target pipes; density-dependent search distance |
| G08 | Adaptive search distance up to 350 m; candidate groups up to 16 circles / 48 target pipes; same planned year |
| G17 | One additional selected pair merge applied to G08 |

These are search limits, not a requirement to merge that many circles or use a 350 m radius. In the G08 construction, 21 merges were accepted; accepted groups contained 2–6 circles and their largest resulting radius was about 33.36 m.

For each proposed group:

1. Take the union of its new target pipes.
2. Search a containing circle for those endpoints; reject unintended live-pipe inclusion and reprice all contained surfaces.
3. Compare old and merged fixed charges, including the chance that the work will be unnecessary because leaks have already converted its pipes to PU.
4. Using F168 survival to the planned work year, approximate `P(work needed) = 1 − product(1 − p_i)`, where `p_i` is each target's probability of still being unreplaced at that year. This product assumes independence for the scoring approximation.
5. Calculate `sum(P(old work needed) × old fixed charge) − P(merged work needed) × merged fixed charge`. For same-year groups the length charge is unchanged under the local comparison. Keep favorable candidates, avoid reusing the same old circle twice, insert the merged work at the earliest row of its group, and replay feasibility.

Merging loses some opportunities to skip separate circles for free, so checking only radius or the $100 mobilization charge would miss an important tradeoff.

### Step D4 — the exact extra merge in G17

G17 takes the second recorded merge from the G13 development search and applies only that merge to G08. The G08 active-prefix row indices are **6354 and 7575 (zero-based)**, both planned for 2030. The old radii are approximately **1.897 m and 10.539 m**. The merged grassland circle contains seven target pipes and has radius **10.539 m**: the larger circle can cover the combined targets without enlargement. The local expected fixed-cost saving was about **$113.66**.

The submitted G17 Public score exceeds G08 by **$123.56**. Their official repair expenditure is identical; this observed improvement comes from construction expenditure. The confirmation simulations did not establish consistent internal superiority over G08, so this small Public improvement should not be read as proof of future dominance.

### Step D5 — retain the original geometric coverage at the end

Append the original required iron-coverage circles after the active works. Check that their target pipes have already been replaced, making those final circles PU-only and free. These rows preserve the required geometric coverage; their presence does not mean their pipes were left unrepaired. Also validate coverage, execution order, budget and deadline on the exported CSV.

## 6. Identify and inspect this exact artifact

| Item | G17 |
|---|---|
| CSV | `G17_single_merge.csv` |
| SHA-256 | `47a960a0cec73ee2abd1bb5df61891b66f64eca4a05f114e76a25e9b7a6dd86b` |
| Official submission ID | `SuKJib1exdar` |
| Public score | $79,168,928.88 |
| Official CAPEX / OPEX | $139,702,537.08 / $31,128,534.04 |

Implementation/evidence pointers in this repository:

- [G17 submission record and internal comparison](evidence/EXPERIMENT_RECORD.ja.md), [development summary](evidence/round4_development_summary.csv), [confirmation summary](evidence/G17_confirmation_summary.csv).
- [G17 generation record](evidence/generation.json), [shared regional geometry helpers](../common.py), [regional merge search](../regional_merge.py), [larger-circle search](../large_circle_round2/larger_circles.py). The local assembly source is `output/2026-11-02_regional_optimization/run_round4.py`.
- [Exact inherited order and initial geometry formulas](../../2026-11-02_g04_robustness/ALGORITHM_DETAILS.ja.md); original generator sources are named in that report.
- CMS001 source: `notebooks/ensemble_for_cost_prediction/latest_conditional_stack/` on branch `takito/latest-model-articles-2026-10-28` ([method](https://github.com/reinesana/STAT440-star-kingdom-project/blob/takito/latest-model-articles-2026-10-28/notebooks/ensemble_for_cost_prediction/latest_conditional_stack/METHOD.en.md)).
- [F168 base-model evidence](https://github.com/reinesana/STAT440-star-kingdom-project/blob/8359301/docs/reports/2026-10-28_timing_winner/evidence/base_models_2027.json) and [Ridge mapping](https://github.com/reinesana/STAT440-star-kingdom-project/blob/8359301/docs/reports/2026-10-28_timing_winner/evidence/stacking_2027.json).

The model forecasts and planning constants are frozen inputs to this version. Reproducing the CSV requires its inherited plan and the saved search/selection stages as well as the two fitted predictors; refitting predictors alone does not recreate G17.
