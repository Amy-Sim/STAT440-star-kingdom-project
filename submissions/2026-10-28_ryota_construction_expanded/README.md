# Expanded same-year mergers — public display $77.22M

The user supplied a score screenshot showing **$77.22M**, versus the prior best**$77.07M**:**+$0.15M** using rounded displayed values. From the original $76.91M
plan, the cumulative displayed gain is $0.31M. Private performance is unknown.
CSV hashes and evidence provenance are in [official_results.json](official_results.json).

## What changed from $77.07M

Leak probabilities, repair severity predictions, cost formula and merger acceptance
rules are unchanged. Only the same-planned-year search range was expanded:

| Search setting | Previous | This version |
|---|---:|---:|
| Nearest circles examined | 12 | **24** |
| Maximum center distance | 80m | **120m** |
| Maximum CSV row separation | 160 | **320** |
| Maximum union of original contained pipes | 12 | 12 |

An additional **226 pairs** were merged, reducing**19,578 circles to 19,352**.
The previous 260-merger plan is the baseline; no model mixing or risk re-ranking
is introduced. The merged circle goes at the earlier row, the later row is removed,
and other circles retain relative order.

9,118 pairs were geometrically evaluated, 254 passed the savings filters, and 226
non-overlapping pairs were selected. All pipes contained in either original circle
must remain contained. Candidates newly containing live pipes scheduled for the
same or a later year are rejected. Fixed and expected leak-adjusted savings must
be positive. Detailed acceptance rules match the [previous version](../2026-10-28_ryota_construction_savings/README.md).

## Executed results

| No-future-leak result | $77.07M baseline | This version |
|---|---:|---:|
| Construction | $180,425,969.20 | **$180,290,222.26** |
| Finish year | 2045 | 2045 |
| Circles | 19,578 | **19,352** |

Additional construction saving is **$135,746.94**. All baseline-covered pipes remain
covered. No replacement year is delayed in the no-future-leak schedule; 155 pipes
are advanced. Relative to the $76.91M plan, cumulative construction savings in that
scenario are $374,384.27, with 486 merger operations across both stages.

In 30 common-random-number trials for each of two hazard models at multipliers
0.5/1/2, all six conditions improved mean construction cost and mean score.
Mean score gains versus the $77.07M CSV ranged from **$0.110M to $0.174M**.
These are model-conditional estimates, not official scores or private guarantees.

"Same year" and "no delayed pipes" refer to the **no-future-leak planned schedule**.
Future leaks change timing in both plans. The public gain cannot be attributed
entirely to construction without a complete like-for-like public cost analysis.

Inherited coverage qualification: all active iron is covered, but the scored
baseline's geometric omission of some historical repaired original iron is not
supplemented. Shared validation explicitly uses active iron; strict all-original
geometric compliance is not claimed.

## Artifacts and reproduction

- [Submitted CSV](outputs/submission_construction_expanded.csv)
- [226 new mergers](outputs/merges.csv)
- [Score screenshot](outputs/official_score_77_22m.png)
- [User-provided annual table](outputs/official_annual_table_77_22m.png)
- [Simulation comparisons](outputs/comparison.csv) and [original report](outputs/report.json)
- [Integration checks](outputs/integration_validation.json)

Install the root requirements. Uses repository `data/` and the frozen prediction
helpers in `submissions/2026-10-28_ryota_early3/`:

```sh
python -m unittest discover -s submissions/2026-10-28_ryota_construction_expanded -v
python submissions/2026-10-28_ryota_construction_expanded/expand_construction.py --sims 30
```

Reproduction overwrites this folder's local outputs. Use a new dated folder for
new experiments. The packaged generator differs from the executed local source
only in import/input/output paths. Submitted bytes and the baseline hash match.
Cost-model version is `2026-10-26-area-exponent`.
The original pre-submission report retains its null official-score field; the
subsequent user-reported public result is recorded in `official_results.json`.
