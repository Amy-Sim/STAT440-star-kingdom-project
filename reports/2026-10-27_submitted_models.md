# List of submitted model materials (2026-10-26 submission session)

Organized on 2026-10-27 UTC. "Today" in the conversation is treated as the submission session of October 26th, which remains on the submission screen and existing records, and the date is not uniformly rewritten. We compared the current contents of the shared Google Doc, GitHub main, and verified chat records.

## Model where you can check submission and results

| ID | Method/Changes | Public (M$) | Submitted CSV |
| --- | --- | ---: | --- |
| 09a | Fixed initial net benefit / corrected cost | 65.40 | [CSV](../submissions/2026-10-26_after_second_bug%202/09a_corrected_reference.csv) |
| 10a | Nearby grouping rebuilt with corrected costs | 65.78 | [CSV](../submissions/2026-10-26_after_second_bug%202/10a_corrected_nearby_pairs.csv) |
| 11b | Fixed net benefit only; unchanged order | 51.99 | [CSV](../submissions/2026-10-26_after_second_bug%202/11b_corrected_net_benefit_only.csv) |
| 11c | Fixed net benefit / sqrt(corrected cost) | 61.70 | [CSV](../submissions/2026-10-26_after_second_bug%202/11c_corrected_net_benefit_sqrt_cost.csv) |
| 12a | Dynamic overlap updates, original circles | 69.89 | [CSV](../submissions/2026-10-26_after_second_bug%202/12a_corrected_dynamic.csv) |
| 13a | Rebuilt grouping plus dynamic overlap updates | 70.24 | [CSV](../submissions/2026-10-26_after_second_bug%202/13a_corrected_grouped_dynamic.csv) |
| 21a | 20a circles + p17b + CatBoost 68.627% / corrected log RF 31.373%; dynamic net benefit/cost | 74.78 | [CSV](../submissions/2026-10-26_best20a_catboost_logrf/21a_20a_catboost6863_logrf3137.csv) |

09a-13a are Rion modified rebuild packages. The responses for the six cases are based on the order of submission as stated by the person. For 21a, Takito has confirmed the correspondence between the file name and $74.78M. 11b and 11c are not treated as works by Takito.

- [09a-13a: Methodology, differences from previous versions, budget, reproduction steps](../submissions/2026-10-26_after_second_bug%202/README.md). Reproduce `python rebuild_corrected.py` in that folder.
- [21a: Model configuration, annual validation, weights, team contributions, limits](2026-10-26_takito_latest_model.md). To reproduce a frozen submission, go to `python submissions/2026-10-26_best20a_catboost_logrf/reproduce.py` directly under the repository. Only this command explicitly uses legacy calculations for past reproduction.
- [Machine-readable submission ledger](2026-10-27_submission_register.json): Contains SHA-256 of submission CSV and source classification of results.

## Result on the submission screen but file correspondence is not confirmed

| Displayed time (as recorded) | Public (M$) | Status |
| --- | ---: | --- |
| 15:25 | 74.16 | File name not confirmed |
| 15:34 | 74.25 | File name not confirmed |
| 15:34 | 74.00 | File name not confirmed |

The source is the user-provided screenshot cited in the [existing 21a report](2026-10-26_takito_latest_model.md). Scores alone were not assigned to 18a, 20a, or stacking comparisons. Model names for all submissions remain unresolved until the exact file mappings are confirmed.

## Rebuilt and prepared, but new submission results cannot be confirmed

- [Fixed version 09b](../submissions/2026-10-26_09b_corrected_after_second_bug/README.md): Use leak probability of CatBoost + LightGBM only. The generated code/CSV exists in main. New public score based on current evaluation has not been confirmed. 59.32M of shared Doc is the old condition of 10/21, so it will not be posted.
- 06/07a/07b: The shared Doc says "Fixed on 10/27", but there is no corresponding new submission package/confirmed score in the main we checked this time. Do not treat old scores as current results.
- [Modified version 21a](../submissions/2026-10-27_current_rules/README.md): Rebuild order with new cost formula. Official public score not evaluated. $74.78M is not the result of this other CSV.
- Local `2026-10-26_cost_stacking_comparison` is ready for comparison of 18a control and stacking replacement. Both public scores of the manifest are null and cannot be used as a basis for confirmation of submission.

## Notes on cost formulas and comparisons

The current formula is `100 + surface_rate * area**0.85 + 200 * unreplaced_length`. Only area is raised to 0.85; coordinates and straight pipe lengths are meters. Use the [current rules](../docs/current_rules.md) for new experiments.

09a to 13a are comparisons of the same evaluation conditions reconstructed using the correction formula. The 21a submission generation/existing local verification is the old cost formula, and the official score and local construction cost are different metrics. We do not conclude that the difference between the old 20a and 21a is an improvement in the model alone. All results are public and private results are unconfirmed.

Shared record: [STAT440 Google Doc](https://docs.google.com/document/d/1N32Z_DC6Frw1OYwSNA9mIlXjgDPuKiOQXH4nJV2RZcQ/edit), read 2026-10-27. The shared document was not edited.
