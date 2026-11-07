# Ryota: Circle optimization that emphasizes the initial 3 years (2026-10-28)

In the screenshot supplied for this submission, the displayed public score for the first-three-year plan was
**$76.91M**, previous edition**$71.40M**. The difference in displayed value is**+$5.51M (approximately 7.72%)**.
Both results rely on user-provided screenshots and file-to-result confirmation in the conversation.
These were not independently checked on the evaluator site. Displayed scores use 0.01M increments, so
Differences likewise use displayed values. Private scores remain unknown.

## Submission and reproduction materials

| Version | Displayed public score (M$) | CSV |
|---|---:|---|
| Previous: Up to 6 savings groups + 2 years risk order | 71.40 | [multi_pipe.csv](../submissions/2026-10-28_ryota_early3/outputs/multi_pipe.csv) |
| This time: Dynamic selection of group/single depending on risk in the initial 3 years | 76.91 | [early3_adaptive.csv](../submissions/2026-10-28_ryota_early3/outputs_early3/early3_adaptive.csv) |

- [How to and re-run steps](../submissions/2026-10-28_ryota_early3/EARLY3_METHOD.md)
- [Time series verification/comparative calculation/constraints](../submissions/2026-10-28_ryota_early3/outputs_early3/SUMMARY.md)
- [Official display source, image, CSV SHA-256](../submissions/2026-10-28_ryota_early3/outputs_early3/official_results.json)
- [This time's score image](../submissions/2026-10-28_ryota_early3/outputs_early3/official_score_76_91m.png)
- [Previous score image](../submissions/2026-10-28_ryota_early3/outputs_early3/official_score_71_40m.png)
- [Verification of differences and costs with common verification](../submissions/2026-10-28_ryota_early3/outputs_early3/shared_validation.json)

## Method

Estimate leak probability from material, surface, and half-year age bands, smoothing over nearby ages.
Older history is weighted by 0.85 per year. The smoothing bandwidth and history weights were
It was selected for time series verification in 2024 and 2025, and confirmed without using 2026 as a setting selection.
The final submission model was fitted using history through 2026.

From 2027 to 2029, we will use the “anticipated leak loss/construction costs that can be newly prevented in the remaining initial three years”.
choose between single circles and savings candidates grouping up to six pipes. For overlapping replacement targets, after each selected circle,
update remaining risk and costs. Choose a single circle when larger grouping is inefficient.
The later phase primarily uses groups of at most three design targets. Radius is not constrained to decrease monotonically,
In the first three years, many short high-risk pipes were replaced individually; median radii were 3.86 → 5.24 → 6.43 m.

The leak capture rate for the top 10% of risks in 2026 is 28.28% for the old model and 49.57% for the new model.
Mean predicted probability remains below the observed rate, and log loss did not improve.
Saved paired simulations for the old/new models, hazard multipliers 0.5/1/2, and 30 repetitions per setting.
Under standard settings, first-three-year repair costs fell by 3.23% under the old model and 8.25% under the new model.
Keep these simulations separate from the public scores displayed above.

## Reservations found by checking with common rules

Cost model: `2026-10-26-area-exponent`. Shared repository `data/pipes.csv` and
`data/train.csv` matched the input hash for this experiment.
Submitted CSV bytes are preserved; files corresponding to official displayed results were not regenerated.

**It satisfies the cover for all unreplaced iron pipes, but fails the shared verification "geometric cover for all original iron."**
The original experiment excluded historically leaking pipes from circle generation because they were already replaced.
Shared validation also requires circles for historically replaced pipes. The original strict geometry check was run and its failure recorded;
Report budget/completion validation restricted to unreplaced iron separately.
Do not treat this record as evidence of full rule compliance or guaranteed private performance.

No-future-leak construction costs matched between the shared simulator and original independent implementation.
Full-period leak evaluation differs between implementations, including treatment after construction completes, so
We do not claim to have reproduced every Monte Carlo comparison with the shared simulator.

Google Doc attempted to read it, but was unable to retrieve it during this GitHub integration.
This integration added saved results and shared validation; it did not retrain models or run new model experiments.

## Rerun

Inputs resolve automatically to the repository's `data/` directory. Raw data need not be copied into the experiment folder.
Only input-path fallback behavior changed from the previous experiment code; the submitted CSV is unchanged.

```sh
cd submissions/2026-10-28_ryota_early3
python -m unittest discover -v
python verify_early_outputs.py
python validate_shared.py
# Execute the following only when regenerating saved local results.
python early_three_years.py --sims 30
```

Regeneration overwrites this folder's experiment outputs. For new experiments, create a newly dated
folder. Shared validation requires the repository dependencies.
