# Radius prediction by pipe and value prediction of circle candidates: Comparison of stacking

G17 held the highest existing public score at $79,168,928.88. The user explicitly authorized one submission per method for comparison, even with worse internal results, provided coverage, budget, and deadline requirements passed. The best existing submission was retained.

|Candidate|Origin and method|Public score( dollars)|Difference from G17( dollars)|Mean internal difference( dollars)|Internal settings with positive mean gain|
|---|---|---:|---:|---:|---:|
|G20|User: per-pipe radius prediction|74,260,900.63|-4,908,028.25|-6,171,269.62|0/24|
|G21|Codex: candidate-circle value prediction and updates|64,958,612.21|-14,210,316.67|-15,882,357.23|0/24|

## Two methods implemented

The 166 pipe/neighborhood features include other-pipe counts/lengths by material and surface within 25/50/100/250 m, replaced fractions, coordinates, pipe length/orientation/age, CMS001 costs, and F168 probabilities. Official public annual breakdowns were not used to construct training targets.

The radius method compares circles enclosing 1/2/4/8 neighboring pipes with existing circles; the radius with the best local expected cost is the learning target. Stacking predicts per-pipe radius multipliers. Pipes are processed in the original priority order, using circles that contain both endpoints. Centers are selected from the midpoint and several perpendicular offsets; replaced pipes are skipped. Overly expensive circles fall back to single-pipe circles.

The candidate-value method uses 186 features: the same neighborhood inputs plus 20 circle-specific features, including radius, center displacement, contained pipes, all surfaces, replacement length, predicted costs, and probabilities. Stacking predicts local work value and ranks candidates within scheduled-year groups. Each acceptance updates neighboring candidates' unreplaced pipes, lengths, and remaining values. Remaining value approximates the initial prediction using the unreplaced-risk fraction; the stack is not retrained at every step. Overly expensive circles fall back to single-pipe circles.

Both methods retain all existing circles as a suffix. The construction prefix replaces the original plan's entire target set, so the suffix contains only replaced pipes and meets geometric coverage at zero cost. The exported CSV was reloaded and checked for complete iron coverage, annual budget and carryover, and completion by 2051.

## Learning and evaluation

Base models are ExtraTrees, HistGradientBoosting, and standardized Ridge. Ridge combines three-fold OOF predictions split by 500 m cells.
Extensions add a lightweight MLP (32 → 16 hidden units, at most 10,000 training rows and 100 iterations, with early stopping) plus a 64-component Nyström RBF approximation with Ridge. Standardization is fitted within each training split.
Final neural networks contain 5,889 radius-model parameters and 6,529 candidate-value parameters. The radius network stopped after 59 iterations; the candidate-value network reached its 100-iteration cap, so convergence is unconfirmed. Neural networks and kernels were added together; public differences cannot be attributed to neural networks alone.

The northeast region was held out, with training locations at least 500 m from its boundary. This measures approximation to local targets derived from existing forecasts, not independent accuracy on future construction costs. Final models were then fitted across all regions.

Targets compare expected costs of grouped construction in the scheduled year with individual-pipe work three years later. The later single-pipe surface cost approximates only that pipe's surface and minimum radius; it is not an observed optimal-plan target. Both this approximation and conversion of local values into a budget-constrained global plan introduce error.

Compare the frozen CSVs against G17 across 24 settings: two forecast families, three leak rates, two cost-dispersion levels, and two regional-correlation levels, each with 128 common-random-number scenarios (3,072 total). G05 is a legacy internal reference-arm key; the actual comparator is G17, as recorded in the protocol.

## Conclusion

These results do not rule out stacking in general. Learning local approximations to radii or candidate values need not outperform existing geometry optimization and work ordering that account for budgets and leaks. Consider public and internal results together.

The folder contains submission CSVs, fitted models, generation code, feature lists, held-out-region approximation metrics, full-plan simulation summaries, and official annual breakdowns.

Official breakdown [G20](http://172.16.42.11:51238/static/output/8knotyeCJ3SEPEdPhLtmrZGd.txt)

Official breakdown [G21](http://172.16.42.11:51238/static/output/PDX7_pow07eh5Yl368C3gaz9.txt)
