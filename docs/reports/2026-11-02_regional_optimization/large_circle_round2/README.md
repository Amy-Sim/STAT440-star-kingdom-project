# Comparison of large construction circles based on G05

Public's highest is **$79,168,805.32 for G08**. This was an improvement of $17,992.74 from G05 and $177,837.07 from G04. Since the selection criteria for internal evaluation has also been passed, the current final submission candidates will be updated to G08.

## Official submission results

|Candidate|Public score( dollars)|Gain over G05|
|---|---:|---:|
|G04|78,990,968.25|−159,844.33|
|G05|79,150,812.58|0.00|
|G06|79,150,351.83|−460.75|
|G08|79,168,805.32|+17,992.74|
|G07|79,167,182.01|+16,369.43|

The total repair costs for G08 and G07 are the same: $31,128,534.04. The difference between the two was $1,623.31 in construction costs. Improvements to G08 over G05 cost $13,369.96 in construction and $4,622.78 in repairs. The annual breakdown was saved from the official output of the submission site.

## What I changed this time

Expand neighbor searches to 250/350/500 m and consider up to 24 circles/64 pipes. These are computational search limits, not requirements to use large circles. Actual radii cover target endpoints while centers minimize surface costs. Density, pipe lengths, and surfaces determine locally accepted group sizes.

G07-G09 will be integrated within the same scheduled year. For G10 and G11, we also looked into neighboring circles whose planned years differ by 1 or 2 years. The latter adds ``repair costs that could be prevented by bringing them forward'' to the savings in construction costs, and subtracts ``the loss of the opportunity to eliminate the need for construction due to natural leak replacement.'' G12 further adopted only the integration that lowers the local expected cost in both types of predictions. The final annual budget deviation was evaluated through a simulation of the entire plan.

## Adoption conditions for internal evaluation

Fix G05 as comparator and use 24 settings: two leak/cost forecast families, three leak rates, two repair-cost dispersions, and two regional leak correlations. Only candidates passing development with 48 seeds per setting proceed to confirmation using 128 separate seeds per setting (3,072 scenarios).

Acceptance requires positive mean gains in all 24 settings, coverage/budget/deadline feasibility in every scenario, and positive lower bounds of Monte Carlo 95% mean-gain intervals in both forecast families, on both random-number sets. These intervals reflect simulation randomness, not guaranteed private scores.

|Candidate|Search radius / year gap|Observed merged-circle count|Maximum new merged-circle radius|Confirmation mean gain vs G05|Worst mean gain across 24 settings|Accepted|
|---|---|---|---:|---:|---:|---|
|G07_wider250|250m / 0 years|2〜5 (range)|33.36m|+26,750.85 dollars|+17,737.21 dollars|Accepted|
|G08_adaptive350|350m / 0 years|2〜6 (range)|33.36m|+29,092.05 dollars|+19,291.46 dollars|Accepted|
|G10_neighbor_year350|350m / 1 years|2〜12 (range)|74.71m|Unconfirmed|Failed development gate|Not submitted|
|G11_neighbor_year500|500m / 2 years|2〜23 (range)|74.71m|Unconfirmed|Failed development gate|Not submitted|
|G12_robust_year500|500m / 2 years|2〜16 (range)|74.71m|Unconfirmed|Failed development gate|Not submitted|

G09_adaptive500 and G08_adaptive350 have exactly the same SHA256 of CSV. Do not submit duplicates because they are the same plan.

## Submitted file

- [G08_adaptive350](submit/G08_adaptive350.csv): Passed internal evaluation recruitment conditions.
- [G07_wider250](submit/G07_wider250.csv): Passed internal evaluation recruitment conditions.

## Interpretation of results

Whether a larger circle helps depends on additional surface costs and lost opportunities to skip small circles at zero cost. Increasing radius or group-count limits does not force large circles when no economical candidate exists. Public annual breakdowns record results only; they are not inputs to candidate leak/cost forecasts.

Inputs and calculations are documented in `round2_protocol.json`, `round2_*_by_setting.csv`, candidate `*_moves.json`/`*_report.json` files, and generation code. The supplied pipes.csv/train.csv and existing CMS001/F168 predictions were used.

![Verification simulation comparison](confirmation_comparison.png)

Official breakdown: [G08](http://172.16.42.11:51238/static/output/Plxjzj67LjZYhTrIKJwaLeM8.txt) / [G07](http://172.16.42.11:51238/static/output/ysr21yEQwIJVyt_wksJdOUBY.txt)
