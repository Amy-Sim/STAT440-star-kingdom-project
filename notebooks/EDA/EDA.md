# Star Kingdom: leak costs are concentrated, and 26.2k iron pipes remain

An exploratory analysis of the gas network, historical leaks, and the starting point for the 2027–2051 replacement project.

## Executive Summary

- **Start from the repaired inventory.** The 43,039 original pipe records include 38,455 iron pipes. Every pipe recorded in train.csv is treated as polyurethane after its leak; eight unknown-material pipes remain unresolved.
- **Severity matters alongside leak probability.** The 14,113 historical leaks cost**$353.0M**. The most expensive 1% account for**45.3%** of repair dollars. Median cost is**$3,275**, far below the**$25,012** mean.
- **Original material is not a causal risk estimate.** Historical leak fractions differ markedly by material, but age, surface, location, and repair-driven removal are intertwined. The age comparison therefore includes a separate original-iron-only view.
- **Within-material unit costs vary by year.** Annual mean and median repair dollars per pipe metre are shown within each original material, together with an indexed red–blue heatmap. These nominal values are descriptive and can be moved by extreme repairs or changing surface and location mix.

## 1. Data scope and quality

The supplied files contain one row per pipe and one recorded leak per leaking pipe. All leak IDs join successfully; no duplicate pipe IDs, nonpositive lengths, or leaks preceding known installation dates were found. The brief names the leak file costs.csv; the supplied train.csv is treated as that history. The supplied competition window is used through 2026-12-31, even though it extends beyond the current real-world date. No real-world freshness claim is made.

### Missing values in source columns

![Missing values in source columns](figures/01_missingness.png)

15 installation dates and 8 materials are missing. No missing values occur in coordinates or leak-record fields. Unknown material must remain unresolved rather than silently classified as iron or polyurethane.

## 2. What is in the network?

### Original pipe materials

![Original pipe materials](figures/02_material_inventory.png)

The inventory is dominated by wrought iron. Original material is not the material remaining at the project start: historical leaks trigger polyurethane replacement.

### Material changes after historical leak repairs

![Material changes after historical leak repairs](figures/03_material_transition.png)

This reconstruction is essential before replacement planning. A leak during 2019–2026 removes that pipe from its original material's remaining inventory.

### Network inventory by surface type

![Network inventory by surface type](figures/04_surface_inventory.png)

Surface is a label attached to each pipe, not a polygon or terrain model. Pipe counts and pipe kilometres must not be interpreted as surface-area proportions.

### Distribution of individual pipe lengths

![Distribution of individual pipe lengths](figures/05_length_distribution.png)

This is the distribution of the length of each pipe record—not the total length of the network. Length is computed from the two recorded endpoints and directly affects the $200/m replacement charge.

### Time since original installation at 2027

![Time since original installation at 2027](figures/06_age_distribution.png)

All known installation dates precede the 2019 observation window. This is original-installation age, not current polyurethane age; missing dates are excluded.

### Installation age differs by original material

![Installation age differs by original material](figures/07_age_by_material.png)

Material and installation age are intertwined. An unadjusted age–leak relationship can reflect material mix rather than an independent aging effect.

### Surface mix within each original material

![Surface mix within each original material](figures/08_material_surface_mix.png)

Each row sums to 100%. Differences in surface composition can confound comparisons between materials; the Unknown row contains only eight pipes.

## 3. When were leaks recorded?

### Historical leak counts and repair costs

![Historical leak counts and repair costs](figures/09_annual_history.png)

Counts and total costs do not move identically because leak severity varies. Eight historical years are insufficient to assume a stable future trend or repeat the same years through 2051.

### Monthly leak counts, 2019–2026

![Monthly leak counts, 2019–2026](figures/10_monthly_heatmap.png)

The year-by-month view distinguishes isolated bursts from recurring seasonality. These are counts without adjustment for the changing material inventory.

### Annual leaks by original material

![Annual leaks by original material](figures/11_material_time.png)

Separate material series reveal whether aggregate movements are shared across groups. The plot does not establish the cause of any annual surge.

## 4. Which groups experienced leaks?

### Observed leak fraction by original material

![Observed leak fraction by original material](figures/12_material_leak_fraction.png)

The observed eight-year fraction is 76.1% for brass and 56.9% for copper, versus roughly 30–34% for the three iron groups. These are original-material, unadjusted fractions—not annual probabilities or causal effects. Wilson 95% intervals do not account for spatial dependence.

### First-leak incidence by original material

![First-leak incidence by original material](figures/13_exposure_adjusted_rates.png)

Exposure ends when a pipe first leaks and is replaced, or at the end of 2026. Exact Poisson 95% intervals are descriptive; zero recorded polyurethane leaks do not prove zero future risk.

### Observed leak fraction: material and surface

![Observed leak fraction: material and surface](figures/14_material_surface_risk.png)

Cross-classification helps reveal heterogeneity hidden by one-variable comparisons. Cells with fewer than 30 pipes are omitted from the graphic; all counts remain in the exported table.

### Observed leaks by original-installation age

![Observed leaks by original-installation age](figures/15_age_leak_fraction.png)

The left panel includes all materials; the right restricts the comparison to pipes originally made of iron, reducing—but not eliminating—material-mix confounding. Geography and repair-driven removal still affect the pattern, so the bars describe observed groups rather than a causal aging effect.

## 5. What drives historical repair dollars?

### Repair costs have a long upper tail

![Repair costs have a long upper tail](figures/16_cost_distribution.png)

The median is $3,275, versus a mean of $25,012. Logarithmic axes retain all positive costs, including the largest events; the cumulative curve uses statsmodels ECDF.

### A small share of leaks drives much of the cost

![A small share of leaks drives much of the cost](figures/17_cost_concentration.png)

The most expensive 1% of events account for 45.3% of historical repair dollars; the top 10% account for 81.6%. These are hindsight rankings, not an achievable model performance estimate.

### Repair severity by original material

![Repair severity by original material](figures/18_cost_by_material.png)

Boxplots summarize observed costs conditional on a leak. They do not combine leak probability with severity, and do not by themselves measure replacement priority. Outliers are retained.

### Repair severity by surface type

![Repair severity by surface type](figures/19_cost_by_surface.png)

Road-associated pipes account for 835 recorded leaks (5.9% of events) but 54.9% of repair dollars. Their median repair cost is $71,592. This is conditional severity, not a causal surface effect or the work-unit earthwork tariff. All outliers are retained.

### Pipe length and observed repair cost

![Pipe length and observed repair cost](figures/20_length_cost.png)

Spearman rank correlation is 0.171. It compares the rank order of pipe length with the rank order of repair cost: +1 means longer pipes always rank as more expensive, 0 means no monotonic ordering, and -1 means the reverse. Here 0.171 is a weak positive association. Hexagonal bins count overlapping events; this does not show that length causes repair cost.

### Installation age at leak and repair severity

![Installation age at leak and repair severity](figures/21_age_cost.png)

Each point is one recorded leak, positioned by original-installation age at that leak and repair cost. The orange LOWESS curve summarizes the local tendency of log cost without assuming a straight line; Spearman correlation is -0.018. Read it as evidence about whether older observed pipes tended to have larger repairs, not as a forecast or a causal aging effect. Material, surface, and location can explain part of the pattern.

### Repair cost per metre over time within original material

![Repair cost per metre over time within original material](figures/21b_material_cost_per_m_time.png)

The left panel shows annual means, which react strongly to rare very expensive repairs; the right shows medians, which describe a typical recorded event. Comparing lines within the same original material removes between-material level differences, but changing surface and location mix can still move the series. Values are nominal dollars and are not inflation-adjusted.

### Annual mean cost per metre relative to each material's own average

![Annual mean cost per metre relative to each material's own average](figures/21c_material_cost_per_m_heatmap.png)

Red cells are years above that material's own 2019–2026 mean cost per metre; blue cells are below it. Each cell also shows its number of recorded leaks. This makes within-material rises and falls visible, but extreme repairs can dominate the mean and cells with small n are uncertain.

## 6. Where are pipes and recorded replacements?

### Pipe-network materials at the start of 2027

![Pipe-network materials at the start of 2027](figures/22_material_map.png)

Every pipe appearing in train.csv is treated as replaced with polyurethane after its recorded leak; those pipes are therefore shown as polyurethane. Other pipes retain their original material, and missing material remains Unknown. Coordinates are local metres without a basemap.

### Estimated surface regions with pipe network

![Estimated surface regions with pipe network](figures/23_surface_map.png)

Areas assigned the same recorded surface type use the same fill color, while every pipe is drawn as the same dark line. The background is a nearest-pipe estimate within 60 coordinate units—not measured land boundaries, elevation, or a geographic basemap.

### Pipes replaced after leaks recorded in train.csv

![Pipes replaced after leaks recorded in train.csv](figures/24_replaced_pipe_map.png)

Orange lines are exactly the pipes listed in train.csv and therefore treated as replaced with polyurethane after their recorded leak. Every other pipe is gray; this map does not distinguish their original materials.

### Map of the 15 longest pipes

![Map of the 15 longest pipes](figures/25_longest_pipe_map.png)

The 15 longest endpoint-to-endpoint pipe records are individually colored and labelled with length; all other pipes are gray. This tests the visual plausibility of a length explanation for expensive repairs, but the overall length–cost Spearman correlation is only weakly positive and several highlighted pipes have no recorded leak cost.

### Map of pipes in the highest 1% of repair costs

![Map of pipes in the highest 1% of repair costs](figures/26_top1_cost_pipe_map.png)

Only the 142 pipes in the highest 1% of recorded repair costs are colored; all other pipes are gray. Color varies with recorded cost on a logarithmic scale. These highlighted events account for 45.3% of historical repair dollars, but their locations do not by themselves explain why the repairs were expensive.

## Methods and interpretation

**Observation window.** 2019-01-01 through 2026-12-31; 2027-01-01 is the project-start reference. The supplied history is assumed complete for that window. All known installation dates precede it. The original state at 2019 is assumed to be the stated original material; unrecorded earlier replacements cannot be reconstructed.**Inventory update.** Every pipe with a recorded historical leak is set to polyurethane for 2027, following the competition rule. Unknown materials stay unknown. Original-installation age must not be used as the actual age of newly installed polyurethane.**Geometry.** Each pipe length is the straight-line Euclidean distance between its supplied endpoints; the length distribution is therefore a distribution across individual pipe records, not total network length. Coordinates are local metres without a geographic basemap. Surface regions are nearest-pipe estimates used only for display, not measured land boundaries.**Fractions versus incidence.** An eight-year leak fraction divides leaking pipes by the source inventory. Original-material incidence divides recorded first leaks by pipe-years until leak/replacement or the end of observation. Missing installation dates are assigned observation entry at 2019-01-01 for exposure only; no age is imputed. Wilson intervals summarize binomial fractions; exact Poisson intervals summarize incidence. Their independence assumptions do not model spatial clustering or competing unrecorded changes.**Cost analysis.** Costs are nominal competition dollars; no inflation adjustment is assumed. Cost per metre divides each recorded repair cost by that pipe's endpoint-to-endpoint length. Annual mean values are sensitive to extreme repairs, so medians and event counts are shown alongside them. Spearman correlation compares rank order on a -1 to +1 scale; LOWESS summarizes local log-cost tendency. Both are descriptive, not forecasts or causal effects.**Python libraries.** pandas joins and aggregates; NumPy computes geometry and arrays; Matplotlib exports PNG/SVG; Seaborn draws statistical plots; SciPy computes rank correlation, nearest-neighbour surface estimates, and Poisson interval quantiles; statsmodels supplies Wilson intervals, ECDF, and LOWESS. A fixed seed is unnecessary because this analysis uses no random subsampling.**Reproducibility.** eda/run_eda.py regenerates the figures, tables, metrics and source hashes. eda/build_reports.py rebuilds the two HTML reports from the same evidence. Package versions and validation checks are saved in validation.json. This EDA does not train a forecast, simulate future leaks, or construct a submission.
