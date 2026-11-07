"""Publish English, evidence-backed candidate files into the repository checkout."""
from pathlib import Path
import sys, json, shutil, hashlib
import numpy as np
import pandas as pd
import joblib
from features import FeatureBuilder, HERE, BASE
from optimize import predict, CORE, MODELS, OUT

DEST=HERE.parent/'github-main/notebooks/ensemble_for_cost_prediction'
METHODS=['takito_catboost','ensemble_equal','ensemble_stable','ensemble_balanced','ensemble_rmse_weighted','prior_surface_mean']
DESCRIPTIONS = {'takito_catboost': ('Best single model: CatBoost', 'One raw-cost CatBoost model. Lowest mean annual and pooled RMSE among evaluated single models; higher budget bias.'), 'ensemble_equal': ('Equal-weight ensemble', 'Ten components, each weighted 10%. Lowest mean annual RMSE among the ensembles.'), 'ensemble_stable': ('Shrinkage ensemble (budget-focused default)', '50% regularized past-OOF RMSE weights + 50% equal weights. Every component has at least 5% weight. Lowest mean and worst absolute annual total bias among compared candidates.'), 'ensemble_balanced': ('Constrained balance ensemble', 'Past-only optimization considers annual total bias, relative annual RMSE variation and a uniform-weight penalty, with 1–70% component weights and an RMSE constraint. Its observed bias is worse than shrinkage.'), 'ensemble_rmse_weighted': ('RMSE-optimized ensemble', 'Nonnegative weights summing to one minimize past mean annual RMSE. Zero weights are allowed; concentration risk remains.'), 'prior_surface_mean': ('Surface mean (reference)', 'All-history surface-specific mean, shrunk toward the global mean using an Optuna-selected smoothing strength.')}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    for folder in ['predictions','evidence','configs','training_code']: (DEST/folder).mkdir(exist_ok=True)
    pipes=pd.read_csv(HERE.parent/'github-main/data/pipes.csv');train=pd.read_csv(HERE.parent/'github-main/data/train.csv')
    target=pipes.loc[~pipes['Pipe ID'].isin(train['Pipe ID'])].copy()
    saved=pd.read_csv(OUT/'forecast_costs_2027.csv')
    extra=target.loc[~target['Pipe ID'].isin(saved.pipe_id)].copy()
    assert len(train)==14113 and train['Pipe ID'].is_unique and len(target)==28926
    builder=FeatureBuilder()
    q=pd.DataFrame({'pipe_id':extra['Pipe ID'].to_numpy(),'scenario_year':2027,
       'material':extra.Material.fillna('__unknown__').to_numpy(),'surface':extra.Surface.fillna('__unknown__').to_numpy()})
    q['pipe_length_m']=np.linalg.norm(extra[['GPS x2','GPS y2']].to_numpy()-extra[['GPS x1','GPS y1']].to_numpy(),axis=1)
    q['log1p_pipe_length_m']=np.log1p(q.pipe_length_m)
    q['midpoint_x_m']=(extra['GPS x1'].to_numpy()+extra['GPS x2'].to_numpy())/2
    q['midpoint_y_m']=(extra['GPS y1'].to_numpy()+extra['GPS y2'].to_numpy())/2
    q['age_at_year_start']=(pd.Timestamp('2027-01-01')-pd.to_datetime(extra['Lay date'])).dt.days.to_numpy()/365.25
    q['age_missing']=q.age_at_year_start.isna().astype(int);q['log1p_age_at_year_start']=np.log1p(q.age_at_year_start)
    q['material_surface']=q.material+' | '+q.surface
    x=builder.build(q,origin_year=2027)
    ext=q[['pipe_id']].copy();weights=json.loads((MODELS/'ensemble_weights.json').read_text())
    for name in CORE:
        cfg=json.loads((OUT/'configs'/name/'2027.json').read_text());assert cfg['training_rows']==len(train) and cfg['training_end']==2026
        bundle=joblib.load(MODELS/(name+'.joblib'));ext[name]=predict(bundle,x)
        assert np.isfinite(ext[name]).all()
        shutil.copy2(OUT/'configs'/name/'2027.json',DEST/'configs'/f'{name}_2027.json')
        print('Replayed full-data model:',name,flush=True)
    for method,w in weights.items():ext[method]=ext[CORE].to_numpy()@np.array([w[n] for n in CORE])
    joined=pd.concat([saved[['pipe_id']+METHODS],ext[['pipe_id']+METHODS]],ignore_index=True)
    assert joined.pipe_id.is_unique and set(joined.pipe_id)==set(target['Pipe ID'])
    for method in METHODS:
        result=joined[['pipe_id',method]].rename(columns={'pipe_id':'id',method:'predicted_cost'})
        result=result.sort_values(['predicted_cost','id'],ascending=[False,True]).reset_index(drop=True)
        assert len(result)==len(target) and np.isfinite(result.predicted_cost).all() and result.predicted_cost.ge(0).all()
        result.to_csv(DEST/'predictions'/f'{method}.csv',index=False,float_format='%.10f')
        read=pd.read_csv(DEST/'predictions'/f'{method}.csv')
        assert read.columns.tolist()==['id','predicted_cost'] and read.predicted_cost.is_monotonic_decreasing
    scope=target[['Pipe ID','Material']].rename(columns={'Pipe ID':'id','Material':'material'})
    scope['prediction_support']=np.where(scope.id.isin(extra['Pipe ID']),'unvalidated_unseen_material_extrapolation','supported_material')
    scope.to_csv(DEST/'evidence/prediction_scope.csv',index=False)
    summary=pd.read_csv(OUT/'summary_metrics.csv').set_index('model')
    annual=pd.read_csv(OUT/'annual_metrics.csv')
    for filename in ['summary_metrics.csv','annual_metrics.csv','selected_configs_summary.csv','validation.json','out_of_time_weights.csv']:
        source=OUT/filename
        if source.exists():shutil.copy2(source,DEST/'evidence'/filename)
    shutil.copy2(MODELS/'ensemble_weights.json',DEST/'evidence/ensemble_weights.json')
    shutil.copy2(MODELS/'training_contract.json',DEST/'evidence/training_contract.json')
    shutil.copy2(HERE/'optuna/search_policy.json',DEST/'evidence/search_policy.json')
    for name in ['features.py','optimize.py','train.py','stabilize.py','finish_optuna.py','run_optuna.py','package_candidates.py']:
        shutil.copy2(HERE/name,DEST/'training_code'/name)
    shutil.copy2(HERE/'optuna/sources.html',DEST/'evidence/sources.html')
    shutil.copy2(HERE/'optuna/sources.json',DEST/'evidence/sources.json')
    model_table=[]
    for n in CORE:
        c=json.loads((DEST/'configs'/f'{n}_2027.json').read_text())
        model_table.append([n,c['params'].get('feature_pack','surface'),len(c.get('features',[])),json.dumps(c['params'],ensure_ascii=False)])
    pd.DataFrame(model_table,columns=['model','feature_pack','n_features','parameters']).to_csv(DEST/'evidence/final_model_settings.csv',index=False)
    weights_table=pd.DataFrame({m:([1. if n=='takito_catboost' else 0. for n in CORE] if m=='takito_catboost' else [1. if n=='prior_surface_mean' else 0. for n in CORE] if m=='prior_surface_mean' else [weights[m][n] for n in CORE]) for m in METHODS},index=CORE)
    weights_table.index.name='component';weights_table.to_csv(DEST/'evidence/candidate_weights.csv')
    for lang in ['en']:write_report(lang,summary,annual,weights_table,model_table,len(target),len(extra))
    manifest={'status':'passed','scenario_year':2027,'training_rows':14113,'inventory_rows':len(pipes),'skipped_training_ids':len(train),
      'prediction_rows_per_candidate':len(target),'supported_material_rows':len(saved),'unvalidated_material_rows':len(extra),
      'unvalidated_material_breakdown':{'polyurethane':1678,'missing':8},'candidates':METHODS,'sort':'predicted_cost descending, id ascending ties',
      'columns':['id','predicted_cost'],'seed':440,'finite_nonnegative_predictions':True,'exact_inventory_minus_train_id_coverage':True,
      'source_sha256':{str(p.relative_to(HERE.parent)):digest(p) for p in [HERE.parent/'github-main/data/train.csv',HERE.parent/'github-main/data/pipes.csv',OUT/'forecast_costs_2027.csv']},
      'prediction_sha256':{p.name:digest(p) for p in (DEST/'predictions').glob('*.csv')}}
    (DEST/'evidence/export_validation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (DEST/'README.md').write_text('# Repair cost model candidates for 2027\n\n[English report](report_en.md)\n\nSix CSVs are in `predictions/`: five model candidates plus one reference. Each contains all 28,926 inventory IDs absent from train.csv, with exactly `id,predicted_cost`, sorted by decreasing cost. See the reports before using the 1,686 extrapolated rows.\n\n[Export validation](evidence/export_validation.json) · [Model composition](evidence/candidate_weights.csv) · [Final settings](evidence/final_model_settings.csv) · [Sources](evidence/sources.html)\n\nTraining-code snapshots are provided for inspection. They retain their original workspace paths and are not a standalone execution package; the CSV exporter was run in the original reviewed workspace. Fitted model binaries and large intermediate feature tables are not included.\n',encoding='utf-8')
    print('Validated package:',DEST,flush=True)

def write_report(lang,s,a,w,settings,n,extra):
    title='Repair cost prediction: single-model and ensemble candidates'
    text=[f'# {title}', '']
    text.append(('CatBoost is now an explicit candidate: it has the best single-model RMSE. The shrinkage ensemble remains the budget-focused default because it has smaller annual total bias. The candidate set has been expanded without automatically replacing that default.'))
    text+=['', '## '+('Observed evaluation results'),'']
    metric_cols=['mean_annual_RMSE','pooled_RMSE','annual_RMSE_sd','mean_absolute_annual_total_bias_pct','worst_absolute_annual_total_bias_pct']
    table=s.loc[METHODS,metric_cols].copy();table.index.name='candidate'
    text.append(table.to_markdown(floatfmt='.2f'))
    text.append('')
    text.append(('Evaluation covers 8,592 observed repair events in 2023–2026. RMSE in original cost units is primary. Mean annual RMSE gives each year equal weight; pooled RMSE combines all events; annual_RMSE_sd is the sample standard deviation across four years. Annual total bias is 100 × (predicted total / observed total − 1); the table reports the mean and maximum absolute annual bias.'))
    text+=['',('CatBoost mean annual RMSE is 124,569.85 versus 125,230.52 for shrinkage (about 0.53% higher). Worst absolute annual total bias is 34.45% versus 10.02%. Shrinkage annual RMSE standard deviation is about 2.34% higher than the reference: annual RMSE stabilization has not been established. Budget-bias improvement and RMSE variation should be assessed separately.'),'']
    text+=['## '+('Candidate explanations'),'']
    for method in METHODS:
        d=DESCRIPTIONS[method];text +=['### '+d[0],d[1],'',f'CSV: [predictions/{method}.csv](predictions/{method}.csv)','']
    text+=['## '+('Components and final deployment weights'),'']
    text.append((w*100).to_markdown(floatfmt='.2f'));text+=['',('Weights are percentages. Ensembles combine the same ten components: surface mean; Anthony linear/Gamma/log-RF; Takito XGBoost/CatBoost/LightGBM; Rion Gamma/raw-RF/log-LightGBM. Log-model back-transform corrections were also selected using past data only.'),'']
    text+=['## '+('Work performed and leakage controls'),'']
    text.append(('1. Retained all 14,113 train.csv events from 2019–2026 and joined inventory by ID. Restored six missing-date records; no expensive events were removed or capped.\n2. Built January-1 age, material/surface, metric distances, inventory neighborhoods, endpoint routes and past-cost aggregates using labels strictly before each prediction year. Coordinates are meters; planar crossings do not imply connectivity.\n3. Ran 30 Optuna trials per model/origin in 2021–2027, with up to two latest preceding inner validation years and six feature packs. The 2020 cold start uses fixed settings. Of 2,100 trial slots, 1,978 completed and 122 failed/were interrupted.\n4. Compared OLS/Ridge/Lasso/ElasticNet; searched L1/L2 for XGBoost/LightGBM, L2 for Gamma/CatBoost, and structural controls for RF. Final Anthony linear regression selected no regularization. Gamma L1 was not evaluated.\n5. Learned ensemble weights only from preceding OOF years. Final 2027 components were trained on all 14,113 events with seed 440. Excluded existing Shana predictions and models requiring unavailable realized failure time/weekday.\n6. Verified ten saved models, 80 temporal configurations, independent metric/blend recomputation and invariance to future cost/date changes.'))
    text+=['','## '+('Best single-model settings'),'']
    cfg=json.loads((DEST/'configs/takito_catboost_2027.json').read_text());text+=['```json',json.dumps(cfg['params'],indent=2),'```','']
    text.append(('Final CatBoost selected 49 topology-pack features, depth 2 and 150 iterations. These are deployment settings for 2027; each historical fold used separately tuned past-only settings. All ten final configurations are in configs/ and evidence/final_model_settings.csv.'))
    text+=['','## '+('Prediction population and interpretation'),'']
    text.append((f'The actual inventory filename is pipes.csv. All 43,039 IDs were considered and the 14,113 IDs in train.csv skipped, leaving {n:,} predictions per candidate. CSVs contain exactly id,predicted_cost, sorted by decreasing cost and then ascending ID. Scenario year is 2027 with history frozen at end-2026. Predictions for 27,240 supported-material pipes come from saved full-data fits; the same models additionally predict {extra:,} pipes (1,678 PU and eight missing-material rows). No cost labels exist for these materials. These predictions use native unknown-category handling and are unvalidated extrapolations, outside the OOF evaluation. They are numeric estimates, not zero assignments, but should not be budgeted with the same confidence as supported-material estimates. Identify them in evidence/prediction_scope.csv.'))
    text+=['',('Costs are conditional on a failure, not repair necessity or failure probability. Summing every CSV row does not produce an annual budget: failure probabilities/counts are needed. Monetary units follow the source data and are not assumed to be yen. Candidate selection follows inspection of historical results; this is not an untouched final holdout guarantee.'),'','## '+('Annual results'),'']
    text.append(a[a.model.isin(METHODS)][['model','year','n_test','RMSE','total_bias_pct']].to_markdown(index=False,floatfmt='.2f'))
    text+=['','## '+('Sources and validation'),'','Source snapshot: `a09355d835d9acbb5746f11edcddd0cfd5e8ec3e`. [Training labels](https://github.com/reinesana/STAT440-star-kingdom-project/blob/a09355d835d9acbb5746f11edcddd0cfd5e8ec3e/data/train.csv), [Inventory](https://github.com/reinesana/STAT440-star-kingdom-project/blob/a09355d835d9acbb5746f11edcddd0cfd5e8ec3e/data/pipes.csv).','[Sources receipt](evidence/sources.html) · [Temporal validation](evidence/validation.json) · [Export checks](evidence/export_validation.json) · [Per-pipe support](evidence/prediction_scope.csv)','']
    (DEST/f'report_{lang}.md').write_text('\n'.join(text),encoding='utf-8')

if __name__=='__main__':main()
