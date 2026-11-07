# after second bug 10/26

STAT 440 — Star Kingdom Pipe Replacement
Rion | October 26, 2026

## Summary

Rebuilt experiments 09a–13a using the corrected surface-cost formula and submitted six CSVs on October 26. **The best result among these six rebuilt candidates is 13a at +$70.24M**, followed by 12a at +$69.89M. These are displayed public scores, not private scores or simulator estimates. This report does not claim 13a is the team's overall best candidate; the Google Doc also records later experiments such as 20a under earlier evaluation conditions.

## Score history

All scores and differences below are in millions of dollars (M$). “Before second fix” means the results recorded after the October 21 fix but before the October 26 formula correction. An em dash means no result was recorded, not a zero score.

| Candidate | Original record, before Oct 21 fix | After Oct 21 / before Oct 26 fix | After second bug, Oct 26: rebuilt CSV | Change from preceding recorded phase |
| --- | ---: | ---: | ---: | ---: |
| 09a | -6.79 | +64.56 | **+65.40** | +0.84 |
| 10a | -5.98 | +64.62 | **+65.78** | +1.16 |
| 11b | approximately -19.00 | — | **+51.99** | — |
| 11c | -9.69 | — | **+61.70** | — |
| 12a | +22.50 | +69.54 | **+69.89** | +0.35 |
| 13a | +23.29 | +69.60 | **+70.24** | +0.64 |**Important:** October 26 CSVs were rebuilt rather than merely rescoring the old files. For 09a, 10a, 11c, 12a and 13a, changes between phases combine evaluator changes with changed planning decisions. They cannot be attributed solely to a better algorithm or solely to the bug fix. 11b is the exception: its priority uses no construction-cost denominator, so its submission hash is unchanged; only its cost validation changed. Different evaluator versions must not be pooled for method comparisons.

The older 11b score was reported only as approximately -$19M. No post-October-21, pre-October-26 scores for 11b or 11c were found in the reviewed Doc section.

## Current comparison under the same October 26 evaluation

| Candidate | Public score (M$) | Difference vs. corrected 09a | Difference vs. corrected 12a |
| --- | ---: | ---: | ---: |
| 09a | +65.40 | +0.00 | -4.49 |
| 10a | +65.78 | +0.38 | -4.11 |
| 11b | +51.99 | -13.41 | -17.90 |
| 11c | +61.70 | -3.70 | -8.19 |
| 12a | +69.89 | +4.49 | +0.00 |
| 13a | +70.24 | +4.84 | +0.35 |

Dynamic ordering outperformed the fixed-priority variants in these public results. The grouped dynamic candidate 13a exceeded ungrouped dynamic 12a by approximately **$0.35M**. Fixed grouping 10a exceeded fixed reference 09a by approximately**$0.38M**. These are comparisons of the tested candidates, not proof of global optimality. All differences use rounded displayed scores.

## Corrected formula

    cost = round_to_cents(100 + surface_rate * (area ** 0.85) + 200 * unreplaced_length)
    area = pi * radius ** 2

Only area is raised to 0.85. Original implementations raised the product of surface rate and area to 0.85. Surface rate still counts each surface type once among ALL wholly contained pipes, including already-polyurethane pipes. Linear length charges apply only to currently non-polyurethane contained pipes. A unit containing no replacement targets is skipped for free.

## What was rebuilt?

| Candidate | Planning method | Geometry |
| --- | --- | --- |
| 09a corrected reference | Fixed initial net benefit / corrected construction cost | Same original 38,455 circles as 09a |
| 10a corrected grouping | Regenerate nearby-pair merges using corrected savings and corrected reference order | 666 pairs merged; 37,789 circles |
| 11b net benefit only | Fixed net benefit, without cost weighting | Same original circles; same CSV order as old 11b |
| 11c square-root cost | Fixed net benefit / sqrt(corrected cost) | Same original circles |
| 12a corrected dynamic | Update remaining net benefit / current corrected cost after every planned work unit | Same original circles |
| 13a corrected grouped dynamic | Apply dynamic updates to the newly grouped geometry | Exactly the corrected 10a circles |

Per-pipe net benefit remains:

    p(leak in 2027) * (predicted repair cost - 200 * pipe length)

The team’s existing probability and repair-cost predictions are unchanged. No models were retrained. The new grouping search retains the earlier proximity/rank-window/settings but selects 666 pairs rather than the old 656 because costs and priorities changed.

“Dynamic” means the order is constructed in a planning simulation before submission. Previously selected work units mark their pipes replaced, and overlapping circles have their benefits and costs updated. It does not observe actual future leaks or modify the CSV during official evaluation.

## Local construction validation

These values assume NO future leaks. They are separate from official public scores.

| Candidate | Work units | Construction cost | Completion year | Uncovered original iron |
| --- | ---: | ---: | ---: | ---: |
| 09a | 38,455 | $196,422,709.41 | 2046 | 0 |
| 10a | 37,789 | $194,881,031.96 | 2046 | 0 |
| 11b | 38,455 | $195,914,746.73 | 2046 | 0 |
| 11c | 38,455 | $195,690,242.78 | 2046 | 0 |
| 12a | 38,455 | $194,098,428.46 | 2046 | 0 |
| 13a | 37,789 | $192,591,377.43 | 2046 | 0 |

All six plans cover every known original iron pipe and complete within the 25-year construction window in this scenario. Budgets use $10M yearly allocations, carryover, integer cents, per-unit half-up rounding and stopping at the first unaffordable work unit. Historical leak pipes start as polyurethane. Overlaps, copper/brass and free skipped units are accounted for. Each exported CSV is reparsed, and merged coverage was independently checked against all pipe endpoints. See validation JSONs and REBUILD_NOTES.md for details and limitations.

## Evidence and data sources

- Google Doc: https://docs.google.com/document/d/1N32Z_DC6Frw1OYwSNA9mIlXjgDPuKiOQXH4nJV2RZcQ/edit — Part 2: Merge, read October 26. Historical score phases were copied as records, not treated as current-evaluator results.
- GitHub: https://github.com/reinesana/STAT440-star-kingdom-project — team pipes.csv, train.csv, ensemble_stable repair-cost predictions, full-inventory 2027 probabilities, and original 09a circles/audit.
- Current official results: user-provided October 26 evaluator screenshot. The user stated the submission order from oldest/bottom to newest/top as 09a → 10a → 11b → 11c → 12a → 13a. The screenshot does not display filenames; this mapping follows that stated order, not an independently observed filename/hash match.
- Original scores for 11b/11c: user reports in this chat; 11b is approximate.
- Source snapshots and SHA256 values are included for reproducibility. See rebuild_checks.json and public_score_comparison.csv.

## Files and GitHub placement

Upload the entire extracted folder under:

    submissions/2026-10-26_after_second_bug/

The six candidate submission CSVs are at the top level. Files ending `.audit.csv`, comparison CSVs, JSONs and source/ are supporting records, not evaluator submissions. This package includes the generator, validation, inputs, comparison table and public result record. Existing original files are not overwritten.

Reproduce locally with Python, numpy and pandas:

    python rebuild_corrected.py

Rion used Codex to implement, validate and document the rebuild using the team's existing data. Private performance remains unknown. No upload to GitHub or Google Doc has been performed by preparing this package.
