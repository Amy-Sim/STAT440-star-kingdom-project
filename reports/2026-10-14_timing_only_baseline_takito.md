# Timing-only baseline on October 14 by Takito

10/14 By Takito · 2026

This baseline replaces iron pipes individually, prioritizing pipes with the highest predicted probability of leaking in 2027.

- We created one circle for each of the **38,455 original iron pipes**, centered at its midpoint, with a radius equal to half its endpoint length plus a**0.000001 m numerical margin**.
- Circles are ordered by **2027 leak probability, highest first**. Ties use Pipe ID, and the**9 iron pipes with missing predictions go last**.
- We used the selected **equal-weight ensemble of XGBoost, CatBoost, and LightGBM**, with the confirmed zero-leak rules applied.
- The model predicts annual leak probability rather than an exact leak date. Higher probability is used as a proxy for earlier leakage.
- Iron pipes already replaced after historical leaks are included to satisfy the coverage requirement, but are not replaced again. Work units containing only polyurethane pipes are skipped at no cost.
- Any unreplaced copper or brass pipes wholly inside a circle are also replaced, as required by the rules.
- **No predicted repair costs, construction-cost weighting, or pipe grouping are used to determine priority.**

## Results

| Item | Result |
| --- | --- |
| Priority rule | Predicted 2027 leak probability, highest first |
| Submitted circles | 38,455 |
| Uncovered original iron pipes | 0 |
| Construction cost, assuming no future leaks | $149.21 million |
| Completion year, assuming no future leaks | 2041 |
| Work units skipped at no cost | 16,368 |
| Remaining allocation, assuming no future leaks | $100.79 million |

The exported CSV was read back and checked for full endpoint coverage and construction-budget feasibility. Exact construction cost was **$149,211,442.76**.**The remaining allocation excludes future leak repair costs and is not directly comparable with the scores in the October 13 experiment table.** No claim of superior realized score is made.

Nine iron pipes have unknown probabilities and are placed last, not assigned zero. Eight pipes with unknown material have no target circles and remain uncovered; their treatment requires clarification if they are deemed iron. Overlapping circles can replace another pipe before its own listed circle, so realized pipe replacement order can differ from the target order.

## Files and reproduction

- [Submission CSV](../submissions/2026-10-14_timing_only_baseline.csv) — no header, center and radius only.
- [Validation results](../submissions/2026-10-14_timing_only_baseline.validation.json).
- [Order audit](../submissions/2026-10-14_timing_only_baseline.order_audit.csv) — pipe IDs, probabilities, and circle geometry; not a submission file.
- [Builder](../src/build_timing_only_baseline.py). From the repository root, run `python src/build_timing_only_baseline.py` with numpy and pandas installed.

Source files are pinned to commit `58fd8a5b4b3f8b5365c525b0156163ece60a8100` for this result. The builder uses the checked-out source files; rerunning after those files change is a new result. Input and submission SHA-256 hashes are recorded in the validation file.
