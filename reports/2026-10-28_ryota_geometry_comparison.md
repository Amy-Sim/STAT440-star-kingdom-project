# Ryota: 3 comparisons of circle integration, skip countermeasures, and reduction, highest display $77.29M

**All three versions are separate experiments based on the original $77.22M exploration extension. They are not stacked in order.**
Geometry and acceptance rules were varied to assess construction savings while keeping leak and repair-cost forecasts fixed.

| Version | Baseline | Main change | Circles | Displayed public score | Difference from baseline (displayed) |
|---|---:|---|---:|---:|---:|
| Criteria: Same year integration exploration expansion | — | Highest score until last time | 19,352 | $77.22M | — |
| 3 circle simultaneous integration | $77.22M | 24 pairs of 3 circle integration | 19,304 | $77.21M | −$0.01M |
| Stricter skip conditions | $77.22M | Exclude candidates that are likely to become empty circles, adopt 9 pairs | 19,334 | $77.22M | Same value on display |
| **Reducing subsequent circles** | $77.22M |**Reducing 81 circles, preserving number and order** |**19,352** |**$77.29M** |**+$0.07M** |

Public value is based on user-provided submission screen and file correspondence confirmation. Click here for evaluation site
These were not independently fetched. Scores display to 0.01M, so identical displays need not mean exact ties.
Private evaluation is unconfirmed. I saved the submitted CSV, score image, annual breakdown image, and SHA-256 in each folder.

## 1. 3 circle simultaneous integration

Evaluate 2,570 candidate triples of existing multi-pipe circles and accept 24. Five groups saved costs only as triples; no pair
combination saved fixed costs, whereas the triple did.
No-leak costs fell by $31,274.70, but the displayed public best did not improve.
Under high-leak simulations, some settings increased mean construction costs because merging lost opportunities for free skips of original circles.

[Submission/Method/Results](../submissions/2026-10-28_ryota_circle_triples/README.md)

## 2. Stricter skip conditions

Calculate a conservative upper bound on the empty-circle probability without assuming independent pipe leaks.
Require at most 10% empty probability per circle, at most 15% for any member of a group becoming empty, and a conservative fixed-savings lower bound of at least $25,
Required under all conditions of 2 models x hazard 0.5/1/2 times. 19 candidates were excluded and 9 were selected.
No-leak savings were $3,171.74. The displayed public score matched the baseline, so no improvement was confirmed.

[Submission/Method/Results](../submissions/2026-10-28_ryota_skip_guard/README.md)

## 3. Reduction of subsequent circle: highest point this time

Process circles in execution order; recalculate later circles after excluding pipes already covered by earlier circles.
Confirm no new unreplaced pipes, unchanged per-row replacement targets, and preserved cumulative coverage of all original
coverage must be maintained. Even historically replaced pipes must remain covered if no earlier circle has covered them;
were not removed from coverage unconditionally.

81 Shrink the circle, keeping the number and order of circles. In the future with zero leak, construction costs will be reduced.
From $180,290,222.26 to **$180,205,924.17, a reduction of $84,298.09**.
Under the same conditions, no pipe was delayed and 102 were advanced. The displayed public score reached a new best of **$77.29M**.
In the user-provided annual breakdown images, repair counts and repair costs match the original baseline, and
The public improvement is consistent with the construction savings.

[Highest score submission CSV](../submissions/2026-10-28_ryota_shrink_after_work/outputs/submission_shrink_after_work.csv)
/ [Method, validation, and reproduction](../submissions/2026-10-28_ryota_shrink_after_work/README.md)

## Verification reservations

Original coverage and budget-feasible completion were verified without future leaks. Future leaks can change work timing, so
This does not guarantee unchanged replacement years in every future scenario. Treat the model-conditional simulations and
Record official displayed scores separately.
The baseline's missing geometric coverage for historically replaced original iron is documented in each README and
The validation JSON explicitly distinguishes active-iron validation from full original-iron coverage.
