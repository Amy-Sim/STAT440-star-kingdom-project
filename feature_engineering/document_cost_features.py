"""Append dated documentation without altering existing document bytes."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def describe(col):
    if col.startswith('hist_'):
        name = col[:-6] if col.endswith('_log1p') else col
        log = ' Apply ln(1+x) to the statistic.' if name != col else ''
        stats = {'n': 'recorded event count', 'mean': 'mean cost', 'median': 'median cost',
                 'max': 'maximum cost', 'std': 'sample standard deviation of cost',
                 'tail_rate': 'fraction of high-cost events'}
        group = re.fullmatch(r'hist_(.+)_(all|last1|last2)_(n|mean|median|max|std|tail_rate)', name)
        spatial = re.fullmatch(r'hist_(radius\d+|nearest\d+)_(n|mean|median|max|tail_rate)', name)
        if group:
            key, window, stat = group.groups()
            keys = {'material': 'same material', 'surface': 'same surface', 'material_surface': 'same material/surface pair',
                    'grid250': 'same 250m square grid cell', 'grid500': 'same 500m square grid cell',
                    'grid1000': 'same 1000m square grid cell', 'age_band': 'same age band (20/40/60/80 years)',
                    'length_band': 'same length band (10/25/50/100m)'}
            neighborhood = keys.get(key, 'segments within '+key.replace('segment','')+'m shortest planar distance')
            period = {'all': 'all preceding years', 'last1': 'previous calendar year', 'last2': 'previous two calendar years'}[window]
        elif spatial:
            key, stat = spatial.groups()
            neighborhood = ('events within '+key[6:]+'m midpoint distance') if key.startswith('radius') else ('nearest '+key[7:]+' prior event pipe midpoints')
            period = 'all preceding years'
        else:
            raise ValueError(col)
        smoothing = ''
        if stat == 'mean' and not neighborhood.startswith('nearest'):
            smoothing = ' Smoothed as (local cost sum + 20 * prior mean)/(count + 20).'
        if stat == 'tail_rate':
            smoothing = ' Threshold is the 99th percentile of all earlier-year costs; rate uses 50 prior pseudo-observations.'
        return f'{stats[stat].capitalize()} for {neighborhood}, using {period}.{smoothing}{log}', 'Prior-year severity history'
    if col.startswith('inventory_'):
        suffixes = {'count': 'number of other pipes', 'length_sum': 'sum of whole endpoint lengths (m)',
                    'parallel_count': 'number of nearly parallel pipes (within 15 degrees, positive projected overlap)',
                    'parallel_projected_length': 'sum of projected overlap lengths for nearly parallel pipes (m)',
                    'surface_diversity': 'number of distinct surface labels', 'road_count': 'road-labelled pipe count',
                    'structure_count': 'structure-labelled pipe count', 'water_count': 'water-labelled pipe count',
                    'swamp_count': 'swamp-labelled pipe count', 'same_material_fraction': 'fraction sharing the focal original material',
                    'iron_fraction': 'fraction originally iron', 'age_mean': 'mean age at the event date (years)',
                    'prior_repairs': 'count of prior recorded repairs', 'prior_repair_fraction': 'fraction with a prior recorded repair',
                    'recent_repairs': 'count repaired in the 365 days preceding January 1',
                    'days_since_repair': 'days from latest previous repair to January 1'}
        match = re.fullmatch(r'inventory_(\d+)m_(.+)', col)
        if match:
            radius, suffix = match.groups()
            description = f'Within {radius}m shortest segment distance: {suffixes[suffix]}. Excludes focal pipe and unknown/future lay dates.'
            history = 'repair' in suffix
            return description, 'Prior-year severity-row repair history + inventory' if history else 'Inventory at event date'
        if col.startswith('inventory_distance_to_'):
            return 'Shortest segment distance (m) to another '+col.replace('inventory_distance_to_', '')+'-labelled pipe; not distance to a mapped land boundary.', 'Inventory at event date'
        descriptions = {'inventory_nearest_midpoint_distance': 'Distance (m) to nearest eligible other pipe midpoint.',
                        'inventory_mean5_midpoint_distance': 'Mean midpoint distance (m) to five nearest eligible other pipes.',
                        'inventory_intersection_count': 'Count of intersecting other segments, including endpoint touches/overlaps.',
                        'inventory_proper_crossing_count': 'Count of proper interior segment crossings.',
                        'inventory_collinear_overlap_count': 'Count of collinear overlaps of positive length.',
                        'inventory_shared_endpoint_count': 'Count of other pipes sharing at least one endpoint.'}
        return descriptions[col], 'Inventory at event date; geometry only'
    for name in ['route', 'straight_section']:
        prefix = name + '_'
        if col.startswith(prefix):
            suffix = col[len(prefix):]
            descriptions = {'id': 'Common grouping ID; not an ordered numeric predictor.',
                            'length': 'Sum of member endpoint lengths (m).', 'pipe_count': 'Number of member segments.',
                            'prior_leak_count': 'Number of recorded leaks in all preceding calendar years.',
                            'prior_leak_cost': 'Total recorded leak cost in all preceding calendar years.',
                            'last1_leak_count': 'Number of recorded leaks in the previous calendar year.',
                            'prior_leaks_per_km': 'Prior leak count divided by group length in kilometres; descriptive, not a failure probability.',
                            'prior_cost_per_m': 'Prior leak cost divided by group length in metres.',
                            'days_since_leak': 'Days from last recorded prior leak to January 1; blank if none.',
                            'is_curved': '1 for closed route, accumulated turn >=30 degrees, or tortuosity >1.01.',
                            'is_closed': '1 for a closed endpoint chain.',
                            'total_turn_deg': 'Sum of direction changes at degree-2 nodes in degrees.',
                            'tortuosity': 'Route length / straight distance between ends; blank for closed routes.',
                            'position': 'Distance (m) from deterministic route start to the focal segment midpoint along the route.',
                            'position_fraction': 'Route position divided by route length.'}
            is_history = suffix.startswith(('prior_', 'last1_', 'days_since_'))
            return name.replace('_',' ').capitalize()+': '+descriptions[suffix], 'Full raw prior-year leak history' if is_history else 'Exact endpoint geometry, pre-2019 inventory'
    state = re.fullmatch(r'(prior_repairs|prior_repair_fraction|no_recorded_repair|current_pu_fraction|remaining_iron_count|remaining_iron_length|repairs_last365d|days_since_neighbor_repair)_(\d+)m', col)
    if state:
        name, radius = state.groups()
        descriptions = {'prior_repairs': 'number repaired before January 1', 'prior_repair_fraction': 'fraction repaired before January 1',
                        'no_recorded_repair': 'number with no recorded repair before January 1',
                        'current_pu_fraction': 'fraction originally polyurethane or repaired before January 1',
                        'remaining_iron_count': 'number originally iron and not repaired before January 1',
                        'remaining_iron_length': 'sum of lengths (m) of original iron not repaired before January 1',
                        'repairs_last365d': 'number repaired during the 365 days preceding January 1',
                        'days_since_neighbor_repair': 'days since latest repair before January 1, blank if no repairs'}
        return f'Other eligible pipes within {radius}m shortest segment distance: {descriptions[name]}.', 'Full raw prior-year repair history + inventory'
    if col.startswith('neighbor_count_'):
        return 'Other eligible pipes within '+col.split('_')[-1]+'m midpoint distance (different from segment distance).', 'Inventory at event date'
    if col.startswith('wet_segments_'):
        return 'Count of other water/swamp-labelled segments within '+col.split('_')[-1]+' shortest segment distance.', 'Inventory at event date'
    if col.endswith('_squared'):
        return 'Square of '+col[:-8]+'; distances in m, ages in years.', 'Derived from existing columns'
    exact = {
        'lay_year': 'Original installation year.', 'lay_month': 'Original installation month.',
        'event_weekday': 'Event weekday: Monday=0 through Sunday=6.',
        'event_weekend': '1 when the event occurs on Saturday or Sunday.',
        'event_hour': 'Integer recorded event hour, 0 through 23.',
        'event_night': '1 when recorded event time is before 06:00 or at/after 22:00.',
        'span_x': 'Absolute difference between endpoint x coordinates (m).',
        'span_y': 'Absolute difference between endpoint y coordinates (m).',
        'orientation_sin2': 'sin(2*orientation angle): 2*dx*dy/length^2; invariant to endpoint order.',
        'orientation_cos2': 'cos(2*orientation angle): (dx^2-dy^2)/length^2; invariant to endpoint order.',
        'length_age': 'Pipe length (m) multiplied by pipe age (years).',
        'material_surface': 'Combined original material and surface category.',
        'neighbor_length_sum_100': 'Total endpoint length of other pipes within 100m midpoint distance (m).',
        'neighbor_road_count_100': 'Road-labelled other pipe count within 100m midpoint distance.',
        'age_x_wet_proximity': 'Pipe age * ln(1 + inventory_25m_water_count + inventory_25m_swamp_count).',
        'length_x_structure_exposure': 'Pipe length * ln(1 + inventory_25m_structure_count).',
        'road_x_structure_exposure': 'Indicator that focal surface is road * ln(1 + inventory_25m_structure_count).',
        'topology_eligible': '1 when original lay date is known and before 2019; 0 otherwise.',
        'endpoint_degree_1': 'Number of eligible segments meeting original endpoint 1.',
        'endpoint_degree_2': 'Number of eligible segments meeting original endpoint 2.',
        'is_branch_adjacent': '1 when at least one endpoint has degree >=3.',
        'has_continuation': '1 when at least one endpoint has exactly two incident pipes.',
        'turn_angle': 'Maximum direction change at a degree-2 endpoint (degrees); blank with no continuation.',
        'is_bend': '1 when a degree-2 endpoint direction change exceeds 10 degrees.',
        'is_straight': '1 when there is a degree-2 continuation and its maximum direction change is <=10 degrees; local criterion only.',
    }
    cyclic = re.fullmatch(r'(month|hour|weekday)_(sin|cos)', col)
    if cyclic:
        period = {'month': '(event_month-1)/12', 'hour': 'event_hour/24', 'weekday': 'event_weekday/7'}[cyclic[1]]
        return f'{cyclic[2]}(2*pi*{period}).', 'Recorded event calendar/time'
    return exact[col], 'Inventory/event attributes or endpoint topology'


def append(path, text):
    marker = '## 2026-10-05'
    raw = path.read_bytes()
    if marker.encode() not in raw:
        with path.open('ab') as f:
            f.write(('\n\n'+text.rstrip()+'\n').encode('utf-8'))


def main():
    m = json.loads((ROOT/'data/train_predict_cost_features_2026-10-05.json').read_text())
    rows = []
    for col in m['added_columns']:
        description, source = describe(col)
        rows.append(f'| `{col}` | {description} | {source} |')
    dictionary = '''# Cost feature dictionary — additions on 2026-10-05

The 35 original columns of `train_predict_cost.csv` are unchanged. The following
501 columns are candidate features, not a universally recommended model input.
Rows and original values are unchanged (14,107 events; 536 total columns).
Original data/train.csv and pipes.csv remain unchanged.

All historical statistics exclude the current and future calendar years and
are frozen at January 1. Costs use the dataset's original monetary unit. Distances
and endpoint lengths are metres. Neighbours exclude the focal pipe and require
a known lay date no later than the event. Missing historical statistics are blank;
zero counts mean no recorded events. Means/tail rates use the documented prior
smoothing; nearest-event means, medians/maxima/std are not smoothed.

Historical cost-group features use the original 14,107 severity rows. The explicit
repair-state and route/section histories use all 14,113 raw train.csv records.
The inventory_* repair columns retain the archived severity-row history definition.
Do not treat event counts as exposure-adjusted leak probabilities. Route per-km
counts adjust for length but not time at risk or changes in replacement status.

Endpoint routes use exact coordinate equality (0m snapping tolerance), split at
branches/dead ends, and do not connect interior crossings. All known inventory lay
dates precede 2019 (latest 1985-12-28); 15 unknown-date pipes are excluded from
historical topology. They remain in pipe_route_lookup.csv with topology_eligible=0
and blank route fields. Physical connectivity, depth and a real continuous asset
identity are not established by this inferred geometry.

Direction change is 0 degrees for straight continuation. Local is_straight uses
<=10 degrees and is_bend uses >10 degrees at degree-2 endpoints. Straight sections
split when a member's direction differs by >10 degrees from the section's initial
direction, so accumulated small turns also split sections. Route_is_curved is 1
for accumulated turn >=30 degrees, length/end-distance >1.01, or a closed route.
A local straight flag and a curved route flag may both be 1. Isolated segments
have no continuation and neither local flag. Closed routes have blank tortuosity.
Closed-route straight sections do not merge across the deterministic start seam.

route_position measures distance to the segment midpoint from a deterministic
route endpoint (lexicographically smallest endpoint; same convention for loops).
The original endpoint order is retained for endpoint_degree_1/2. Route and section
IDs are stable grouping strings based on their smallest member Pipe ID, not
ordinal predictors. They change if inventory/topology changes. Use IDs for
grouping, validation and mapping; select numerical group summaries separately.

Event dates/hours are recorded incident attributes. For future cost scenarios,
specify a scenario date/time and recompute age/calendar/history features. Their
existence does not mean future leak times are known. Endpoint sums, segment
proximity and projected overlaps are not actual curved/excavation lengths, measured
surface areas, confirmed physical connections or observed incident mechanisms.
No model retraining or improvement claim accompanies this data extension.

## Added columns

| Column | Definition | Source / availability |
|---|---|---|
'''
    (ROOT/'data/train_predict_cost_feature_dictionary_2026-10-05.md').write_text(dictionary+'\n'.join(rows)+'\n',encoding='utf-8')
    english = '''## 2026-10-05 — Added candidate features and inferred pipe routes

Today, 501 candidate feature columns were appended to `train_predict_cost.csv`.
The original 35 columns, their values and the 14,107-row order were preserved;
the CSV now has 536 columns. Raw `pipes.csv` and `train.csv` were not changed.

The additions cover installation/event calendar information; spans, orientation,
length-age products and squared terms; material/surface combinations; neighbouring
pipe counts, lengths, ages and surface/material composition; nearest surface-pipe
distances, parallel overlaps and planar intersections; prior repair/replacement
state; previous repair-cost statistics by attribute group and spatial neighbourhood;
and age/length/environment interactions. Existing equivalent aliases were not
duplicated. Earlier rolling repair candidates were converted to year-start cutoffs.

Endpoint geometry also supplies `route_id`, `straight_section_id`, local straight/
bend flags, turn angles, endpoint degrees, branch flags, route length/count,
position, accumulated turn and tortuosity. Routes are maximal nonbranching chains
through exactly matching endpoints; interior crossings are not connected. The
initial straight threshold is 10 degrees. Straight sections also split when
accumulated direction deviation from their first pipe exceeds 10 degrees; smooth
curves are represented by route-level turn/tortuosity flags. IDs are grouping keys,
not ordered numeric features, and inferred geometry does not prove connectivity.

All history features use strictly previous calendar years, frozen on January 1.
The explicit repair-state and route/section histories use all raw leak records,
including six rows excluded from severity training. Archived cost-group features
retain the original severity-row source. Group leak counts/costs and per-length
rates support macro analysis, but are not annual failure probabilities.

The full inventory produces 36,304 inferred routes (4,871 with multiple pipes)
and 37,747 straight sections. A route contains at most 52 segments. The 15 pipes
with unknown lay dates are excluded from historical topology and retained as
ineligible rows with blank route fields in the inventory lookup. Known inventory
lay dates all precede the training window. Historical attributes are assumed
applicable at each incident; retirement/attribute-change records are unavailable.

Files added: `pipe_route_lookup.csv` (one row per inventory pipe),
`pipe_route_summary.csv` (one row per inferred route), and
`pipe_route_event_membership.csv` (one row per severity event).
See [the complete added-column dictionary](train_predict_cost_feature_dictionary_2026-10-05.md),
`train_predict_cost_features_2026-10-05.json` for generation settings/provenance,
and `train_predict_cost_validation_2026-10-05.json` for verification evidence.

Rebuild from the repository root with `python feature_engineering/enrich_cost_features.py` using
the pinned dependencies in `notebooks/Takito_Kobayashi/requirements.txt`; verify
with `python feature_engineering/verify_cost_features.py`. The default rebuild uses an isolated
temporary copy of the archived feature code; an optional matching legacy cache
can be supplied with `--legacy-features`. Existing archived model reproduction
extracts and hash-checks the original 35 columns before using its frozen builders.
Select candidate features using temporal validation; do not automatically train
on every column or infer that all candidates improve prediction.
'''
    append(ROOT/'README.md', '''## 2026-10-05 — Cost feature data extension

Today, 501 candidate columns were appended to `data/train_predict_cost.csv`
(14,107 rows; 536 total columns), preserving all original columns/values/order.
Added candidates include prior-year repair costs/state, spatial geometry and
endpoint-based route/straight-section groups for macro leak analysis. Raw inputs
remain unchanged. Full definitions, limitations and rebuild instructions are in
[the dated addendum](data/train_predict_cost.md#2026-10-05--added-candidate-features-and-inferred-pipe-routes), and
[the feature dictionary](data/train_predict_cost_feature_dictionary_2026-10-05.md).
''')
    append(ROOT/'notebooks/Takito_Kobayashi/README.md', '''## 2026-10-05 — Compatibility with the extended shared CSV

Today, the shared `data/train_predict_cost.csv` received 501 additional candidate
columns, including inferred endpoint routes and year-start histories. Existing
published predictions, selected configurations and archived executed code were
not changed. `reproduce.py` now extracts the original 35 columns and checks their
original SHA-256 before invoking the frozen builders, preserving reproduction of
the previous experiments. The new route/state features are not retroactively
part of those models. See the shared data documentation's dated addendum.
''')
    print('Appended four dated document sections; documented all 501 new columns.')


if __name__ == '__main__':
    main()
