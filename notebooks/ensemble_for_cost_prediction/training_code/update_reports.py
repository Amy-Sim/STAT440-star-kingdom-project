"""Update the English report from committed predictions; no fitting or forecast changes.

Run: python notebooks/ensemble_for_cost_prediction/training_code/update_reports.py
from the repository root. Requires pandas, numpy and tabulate.
"""
from pathlib import Path
from decimal import Decimal
import json,hashlib
import numpy as np
import pandas as pd

PACKAGE=Path(__file__).resolve().parents[1]
REPO=PACKAGE.parents[1]
METHODS=['takito_catboost','ensemble_equal','ensemble_stable','ensemble_balanced','ensemble_rmse_weighted','prior_surface_mean']

def main():
    p=pd.read_csv(REPO/'data/pipes.csv');t=pd.read_csv(REPO/'data/train.csv')
    ids=set(p['Pipe ID'])-set(t['Pipe ID']);q=p.loc[p['Pipe ID'].isin(ids)].copy()
    scope=pd.read_csv(PACKAGE/'evidence/prediction_scope.csv')
    assert set(scope.id)==ids and len(ids)==28926
    material=p.set_index('Pipe ID').Material
    issue=q[['Pipe ID','Material','Lay date']].rename(columns={'Pipe ID':'id','Material':'material','Lay date':'lay_date'})
    issue['material_unseen_in_training']=issue.material.eq('polyurethane')
    issue['material_missing']=issue.material.isna()
    issue['lay_date_missing']=issue.lay_date.isna()
    issue.to_csv(PACKAGE/'evidence/input_quality_by_pipe.csv',index=False)
    coords=p[['GPS x1','GPS y1','GPS x2','GPS y2']].apply(pd.to_numeric,errors='coerce')
    lengths=np.linalg.norm(coords[['GPS x2','GPS y2']].to_numpy()-coords[['GPS x1','GPS y1']].to_numpy(),axis=1)
    audit={'inventory_rows':len(p),'training_rows':len(t),'target_rows':len(q),
      'inventory_missing':{k:int(v) for k,v in p.isna().sum().items()},
      'target_missing':{k:int(v) for k,v in q.isna().sum().items()},
      'training_missing':{k:int(v) for k,v in t.isna().sum().items()},
      'invalid_or_nonfinite_coordinate_rows':int((~np.isfinite(coords.to_numpy())).any(axis=1).sum()),
      'zero_length_rows':int((lengths==0).sum()),'nonpositive_training_cost_rows':int(t.Cost.le(0).sum()),
      'maximum_observed_training_cost':float(t.Cost.max()),
      'maximum_endpoint_length_m':float(lengths.max()),
      'source_sha256':{str(z.relative_to(REPO)):hashlib.sha256(z.read_bytes()).hexdigest() for z in [REPO/'data/train.csv',REPO/'data/pipes.csv']}}
    totals=[]
    for name in METHODS:
        path=PACKAGE/'predictions'/f'{name}.csv';df=pd.read_csv(path,dtype={'predicted_cost':str})
        assert set(df.id)==ids and len(df)==len(q)
        values=pd.to_numeric(df.predicted_cost);assert np.isfinite(values).all() and values.ge(0).all()
        mats=df.id.map(material)
        def amount(mask):return float(sum((Decimal(s) for s in df.loc[mask,'predicted_cost']),Decimal(0)))
        pu=mats.eq('polyurethane');missing=mats.isna();supported=~(pu|missing)
        totals.append({'candidate':name,'n_pipes':len(df),'supported_material_total':amount(supported),
           'pu_extrapolation_total':amount(pu),'missing_material_extrapolation_total':amount(missing),
           'all_target_total':amount(pd.Series(True,index=df.index)),'zero_predictions':int(values.eq(0).sum())})
    total=pd.DataFrame(totals);total.to_csv(PACKAGE/'evidence/repair_all_2027_totals.csv',index=False,float_format='%.2f')
    audit['zero_prediction_counts']=dict(zip(total.candidate,total.zero_predictions.astype(int)))
    (PACKAGE/'evidence/input_quality_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    configs={}
    for f in (PACKAGE/'configs').glob('*.json'):
        c=json.loads(f.read_text());configs[c['model']]=c
    (PACKAGE/'evidence/model_input_contract.json').write_text(json.dumps({
      'scenario_year':2027,'history_cutoff_exclusive':'2027-01-01',
      'inventory_columns':p.columns.tolist(),'label_columns':t.columns.tolist(),
      'target_policy':'all inventory IDs not present in train.csv',
      'output_columns':['id','predicted_cost'],'output_meaning':'conditional repair cost per pipe under 2027 scenario, not failure time or probability',
      'per_model_selected_features':{n:c['features'] for n,c in configs.items()},
      'unknown_categories':'CatBoost strings; XGBoost/LightGBM missing category; sklearn OHE ignores unseen (all-zero reference collision)',
      'invalid_new_inputs':'Duplicate IDs, invalid dates, nonfinite coordinates or zero endpoint length require correction and revalidation; no universal sanitization implemented.'
    },ensure_ascii=False,indent=2),encoding='utf-8')
    for language in ['en']:update(language,total,configs)
    print(total.to_string(index=False))

def update(lang,total,configs):
    path=PACKAGE/f'report_{lang}.md';text=path.read_text(encoding='utf-8')
    old_start='## Annual results'
    new_start='## Total cost if every target pipe is repaired in 2027'
    if old_start in text:text=text[:text.index(old_start)]+text[text.index('## Sources and validation',text.index(old_start)):]
    if new_start in text:text=text[:text.index(new_start)]+text[text.index('## Sources and validation',text.index(new_start)):]
    # Remove prior sections before regenerating; preserve all other narrative and results.
    headers=['## Detailed handling of missing, unseen and invalid values','## Model inputs, outputs and coordination with failure-timing models']
    for header in headers:
        if header in text:
            start=text.index(header);end=text.find('\n## ',start+len(header));text=text[:start]+(text[end+1:] if end!=-1 else '')
    note=('\n\n**Why existing Shana submissions were excluded (temporal leakage):** Outcomes from evaluation years 2023–2025 were used for feature/model selection, so those predictions cannot serve as clean OOF ensemble inputs. This temporal validation contamination is distinct from using realized future failure hour/weekday, which is unavailable at forecast time. The architectures themselves can be candidates if refitted with selection entirely inside past-only folds.\n')
    section='## Work performed and leakage controls'
    if '**Reason for exclusion of Shana\'s existing submissions' not in text and '**Why existing Shana submissions' not in text:
        after=text.find('\n## ',text.index(section)+len(section));text=text[:after]+note+text[after:]
    details=details_en()
    interface=interface_en(configs)
    cols=['candidate','supported_material_total','pu_extrapolation_total','missing_material_extrapolation_total','all_target_total']
    table=total[cols].copy()
    table.columns=['Candidate','Supported: 27,240 pipes','PU: 1,678 (extrapolated)','Missing material: 8 (extrapolated)','All 28,926 targets']
    scenario='\n'+new_start+'\n\n'+table.to_markdown(index=False,floatfmt=',.2f')+'\n\n'
    scenario+=('This table sums saved CSV predictions under the explicit assumption that every target pipe is repaired once in 2027. The population is 28,926 pipes after excluding the 14,113 train.csv IDs as requested, not all 43,039 inventory pipes. Units are those of the source costs; neither yen nor dollars is asserted. PU and missing-material contributions are separate to expose reliance on unvalidated extrapolation.\n\nNo failure probabilities are applied. This is a repair-all scenario, not the usual annual failure budget. Models were trained on costs incurred at failures, not planned preventive replacement; shared mobilization costs, coordinated-work discounts and inflation have not been modeled separately. These totals are not calibrated quotes for a coordinated replacement project. The earlier RMSE and total-bias explanations remain as historical validation on actually failed pipes.\n\nTotals were calculated with decimal arithmetic from the saved CSV values. The same figures are available in the [machine-readable totals CSV](evidence/repair_all_2027_totals.csv).\n')
    source='## Sources and validation';text=text.replace(source,details+'\n'+interface+'\n'+scenario+'\n'+source)
    path.write_text(text,encoding='utf-8')



def details_en():return '''## Detailed handling of missing, unseen and invalid values

### What was actually found

| Item | Inventory: 43,039 | Prediction targets: 28,926 | Handling |
|:---|---:|---:|:---|
| PU (`polyurethane`) | 1,678 | 1,678 | Material is known, but has no cost labels; use each model's unseen-category handling |
| Missing material | 8 | 8 | Replace with `__unknown__`, without asserting iron or PU |
| Missing lay date | 15 | 9 | Keep age NaN, set `age_missing=1`; retain the six training rows too |
| Missing surface | 0 | 0 | No observed replacements required; categorical blanks become `__unknown__` |
| Missing/non-numeric/nonfinite coordinates | 0 | 0 | Use observed coordinates; no automatic repair of invalid new coordinates |
| Zero endpoint length | 0 | 0 | None observed; new zero-length input requires correction before directional features |

train.csv has no missing ID, Date, Time or Cost and no nonpositive costs. The six training records with missing inventory lay date were restored from raw train.csv rather than dropped with an incomplete enriched table. All 14,113 labels were retained. Training materials are wrought iron, cast iron, gray iron, brass and copper; neither PU nor missing-material costs were observed. Expensive events, including the maximum observed cost of 7,257,576.36, were not deleted or capped as presumed outliers.

### How each model calculated PU and missing-material costs

PU retains the string `polyurethane`; missing material becomes `__unknown__`. The material–surface composite category carries the same values. Neither is relabeled as a supported material in the source features, although the encoder introduces the limitations below.

| Family | Actual unseen-category handling | Basis and limitation |
|:---|:---|:---|
| CatBoost | Pass PU/`__unknown__` as strings through CatBoost categorical processing | Learned trees and selected age, surface, length, route and other inputs; no PU-specific price relationship was learned |
| XGBoost/LightGBM | Convert categories outside fitted category levels to category missing | Learned missing-category behavior plus remaining features; that path is not validated for PU |
| Linear/Gamma/Random Forest | `OneHotEncoder(handle_unknown='ignore', drop='first')` makes every dummy in the unseen category block zero | Encoding collides with the dropped reference category; other inputs remain, but this does not establish an appropriate PU material effect |
| Surface mean | Ignore material; shrink surface-specific average toward global mean | `(surface cost sum + α × global mean)/(surface count + α)`, with Optuna-selected α; unseen surface falls back to global mean |
| Ensembles | Weighted average of the ten saved component predictions | Averaging does not remove unsupported-material uncertainty or substitute for a PU-specific fit |

### Missing age and missing historical statistics

Age is `(2027-01-01 − Lay date in days)/365.25`. Missing lay date produces NaN age/log-age and `age_missing=1`; the age-band aggregation key is the separate missing group `-1`. Age was not assumed to be zero.

Linear, Gamma and RF pipelines use `SimpleImputer(strategy='median', add_indicator=True)` with medians fitted only on their training period, then standardize. Indicators are added for columns missing during fit, not automatically for every column that might become missing later. CatBoost, XGBoost and LightGBM retain numeric NaN and use their learned native missing-value behavior.

For material, material–surface, route and similar groups with no historical repairs, aggregation count and sum are set to zero. This does not assign zero repair cost. Mean features are `(past sum + 20 × past global mean)/(past count + 20)`; zero count gives the global past mean. Median, maximum and standard deviation remain NaN if unsupported. High-cost rates are shrunk as `(past high-cost count + 50 × past global rate)/(past count + 50)`. Radius aggregates follow the same approach: nearby costs from other materials may be available, but they are not PU observations.

Inventory neighborhoods and endpoint routes use the same pipes.csv; repair-state features use only dates preceding the forecast origin. Neighborhood inventory candidates require known lay dates, so missing-lay-date pipes are excluded as neighbors. Endpoint connections are distinguished from planar crossings; geometry is a proxy, not excavated length or verified physical connectivity.

### Unusual values and limits on new inputs

Observed coordinates are finite, endpoint lengths are nonzero, and known lay dates precede 2019. These were checked before using the data; there is no universal invalid-value sanitization. Nonblank unseen strings follow category rules above; typos are not automatically distinguished from genuinely new categories. Duplicate IDs, unparseable dates, nonfinite coordinates, zero-length geometry or missing inventory IDs require correction and revalidation. Missing coordinates were not replaced with zero or another location.

Negative model predictions are clipped at zero with `max(prediction, 0)`. Log models are first transformed back with `exp`/`expm1` and their fitted correction factor, then clipped. Nonfinite predictions fail validation and are not saved; large predictions are not capped. CatBoost's saved CSV has 35 zero predictions; the other five candidates have none. These arise from model inference and nonnegative constraints, not blanket zero assignment to unseen materials; zero is not evidence of free repair. Counts are recorded in [input_quality_audit.json](evidence/input_quality_audit.json).

See [input_quality_by_pipe.csv](evidence/input_quality_by_pipe.csv) for per-row flags and [input_quality_audit.json](evidence/input_quality_audit.json) for counts. Material support and missing lay date are separate dimensions: a supported-material row can still have missing age.
'''

def feature_table(configs):
    rows=[]
    for n,c in sorted(configs.items()):
        pack=c['params'].get('feature_pack','surface only');features=c['features']
        rows.append({'model':n,'feature_pack':pack,'selected_columns':1 if n=='prior_surface_mean' else len(features),
          'output':('Surface mean cost') if n=='prior_surface_mean' else ('Log prediction → cost') if n in ['anthony_rf_log_mean','rion_lgb_log_mean_refit'] else ('Original-unit cost')})
    return pd.DataFrame(rows).to_markdown(index=False)



def interface_en(c):return '''## Model inputs, outputs and coordination with failure-timing models

### Shared inputs

- Inventory: `Pipe ID`, `Lay date`, `Material`, `Surface`, `GPS x1`, `GPS y1`, `GPS x2`, `GPS y2`. ID is a join/output key, not a predictor.
- Training/history: train.csv `Pipe ID`, `Date`, `Cost`. Date establishes historical years and cutoff. `Time` exists in the file but is not an input to these models.
- Scenario: year 2027, age reference 2027-01-01, observed history strictly before 2027-01-01. Full inventory and past history, not just one pipe row, are needed for neighborhood and route features.
- Estimator inputs: only selected derived columns, explicitly listed in [model_input_contract.json](evidence/model_input_contract.json) and each configs JSON `features`. Ensembles consume the same ten component predictions and apply their saved weights.

### Features and outputs by component

'''+feature_table(c)+'''

base covers year, material, surface, year-start age and endpoint length; inventory adds neighborhood inventory, past repair state, orientation and interactions; group_history adds material/surface/grid/age-band/route historical costs; local_history adds radius/nearest-neighbor historical costs; topology adds endpoint routes and their history; all combines every group. Exact columns are selected/removed by family, so pack names alone are not a full schema. The surface-mean configuration contains common columns, but actual inference only reads surface.

### Outputs

Each candidate returns one nonnegative point estimate of repair cost conditional on a failure in the 2027 scenario, in original cost units. Submitted CSVs contain only `id,predicted_cost`. They do not predict failure time, probability, uncertainty intervals, PU reliability or intervention priority. Input-quality and material-support metadata are separate files.

### Alignment with the failure-timing team

Share ID keys, inventory snapshot, observation cutoff, excluded IDs and material/lay-date missing flags. If that team retains repaired training IDs, repeat failures and material replacement need a separate state definition. For an annual budget, obtain failure probabilities `p_i` for the same population and interval and form `Σ p_i × predicted_cost_i`. If multiple failures are allowed, use expected event counts only after checking that this severity estimate applies to each event. The combined budget model has not thereby been independently validated.

The current severity models do not require realized failure month, weekday or hour; predicted failure dates were not inputs to these CSVs either. Substituting a predicted incident-date age changes the year-start specification and requires validation. For later years, update scenario year/year-start age and re-run inference without adding unobserved future repair history. Track unsupported-material coverage separately in the timing and cost models.
'''

if __name__=='__main__':main()
