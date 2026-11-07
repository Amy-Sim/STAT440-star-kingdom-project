"""Write a compact Japanese result with inspectable per-fold settings."""
from pathlib import Path
import json,sqlite3
import pandas as pd

OUT=Path(__file__).resolve().parent
m=pd.read_csv(OUT/'fold_metrics.csv')
a=pd.read_csv(OUT/'average_metrics.csv')
manifest=json.loads((OUT/'feature_manifest.json').read_text())
verify=json.loads((OUT/'verification.json').read_text())
def table(df):
    head='| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'
    return head+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in df.itertuples(index=False,name=None))+'\n'
text=['# Construction cost prediction comparison of 3 single boosting models \n',
    'Used all 14,107 rows of the specified `github-main/data/train_predict_cost.csv`. Features and parameters were selected primarily by RMSE in original cost units, then tested using the specified four folds.\n',
    '## 4Fold simple average \n']
av=a.copy()
for c in ['MAE','RMSE']: av[c]=av[c].map(lambda v:f'{v:,.2f}')
text.append(table(av))
text.append('These average years equally. Pooled event-level metrics are retained separately in `pooled_metrics.csv` and are distinct from the requested annual means.\n')
text.append('## Test value for each Fold \n')
cols=['model','fold','train_end','test_year','n_train','n_test','MAE','RMSE']
mm=m[cols].copy()
for c in ['MAE','RMSE']: mm[c]=mm[c].map(lambda v:f'{v:,.2f}')
text.append(table(mm))
text.append('## Value on learning data (reference) \n')
tr=m[['model','fold','train_MAE','train_RMSE']].copy()
for c in ['train_MAE','train_RMSE']: tr[c]=tr[c].map(lambda v:f'{v:,.2f}')
text.append(table(tr))
text.append('Training errors measure fit to the same data used to train the model; assess future performance using the test values above. Training periods overlap across folds.\n')
text.append('## Selected features/settings \n')
summary,details,search=[] ,[],[]
for model in ['xgboost','catboost','lightgbm']:
    for year in range(2023,2027):
        folder=OUT/model/str(year)
        c=json.loads((folder/'selected.json').read_text())
        summary.append({'model':model,'test_year':year,'feature_count':len(c['features']),'trees':c['iterations'],'inner_RMSE':f'{c["inner_mean_rmse"]:,.2f}'})
        details.append({'model':model,'test_year':year,'features':json.dumps(c['features'],ensure_ascii=False),'parameters':json.dumps(c['params'],sort_keys=True),'trees':c['iterations']})
        with sqlite3.connect(folder/'studies.sqlite') as db:
            rows=db.execute('SELECT study_name,state,COUNT(*) FROM trials JOIN studies ON trials.study_id=studies.study_id GROUP BY study_name,state').fetchall()
        for stage,state,n in rows:
            search.append({'model':model,'test_year':year,'stage':stage,'state':state,'trials':n})
        text.append(f'### {model} — test{year} year\n')
        text.append('Features: `'+'`, `'.join(c['features'])+'`.\n')
        text.append('Parameters:\n```json\n'+json.dumps(c['params'],indent=2)+'\n```\n')
        actual=int(m.loc[(m.model==model)&(m.test_year==year),'actual_trees'].iloc[0])
        text.append(f'Iteration limit:{c["iterations"]}. Trees in final fit:{actual}. Inner mean RMSE:{c["inner_mean_rmse"]:,.2f}.\n')
pd.DataFrame(summary).to_csv(OUT/'selected_config_summary.csv',index=False)
pd.DataFrame(details).to_csv(OUT/'selected_features_and_parameters.csv',index=False)
search=pd.DataFrame(search)
search.to_csv(OUT/'search_counts.csv',index=False)
complete=int(search.loc[search.state=='COMPLETE','trials'].sum())
text.insert(2,f'Total completed Optuna trials:{complete:,} completed. Feature additions/removals were also assessed within temporal validation. This is the best candidate found in a finite search, not a guaranteed global optimum.\n')
text.append('## Method and verification\n')
text.append('For each fold, use its two latest training years as temporal validation and minimize their equal-weight mean RMSE. After early-stopping exploration, rerank up to five promising configurations using the same tree count in both years. CatBoost is refitted from scratch for each candidate tree count. All 12 configurations were fixed before outer testing. Historical cost features use only costs through the preceding year, assuming those costs are available at the next year-start.\n')
text.append('No cost capping, outlier removal, logarithmic target, or model ensemble was used. Negative predictions were clipped to zero.\n')
text.append(f'Verified the original CSV SHA-256, actual costs, and target IDs; checked historical statistics on{verify["history_samples_verified"]} records independently. Twelve-fold MAE/RMSE and four-fold means were independently recomputed from event-level predictions. Historical-statistic checks were sampled, not an independent recomputation of all rows.\n')
text.append(f'For all four folds, multiply costs from the test year onward by 37 and add 1,234,567, rerun cost-dependent preprocessing, and verify features through that year are unchanged. Candidate columns:{len(manifest["features"])} columns. Cost-independent inventory features were checked structurally and through independent calculations on 24 records across six radii. Training MAE/RMSE were independently recomputed from saved event-level training predictions.\n')
text.append('The expanded search adds neighborhood inventory features and candidates from earlier experiment code. For each model/fold, compare individual additions, removal of selected features, substitutions with absolute training Spearman correlation at least 0.98, equivalent categorical/numeric encodings, and grouped additions/removals. After each improvement, update the baseline and repeat all comparisons. Retune parameters and a shared iteration count for 60 trials each, then repeat feature comparisons to convergence. Verify agreement between the feature set used during parameter search and the rechecked final set. High correlation alone does not exclude a feature; validation RMSE decides. Nearby-segment historical costs were also tested, without claiming actual repair locations or physical connections. Adoption paths and comparisons are saved in expanded_adoption_paths.csv and expanded_candidate_comparisons.csv; fold correlations are in expanded_correlations.csv. Earlier test outputs were archived and their errors were not used in the added search.\n')
text.append('The supplied files include data through end-2026; this does not assert that all outcomes were known on the execution date. Earlier work already inspected 2026. Test costs were excluded from this search, but 2026 is not an untouched project-wide final holdout.\n')
text.append('Neighborhood features exclude pipes installed after the event date and pipes with unknown lay dates. Inventory attributes are assumed valid at forecast time; removal and material/surface change histories are unavailable. Crossings and shared endpoints do not establish verified physical connections. Straight endpoint distance is not actual curved or excavated length.\n')
(OUT/'results.md').write_text('\n'.join(text),encoding='utf-8')
print(a.to_string(index=False))
print('Completed Optuna trials:',complete)
