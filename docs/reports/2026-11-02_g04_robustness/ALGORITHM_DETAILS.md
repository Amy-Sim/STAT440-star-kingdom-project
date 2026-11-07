# G04 expression and settings corresponding to implementation

[Easy-to-read processing description](README.md) / [Indicator definition](COST_METRICS.md)

## Underlying order

The basis of G04 is the existing fixed order of CMS001 + F168. At the beginning of geometric optimization,
Used the existing 75.411M plan (SHA-256 `36810d9c61f1c1000a97230bf0cbae7a0e7bb3eb7cf7c45d5c92a1705ebe68dc`).
This plan adds Ryota/Amy geometry changes to the original 02_OVERLAP_CREDIT order.
The following formula is the 02_OVERLAP_CREDIT priority rule, not simple descending repair cost or probability.

```text
F2 = 1 - S_F168(2)
F25 = 1 - S_F168(25)
R   = (1 - 0.3227327995) * F2 + 0.3227327995 * F25
C = CMS001 repair cost / (max(length, 0.1) / median length of unreplaced pipes)^0.0030795309
V = R^0.8300158668 * max(C - 0.9780439932 * 200 * length, 0)^0.8780168139
```

`V` is a priority score, not the expected loss itself in dollar terms.
Originally PU and historically replaced pipes receive zero priority value.
Sum `V` over newly replaced pipes and select circles using the following score.

```text
priority = (sum of V for unreplaced pipes in the circle + 0.01 * overlapping-circle fixed-cost credit)
         / Current construction cost^0.8490093179
```

The credit is the sum of fixed components ($100 plus surface costs) of other works made unnecessary by selecting this circle. After each selection, update replacement states and scores for overlapping circles and their neighboring dependencies.

The seed order used greedy selection from the two predictors, local moves, block moves, and related steps.
The saved recipe accepted 101 initial local moves, 17 seed-order block changes, and later stages of 40 and 52 moves.
Replay the order against the budget to obtain scheduled years. The final overlap-credit stage processes earlier year groups first and compares priorities within each group.
Add $10M annually. If the next work exceeds remaining funds, carry that work to the front of the next year's queue.

## Geometric optimization

At the G01/G02 stage, while maintaining the set of new exchange targets for each original row,
Drop the constraint of preserving historical geometric coverage at each row; retain original circles as a suffix instead.

- Round the center of circle to 9 decimal places, then set the radius to the maximum distance to all required endpoints + 1e-6m.
- For one pipe, calculate the inclusion boundary of the other pipe end on the perpendicular bisector and evaluate both sides.
- For multiple pipes, the starting point is the minimum enclosing circle, the endpoint average, the center of the bounding box of the endpoints, and the old center.
  Search by shifting 0.005/0.02/0.06/0.15/0.35/0.75/1.5/3 times the radius in 24 directions,
  Refine around improved centers using step scales 0.12/0.04/0.012/0.004.
- Candidates containing unscheduled unreplaced pipes will be rejected. Using the surface of the physical total containment pipe,
  Retain surface types from already replaced pipes in the surface cost.
- For a collection of 2 to 12 pipes, divide each pipe one by one, in x/y order, with boundaries at 1, center, and just before the last.
  two-way splits are compared. Accept a split only if it reduces actual costs by more than $1.

## G04 integration

We regenerated the 23,707 lines of G02 construction work without leaks and determined the new replacement target and expected year for each line.
Search at most 16 same-year neighboring circles, including the current circle, within 100 m.
Evaluate pairs up to 4,000 rows later and triples formed from four nearby candidates.
Require the union of replacement targets to contain at most 10 pipes.

Subtract a lower bound based on mandatory surfaces and the minimum enclosing circle from the original combined fixed costs. If less than $25 remains,
skip detailed search. Optimize the new center and additionally require actual fixed-cost savings of at least $25.
Reject candidates containing unrelated unreplaced pipes.

Let `p_i` be the F168 probability of surviving until the start of the scheduled year. Then
The probability that a circle requires construction is `1 - product(1 - p_i)`.
This approximation assumes independence; it does not establish actual independence between pipes.

```text
expected fixed-cost savings = sum(probability each original circle needs work * its fixed cost)
                 - (probability that new circle requires construction * fixed cost of new circle)
```

Accept candidates saving at least $10, in descending savings order, without reusing a circle.
Place the merged circle at the group's first row and remove its other rows; then reoptimize centers, radii, and splitting.
Final G04 contains 22,154 construction circles plus a 37,314-circle coverage suffix.
Set checks also confirmed zero new replacements and zero construction costs in the suffix.

## Corresponding implementation

The original implementation was checked against these saved local files.
Besides code that evaluates published candidate CSVs, the generation algorithm is documented below.

- `output/2026-10-28_CMS001_F168_only/generator.py`
- `output/2026-10-28_CMS001_F168_only/self_anchor_generator.py`
- `output/2026-10-28_CMS001_F168_only/protected_profile_generator.py`
- `output/2026-10-28_CMS001_F168_only/overlap_credit_generator.py`
- `output/2026-11-02_geometry_optimization/optimize_geometry.py`
- `output/2026-11-02_geometry_optimization/merge_active.py`

This document explains the saved G04 plan; it does not involve new optimization or an official submission.
