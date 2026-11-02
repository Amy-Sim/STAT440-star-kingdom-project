"""Frozen-plan sensitivity audit; no candidate tuning or official submissions.

Run: python evaluate.py --repo-root /path/to/repository --draws 256
The bundle carries the exact candidate CSVs and frozen CMS001/F168 forecasts.
"""
from pathlib import Path
import argparse,sys,json,hashlib,csv
import numpy as np
import pandas as pd
from scipy.special import ndtr
from numba import njit

HERE=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

@njit(cache=True)
def replay(off,flat,fixed,length,initial,iron,first,severity):
    state=initial.copy();replaced=np.full(len(state),25,np.int64)
    cursor=0;balance=construction=0;finish=-1
    for yi in range(25):
        balance+=1000000000
        for i in range(len(state)):
            if first[i]<yi:state[i]=True
        while cursor<len(fixed):
            live=0;ls=0.
            for k in range(off[cursor],off[cursor+1]):
                i=flat[k]
                if not state[i]:live+=1;ls+=length[i]
            if not live:cursor+=1;continue
            cost=int(np.floor((fixed[cursor]+200*ls)*100+.5))
            if cost>balance:break
            balance-=cost;construction+=cost
            for k in range(off[cursor],off[cursor+1]):
                i=flat[k]
                if not state[i]:state[i]=True;replaced[i]=yi
            cursor+=1
        if cursor==len(fixed) and finish<0:finish=yi
    repair=leaks=remaining=0
    for i in range(len(state)):
        if first[i]<replaced[i] and first[i]<25 and not initial[i]:repair+=severity[i];leaks+=1
        if iron[i] and not state[i]:remaining+=1
    return construction,repair,leaks,finish,remaining

def pack(units):
    off=np.concatenate(([0],np.cumsum([len(u[2]) for u in units]))).astype(np.int64)
    return off,np.concatenate([u[2] for u in units]).astype(np.int64),np.array([u[3] for u in units])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,required=True);ap.add_argument('--draws',type=int,default=256);args=ap.parse_args()
    repo=args.repo_root.resolve();sys.path[:0]=[str(repo/'src'),str(repo/'submissions/2026-10-28_ryota_early3')]
    from optimize import Problem,execute
    from early_three_years import read,fit_fine
    pr=Problem();evidence=HERE/'evidence';evidence.mkdir(exist_ok=True)
    candidates=json.loads((HERE/'candidates.json').read_text(encoding='utf8'))
    paths={k:HERE/v['file'] for k,v in candidates.items()}
    for k,p in paths.items():assert digest(p)==candidates[k]['sha256']
    curves=HERE/'inputs/F168_curves_2027.npz';costpath=HERE/'inputs/CMS001_predictions_2027.csv'
    with np.load(curves) as z:ids=z['pipe_id'].astype(str);small=z['survival'].astype(float)
    positions=pd.Index(pr.p['Pipe ID']).get_indexer(ids);assert (positions>=0).all()
    assert set(positions)==set(np.flatnonzero(~pr.start))
    s=np.ones((len(pr.p),25));s[positions]=small
    c=pd.read_csv(costpath);m=pr.p['Pipe ID'].map(c.set_index('pipe_id').predicted_repair_cost).fillna(float(c.predicted_repair_cost.median())).to_numpy();m[pr.start]=0
    f,fm=fit_fine(pr,2026,.5,.85);h=np.column_stack([f(y) for y in range(2027,2052)])
    fs=np.cumprod(1-h,axis=1);fs[pr.start]=1;fm[pr.start]=0
    families={'A_CMS001_F168':(s,m),'B_fine_age_historical_cost':(fs,fm)}
    region=np.floor(pr.mid/500).astype(np.int64);_,region_index=np.unique(region,axis=0,return_inverse=True)
    protocol=dict(seed=2026110257,draws=args.draws,forecast_families=list(families),hazard_scales=[.5,1.,1.5],severity_cv=[0.,1.5],spatial_rho=[0.,.35],spatial_cell_metres=500,
       setting_count=24,scenario_count=args.draws*24,selection='Post-selection robustness audit of already published/submitted frozen candidates; not an untouched holdout.',
       future_outcomes_used_in_candidate_or_forecast_fit=False,candidate_parameter_tuning=False,conditional_independence_note='rho .35 adds a Gaussian-copula regional timing shock; marginal event probabilities are unchanged.',
       cvar_note='Settings are sensitivity assumptions; equal weighting is descriptive and not a probability distribution over real futures.',
       input_sha256={p.name:digest(p) for p in [curves,costpath,repo/'data/pipes.csv',repo/'data/train.csv']},candidate_sha256={k:digest(p) for k,p in paths.items()},algorithm_sha256=digest(Path(__file__)))
    (evidence/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    arms={};audits={};rng=np.random.default_rng(2026110258)
    for name,path in paths.items():
        u=read(pr,path);arms[name]=pack(u);covered=np.zeros(len(pr.p),bool)
        for x in u:covered[x[2]]=True
        miss=pr.iron&~covered
        first=np.full(len(pr.p),25,np.int64);zero=np.zeros(len(pr.p),np.int64)
        r=replay(*arms[name],pr.length,pr.start,pr.iron,first,zero);old=execute(pr,u)
        assert abs(r[0]/100-old['construction'])<.01
        for k in range(3):
            first=rng.integers(0,26,len(pr.p)).astype(np.int64);rc=rng.integers(0,10000000,len(pr.p)).astype(np.int64)
            r=replay(*arms[name],pr.length,pr.start,pr.iron,first,rc);old=execute(pr,u,first,rc)
            assert abs(r[0]/100-old['construction'])<.01 and abs(r[1]/100-old['repair'])<.01 and r[2]==old['leaks']
        audits[name]=dict(rows=len(u),uncovered_original_iron=int(miss.sum()),uncovered_active_iron=int((miss&~pr.start).sum()),
            no_future_leak_construction=execute(pr,u)['construction'],valid_geometry=not miss.any(),sha256=digest(path))
        print('AUDITED',name,audits[name]['uncovered_original_iron'],flush=True)
    (evidence/'geometry_and_replay_checks.json').write_text(json.dumps(audits,indent=2),encoding='utf8')
    rng=np.random.default_rng(protocol['seed']);records=[]
    for draw in range(args.draws):
        zi=rng.normal(size=len(pr.p));zr=rng.normal(size=region_index.max()+1);cost_z=rng.normal(size=len(pr.p))
        for rho in protocol['spatial_rho']:
            uniforms=ndtr(np.sqrt(rho)*zr[region_index]+np.sqrt(1-rho)*zi)
            for family,(survival,mean) in families.items():
                for scale in protocol['hazard_scales']:
                    hit=uniforms[:,None]>survival**scale
                    first=np.where(hit.any(1),hit.argmax(1),25).astype(np.int64)
                    for cv in protocol['severity_cv']:
                        sigma=np.sqrt(np.log(1+cv*cv));severity=np.floor(mean*np.exp(sigma*cost_z-sigma*sigma/2)*100+.5).astype(np.int64)
                        for name,arm in arms.items():
                            construction,repair,leaks,finish,remaining=replay(*arm,pr.length,pr.start,pr.iron,first,severity)
                            records.append(dict(draw=draw,rho=rho,family=family,scale=scale,severity_cv=cv,arm=name,
                                construction=construction/100,repair=repair/100,score=(25000000000-construction-repair)/100,
                                leaks=leaks,finish=finish+2027 if finish>=0 else None,state_feasible=remaining==0 and finish>=0,valid_plan=remaining==0 and finish>=0 and audits[name]['valid_geometry']))
        if draw%32==0:print('DRAW',draw,flush=True)
    df=pd.DataFrame(records);df.to_csv(evidence/'simulations.csv',index=False)
    rows=[];ref='amy_integrated'
    for keys,g in df.groupby(['family','scale','severity_cv','rho','arm']):
        fam,scale,cv,rho,arm=keys
        b=df[(df.family==fam)&(df.scale==scale)&(df.severity_cv==cv)&(df.rho==rho)&(df.arm==ref)].set_index('draw')
        delta=g.set_index('draw').score-b.score;se=delta.std(ddof=1)/np.sqrt(args.draws)
        rows.append(dict(family=fam,scale=scale,severity_cv=cv,rho=rho,arm=arm,mean_score=g.score.mean(),mean_gain_vs_amy=delta.mean(),
           paired_mc95_low=delta.mean()-1.96*se,paired_mc95_high=delta.mean()+1.96*se,mean_construction=g.construction.mean(),mean_repair=g.repair.mean(),
           p10_score=float(g.score.quantile(.1)),scenario_win_fraction=float((delta>0).mean()),all_valid=bool(g.valid_plan.all())))
    detail=pd.DataFrame(rows);detail.to_csv(evidence/'setting_metrics.csv',index=False)
    summary=[]
    for arm in paths:
        a=detail[detail.arm==arm];g=df[df.arm==arm]
        summary.append(dict(arm=arm,author=candidates[arm]['author'],public_score_M=candidates[arm].get('public_score_M'),public_note=candidates[arm]['public_note'],
            A_mean_gain_M=a[a.family.str.startswith('A_')].mean_gain_vs_amy.mean()/1e6,
            B_mean_gain_M=a[a.family.str.startswith('B_')].mean_gain_vs_amy.mean()/1e6,
            worst_setting_gain_M=a.mean_gain_vs_amy.min()/1e6,winning_settings=int((a.mean_gain_vs_amy>0).sum()),
            all_valid=bool(g.valid_plan.all()),uncovered_original_iron=audits[arm]['uncovered_original_iron'],
            mean_score_M=a.mean_score.mean()/1e6,no_future_leak_construction_M=audits[arm]['no_future_leak_construction']/1e6))
    summary=pd.DataFrame(summary);summary.to_csv(evidence/'summary.csv',index=False)
    print(summary.to_string(index=False),flush=True)

if __name__=='__main__':main()
