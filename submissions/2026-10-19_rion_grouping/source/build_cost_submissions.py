"""Create six cost-informed circle orderings; validate exported geometry and budgets."""
from pathlib import Path
import csv
import hashlib
import json
import math
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd
import lightgbm as lgb
from scipy.spatial import cKDTree
from build_baseline import RATES, IRON, MARGIN_M

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submissions/2026-10-13_cost_candidates'
PRED = ROOT / 'notebooks/ensemble_for_cost_prediction/predictions'
MODELS = ROOT / 'submissions/risk_priority_models'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_units(path):
    units = []
    with path.open(newline='', encoding='utf-8') as f:
        for row in csv.reader(f):
            assert len(row) == 2 and row[0].startswith('(') and row[0].endswith(')')
            x, y = map(float, row[0][1:-1].split(','))
            r = float(row[1])
            assert np.isfinite([x, y, r]).all() and r >= 0
            units.append((np.array([x, y]), r))
    return units


def containment(units, tree, a, b):
    result = []
    for center, radius in units:
        ids = np.asarray(tree.query_ball_point(center, radius), dtype=int)
        ids = ids[(np.linalg.norm(a[ids]-center, axis=1) <= radius)
                  & (np.linalg.norm(b[ids]-center, axis=1) <= radius)]
        result.append(ids)
    return result


def validate(path, pipes, history, a, b, mid, lengths, target):
    units = read_units(path)
    inside = containment(units, cKDTree(mid), a, b)
    covered = np.zeros(len(pipes), bool)
    for ids in inside:
        covered[ids] = True
    assert covered[target].all(), 'Uncovered original iron'
    current = (pipes.Material.eq('polyurethane') | pipes['Pipe ID'].isin(history['Pipe ID'])).to_numpy(copy=True)
    budget = total = cursor = skipped = 0
    annual = []
    for year in range(2027, 2052):
        budget += 1_000_000_000
        spent = executed = 0
        while cursor < len(units):
            ids = inside[cursor]
            replace = ids[~current[ids]]
            if not len(replace):
                cursor += 1
                skipped += 1
                continue
            rate = sum(RATES[s] for s in set(pipes.Surface.iloc[ids]))
            raw = 100 + (rate*math.pi*units[cursor][1]**2)**.85 + 200*lengths[replace].sum()
            cost = int(Decimal(str(raw)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)*100)
            if cost > budget:
                break
            budget -= cost
            total += cost
            spent += cost
            current[replace] = True
            cursor += 1
            executed += 1
        annual.append(dict(year=year, construction_cost=spent/100, executed_units=executed,
                           budget_balance=budget/100, remaining_units=len(units)-cursor))
        if cursor == len(units):
            break
    assert cursor == len(units) and current[target].all(), 'Budget/completion failure'
    report = dict(submission=path.name, work_unit_count=len(units), uncovered_iron_count=int((target & ~covered).sum()),
                  completed_by_2051=True, completion_year=year, construction_cost=total/100,
                  no_future_leak_score=250_000_000-total/100, skipped_units=skipped,
                  scenario='No future leaks; NOT an estimated official score',
                  annual_execution=annual, radius_margin_m=MARGIN_M,
                  sha256=digest(path), exported_csv_reparsed=True)
    path.with_suffix('.validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pipes = pd.read_csv(ROOT/'data/pipes.csv', dtype={'Pipe ID': str})
    history = pd.read_csv(ROOT/'data/train.csv', dtype={'Pipe ID': str})
    assert pipes['Pipe ID'].is_unique and history['Pipe ID'].is_unique
    assert set(history['Pipe ID']) <= set(pipes['Pipe ID'])
    assert set(pipes.Surface) <= set(RATES)
    a = pipes[['GPS x1','GPS y1']].to_numpy(float)
    b = pipes[['GPS x2','GPS y2']].to_numpy(float)
    mid = (a+b)/2
    lengths = np.linalg.norm(b-a, axis=1)
    target = pipes.Material.isin(IRON).to_numpy()
    initial = (pipes.Material.eq('polyurethane') | pipes['Pipe ID'].isin(history['Pipe ID'])).to_numpy()
    indices = np.flatnonzero(target)
    # Preserve baseline circle geometry; round first so ranking uses exported geometry.
    units = [(np.round(mid[i], 9), float(f'{lengths[i]/2+MARGIN_M:.9f}')) for i in indices]
    inside = containment(units, cKDTree(mid), a, b)
    meta = json.loads((MODELS/'metadata.json').read_text())
    model = lgb.Booster(model_file=str(MODELS/'risk.txt'))
    frame = pd.DataFrame(dict(material=pipes.Material, surface=pipes.Surface, pipe_length=lengths,
                              midpoint_x=mid[:,0], midpoint_y=mid[:,1]))
    for col, categories in meta['categories'].items():
        frame[col] = pd.Categorical(frame[col], categories=categories)
    survival = np.ones(len(pipes))
    for year in [2027, 2028]:
        frame['pipe_age'] = (pd.Timestamp(year,1,1)-pd.to_datetime(pipes['Lay date'])).dt.days/365.25
        prob = model.predict(frame[meta['features']], num_threads=4)
        assert np.isfinite(prob).all() and ((prob>=0)&(prob<=1)).all()
        survival *= 1-prob
    probability = 1-survival
    probability[initial] = 0
    construction = []
    for (_, radius), ids in zip(units, inside):
        active = ids[~initial[ids]]
        rate = sum(RATES[s] for s in set(pipes.Surface.iloc[ids]))
        construction.append(0 if not len(active) else 100+(rate*math.pi*radius**2)**.85+200*lengths[active].sum())
    construction = np.array(construction)
    configurations = [('01_catboost_risk','takito_catboost','risk'),
                      ('02_stable_risk','ensemble_stable','risk'),
                      ('03_equal_risk','ensemble_equal','risk'),
                      ('04_rmse_weighted_risk','ensemble_rmse_weighted','risk'),
                      ('05_catboost_cost_only','takito_catboost','cost'),
                      ('06_stable_risk_per_work_cost','ensemble_stable','ratio')]
    results = []
    for name, method, strategy in configurations:
        source = PRED/f'{method}.csv'
        predictions = pd.read_csv(source, dtype={'id':str})
        assert predictions.id.is_unique
        severity = pipes['Pipe ID'].map(predictions.set_index('id').predicted_cost).to_numpy(copy=True)
        assert np.isfinite(severity[~initial]).all() and (severity[~initial]>=0).all()
        severity[initial] = 0
        expected = severity*probability
        benefit = severity if strategy == 'cost' else expected
        priority = np.array([benefit[ids].sum() for ids in inside])
        if strategy == 'ratio':
            priority /= np.maximum(construction, 1)
        order = np.lexsort((pipes['Pipe ID'].iloc[indices].to_numpy(), -priority))
        path = OUT/f'{name}.csv'
        with path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for j in order:
                center, radius = units[j]
                writer.writerow([f'({center[0]:.9f}, {center[1]:.9f})', f'{radius:.9f}'])
        pd.DataFrame(dict(rank=np.arange(1,len(order)+1), pipe_id=pipes['Pipe ID'].iloc[indices[order]].to_numpy(),
                          priority=priority[order], initial_circle_work_cost=construction[order],
                          pipe_cost_prediction=severity[indices[order]], pipe_leak_probability_2y=probability[indices[order]])
                     ).to_csv(OUT/f'{name}.audit.csv', index=False)
        report = validate(path,pipes,history,a,b,mid,lengths,target)
        results.append(dict(candidate=name, cost_model=method, ordering=strategy,
                            construction_cost=report['construction_cost'], completion_year=report['completion_year'],
                            uncovered_iron_count=report['uncovered_iron_count'], source_prediction_sha256=digest(source),
                            submission_sha256=report['sha256']))
        print(json.dumps(results[-1]), flush=True)
    pd.DataFrame(results).to_csv(OUT/'comparison.csv',index=False)
    manifest = dict(seed=440, history_cutoff='2026-12-31', ranking_window=[2027,2028],
                    baseline_reported_official_score_approx=-26_000_000,
                    source_sha256={str(p.relative_to(ROOT)):digest(p) for p in
                        [ROOT/'data/pipes.csv', ROOT/'data/train.csv', MODELS/'risk.txt', MODELS/'metadata.json', Path(__file__)]},
                    candidates=results,
                    limitations=['Conditional cost predictions are not leak probabilities.',
                                 'Fixed 2027 severity and 2027-2028 probability ranking, not a full horizon optimizer.',
                                 'Circle priorities overlap; benefits are ranking heuristics, not additive savings.',
                                 'No future leak validation establishes construction feasibility, not official score improvement.',
                                 'Unknown-material pipes are not original-iron targets; incidental replacement is charged.'])
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (OUT/'README.md').write_text('''# Submission candidates using cost prediction

Submit only CSVs 01–06: no header, two columns containing center coordinates and radius. Do not submit audit.csv or comparison.csv.

1. 01_catboost_risk.csv: CatBoost × 2-year leakage probability
2. 02_stable_risk.csv: Shrinkage ensemble × 2-year leakage probability
3. 03_equal_risk.csv: Equal weight ensemble × 2-year leakage probability
4. 04_rmse_weighted_risk.csv: RMSE weighted ensemble × 2-year leakage probability
5. 05_catboost_cost_only.csv: Descending by CatBoost repair cost only
6. 06_stable_risk_per_work_cost.csv: Descending order by expected repair cost / initial construction cost

First compare submissions 01 and 02 to assess a single model versus the ensemble, then use 06 to assess the construction-cost adjustment.
The original one-circle-per-iron-pipe geometry was retained. Order used the summed priority of all unreplaced pipes contained in each circle. Coordinates and distances are in meters.
Each exported CSV was reloaded to verify full endpoint containment, distinct surfaces, overlapping replacement, historical PU conversion, budget carryover, and stopping at the first unaffordable unit.
All candidates completed within budget without future leaks. See comparison.csv for construction costs/completion years and validation.json for annual details.
Scores including future leak repair costs were not estimated. `no_future_leak_score` is not an official result.
The official baseline score of approximately -26M dollars is based on user reports, and improvements to this model will be determined based on the submitted results.
This compares orders using fixed 2027 repair costs and 2027–2028 leak probabilities, not a 25-year optimization.

Reproduce from the project root: `.venv-eda/Scripts/python.exe github-main/src/build_cost_submissions.py`
''',encoding='utf-8')


if __name__ == '__main__':
    main()

