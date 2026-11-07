"""Replace only repair-cost severity on the best documented public plan (20a).
Read-only GitHub evidence checked at main commit668a598ba8efd478d1c5bf569b39fc7fb93162e2.
"""
from pathlib import Path
import sys,hashlib,json,shutil,csv
from collections import Counter
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'survival-models-worktree'
sys.path.insert(0,str(WORK/'src'))
import simulate_score as sim
import search_orders as so
from build_candidate_16 import team_inputs
from build_candidate_17 import p17b
from build_baseline import IRON
from build_cost_submissions import validate
HERE=Path(__file__).resolve().parent
BASE=WORK/'submissions/2026-10-22_candidate_20_sameyear_merge/20a_sameyear_merge_17b_order.csv'
STACK=ROOT/'github-main/notebooks/Takito_Kobayashi/2026-10-26/AllModelStacking'
OLD=ROOT/'ensemble_training/optuna/results/forecast_costs_2027.csv'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def blob_hash(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
# Windows checkout line endings may differ from Git's canonical blob.
canonical=BASE.read_bytes().replace(b'\r\n',b'\n')
assert blob_hash(canonical)=='5b2a0f4a7a552a05f611f8dba4df9c57e49296df','Local best20a differs from current GitHub blob'
config=json.loads((STACK/'weights_2027.json').read_text())
weights={k:v for k,v in config['weights'].items() if v!=0}
assert set(weights)=={'takito_catboost','anthony_rf_log_mean'}
assert abs(weights['takito_catboost']-.6862701169749837)<1e-14
assert abs(sum(weights.values())-1)<1e-14
forecast=pd.read_csv(STACK/'predictions_2027.csv',dtype={'pipe_id':str})
sources=pd.read_csv(OLD,dtype={'pipe_id':str}).set_index('pipe_id')
assert forecast.pipe_id.is_unique and sources.index.is_unique
recomputed=sum(w*sources.reindex(forecast.pipe_id)[name].to_numpy(float) for name,w in weights.items())
np.testing.assert_allclose(recomputed,forecast.predicted_repair_cost,rtol=1e-12,atol=1e-8)
pipes,a,b=sim.load();lengths=pipes.len.to_numpy()
p_ml,stable=team_inputs(pipes);prob=p17b(pipes,p_ml)
active=(~(pipes.mat.eq('polyurethane')|pipes.leak_date.notna())).to_numpy()
severity=pipes['Pipe ID'].map(forecast.set_index('pipe_id').predicted_repair_cost).to_numpy(float)
missing=active&~np.isfinite(severity)
severity[missing]=stable[missing]
severity[~active]=0
assert np.isfinite(severity).all() and (severity>=0).all()
assert np.isfinite(prob).all() and ((prob>=0)&(prob<=1)).all()
lines=BASE.read_text(encoding='utf-8').splitlines()
xy,r=sim.read_units(BASE);inside=sim.containment(xy,r,a,b,lengths)
dummy=np.zeros((len(pipes),len(sim.YEARS)))
history=pd.read_csv(WORK/'data/train.csv',dtype={'Pipe ID':str})
target=pipes.Material.isin(IRON).to_numpy()
# The existing final greedy order must be a fixed point when re-ordered using its
# original costs and identical risk/ranking rule. This checks tie handling too.
oldvalue=np.clip(prob*(stable-200*lengths),0,None)
control_order=so.order_dynamic(inside,r,pipes,lengths,value_by_year=dummy,static_value=oldvalue,blend=1.)
assert [lines[k] for k in control_order]==lines,'Original20a order not reproduced'
control=HERE/'20a_original_control.csv';shutil.copyfile(BASE,control)
assert digest(control)==digest(BASE)
newvalue=np.clip(prob*(severity-200*lengths),0,None)
order=so.order_dynamic(inside,r,pipes,lengths,value_by_year=dummy,static_value=newvalue,blend=1.)
assert sorted(order)==list(range(len(lines)))
output=HERE/'21a_20a_catboost6863_logrf3137.csv'
output.write_text('\n'.join(lines[k] for k in order)+'\n',encoding='utf-8')
assert Counter(output.read_text().splitlines())==Counter(lines)
rep=validate(output,pipes,history,a,b,(a+b)/2,lengths,target)
control_rep=validate(control,pipes,history,a,b,(a+b)/2,lengths,target)
# These audit CSVs are not submission files.
rank=np.empty(len(lines),int);rank[order]=np.arange(1,len(lines)+1)
pd.DataFrame(dict(original20a_rank=np.arange(1,len(lines)+1),new_rank=rank,circle_x=xy[:,0],circle_y=xy[:,1],radius_m=r)).to_csv(HERE/'order_change.audit.csv',index=False)
pd.DataFrame(dict(pipe_id=pipes['Pipe ID'],active=active,leak_probability=prob,old_severity=stable,new_severity=severity,new_value=newvalue,used_old_severity_fallback=missing)).to_csv(HERE/'severity_join.audit.csv',index=False)
inputs=[BASE,STACK/'predictions_2027.csv',STACK/'weights_2027.json',OLD,WORK/'data/pipes.csv',WORK/'data/train.csv',WORK/'notebooks/ensemble_for_cost_prediction/predictions/ensemble_stable.csv',WORK/'submissions/2026-10-20_rion_dynamic/source/probabilities.csv',WORK/'src/build_candidate_17.py',WORK/'src/build_candidate_16.py',WORK/'src/search_orders.py',WORK/'src/build_cost_submissions.py',Path(__file__)]
manifest=dict(candidate=output.name,reference='20a_sameyear_merge_17b_order.csv',reference_public_score_millions=74.03,reference_score_source='https://github.com/reinesana/STAT440-star-kingdom-project/blob/668a598ba8efd478d1c5bf569b39fc7fb93162e2/src/calibrate_simulator.py',github_main_commit='668a598ba8efd478d1c5bf569b39fc7fb93162e2',github_reference_blob_sha1=blob_hash(canonical),local_reference_matches_github_canonical_blob=True,original_control_byte_identical=True,original20a_order_reproduced=True,exact_repair_cost_weights=weights,repair_cost_weighted_forecast_recomputed=True,geometry='20a frozen circles; same circle multiset; only execution order changes',leak_probabilities='unchanged p17b from build_candidate_17.py',priority='dynamic overlap update, clipped p*(conditional cost-200*length), blend=1',unsupported_active_fallback_ids=pipes.loc[missing,'Pipe ID'].tolist(),unsupported_fallback='unchanged stable-control severity; eight unknown-material pipes',rows=len(lines),changed_rank_rows=int((rank!=np.arange(1,len(lines)+1)).sum()),submission_sha256=digest(output),control_sha256=digest(control),new_validation=rep,control_validation=control_rep,source_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},public_score_millions=None,limitations=['No new official score;74.03M belongs to original20a only.','Construction/budget validation assumes no future leaks; not an official score forecast.','Geometry was optimized under the prior recipe and deliberately frozen for cost-only comparison.','Conditional repair-cost backtests reuse previously inspected historical years.'])
dump(HERE/'manifest.json',manifest)
notes=f'''# Replace the repair-cost predictor in the best-scoring 20a plan

**Submission file: 21a_20a_catboost6863_logrf3137.csv**

GitHub main (commit668a598) and the current shared document identify 20a at 74.03M as the previous best. This is a distinct candidate from the earlier 18a-based CSV.

Retain 20a geometry, p17b leak probabilities, and dynamic overlap-aware work prioritization; change only conditional repair-cost predictions. Weights: CatBoost {weights['takito_catboost']:.15f} + corrected log RF {weights['anthony_rf_log_mean']:.15f}. Saved 2027 forecasts were recomputed from base predictions and matched. Eight unsupported unreplaced pipes with unknown material retain the common original stable predictions.

Submission CSV: no header, two columns containing circle center and radius.{len(lines):,} rows. Circle sets match original 20a. Verified full iron coverage, finite predictions, exported CSV readback, and no-leak budget-feasible completion by 2051. Completion year under those conditions:{rep['completion_year']}; construction costs: ${rep['construction_cost']:,.2f}. This is not an official-score forecast.

20a_original_control.csv is a byte-identical copy of original 20a. Reordering original 20a with its existing cost forecasts also reproduced its order. No score for the new candidate was available at that stage; do not interpret 74.03M as its result.

Submit only 21a_20a_catboost6863_logrf3137.csv. Do not submit audit.csv, manifest.json, or validation.json. Use 20a_original_control.csv only to rescore the original plan for comparison.

Reproduce by running build_submission.py with .venv-eda/Scripts/python.exe from the project root. Source SHA-256 hashes and GitHub references are in manifest.json. This historical run neither published to GitHub nor edited the shared document.
'''
(HERE/'README.md').write_text(notes,encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ['candidate','reference_public_score_millions','local_reference_matches_github_canonical_blob','original20a_order_reproduced','exact_repair_cost_weights','rows','changed_rank_rows','unsupported_active_fallback_ids','submission_sha256']},ensure_ascii=False,indent=2),flush=True)
print(json.dumps(dict(completion_year=rep['completion_year'],construction_cost_no_future_leaks=rep['construction_cost'],uncovered_iron_count=rep['uncovered_iron_count'])),flush=True)
