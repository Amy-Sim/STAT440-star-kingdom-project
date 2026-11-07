# Ryota: $77.07M → $77.22M in exploration expansion of same year integration

The user-provided screenshot confirms a **displayed public score of $77.22M**.**+$0.15M** over the previous $77.07M best, or**+$0.31M** over the original $76.91M plan.
Both differences use displayed scores rounded to 0.01M; private scores remain unknown.

## Changes

**We fixed the leak prediction and expanded only the search range that integrates circles with the same scheduled construction year.**

- Neighborhood candidates: 12 circle → **24 circle**.
- Upper limit of center distance: 80m → **120m**.
- Original CSV line spacing: 160 lines → **320 lines**.
- Added **226 sets** integrated. Circle count 19,578 →**19,352**.
- Same-year constraints, coverage of original target pipes, confirmation of accompanying pipes, and conditions requiring positive savings are maintained.
- The relative order of risk prediction, repair cost prediction, cost formula, and other circles is maintained.

No-future-leak construction costs fell from $180,425,969.20 to **$180,290,222.26**,**$135,746.94 reduction**. Under the same conditions, 0 pipes will be replaced later in the year, and 155 pipes will be replaced earlier.
Same-year execution and no delay describe the planned schedule, not guarantees across all possible futures.

| Stage | Displayed public score | Circles | Construction cost, no future leaks |
|---|---:|---:|---:|
| Initial 3 years emphasis version | $76.91M | 19,838 | $180,664,606.53 |
| 260 groups integrated in the same year | $77.07M | 19,578 | $180,425,969.20 |
| This time: 226 more pairs | **$77.22M** |**19,352** |**$180,290,222.26** |

The Public score difference cannot be directly treated as the construction cost difference. Budget savings accelerate construction time,
repair costs may also change. The annual breakdown for this experiment is retained as user-provided images.

## Deliverables

- [Submit CSV](../submissions/2026-10-28_ryota_construction_expanded/outputs/submission_construction_expanded.csv)
- [Method/Re-execution procedure/Reservation](../submissions/2026-10-28_ryota_construction_expanded/README.md)
- [Official display source and CSV hash](../submissions/2026-10-28_ryota_construction_expanded/official_results.json)
- [Score image](../submissions/2026-10-28_ryota_construction_expanded/outputs/official_score_77_22m.png)
- [Yearly Breakdown Image](../submissions/2026-10-28_ryota_construction_expanded/outputs/official_annual_table_77_22m.png)
- [Integrated 226 pairs](../submissions/2026-10-28_ryota_construction_expanded/outputs/merges.csv)
- [Comparative calculation](../submissions/2026-10-28_ryota_construction_expanded/outputs/comparison.csv)

2 models × hazard 0.5/1/2 times, common random number comparison 30 times each, average construction cost for all 6 conditions
Mean scores improved, with model-conditional gains of approximately +$0.110M to +$0.174M.
The baseline's geometric-coverage limitation for historically replaced iron is explicit in the README and validation JSON.
