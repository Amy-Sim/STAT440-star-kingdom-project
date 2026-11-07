# STAT 440 – Star Kingdom Pipe Replacement

## Final selected plan: G17

**G17 is the final choice**, based on confidence in the plan. Recorded public score: **$79,168,928.88**.

[Final CSV](docs/reports/2026-11-02_regional_optimization/G17/G17_single_merge.csv) · [Method and evidence](docs/reports/2026-11-02_regional_optimization/G17/README.md)

The dated reports below preserve historical comparisons. Their earlier recommendations and later public-score records do not change the G17 selection.


[October 30: three submitted plans — best public $77.46M (integrated coverage)](reports/2026-10-30_submission_comparison.md)

[October 28th: Comparison of Ryota latest 3 editions/highest score $77.29M (reduced by 81 circles)](reports/2026-10-28_ryota_geometry_comparison.md)

[October 28: Ryota Search Expansion Version $77.22M (Integrated 226 additional pairs from $77.07M version)](reports/2026-10-28_ryota_construction_expanded.md)

[October 28: Ryota construction cost reduction version $77.07M (integrated 260 neighboring circles from $76.91M version)](reports/2026-10-28_ryota_construction_savings.md)

[October 28: Ryota Initial 3-year focused version $76.91M (Submitted CSV/Reproduction code/Verification results)](reports/2026-10-28_ryota_early3.md)

[Integrated list of submitted models, scores, and reproduction materials (October 26th session)](reports/2026-10-27_submitted_models.md)

## Project description — updated October 14, 2026

Star Kingdom has a natural gas network of approximately 43,000 iron, copper, brass and polyurethane pipes. The project replaces every iron pipe with polyurethane during **2027–2051**, using**$10 million per year for 25 years**. We choose circular work areas and their execution order to prevent costly leaks and reduce earthwork costs.

The supplied data comprise `pipes.csv` and leak history for **2019–2026**. The assignment calls the historical file `costs.csv`; this repository stores the leak history as `data/train.csv`.

Submit a **headerless CSV**, one circular work unit per line, in the form `"(x, y)",r`, with coordinates and radius in metres. Every original iron pipe must be wholly inside at least one circle. Executed work units replace every currently non-polyurethane pipe wholly inside them, including copper and brass. Work runs in CSV order, subject to the annual budget and carryover; it stops at the first unaffordable unit each year.**Score = $250 million − work-unit costs − leak repair costs during 2027–2051.** Plans are rejected if they cannot complete within the project window or leave iron pipes unreplaced. Historical and future leak repairs replace the affected pipes with polyurethane; empty or polyurethane-only work units are skipped at zero cost.

### Public and private evaluation

- During the competition, the leaderboard uses the **public testing set**, representing one version of future leaks.
- At the end, submissions are re-scored on the **private testing set**, representing another version of the future. Public and private sets are independent and identically distributed conditional on the training set.
- You may submit multiple solutions and withdraw submissions. Your mark uses the **private score of the submission with the highest public score**. A public improvement does not guarantee the same private improvement.

### Competition rules

- **Do not augment the provided data with data from outside sources.**
- Outside code is allowed only when you have the right to use it, such as public-domain or appropriately licensed open-source code.

The [full supplied assignment description, updated October 14](docs/assignment_2026-10-14.md) records the detailed submission, cost, evaluation and competition rules. The implementation notes below provide additional project guidance; the assignment specification remains authoritative.


Historical source-code hash receipts refer to their original publication snapshots in Git history. Translated comments and reports can have new hashes; raw inputs, model outputs, and submitted CSVs retain their original bytes.

## Layout

```text
data/                 pipes.csv, train.csv (leak history 2019–2026). Don't edit these.
feature_engineering/  scripts that build, verify and document the extra columns in data/train_predict_cost.csv
notebooks/            exploration and model work, one folder per person (First_Last)
submissions/          submission CSVs, named YYYY-MM-DD_description.csv
```

Setup: create a `.venv` and install the packages in `requirements.txt`.

The assignment calls the historical leak file `costs.csv`; our project uses `train.csv`. Confirm that these refer to the same supplied data.

## Submission format

Submit a CSV with **no header**, one work unit per line:

```csv
"(1234.5, 6789.0)",25.0
```

- Coordinates and radii are in **metres**.
- Each work unit describes a **closed circle**, so the boundary counts as inside.
- Every original iron pipe must be **wholly inside at least one submitted circle**.
- When a unit executes, every currently non-polyurethane pipe wholly inside its circle is replaced, including copper and brass.
- A pipe that only intersects the circle is not replaced.
- For straight pipes, check that **both endpoints** are inside. Checking only the midpoint is insufficient.
- Validate coverage again after exporting the CSV, accounting for numerical precision.

## Current experiment rules — October 26 correction

Use the corrected formula below for all new experiments. [Current rules and migration](docs/current_rules.md) supersede the cost formula in the archived October 14 specification. The merged team rebuild is in `submissions/2026-10-26_after_second_bug 2/`. Earlier plans and validation JSON are historical artifacts: revalidate or rebuild into a new dated directory before comparing them.

## Work-unit cost

| Component | Rate |
| --- | ---: |
| Groundbreaking | $100/work unit |
| Grass | $3/m² |
| Farm | $7/m² |
| Swamp | $12/m² |
| Road | $17/m² |
| Structure | $50/m² |
| Water | $32/m² |
| Replacement length | $200/m |

For a circle with radius `r`:

```text
area = pi * r²
surface_rate = sum of rates for distinct surface types among all wholly contained pipes
replacement_length = total length of currently non-polyurethane wholly contained pipes

cost = round_to_cents(
    100 + surface_rate * area^0.85 + 200 * replacement_length
)
```

### Important cost details

- Count each surface type **once**, regardless of the number or length of pipes.
- Apply the combined surface rate to the **whole circle area**.
- For example, grass and road give a rate of `3 + 17 = 20`.
- Surface types are counted from **all wholly contained pipes**, including polyurethane pipes and pipes already replaced by leaks or earlier work units.
- Only currently non-polyurethane pipes contribute the $200/m term.
- Overlapping circles must not charge replacement length twice.
- If a circle contains no pipes or only currently polyurethane pipes, it is **skipped at zero cost**, including no groundbreaking charge.
- Round each executed work unit's final cost to cents. Use consistent rounding and avoid floating-point budget errors.

## Budget and execution

1. At the beginning of 2027, start with $10M.
2. Execute work units in CSV order. Execution is instantaneous.
3. If the next unit would make the budget negative, stop work for that year. **Do not skip ahead to a cheaper unit.**
4. Carry the remaining budget forward and add $10M at the beginning of the next year.
5. Resume from the blocked unit, recalculating its cost using the current pipe materials.
6. Continue through 2051.

A unit costing exactly the available budget can execute. A unit costing more than $10M may execute after budget accumulates.

The specification is rejected if it cannot finish within the 25-year window or if the required iron replacement and coverage conditions are not satisfied.

Surplus uses the full **$250M allocation**, even if work finishes early. Under the stated rules, repair costs are deducted separately from the score rather than from the construction budget.

## Things to know

- **Order affects both repair costs and work-unit costs.** A pipe that leaks before scheduled replacement becomes polyurethane, reducing later replacement length and sometimes causing a unit to be skipped.
- Pipes that leaked in `train.csv` are already polyurethane when the project starts. `pipes.csv` records their original material.
- Keep original material and current material in separate fields.
- During the project, a leak incurs a repair cost and the pipe is then replaced by polyurethane.
- Evaluate leaks throughout **2027–2051**, even if scheduled work finishes early.
- Every currently non-polyurethane pipe fully inside a circle is replaced and charged $200/m. Avoid unnecessary copper and brass replacement when it increases total cost.
- One structure or water pipe can make a large circle expensive because its surface rate applies to the whole area.
- The `0.85` exponent and $100 charge can favour grouping, but larger circles may add area, expensive surface types and extra replacement length. **Fewer, bigger circles are not always cheaper.**
- Prioritize expected **avoidable repair cost**, using both leak probability and repair severity.

Confirm any unspecified details with the instructor or official evaluator, especially the ordering of leaks and work at exactly the start of a year and whether all pipe geometry is represented by straight segments.

## Baseline

Start with one circle per original iron pipe.

For a straight pipe:

```text
centre = midpoint of the two endpoints
radius = half the pipe length
```

Use a small, documented numerical margin if necessary, then recheck containment.

This gives geometric coverage, but **budget feasibility must still be checked**. Baseline circles can contain other pipes, including copper, brass and expensive surface types.

Order the baseline using estimated avoidable repair costs, then evaluate it with the simulator.

## Scorer and validation — first priority

Build the cost function, simulator and validator before optimizing circles.

Check:

- Full containment, boundary cases and overlapping circles.
- Distinct surface counting, including surfaces from polyurethane pipes.
- Historical leaks and material status at the start of 2027.
- Project-window leaks and their effects on later costs.
- Zero-cost skipped units.
- Exact-budget execution and budget carryover.
- Stopping at the first unaffordable work unit.
- Complete geometric coverage of every original iron pipe.
- Completion by 2051.
- Correct parsing and validation of the exported submission CSV.

For each candidate, report:

- Total work-unit costs.
- Estimated repair costs.
- Estimated score.
- Completion year.
- Uncovered iron count.
- Model/data version and random seed.

Unknown future leaks mean our score is an **estimate**, not the official future score. Compare candidates using the same leak scenarios and record uncertainty.

Also run a no-future-leak simulation as a construction-budget check.

## Data and backtesting

- Preserve pipe IDs as strings.
- Check duplicate records, missing values, dates, units and material/surface labels.
- Verify joins between `pipes.csv` and `train.csv`.
- Keep raw data unchanged.
- Fit models on **2019–2023** and evaluate on**2024–2026**.
- Reconstruct pipe status at each cutoff using only information available at that time.
- Do not use future leaks, future repair costs or future replacement status as training features.

Historical backtesting evaluates predictions. It does not directly observe the score of a proposed 2027–2051 replacement plan.

## Roles

| # | Role | Person |
| --- | --- | --- |
| 1 | Data cleaning and exploratory analysis | |
| 2 | Leak probability model (per pipe, per year) | |
| 3 | Leak cost model and backtest (fit on 2019–2023, test on 2024–2026) | |
| 4 | Cost function, scorer and validator (**first priority**) | |
| 5 | Circle design (grouping pipes cheaply) | |
| 6 | Ordering within the budget, final submission | |

## Steps

1. **Week 1:** everyone reads the specification. Build the scorer and validator, clean the data, and make a simple leak-risk estimate.
2. **Week 2:** create a baseline submission, check coverage and budget feasibility, and estimate its score.
3. **Weeks 3–4:** improve the risk model, circles and ordering. Keep changes supported by validation that outperform the best candidate so far.
4. **Week 5:** pick the final submission, have someone else independently recheck the exported CSV, and write the report.

Work on branches and open pull requests into `main`.

Record each candidate's method, model/data version, random seed, costs, completion year and validation result so results can be reproduced.


## Data handling reminders

- Treat both `cast iron` and `wrought iron` as iron replacement targets. Check the actual material labels before filtering.
- Keep missing materials as unknown; do not assume these pipes are polyurethane or exempt from replacement. Confirm how they should be handled.
- For pipes replaced after historical leaks, the original `Lay date` is not the installation date of the replacement polyurethane pipe.
- EDA surface maps show estimated regions, not measured land boundaries. Calculate work-unit surface costs from the labels of wholly contained pipes, not map colours or area proportions.

[Exploratory data analysis](notebooks/EDA/EDA.md).

## 2026-10-05 — Cost feature data extension

Today, 501 candidate columns were appended to `data/train_predict_cost.csv`
(14,107 rows; 536 total columns), preserving all original columns/values/order.
Added candidates include prior-year repair costs/state, spatial geometry and
endpoint-based route/straight-section groups for macro leak analysis. Raw inputs
remain unchanged. Full definitions, limitations and rebuild instructions are in
[the dated addendum](data/train_predict_cost.md#2026-10-05--added-candidate-features-and-inferred-pipe-routes), and
[the feature dictionary](data/train_predict_cost_feature_dictionary_2026-10-05.md).

## Takito latest model — 26 October 2026

[Model and experiment report](reports/2026-10-26_takito_latest_model.md) · [21a submission and reproducible evidence](submissions/2026-10-26_best20a_catboost_logrf/). The user confirmed that the screenshot’s Takito **$74.78M** result belongs to**21a**. Evaluator-version comparability is qualified in the report.
