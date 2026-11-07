# Experiments 09a–13a: replacement planning

Prepared by Rion with Codex assistance. Updated October 20, 2026.

**Candidate 13a achieved a displayed public score of +$23.29M**, approximately $0.79M above 12a and $30.08M above 09a. Private scores are unknown.

## Submission

Upload this entire folder to:

    submissions/2026-10-20_rion_combined/

The evaluator submission is **13a_grouped_dynamic_net_benefit_per_cost.csv**. Other CSVs are audit or source files, not alternative submissions. Do not edit or resave the submission through a spreadsheet application.

## Experiment comparison

Let B be the total expected net benefit over currently relevant, wholly contained unreplaced pipes:

    B = sum[p(leak in 2027) × (predicted repair cost − $200 × pipe length)]

Let C be the construction cost for that circle and pipe state. The $200/m term is subtracted from predicted repair cost because a pipe repaired after a leak becomes polyurethane and no longer requires scheduled linear replacement charges. B is a priority heuristic, not an exact calculation of total lifetime savings.

| Candidate | Geometry | Priority rule | Updates after planned replacements? | Public score | Change vs. 09a |
| --- | --- | --- | --- | ---: | ---: |
| 09a — Shana reference | 38,455 original per-iron-pipe circles | Initial B / max(C, $1) | No | -$6.79M | — |
| 09b — comparison from Shana’s experiment | Same original circles | Same net-benefit rule, with XGBoost excluded from leak ensemble | No | -$14.40M | -$7.61M |
| 10a — nearby-pair grouping | 37,799 circles after merging 656 pairs | Preserve 09a order except merged circles enter at the earlier position | No | -$5.98M | +$0.81M |
| 11b — net benefit only | Same circles as 09a | Initial B | No | Approximately -$19M | Approximately -$12.21M |
| 11c — weaker cost weighting | Same circles as 09a | Initial B / sqrt(max(C, $1)) | No | -$9.69M | -$2.90M |
| 12a — dynamic priority | Same circles as 09a | Remaining B / max(current C, $1) | Yes | +$22.50M | +$29.29M |
| **13a — grouping + dynamic priority** |**Exactly the same circles as 10a** |**Remaining B / max(current C, $1)** |**Yes** |**+$23.29M** |**+$30.08M** |

Scores are user-reported evaluator results, including screenshot evidence for 10a, 12a and 13a. Differences use displayed, rounded scores; 11b was reported only as approximately -$19M. Candidate labels are experiment identifiers, not a claim that every intervening number was used.

## Shared data and models

The source repository is https://github.com/reinesana/STAT440-star-kingdom-project.

- `data/pipes.csv`: original material, surface, installation date and endpoint coordinates.
- `data/train.csv`: historical leaks from 2019–2026; these pipes start the project as polyurethane.
- `notebooks/ensemble_for_cost_prediction/predictions/ensemble_stable.csv`: the team’s predicted conditional repair costs.
- `notebooks/leak_model_comparison/deployment_2027_zero_leak_applied/full_inventory_2027_probabilities.csv`: existing 2027 probabilities. The full ensemble averages XGBoost, CatBoost and LightGBM.
- `submissions/2026-10-18_candidate_07_leak_ensemble/09a_full_ensemble_net.csv` and its audit CSV: reference circles, order, initial benefits, construction costs and source-pipe fallback probabilities.
- `submissions/2026-10-19_rion_grouping/10a_09a_nearby_pairs.csv`: grouped geometry reused by 13a.

Experiments 10a–13a do not retrain predictive models or change the ensemble weights. They change replacement planning using the team’s existing predictions.

## What changed in each experiment?

### 09a: the reference

Shana combined the team’s full-ensemble leak probabilities with shrinkage-ensemble repair-cost predictions. She ranked original circles by their initial net benefit per construction dollar, with Pipe ID ties. Priorities were calculated once. Circles overlap, so their initial benefits can include the same pipe.

09b used the same approach but removed XGBoost from the leak-probability ensemble. It is included above as context; Rion’s later experiments use 09a’s full ensemble.

### 10a: merge nearby circles

Considered spatially nearby pairs within 100 positions of each other in 09a’s order. Constructed a new enclosing circle covering all pipes wholly contained in either original circle, with a numerical margin. Accepted pairs with initial sequential construction savings above $100, greedily selecting the best available pair for each scanned position. A unit was merged at most once.

Merged 656 pairs and reduced the count from 38,455 to 37,799. Each merged circle was placed at the earlier original position; untouched circles kept their relative order. This changed geometry and some replacement timing, without dynamic reprioritization.

### 11b and 11c: change the denominator

Kept all original 09a circle records and forecasts. 11b removed construction-cost weighting; 11c weakened it by dividing by the square root of construction cost. Both used a fixed initial ordering and both underperformed 09a publicly. These tests support retaining 09a’s cost weighting for these candidates; they do not establish that its formula is globally optimal.

### 12a: update priorities as planned work proceeds

Kept the original 09a geometry and B/C concept. Repeatedly selected the circle with the highest remaining net benefit per current construction dollar, marked its contained pipes replaced in a planning simulation, and updated affected overlapping circles.

Example: circle A contains pipes 1 and 2; circle B contains pipes 2 and 3. After selecting A, B’s remaining benefit and linear replacement charge include pipe 3 only. Surface types still include all wholly contained pipes, including pipe 2. B can therefore move below other circles.

Polyurethane-only units are retained for geometry but skipped at zero cost. Priorities use unrounded construction cost; the budget validator rounds executed-unit costs to cents. Ties use the original source Pipe ID.

### 13a: combine the two changes

Used exactly the 37,799 circles from 10a and applied 12a’s dynamic greedy selection. Existing circles retained their original source-pipe tie breaker; merged circles use the smallest contained original-iron Pipe ID, then source position.

13a does not enlarge or shrink the 10a circles. Compared with 12a, grouped geometry and the resulting ordering change together. Its +$0.79M public gain supports this particular combination, not a guarantee that every grouping strategy will help.

## Important distinction: planning versus actual evaluation

“Dynamic” refers to computing the order **before submission**, accounting for replacements from previously selected work units. The result is a fixed CSV. It does not observe or react to actual future evaluation leaks. The greedy construction order does not explicitly optimize calendar years; annual execution is simulated afterward for feasibility.

All these priority experiments use fixed 2027 forecasts for a 25-year project. They are heuristics, not globally optimal or complete future-risk models.

## Local validation

| Candidate | Work units | No-future-leak construction cost | Completion year | Uncovered original iron |
| --- | ---: | ---: | ---: | ---: |
| 09a | 38,455 | $152,944,811.51 | 2042 | 0 |
| 10a | 37,799 | $152,227,909.47 | 2042 | 0 |
| 11b | 38,455 | $152,201,702.27 | 2042 | 0 |
| 11c | 38,455 | $152,190,152.11 | 2042 | 0 |
| 12a | 38,455 | $151,529,540.50 | 2042 | 0 |
| 13a | 37,799 | $150,868,763.59 | 2042 | 0 |

These construction costs exclude future leaks and repair costs. They are not official score forecasts. Annual spending can exceed $10M when carried-over funds are available. A negative official score does not by itself mean the construction budget was exceeded.

For 13a, the exported CSV is reparsed and checked against 10a’s exact circle multiset. All 38,455 known original iron pipes are covered by endpoint containment, and no original iron remains after the construction simulation. Costs include distinct surface types from all contained pipes, current non-polyurethane replacement length, copper/brass, conservative treatment of unknown material, overlaps and zero-cost skips. Budget simulation uses half-up cent rounding, integer cents, annual carryover and stopping at the first unaffordable unit. Completion by 2051 is asserted under the no-future-leak scenario.

The script first reproduces 09a’s original construction cost. Initial per-circle benefits match the published audit with maximum absolute error about 2.91e-11. Missing iron probabilities use audit fallback values. For eight unknown-material pipes with missing prediction inputs, relevant benefit contributions are recovered from 09a’s aggregate-benefit constraints; identifiability is asserted for participating pipes. Pipes outside all source circles do not affect priority. This preserves the reference contributions rather than declaring unknown predictions to be confirmed zero risk.

No-future-leak validation is a construction check, not proof of performance or feasibility for every possible future leak path. The displayed public score does not reveal separate realized construction and repair costs. Private performance remains unknown.

## Contents and reproduction

- `13a_grouped_dynamic_net_benefit_per_cost.csv`: official submission file.
- Matching `.validation.json`: coverage, budget, annual schedule and submission SHA256.
- `13a_order.audit.csv`: final ordering and original 10a ranks.
- `build_combined.py`: executable generator and validator.
- `source/`: unchanged input snapshots for a self-contained reproduction.
- `public_result.json`: recorded public result and comparisons.
- `experiment_comparison.csv`: experiment summary for team records.

Requires Python, numpy and pandas. From this directory:

    python build_combined.py

Expected submission SHA256:

    74c56b8bcdd7a7638f8dac9bee4cea991172981a4495fcea163f5f01e819bf24

Keep the existing 12a and 13a submissions unchanged as references for further experiments. Do not select future modifications solely on a small public-score gain without checking validity and documenting the change.
