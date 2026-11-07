"""Independent invariants, topology fixtures, prior-cost checks and leakage audits."""
from pathlib import Path
import hashlib
import json
import subprocess
import ast
import csv
import io
import tempfile

import numpy as np
import pandas as pd

import enrich_cost_features as e

ROOT = Path(__file__).resolve().parents[1]


def fixture(segments):
    return pd.DataFrame([{'Pipe ID': f'P{i:03}', 'Lay date': '1980-01-01',
                          'GPS x1': a[0], 'GPS y1': a[1], 'GPS x2': b[0], 'GPS y2': b[1]}
                         for i, (a, b) in enumerate(segments)])


def main():
    metadata = json.loads((ROOT/'data/train_predict_cost_features_2026-10-05.json').read_text())
    path = ROOT/'data/train_predict_cost.csv'
    d = pd.read_csv(path)
    reconstructed = e.original_rows(path, metadata['original_columns'])
    assert hashlib.sha256(reconstructed).hexdigest() == metadata['original_source_sha256']
    assert len(d) == 14107 and d.pipe_id.is_unique and d.columns.is_unique
    assert d.columns[:len(metadata['original_columns'])].to_list() == metadata['original_columns']
    assert not np.isinf(d.select_dtypes(include=np.number).to_numpy()).any()
    # Exercise the actual input-loading block from the updated archived runner,
    # without retraining its 12 models or changing their published outputs.
    runner = ROOT/'notebooks/Takito_Kobayashi/reproduce.py'
    tree = ast.parse(runner.read_text(encoding='utf-8'))
    main_node = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    block = next(n for n in main_node.body if isinstance(n,ast.For) and ast.unparse(n.iter)=='hashes.items()')
    with tempfile.TemporaryDirectory(prefix='stat440_original_check_') as tmp:
        context = {'repo': ROOT, 'data': Path(tmp), 'hashes': json.loads((runner.parent/'source_hashes.json').read_text()),
                   'hashlib': hashlib, 'json': json, 'csv': csv, 'io': io}
        exec(compile(ast.Module(body=[block],type_ignores=[]),str(runner),'exec'),context)
        assert (Path(tmp)/'train_predict_cost.csv').read_bytes()==reconstructed
    for doc in ['README.md', 'data/train_predict_cost.md',
                'notebooks/Takito_Kobayashi/README.md']:
        original = subprocess.check_output(['git', 'show', 'HEAD:' + doc], cwd=ROOT).decode('utf-8').replace('\r\n', '\n')
        current = (ROOT/doc).read_text(encoding='utf-8').replace('\r\n', '\n')
        assert current.startswith(original), 'Original document changed: ' + doc
    straight, _ = e.route_features(fixture([((0,0),(1,0)), ((1,0),(2,0)), ((2,0),(3,0))]))
    assert straight.route_id.nunique() == 1 and straight.straight_section_id.nunique() == 1
    assert straight.is_straight.eq(1).all() and straight.is_bend.eq(0).all()
    assert np.allclose(straight.route_position, [0.5, 1.5, 2.5])
    corner, _ = e.route_features(fixture([((0,0),(1,0)), ((1,0),(1,1))]))
    assert corner.route_id.nunique() == 1 and corner.straight_section_id.nunique() == 2
    assert np.allclose(corner.turn_angle, 90) and corner.is_bend.eq(1).all()
    branch, _ = e.route_features(fixture([((0,0),(1,0)), ((1,0),(2,0)), ((1,0),(1,1))]))
    assert branch.route_id.nunique() == 3 and branch.is_branch_adjacent.eq(1).all()
    crossing, _ = e.route_features(fixture([((-1,0),(1,0)), ((0,-1),(0,1))]))
    assert crossing.route_id.nunique() == 2 and crossing.has_continuation.eq(0).all()
    loop, _ = e.route_features(fixture([((0,0),(1,0)), ((1,0),(1,1)), ((1,1),(0,1)), ((0,1),(0,0))]))
    assert loop.route_id.nunique() == 1 and loop.route_is_closed.eq(1).all()
    assert loop.route_tortuosity.isna().all() and loop.route_is_curved.eq(1).all()
    angles = np.radians([0, 8, 16, 24, 32, 40])
    points = np.vstack([[0,0], np.cumsum(np.column_stack([np.cos(angles), np.sin(angles)]), axis=0)])
    smooth, _ = e.route_features(fixture(list(zip(points[:-1], points[1:]))))
    assert smooth.route_is_curved.eq(1).all() and smooth.is_bend.eq(0).all()
    assert smooth.straight_section_id.nunique() > 1
    unknown = fixture([((0,0),(1,0)), ((1,0),(2,0))])
    unknown.loc[1, 'Lay date'] = None
    uncertain, _ = e.route_features(unknown)
    assert uncertain.topology_eligible.tolist() == [1, 0] and pd.isna(uncertain.loc[1, 'route_id'])
    p = pd.read_csv(ROOT/'data/pipes.csv')
    topology = pd.read_csv(ROOT/'data/pipe_route_lookup.csv')
    summaries = pd.read_csv(ROOT/'data/pipe_route_summary.csv').set_index('route_id')
    eligible = topology.topology_eligible.eq(1)
    assert len(topology) == len(p) == 43039 and topology.pipe_id.is_unique
    lengths = pd.Series(np.hypot(p['GPS x2']-p['GPS x1'], p['GPS y2']-p['GPS y1']).to_numpy(), index=p['Pipe ID'])
    grouped = topology.loc[eligible].assign(length=lambda x: x.pipe_id.map(lengths)).groupby('route_id')
    assert np.allclose(grouped.length.sum().sort_index(), summaries.route_length.sort_index())
    assert np.array_equal(grouped.size().sort_index(), summaries.route_pipe_count.sort_index())
    # Independently reconstruct the group-based historical cost statistics.
    for year in sorted(d.event_year.unique()):
        old = d[d.event_year < year]
        q = d[d.event_year == year]
        for window, width in [('all', None), ('last1', 1), ('last2', 2)]:
            h = old if width is None else old[old.event_year >= year-width]
            for key in ['material', 'surface', 'material_surface']:
                stats = h.groupby(key).cost.agg(['count', 'sum', 'median', 'max', 'std'])
                n = q[key].map(stats['count']).fillna(0)
                prefix = f'hist_{key}_{window}_'
                assert np.allclose(q[prefix+'n'], n)
                mean = (q[key].map(stats['sum']).fillna(0) + 20*h.cost.mean())/(n+20)
                assert np.allclose(q[prefix+'mean'], mean, equal_nan=True)
                for name in ['median','max','std']:
                    assert np.allclose(q[prefix+name], q[key].map(stats[name]), equal_nan=True)
        # Brute-force spatial histories on 16 representative rows, without KDTree.
        for row in q.head(2).itertuples():
            z = old.cost.to_numpy()
            mean = old.cost.mean()
            threshold = old.cost.quantile(.99)
            rate = float((old.cost >= threshold).mean()) if len(old) else np.nan
            distances = np.hypot(old.midpoint_x-row.midpoint_x,old.midpoint_y-row.midpoint_y).to_numpy()
            for radius in [50,100,250,500]:
                values = z[distances <= radius]
                n = len(values)
                prefix = f'hist_radius{radius}_'
                assert getattr(row,prefix+'n') == n
                expected_mean = (values.sum()+20*mean)/(n+20)
                assert np.allclose(getattr(row,prefix+'mean'),expected_mean,equal_nan=True)
                expected_tail = ((values>=threshold).sum()+50*rate)/(n+50)
                assert np.allclose(getattr(row,prefix+'tail_rate'),expected_tail,equal_nan=True)
                expected_median = np.median(values) if n else np.nan
                assert np.allclose(getattr(row,prefix+'median'),expected_median,equal_nan=True)
            if len(old):
                order = np.argsort(distances)
                for k in [5,10,25]:
                    values = z[order[:k]]
                    # Exactly equidistant ties can have a different valid KDTree
                    # ordering; check only samples without ties at the boundary.
                    if len(order)>k and np.isclose(distances[order[k-1]],distances[order[k]]):
                        continue
                    assert np.allclose(getattr(row,f'hist_nearest{k}_mean'),values.mean())
    history = pd.read_csv(ROOT/'data/train.csv')
    # Full route histories: changing all current/future costs leaves every
    # current-year route/section feature identical in every year.
    original_history = e.route_history(d, topology, history)
    for col in original_history:
        assert np.allclose(d[col], original_history[col], equal_nan=True)
    for year in sorted(d.event_year.unique()):
        changed = history.copy()
        future = pd.to_datetime(changed.Date).dt.year >= year
        changed.loc[future, 'Cost'] = changed.loc[future, 'Cost'] * 1000 + 12345
        changed.loc[future, 'Date'] = '2027-12-31'
        actual = e.route_history(d, topology, changed)
        selected = d.event_year == year
        for col in original_history:
            assert np.allclose(actual.loc[selected,col], original_history.loc[selected,col], equal_nan=True)
        sample = d.loc[selected].head(2).reset_index(drop=True)
        before = e.extra_candidates(sample, p, history)
        after = e.extra_candidates(sample, p, changed)
        pd.testing.assert_frame_equal(before, after)
        for col in before:
            assert np.allclose(sample[col], before[col], equal_nan=True)
    # Independently compute route history counts, costs and normalized counts.
    lookup = topology.set_index('pipe_id').route_id
    for year in sorted(d.event_year.unique()):
        past = history[pd.to_datetime(history.Date).dt.year < year].copy()
        past['route_id'] = past['Pipe ID'].map(lookup)
        counts = past.groupby('route_id').size()
        costs = past.groupby('route_id').Cost.sum()
        q = d[d.event_year == year]
        expected = q.route_id.map(counts).fillna(0)
        assert np.allclose(q.route_prior_leak_count, expected)
        assert np.allclose(q.route_prior_leak_cost, q.route_id.map(costs).fillna(0))
        assert np.allclose(q.route_prior_leaks_per_km, expected/(q.route_length/1000))
    report = {'validated_on': '2026-10-05', 'rows': len(d), 'columns': len(d.columns),
              'added_columns': len(metadata['added_columns']), 'output_sha256': e.sha(path),
              'original_cells_preserved': True, 'original_documents_preserved': True,
              'topology_fixtures': ['straight','right angle','branch','interior crossing','closed loop','smooth curve','unknown lay date'],
              'full_prior_group_cost_statistics_checked': True,
              'brute_force_spatial_history_samples': 16,
              'archived_runner_original_input_restored': True,
              'full_route_history_checked': True, 'future_mutation_years': list(range(2019,2027)),
              'state_history_samples': 16, 'no_infinite_values': True}
    (ROOT/'data/train_predict_cost_validation_2026-10-05.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
