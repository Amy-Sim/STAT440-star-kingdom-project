# Takito 21a — latest repair-cost model and plan

Read the [full report](../../reports/2026-10-26_takito_latest_model.md) for method, results, limitations, credits and reproduction.

Candidate: `21a_20a_catboost6863_logrf3137.csv` (36,375 circles). Repair-cost stack: Takito CatBoost 68.627% + Anthony corrected log RF 31.373%. Geometry and p17b probabilities are frozen from 20a; execution order changes.

The user's screenshot shows Takito **$74.78M**, and the user confirmed that this is the result of**21a**. Local validation files use the historical local formula and no future leaks; see the report's evaluator-change note.

Portable reproduction: `python submissions/2026-10-26_best20a_catboost_logrf/reproduce.py` from the repository root. Dependencies: `requirements.txt`. Frozen base predictions and coefficients allow the severity forecast to be recomputed; historical tables support the report's model comparison. Original workspace code is retained for provenance and is not the portable entry point.
