"""Assemble, independently verify and document the optimized members."""
import argparse
import hashlib
import json
import importlib.metadata
from pathlib import Path
from contextlib import redirect_stdout
import io
import ast
import joblib
import numpy as np
import pandas as pd
import nbformat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import train
from features import HERE, FeatureBuilder
from optimize import ROOT, OUT, MODELS, CORE, predict

def forecast_year(year):
    builder=FeatureBuilder();q,x=builder.future(year)
    c=json.loads((MODELS/'training_contract.json').read_text())
    assert list(x)==c['features']
    f=q[['pipe_id']].assign(scenario_year=year)
    for name in CORE:f[name]=predict(joblib.load(MODELS/f'{name}.joblib'),x)
    weights=json.loads((MODELS/'ensemble_weights.json').read_text())
    for name,w in weights.items():f[name]=f[CORE].to_numpy()@np.array([w[n] for n in CORE])
    f['predicted_cost']=f[c['default_ensemble']]
    assert np.isfinite(f[CORE+['predicted_cost']].to_numpy()).all()
    f.to_csv(OUT/f'forecast_costs_{year}.csv',index=False)
    f[['pipe_id','scenario_year','predicted_cost']].to_csv(OUT/f'forecast_costs_{year}_adopted.csv',index=False)
    return f

def main():
    train.OUT=OUT;train.MODELS=MODELS
    # Import only after redirecting module constants to the isolated new run.
    import stabilize
    d=pd.read_csv(HERE/'data/training_rich.csv');oof=pd.read_csv(OUT/'out_of_time_predictions.csv')
    oof,weights=train.ensemble_methods(oof)
    oof.to_csv(OUT/'out_of_time_predictions.csv',index=False);weights.to_csv(OUT/'past_only_weights.csv',index=False)
    train.diagnostics(oof,d)
    final={'ensemble_equal':np.full(len(CORE),1/len(CORE)),
        'ensemble_rmse_weighted':train.fit_weights(oof,0),
        'ensemble_stable':.5*train.fit_weights(oof,.02)+.5/len(CORE)}
    train.dump(MODELS/'ensemble_weights.json',{n:dict(zip(CORE,w.tolist())) for n,w in final.items()})
    f=pd.read_csv(OUT/'forecast_costs_2027.csv')
    for name,w in final.items():f[name]=f[CORE].to_numpy()@w
    f.to_csv(OUT/'forecast_costs_2027.csv',index=False)
    stabilize.main()
    f=pd.read_csv(OUT/'forecast_costs_2027.csv')
    summary=pd.read_csv(OUT/'summary_metrics.csv').set_index('model')
    # Retrospective deployment choice, clearly distinct from temporal fitting.
    # Preserve every retrained family in production, as requested for
    # stabilization. Unconstrained weights remain a comparison benchmark.
    choices=summary.loc[['ensemble_equal','ensemble_stable','ensemble_balanced']]
    eligible=choices[choices.mean_annual_RMSE<=choices.mean_annual_RMSE.min()*1.01]
    selected=eligible.sort_values(['worst_absolute_annual_total_bias_pct','mean_absolute_annual_total_bias_pct','annual_relative_RMSE_sd']).index[0]
    contract=json.loads((MODELS/'training_contract.json').read_text())
    contract.update(default_ensemble=selected,default_is_provisional=False,
        adoption_reason='Among diversified ensemble methods (positive weight for every member) within 1% of their best mean annual RMSE, prefer lower worst annual total bias, then mean absolute bias, then relative annual RMSE variability.',
        selection_caveat='Deployment method chosen after inspecting retrospective 2023-2026 results; not an untouched holdout. No future labels used.')
    train.dump(MODELS/'training_contract.json',contract)
    f['predicted_cost']=f[selected];f.to_csv(OUT/'forecast_costs_2027.csv',index=False)
    f[['pipe_id','scenario_year','predicted_cost']].to_csv(OUT/'forecast_costs_2027_adopted.csv',index=False)
    validate(d,oof=pd.read_csv(OUT/'out_of_time_predictions.csv'),forecast=f,contract=contract)
    document(summary,contract)
    print('Optuna models and verified ensemble complete:',selected,flush=True)

def validate(d,oof,forecast,contract):
    assert len(d)==14113 and len(oof)==13035 and len(forecast)==27240
    assert d.event_id.is_unique and oof.event_id.is_unique and forecast.pipe_id.is_unique
    assert set(oof.event_id)==set(d.loc[d.event_year>=2020,'event_id'])
    assert np.allclose(oof.cost,d.set_index('event_id').cost.reindex(oof.event_id))
    assert np.isclose(d.cost.sum(),352997703.33)
    assert np.isfinite(oof[CORE].to_numpy()).all() and (oof[CORE].to_numpy()>=0).all()
    x=pd.read_csv(HERE/'data/forecast_features_2027.csv');sample=x.iloc[np.linspace(0,len(x)-1,100,dtype=int)]
    assert forecast.pipe_id.tolist()==x.pipe_id.tolist()
    configs=[]
    for name in CORE:
        bundle=joblib.load(MODELS/f'{name}.joblib')
        assert np.allclose(predict(bundle,sample),forecast[name].iloc[sample.index],rtol=1e-9,atol=1e-5),name
        for year in range(2020,2028):
            cfg=json.loads((OUT/'configs'/name/f'{year}.json').read_text())
            if name=='anthony_linear_raw':assert 'regularizer' in cfg['params']
            assert cfg['training_end']<year and all(y<year for y in cfg['inner_years'])
            assert cfg['training_rows']==int((d.event_year<year).sum())
            assert set(cfg['features'])<=set(contract['features'])
            trials=pd.read_csv(OUT/f'trials_{name}_{year}.csv') if year>2020 else pd.DataFrame()
            if year>2020:
                assert len(trials)==contract['optuna_trials'] and cfg['completed_trials']>0
                assert np.isclose(trials.loc[trials.state=='COMPLETE','value'],cfg['inner_mean_RMSE']).any()
            configs.append({'model':name,'prediction_year':year,'trials':len(trials),'completed_trials':cfg['completed_trials'],
                'feature_pack':cfg['params'].get('feature_pack','surface'),'inner_mean_RMSE':cfg['inner_mean_RMSE'],
                'training_end':cfg['training_end'],'training_rows':cfg['training_rows']})
        oof[['event_id','pipe_id','event_year','cost',name]].rename(columns={name:'predicted_cost'}).to_csv(OUT/f'output_{name}_out_of_time.csv',index=False)
        forecast[['pipe_id','scenario_year',name]].rename(columns={name:'predicted_cost'}).to_csv(OUT/f'output_{name}_2027.csv',index=False)
    for filename in ['past_only_weights.csv','balanced_past_only_weights.csv']:
        w=pd.read_csv(OUT/filename);assert (w.weight_training_end<w.test_year).all()
        by=['test_year']+(['method'] if 'method' in w else [])
        assert np.allclose(w.groupby(by).weight.sum(),1) and w.weight.ge(-1e-9).all()
    weights=json.loads((MODELS/'ensemble_weights.json').read_text())
    for method,w in weights.items():
        assert set(w)==set(CORE) and min(w.values())>=0 and np.isclose(sum(w.values()),1)
        assert np.allclose(forecast[CORE].to_numpy()@np.array([w[n] for n in CORE]),forecast[method],rtol=1e-10,atol=1e-6)
    for _,row in pd.read_csv(OUT/'annual_metrics.csv').iterrows():
        q=oof[oof.event_year==row.year]
        assert np.isclose(train.rmse(q.cost,q[row.model]),row.RMSE)
        assert np.isclose(100*(q[row.model].sum()/q.cost.sum()-1),row.total_bias_pct)
    builder=FeatureBuilder();checks=[]
    for year in range(2023,2027):
        q=builder.events[builder.events.event_year==year].head(8);before=builder.build(q,year)
        saved=builder.repair_date.copy();builder.repair_date[builder.repair_date>=np.datetime64(f'{year}-01-01')]=np.datetime64('2099-01-01')
        pd.testing.assert_frame_equal(before,builder.build(q,year));builder.repair_date=saved
        expected=d.loc[d.event_id.isin(q.event_id),contract['features']].reset_index(drop=True)
        pd.testing.assert_frame_equal(before,expected,check_dtype=False,rtol=1e-9,atol=1e-9)
        checks.append(year)
    q,_=builder.future(2027);q=q.head(8);clean=builder.build(q,2027)
    injected=pd.concat([builder.events,builder.events.head(1).assign(event_year=2030,cost=1e12)],ignore_index=True)
    pd.testing.assert_frame_equal(clean,builder.build(q,2027,injected))
    manifest=json.loads((HERE.parent/'ensemble_preparation/sources/manifest.json').read_text())
    for meta in manifest['local_inputs'].values():assert hashlib.sha256(Path(meta['path']).read_bytes()).hexdigest()==meta['sha256']
    pd.DataFrame(configs).to_csv(OUT/'selected_configs_summary.csv',index=False)
    train.dump(OUT/'validation.json',{'status':'passed','training_rows':len(d),'out_of_time_rows':len(oof),
        'evaluation_rows':int((oof.event_year>=2023).sum()),'future_supported_pipes':len(forecast),
        'features':len(contract['features']),'temporal_config_checks':len(configs),
        'saved_models_replayed':len(CORE),'all_metrics_and_blends_independently_recomputed':True,
        'future_date_mutation_invariance_years':checks,'future_cost_injection_invariance':True,
        'all_2026_and_earlier_events_retained':True,'source_commit':manifest['commit'],
        'versions':{name:importlib.metadata.version(name) for name in ['optuna','numpy','pandas','scipy','scikit-learn','xgboost','lightgbm','catboost','joblib']},
        'sha256':{str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [HERE/'data/training_rich.csv',HERE/'data/forecast_features_2027.csv',HERE/'features.py',HERE/'optimize.py',
             HERE/'finish_optuna.py',OUT/'out_of_time_predictions.csv',OUT/'forecast_costs_2027.csv']}})

def document(summary,c):
    oof=pd.read_csv(OUT/'out_of_time_predictions.csv');metrics=pd.read_csv(OUT/'annual_metrics.csv')
    methods=['prior_surface_mean','ensemble_equal','ensemble_rmse_weighted','ensemble_stable','ensemble_balanced']
    fig,ax=plt.subplots(1,2,figsize=(12,4))
    for name in methods:
        q=metrics[metrics.model==name];ax[0].plot(q.year,q.RMSE,marker='o',label=name);ax[1].plot(q.year,q.total_bias_pct,marker='o',label=name)
    ax[0].set(ylabel='RMSE in original cost units',xlabel='Validation year');ax[1].set(ylabel='Annual total bias (%)',xlabel='Validation year');ax[1].axhline(0,color='grey',lw=.7)
    for a in ax:a.set_xticks(range(2023,2027));a.grid(alpha=.2)
    fig.legend(*ax[0].get_legend_handles_labels(),loc='lower center',ncol=3,fontsize=8);fig.tight_layout(rect=(0,.15,1,1));fig.savefig(ROOT/'stability.png',dpi=180);plt.close(fig)
    table=summary.loc[methods,['mean_annual_RMSE','annual_RMSE_sd','mean_absolute_annual_total_bias_pct','worst_absolute_annual_total_bias_pct']].round(2).to_markdown()
    text=f'''# Ensembles after Optuna optimization

Thirty trials per model/origin. The 2020 cold start uses fixed settings because only 2019 training labels exist. Ten models across 2021–2027 give 2,100 trial slots, including convergence failures and interruptions during execution changes; completed counts are in CSVs. Rank valid trials by inner RMSE and verify convergence and finite predictions on full training data. Every 2027 base is refitted on all 14,113 events from 2019–2026.

Selected candidate: `{c['default_ensemble']}`. For diversification, compare equal, shrinkage, and constrained weights retaining positive weight on every component. Among these methods within 1% of their best mean annual RMSE, compare worst absolute annual total bias, mean absolute bias, and relative annual RMSE variation, in that order. Unconstrained RMSE weights remain a benchmark. Selection followed inspection of historical results, so this is not untouched-holdout evaluation.

{table}

## Leakage prevention

For outer year Y, train only on earlier years and validate forward on the latest two inner years. Feature selection, preprocessing, search, log correction, and weight learning exclude outer-year outcomes. Each inner prediction also uses only preceding labels. Spatial distances are meters; historical repair-state and cost summaries use observations strictly before January 1 of each year.

Weights use 13,035 valid forward OOF predictions from 2020–2026. No 2019 OOF predictions are produced because earlier training labels are unavailable. Final bases use all 14,113 events, including 1,078 from 2019.

Exclude Shana's existing predictions and predictions requiring realized future failure times or weekdays. Use only newly optimized/refitted Anthony/Rion model families and Takito's three models.

## Search scope

The full search is in `../optimize.py` function `space()`. It covers six feature packs; OLS/Ridge/Lasso/ElasticNet with regularization, L1 ratio, intercept, and nonnegative-coefficient options; Gamma L2/intercept; RF tree count/depth, minimum split/leaf sizes, feature fraction, maximum leaves, bootstrap/sample fraction, and two squared-error criteria; and booster learning rates, iterations, complexity, regularization, sample/feature fractions, and bins. XGBoost/LightGBM search L1/L2; CatBoost searches L2. Log models compare no correction, training-residual correction, and past-OOF correction.

Linear models standardize numeric features within each training period and normalize targets by training mean cost, then restore original units. Ridge alpha ranges from 1e-4 to 1e5; Lasso/ElasticNet alpha from 1e-4 to 10 on normalized targets; ElasticNet L1 ratio from 0.01 to 0.99. The initial OLS-only search is archived in `previous_ols/`; the adopted linear procedure ran a separate 30-trial study.

Not every library option was searched. Seeds, threads, target, objective, CPU implementation, and convergence controls are fixed. RF absolute_error/Poisson and other booster/loss families are outside scope. Thirty trials do not guarantee exhaustive search or global optimality. Additional features for Gamma/linear families make this a temporally controlled improvement within the same model families, not numerical reproduction of the original notebooks.

## Applying predictions to budgets

The 2027 CSV estimates repair costs conditional on failure. Future budgets require matching failure probabilities or expected counts. Historical total bias validates these conditional estimates on observed failures; summing costs across all future pipes does not produce an annual budget.

Forecasts cover 27,240 supported-material unrepaired pipes. Native/replaced PU (15,791) and eight unknown-material pipes lack conditional-cost training labels; these 15,799 pipes are tracked as unestimated rather than assigned zero. History is frozen at end-2026 for 2027 onward; unknown future repairs/costs are not added.

## Reproduction and artifacts

Run `python ensemble_training/run_optuna.py` for 30 trials per model, full refitting, ensemble construction, and validation (five independent local processes). Studies are stored in SQLite and completed annual predictions are reused. For later years, use `python ensemble_training/finish_optuna.py --year 2030`.

Selected settings and trials are in `results/selected_configs_summary.csv`, `results/trials_*.csv`, and `results/configs/`. `results/validation.json` records independent recomputation, saved-model replay, and future-label/date mutation checks. Adopted forecasts are in `results/forecast_costs_2027_adopted.csv`; historical forward predictions are in `results/out_of_time_predictions.csv`. Original fixed-grid artifacts are preserved.

Input source: GitHub `reinesana/STAT440-star-kingdom-project` commit `{json.loads((OUT/'validation.json').read_text())['source_commit']}`. File hashes and retrieval details: `../../ensemble_preparation/sources/manifest.json`.
'''
    (ROOT/'README.md').write_text(text,encoding='utf-8')
    notebook=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(text),nbformat.v4.new_code_cell("from pathlib import Path\nimport pandas as pd\ncandidates=[Path.cwd(),Path.cwd()/'optuna',Path.cwd()/'ensemble_training'/'optuna']\nroot=next(p for p in candidates if (p/'search_policy.json').exists())\npd.read_csv(root/'results'/'summary_metrics.csv')"),nbformat.v4.new_code_cell("pd.read_csv(root/'results'/'selected_configs_summary.csv')")])
    # Actually execute cells in one Python namespace; no Jupyter kernel installed.
    namespace={};counter=0
    for cell in notebook.cells:
        if cell.cell_type!='code':continue
        counter+=1;cell.execution_count=counter;tree=ast.parse(cell.source)
        tail=tree.body.pop() if isinstance(tree.body[-1],ast.Expr) else None
        stream=io.StringIO()
        with redirect_stdout(stream):
            exec(compile(tree,'review.ipynb','exec'),namespace)
            result=eval(compile(ast.Expression(tail.value),'review.ipynb','eval'),namespace) if tail else None
        cell.outputs=[]
        if stream.getvalue():cell.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=stream.getvalue()))
        if result is not None:
            data={'text/plain':str(result)}
            if isinstance(result,pd.DataFrame):data['text/html']=result.to_html(index=False)
            cell.outputs.append(nbformat.v4.new_output('execute_result',execution_count=counter,data=data))
    nbformat.write(notebook,ROOT/'review.ipynb')

if __name__=='__main__':
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument('--year',type=int);args=p.parse_args()
    if args.year:
        if args.year<2027:p.error('Year must be >=2027')
        forecast_year(args.year)
    else:main()
