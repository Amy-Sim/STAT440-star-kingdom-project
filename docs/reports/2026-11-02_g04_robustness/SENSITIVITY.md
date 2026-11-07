# Appendix: Candidate sources, internal evaluation, reproduction method

Historical comparison, dated 2026-11-02. The current final selection is [G17](../2026-11-02_regional_optimization/G17/README.md).


See the [main paper](README.md) and [printable A4 PDF](paper.detailed.pdf).

## What was tested?

We investigated whether a fixed repair plan including G04 is advantageous even if assumptions about future leaks and repair costs are changed.
No retraining, reselection, or additional official submission was performed. This is **post-selection sensitivity analysis**, and
This is not an independent test capable of statistically ruling out model overfitting. After selecting the highest-public-score candidates,
comparison, so public-driven selection bias remains.

## Candidate and person in charge

See [candidates.json](candidates.json) for candidate files, SHA-256 hashes, and interpretation of public values.
Author labels identify team planning methods; they do not necessarily match submission accounts or Git commit authors,
may not match. Amy's plan includes improvements based on Ryota's pipeline,
Takito's G04 also develops Ryota/Amy's geometric processing.

|Author|Candidate|Public score ($M)|Evidence and interpretation|
|---|---|---:|---|
|Shana|20a same-year merge|74.03|Matches [20a on Shana's branch](https://github.com/reinesana/STAT440-star-kingdom-project/tree/668a598ba8efd478d1c5bf569b39fc7fb93162e2/submissions/2026-10-22_candidate_20_sameyear_merge) to [src/calibrate_simulator.py](https://github.com/reinesana/STAT440-star-kingdom-project/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/src/calibrate_simulator.py). Old-rule reference; internal results recomputed under current rules.|
|Ryota|shrink-after-work|77.29|Rounded display from the [submission record](https://github.com/reinesana/STAT440-star-kingdom-project/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/submissions/2026-10-28_ryota_shrink_after_work/official_results.json). Missing geometric coverage for 10,704 original iron pipes; zero uncovered unreplaced iron pipes.|
|Ryota original + shared coverage repair|Append coverage-repair circles|Not submitted|Run Amy's existing [repair_baseline](https://github.com/reinesana/STAT440-star-kingdom-project/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/submissions/2026-10-30_center_and_split/build_submission.py) unchanged. Add 10,704 circles; 13 also affect neighboring unreplaced non-iron pipes, so do not assume zero-cost repair.|
|Amy|integrated coverage|77.45649615|[Frozen CSV and annual totals](https://github.com/reinesana/STAT440-star-kingdom-project/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/submissions/2026-10-30_integrated_coverage/official_results.json). Construction $141,186,485.65 + repairs $31,357,018.20.|
|Takito|G04 economic triples|78.99096825|User-provided submission result. Saved [official annual breakdown](evidence/official_G04.csv) sums to construction $139,778,840.95 + repairs $31,230,190.80. Not independently fetched from the service.|

We selected representative candidates that allow you to check the correspondence between CSV and public values on GitHub. Unpublished/file not supported
This does not establish the latest best model across every submission by every team member.
Inputs are preserved; files with LF/CRLF differences retain enough information to compare against submission-time hashes
representation before freezing. Shana 20a uses LF; Ryota and Amy submissions use CRLF.

## Common evaluation rules

Coordinates and straight-line lengths are in meters. A pipe is wholly contained only if both endpoints are inside the circle.
The surface rate sums distinct surface types over every wholly contained pipe, including already replaced pipes.

```text
cost = round_to_cents(100 + sum(distinct surface rates) * (pi*r^2)^0.85
                     + 200 * unreplaced_length)
```

From 2027 through 2051, add $10M annually and carry unused funds forward. If the next circle exceeds available funds, resume from it the following year.
Each year executes construction before leaks. Leaking pipes become PU; PU-only circles are skipped at zero cost.
Include repair costs in the score calculation, but do not deduct them from the construction budget.
Score = $250,000,000 minus construction costs minus leak repair costs.
Geometric coverage of every original iron pipe and completion of all unreplaced iron pipes were checked separately.
Ryota's original plan satisfies only the latter, so it is not included in the ranking of valid plans.

## Fixed 24 conditions and compared using 256 sets of common random numbers

- **Internal A**: Frozen CMS001 repair cost + F168 survival curve starting in 2027.
  F168 predictions for unreplaced pipes were matched exactly by ID. Eight pipes without CMS001 predictions use the median predicted cost.
- **Internal B**: Age-based leak rate of existing `fit_fine(cutoff=2026, width=.5, decay=.85)` and
  Historical material/surface mean repair cost. Used only for evaluation, not candidate generation or reordering.
- leak cumulative hazard multiplier 0.5/1.0/1.5: Changed survival curve to `S(t)^scale`.
- Cost variation coefficient 0/1.5: gives lognormal variation that maintains the mean.
- Without/with spatial dependence of leak time: Gaussian copula for common shock within 500m grid
  with latent-normal correlations 0/0.35, preserving each pipe's marginal leak probability.
  These are synthetic stress assumptions, not estimates of physical connections or actual correlation within 500 m.

2 x 3 x 2 x 2 = 24 conditions, 256 pairs each, 6,144 scenarios/plans in total. The random number seed is 2026110257.
Every plan in a paired comparison receives identical per-pipe leak times and repair costs for that setting and seed.
Random numbers are shared across settings; these are not 6,144 independent observed realities.
Equal weighting across settings is descriptive; it does not imply that the assumptions occur with equal real-world probability.

The primary metric is the difference from Amy's plan. Internal A/B each average 12 settings.
The worst setting is the smallest of the 24 setting-specific mean differences, not the worst individual future scenario.
The number of winning settings counts settings with a positive mean difference; it is not the probability of winning on the private set.
The Monte Carlo 95% interval is calculated from the standard errors of 256 paired differences.
The interval does not include uncertainty in the models or future distributions.
For family-wide intervals, average the 12 setting differences within each seed, then compute the standard error across seeds,
Setting-specific intervals were not averaged.

## What can be read

- The internal A difference of G04 is +7.821M, but the internal B difference is -0.228M.
  The Monte Carlo 95% interval for internal family B's mean difference is [-0.341M, -0.115M].
- +0.108M if there is no neighbor shock in internal B, -0.564M if there is.
  The worst setting was family B, leak multiplier 0.5, no cost variation, and neighborhood shocks,
  Difference with Amy -1.442M, Monte Carlo 95% interval [-1.569M, -1.316M].
- G04 outperforms Amy in 16/24 conditions and Shana 20a in 20/24 conditions.
  G04 is not the best result under all assumptions.
- Shana's old Public and current Public cannot be compared, but the internal value of fixed CSV is
  All candidates were recomputed under the same current rules, allowing comparisons conditional on those settings.
- 4 valid plans (Ryota repair version, Amy, Shana, G04) with a total of 6,144 scenarios
  Geometry, completion-window, and budget checks passed; this is not a guarantee across every future scenario.

## G04 algorithm and specific example

G04 did not learn a new leak model. Based on the existing order of CMS001+F168,
Calculate surface costs, replacement length, budgets, and free-skip opportunities while changing circle centers, radii, partitions, and merges.
Merging two or three neighboring circles within a scheduled year permits local advancement relative to the original order.

When enclosing one pipe, calculate the boundary position where the pipe end enters or leaves the circle on the perpendicular bisector of both ends.
For multiple pipes, compare minimum enclosing circles, centroids, bounding-box centers, 24-direction moves, local refinement, and splitting.
Reject candidates adding unintended unreplaced pipes; select using actual costs.
Accept merges with positive expected fixed-cost savings after subtracting lost F168 free-skip opportunities.
Accepted 1,199 merges, including 366 triple merges. The original 37,314-circle suffix preserves geometric coverage,
After replacement is complete, these circles contain only PU and are processed at zero cost.

In the example of G02, the previous stage of G04, move and reduce the center of the circle with a radius of 32.83m that includes the water surface + building,
the same targets were enclosed in a 22.11 m water-only circle. The surface rate fell from 82 to 32, reducing construction costs by
A reduction of $65,687.97. This amount is a reduction in the circle in the previous stage, and is the reduction in the final G04.
This is neither a same-row comparison nor the overall official improvement.

## Verification and reproduction

Each plan was checked for circle coverage, no-leak execution, and candidate CSV hashes.
The fast replay was checked against the existing Python executor using three leak/cost seeds per plan, matching construction costs, repair costs, and
Leak counts matched. See the [validation JSON](evidence/geometry_and_replay_checks.json) for candidate-specific results.
Only repository `data/pipes.csv` and `data/train.csv` were used; no external modeling data were added.

```powershell
python docs/reports/2026-11-02_g04_robustness/evaluate.py --repo-root . --draws 256
```

Required libraries: numpy, pandas, scipy, and numba.
Coverage-repair candidates, other comparison CSVs, and frozen forecasts are in this folder's `candidates/` and `inputs/` directories.
This reproduces evaluation of saved plans rather than regenerating the candidates.

- [Correspondence between candidate and official value](candidates.json)
- [Evaluation condition/input hash](evidence/protocol.json)
- [Main comparison table](evidence/summary.csv)
- [Indicators for all conditions](evidence/setting_metrics.csv)
- [Paired interval](evidence/family_paired_intervals.csv) of family averages
- [Results for each scenario](evidence/simulations.csv)
- [Share Experiment Doc](https://docs.google.com/document/d/1N32Z_DC6Frw1OYwSNA9mIlXjgDPuKiOQXH4nJV2RZcQ/edit)

## Limitations and future decisions

Previously inspected historical years and public results influenced candidate and predictor selection.
Fresh random numbers assess reproducibility and assumption sensitivity; they do not eliminate selection bias.
An advantage here does not prove the absence of overfitting; a disadvantage does not establish overfitting as its cause.
Private results or evaluation at a pre-fixed, unused actual measured future is required.
At that stage, retaining G04 as the best public submission alongside Amy and Shana comparison candidates was reasonable.

### Final submission decision

At that stage G04 remained the final choice, with the highest current-rule public score of 78.99096825M,
It also performs strongly in internal family A and meets geometry and budget requirements.
[In the scoring rule](https://github.com/reinesana/STAT440-star-kingdom-project/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/docs/assignment_2026-10-14.md),
The private score of the highest-public-score retained submission determines the mark.
Amy leads in internal family B, and Shana remains competitive; G04 is not guaranteed to be best privately.
Nor can you directly compare Shana's old rule Public to the current Public and reselect it.
The Amy/Shana alternative will be preserved, leaving room for separate comparisons with unused actual data.
This statement does not instruct deletion or withdrawal of submissions; neither action was performed.
