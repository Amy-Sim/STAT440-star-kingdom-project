# Ryota: construction-cost reduction — public display $77.07M

The user supplied a screenshot showing **$77.07M**, versus the previous best**$76.91M**:**+$0.16M** using the rounded display. The submitted CSV and screenshot
are preserved with SHA-256 hashes in [official_results.json](official_results.json).
This is user-reported public evaluation evidence; private performance is unknown.

## Exactly what changed from the previous best

| Item | Previous best | This submission |
|---|---|---|
| Public display | $76.91M | **$77.07M** |
| Circle count | 19,838 | **19,578** |
| Circle geometry | Previous submitted circles | **260 pairs merged** |
| Leak probabilities | Fine-age model | **Unchanged** |
| Repair severity predictions | Material/surface means | **Unchanged** |
| Priority strategy | Initial-three-year risk/cost | **Unchanged; no new risk re-ranking** |
| Placement of merged circles | — | Earlier original row; later row removed |
| Other circle order | Original | Relative order preserved |

The baseline is the exact scored file
[`early3_adaptive.csv`](../2026-10-28_ryota_early3/outputs_early3/early3_adaptive.csv).
The new file is [`outputs/submission_construction_savings.csv`](outputs/submission_construction_savings.csv).

## How the 260 mergers were chosen

1. Execute the baseline with no future leaks to assign planned construction years.
2. Search nearby circles in the **same planned year**, within 80m and 160 CSV rows.
   Inspect up to 12 nearest circles per anchor.
3. Build a circle containing every pipe wholly contained in either original circle.
   Recompute containment, all distinct surface types, and replacement costs.
4. Reject newly included live pipes scheduled for the same or a later baseline year.
   Reject pairs without positive fixed construction savings and positive estimated
   savings after accounting for possible future empty-circle skips.
5. Select non-overlapping pairs by estimated savings. Preserve every other circle's
   relative order. Re-read the exported CSV and verify coverage and replacement years.

7,237 candidate pairs were geometrically evaluated; 289 qualified and 260 were selected.
The maximum union of original contained pipes considered was 12. These are local
pair mergers of already multi-pipe circles, not a global optimum.

The current cost formula is
`100 + surface_rate * area**0.85 + 200 * unreplaced_length`, rounded to cents.
Surface types of already replaced pipes still count. Cost-model version:
`2026-10-26-area-exponent`.

## Executed checks and results

| No-future-leak result | Previous best | New |
|---|---:|---:|
| Construction | $180,664,606.53 | **$180,425,969.20** |
| Finish year | 2045 | 2045 |

**Construction saving: $238,637.33** in this deterministic scenario.
All pipes covered by the baseline remain covered. No baseline pipe's replacement
year is delayed in this scenario; 189 are advanced. Both new unit tests pass.

In 30 common-random-number trials per condition, both the fine-age and older-age
hazard models at multipliers 0.5/1/2 produced positive mean construction savings
and positive mean total score gains. Mean score gains ranged from about **$0.131M
to $0.299M**. See [comparison.csv](outputs/comparison.csv) for all conditions and
[SUMMARY.md](outputs/SUMMARY.md) for the original local experiment description.
Conditional Monte Carlo intervals do not measure model error or guarantee private results.

The public score gain is **not** an independently measured public construction-cost
saving: only the score screenshot is available for this submission. Actual repair
costs may also change as budget savings advance work.

## Timing and inherited coverage limits

"Same year" and "no delayed pipes" refer to the baseline **no-future-leak** schedule.
Actual future leaks can change execution years in both plans. No claim is made that
every individual pipe is never delayed in every possible future.

The previous scored submission covered every initially unreplaced iron pipe but
did not geometrically cover all historically repaired original iron. This submission
preserves its covered set and does not add historical-coverage circles. The shared
validator is therefore run with an explicitly labelled active-iron mask; it is not
reported as passing strict all-original-iron geometry. See the validation JSON.

## Reproduce

Uses repository `data/` and the frozen modules in
`submissions/2026-10-28_ryota_early3/`. No data or predictive-model change is needed.
Install the root requirements, then:

```sh
python -m unittest discover -s submissions/2026-10-28_ryota_construction_savings -v
python submissions/2026-10-28_ryota_construction_savings/reduce_construction.py --sims 30
```

Reproduction writes this folder's outputs. For a new experiment use a new dated
folder, preserving the scored CSV and report. Code integration changes only input,
output and import paths; exported submitted bytes match the local scored artifact.

`outputs/report.json` preserves the pre-submission experiment record, including its
original null official score. The later public result is in `official_results.json`.
