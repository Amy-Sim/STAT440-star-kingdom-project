# 10a: nearby-pair grouping from 09a

Submit only `10a_09a_nearby_pairs.csv`, unchanged. This is a local experimental identifier, not an existing team candidate registration.

Reference: GitHub 09a_full_ensemble_net.csv, SHA256 3c871b165901564653cd1acb56cbfbd0df7f943eaf1ef733e55aa9ca20d7c1c2. Source matches the published validation hash. Original reference CSV is preserved under source/.

| Metric | 09a | New grouped candidate |
| --- | ---: | ---: |
| Work units | 38,455 | 37,799 |
| No-future-leak construction cost | $152,944,811.51 | $152,227,909.47 |
| Completion year, no future leaks | 2042 | 2042 |
| Uncovered original iron | 0 | 0 |

Construction saving in this scenario: $716,902.04. This is NOT an official/public score improvement or a repair-cost forecast. Public reference score is -$6.79M. The new candidate has now been evaluated; see Public evaluation below.

Method: scan 09a in order; consider pairs at most 100 positions apart and spatially close. Compute a minimum enclosing circle of endpoints of ALL pipes fully contained in either original circle (including historical replacements and copper/brass). Round to nine decimal places with a 0.000002 m radius margin. Accept pairs with initial sequential savings over $100, greedily choose the largest saving for each scanned position, and do not reuse units. Insert merged circle at the earlier position; preserve relative order of all untouched units. No models are retrained. 656 pairs were merged.

The whole exported plan is reparsed, all endpoint containment recomputed, and all 38,455 known original iron pipes checked. Budget simulation uses integer cents, half-up per-unit rounding, historical leaks as initial polyurethane, all contained surface types, current non-polyurethane length (including unknown material conservatively), zero-cost skips, annual carryover and head-of-line stopping. No future leaks are assumed. No remaining iron and completion before 2052 are asserted. Actual future leak scenarios may change scheduling and score. A no-future-leak check is not proof for every possible future leak path.

Independent verification checks each merged circle against every pipe without the spatial grid and confirms it preserves everything covered by its original pair. Untouched circles match 09a exactly. See independent_check.json. See the submission validation JSON for annual budget balances, costs and CSV hash; pair_merges.csv lists original ranks and initial estimated pair savings. Pair savings do not simply sum to full-plan savings because circles overlap.

Run with Python containing numpy and pandas:

    python build_grouped.py
    python check_independent.py

The user submitted the CSV to the evaluator. GitHub upload is pending.

## Public evaluation — October 19, 2026

Submitted by Rion at 15:52. The evaluator displayed **-$5.98M**, compared with**-$6.79M** for reference 09a: an improvement of approximately**$0.81M**, based on displayed rounded scores. Private performance is unknown. The public improvement includes both construction and repair costs; it must not be equated with the $716,902.04 no-future-leak construction saving.

Rion conducted this experiment using Codex to generate and validate the candidate. Existing leak and repair-cost prediction models were unchanged.
