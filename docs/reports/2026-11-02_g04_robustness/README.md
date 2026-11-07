# Comparison of submission plans using prediction accuracy and public scores

2026-11-02 | Historical comparison | Takito (AI-assisted)

Current final selection: [G17](../2026-11-02_regional_optimization/G17/README.md).

Historical comparison: the current final selection is G17. At that stage, G04 remained the final choice: it had the highest current-rule public score and favorable repair-cost RMSE, worst-year RMSE, and high-cost capture. Shana performed better on MAE and total bias, so G04 was not best on every metric.

|Metric / author and candidate|Shana / 20a|Ryota / reduced draft|Amy / integrated cover|Takito / G04|
|---|---|---|---|---|
|Public score ($M)|74.03 *|77.29 **|77.4565|78.9910|
|Repair-cost RMSE ($)|116,861.56|117,750.96|117,750.96|115,810.35|
|Repair-cost MAE ($)|22,947.17|25,341.67|25,341.67|23,579.27|
|Worst-year RMSE ($)|128,632.64|129,206.19|129,206.19|126,966.13|
|Total prediction bias (%)|+1.58|+19.51|+19.51|+10.78|
|Top-10% cost capture (%)|73.22|71.43|71.43|75.51|

These are dollar prediction errors, not differences from another candidate. Public values in M represent millions of dollars. * Shana's public score is an old-rule reference. ** Ryota's original plan has incomplete geometric coverage and is excluded from adoption comparisons.

### Reading the metrics

RMSE gives greater weight to large errors; MAE is the mean absolute error per event. Lower is better for both. Worst-year RMSE is the largest annual RMSE across the three evaluation years; every model had its worst result in 2026.

Total prediction bias measures the percentage difference between summed predicted and actual repair costs; values near zero are better, and positive values indicate overprediction. Cost capture is the share of actual repair dollars belonging to the top 10% of events by predicted cost; higher values indicate better identification of costly repairs.

### Repair-cost accuracy on a common evaluation population

Predictions for the same 6,766 repairs in 2024–2026 used only earlier-year training data. RMSE and MAE pool all events. Shana uses the stable ensemble, Amy and Ryota use historical material/surface means, and Takito uses CMS001. Amy and Ryota therefore have identical cost-prediction errors.

These validate conditional repair-cost predictions, not circle locations or work order. Assess overfitting through later-year errors, total bias, and high-cost capture rather than a single metric.

### Conclusion: G04 retained as the final choice at that stage

G04 led this historical comparison with a public score of $78.991M and passed full iron-coverage and budget checks. Its lower large-error metrics and strong high-cost capture supported retaining it at that stage.

Shana had better MAE and total calibration, so the comparison did not establish G04 as best on private data. Amy and Shana were retained as comparison candidates. The assignment grades the private score of the highest-public-score retained submission.

## Explaining the G04 algorithm in order of processing

### 1 Create construction order based on predictions

CMS001 estimates repair cost conditional on a leak; F168 estimates cumulative leak probabilities over two and 25 years. Combine short- and long-term risks with repair severity, pipe length, and replacement costs to prioritize costly, leak-prone pipes.

For each candidate circle, sum priority over currently non-PU pipes and discount by its current construction cost. Add a small credit for making overlapping circles unnecessary. Apply local reordering to the seed order, replay the $10M annual budget with carryover to obtain scheduled years, then reselect high-priority circles within each year group.

After selecting a circle, mark its replacement targets as PU and update overlapping priorities and costs. Repeat to produce a fixed submission order; realized future leaks do not trigger online reordering.

### 2 Identify each circle's new replacement targets

Initially mark native PU and historically leaked/replaced pipes as replaced. Read the CSV in order; among all pipes with both endpoints in each circle, remove already replaced pipes. The remainder are newly replaced by that row.

Example: circle A contains P1/P2 and B contains P2/P3. If P1 was historically replaced, A replaces only P2. B then replaces only P3 because P2 is already replaced. Neither P2's length nor its preventive benefit is counted twice.

### 3 Change the center and radius and compare the divisions

For a single target pipe, move the center along its perpendicular bisector. Calculate positions where neighboring endpoints enter or leave the circle and test positions on either side. For multiple targets, start from the minimum enclosing circle, centroid, and other seeds; test 24 directions and multiple distances, then refine locally.

For each proposed center, set the radius to the maximum distance to any target endpoint plus 0.000001 m. Find the distinct surface types of all wholly contained physical pipes, including replaced pipes, and calculate actual construction costs. Reject candidates that include unintended unreplaced pipes.

For multiple targets, also consider individual-pipe circles and two-way groups formed by sorting on x/y. Optimize each small circle's position and split only when total fixed charges, surface costs, and replacement-length costs are lower than for the original circle. Smaller groups are not accepted automatically.

Example from G02, before G04: move a 32.83 m circle containing water and structure surfaces to a 22.11 m water-only circle with identical replacement targets. The surface rate falls from 82 to 32, saving approximately $65,688 for that work.

## Circle merging and the coverage suffix

### 4 Integrate neighboring circles with the same planned year

Replay the order without leaks to obtain each circle's scheduled year and replacement targets. Examine at most 16 neighbors within 100 m in the same scheduled year, forming pairs and nearby triples. G04 restricts the original row gap to 4,000 and the union of replacement targets to 10 pipes.

Build a new circle covering all target pipes and use the preceding position search to reduce costs. Reject unrelated unreplaced pipes. Discard candidates saving less than $25 in the fixed component ($100 plus surface costs).

Use F168 to estimate each pipe's survival probability at the start of the scheduled year. If all contained pipes have already leaked, the circle is free. Compare construction probability times fixed costs for separate and merged circles. This calculation assumes independent leaks within each circle.

Illustration: two circles each have $1,000 fixed costs and a 50% construction probability, so separate expected fixed costs total $1,000. If a merged circle costs $1,500 and has a 75% chance of retaining an unreplaced pipe, its expected fixed cost is $1,125. Although the nominal fixed cost falls, expected cost increases, so reject this merge.

Accept candidates saving at least $10 in expected fixed costs, largest first, without sharing a circle between merges. Place each merged circle at the group's earliest position and remove later members. Reoptimize center, radius, and splitting afterward. The merge selection accepted 1,199 groups, including 366 triples.

### 5 The last circle satisfies only the covering condition

Small construction circles may not geometrically cover every historically replaced original iron pipe. Retain the original 37,314 circles as a suffix to satisfy full original-iron coverage. G04's construction prefix contains 22,154 circles.

Rechecking found zero newly replaced pipes and zero construction costs in the suffix. All 10,826 original iron pipes not geometrically covered by the prefix were already replaced at project start; no unrepaired pipes were left behind.

Merging the suffix cannot reduce costs. Enlarging it to include copper or other pipes not replaced by the prefix can introduce new costs. Optimize the construction circles in the prefix instead.

[Editable Word](G04_comparison_detailed.docx) / [PDF](paper.detailed.pdf) / [How to calculate indicators ](COST_METRICS.md) / [Implementation formulas and settings](ALGORITHM_DETAILS.md)
