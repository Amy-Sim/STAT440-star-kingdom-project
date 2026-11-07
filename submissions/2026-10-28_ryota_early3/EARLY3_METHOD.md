# Select a circle that emphasizes the first 3 years

`early_three_years.py` does not change the previous submission `outputs/multi_pipe.csv`,
Save the new submission to `outputs_early3/early3_adaptive.csv`.
The user's report of a $71.40M official display identifies the previous CSV comparator, but
Those values were not used to tune the predictors or simulator.

## This change

1. Estimate the annual leak probability by material, ground surface, and pipe age using pipe ages in 0.5-year increments and smooth neighborhood averages.
   Capture narrow age-band leak concentrations more effectively than the previous five-year bands.
   Sparse groups shrink toward material-specific age curves.
2. Select the smoothing width and history weight from 6 candidates for time series verification in 2024 and 2025.
   The leak results for 2026 will not be used to select this parameter, and the performance will be checked separately.
   Refit for final submission using history through 2026.
3. For each year between 2027 and 2029, what is expected to occur between that year and the end of 2029?
   Aggregate leak losses only for unreplaced pipes, accounting for survival through earlier years.
4. Simultaneously compare single circle and nearby savings candidates that combine up to 6 iron pipes.
   Select circles in descending order of expected newly avoidable leak loss divided by current construction cost.
   After accepting a new circle, recalculate benefits and costs for every affected candidate.
   Do not count the risk of already replaced pipes again.
5. If it is inefficient to group them together, a single circle will be selected as is.
   After 3 years of initial selection, we will basically form a small design group that brings together 1 to 3 designs.
   Schedule remaining work considering savings and radius.

The annual budget is $10M with unused funds carried forward. Depending on budget remaining at planned year boundaries, CSV execution may
works planned for the next year can execute slightly earlier. Actual post-submission annual allocation is
See `early3_adaptive_annual.csv`, calculated by reading back the serialized CSV.
Natural replacement after future leaks can further change execution timing.

There is no constraint requiring the radius to decrease from one row to the next.
This avoids deferring dangerous isolated pipes because of that constraint.
Choose larger circles when risk/cost efficiency supports them, leaving smaller groups for later years.
Export actual annual radius summaries and inspect the resulting trend.

## Compare and check

Besides the main `early3_adaptive.csv` candidate, a comparison retains the previous circles and changes only forecasts and order;
also compare `early3_reorder_only.csv`, which changes only those predictions and ordering.
Run paired comparisons under both old and new leak models at hazard multipliers 0.5, 1, and 2.
Record first-three-year repair costs separately from the 25-year score.
Do not judge improvement solely from the new model's self-evaluation.

First-three-year repair evaluation uses the same leak times as full-period evaluation,
Extracted using a separate calculation with leak costs after 2030 set to zero.
As in the preceding experiment, construction occurs at the start of each year, followed by leaks.
The budget applies to construction costs; repair costs are deducted from the score.

Even if the top 10% leak capture rate improves in the 2026 verification, it does not guarantee performance from 2027 to 2029.
Calibration and high-risk ranking are distinct; also report log loss and mean predicted probability.
Reservations about missing official specification details are unchanged from the previous README.

## Rerun

```sh
python -m unittest discover -v
python early_three_years.py --sims 30
```

Recheck exported CSV structure, pipe containment, coverage of all unreplaced iron, and budget-feasible completion.
Do not overwrite previous submissions, results, or the GitHub handoff ZIP.
