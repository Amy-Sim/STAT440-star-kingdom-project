"""Round 2: prespecified gate relative to G05, fresh synthetic random banks.
Only candidates passing development are assessed with confirmation draws.
"""
from fast_geometry import *
from evaluate_plans import packed,run
from early_three_years import fit_fine
from optimize import execute
from scipy.special import ndtr
import argparse,shutil,time

OUT=Path(__file__).resolve().parent
G05=HERE/'submit/R05_regional6.csv'

def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=lambda a:a.item() if isinstance(a,np.generic) else str(a)),encoding='utf8')

def gate(detail,df,name):
    a=detail[detail.arm==name];g=df[df.arm==name]
    family=[]
    for fam,f in g.groupby('family'):
        # Pair simulations within random draw, preserving dependence between
        # alternative stress settings rather than counting them as independent.
        dd=f.groupby('draw').gain.mean();se=dd.std(ddof=1)/np.sqrt(len(dd))
        family.append(dict(family=fam,mean=dd.mean(),mc95_low=dd.mean()-1.96*se,mc95_high=dd.mean()+1.96*se))
    passed=(a.mean_gain>0).all() and g.feasible.all() and all(x['mc95_low']>0 for x in family)
    return dict(arm=name,mean_gain=a.mean_gain.mean(),worst_setting_gain=a.mean_gain.min(),positive_settings=int((a.mean_gain>0).sum()),
        all_feasible=bool(g.feasible.all()),win_fraction=float((g.gain>0).mean()),p05_gain=float(g.gain.quantile(.05)),
        A_mean_gain=family[0]['mean'],B_mean_gain=family[1]['mean'],minimum_family_mc95_low=min(x['mc95_low'] for x in family),gate_pass=bool(passed))

def bank(pr,arms,families,region,seed,draws,name):
    rng=np.random.default_rng(seed);rows=[];start=time.time()
    for draw in range(draws):
        zi=rng.normal(size=len(pr.p));zr=rng.normal(size=region.max()+1);cz=rng.normal(size=len(pr.p))
        for rho in [0.,.35]:
            uniform=ndtr(np.sqrt(rho)*zr[region]+np.sqrt(1-rho)*zi)
            for family,(sv,cm) in families.items():
                for scale in [.5,1.,1.5]:
                    hit=uniform[:,None]>sv**scale;first=np.where(hit.any(1),hit.argmax(1),25).astype(np.int64)
                    for cv in [0.,1.5]:
                        sigma=np.sqrt(np.log(1+cv*cv));severity=np.floor(cm*np.exp(sigma*cz-sigma*sigma/2)*100+.5).astype(np.int64)
                        result={k:run(*v,pr.length,pr.start,pr.iron,first,severity) for k,v in arms.items()}
                        b=result['G05'];ref=250000000-(b[0]+b[1])/100
                        for k,a in result.items():
                            score=250000000-(a[0]+a[1])/100
                            rows.append(dict(arm=k,draw=draw,family=family,scale=scale,cv=cv,rho=rho,score=score,gain=score-ref,
                                construction=a[0]/100,repair=a[1]/100,finish=2027+a[3],feasible=a[4]==0 and a[3]>=0))
        if draw%16==0:print(name,'draw',draw,'seconds',round(time.time()-start),flush=True)
    df=pd.DataFrame(rows);df.to_csv(OUT/(name+'_simulations.csv'),index=False)
    details=[]
    for keys,g in df.groupby(['arm','family','scale','cv','rho']):
        se=g.gain.std(ddof=1)/np.sqrt(draws)
        details.append(dict(zip(['arm','family','scale','cv','rho'],keys))|dict(mean_gain=g.gain.mean(),mc95_low=g.gain.mean()-1.96*se,mc95_high=g.gain.mean()+1.96*se,all_feasible=bool(g.feasible.all())))
    detail=pd.DataFrame(details);detail.to_csv(OUT/(name+'_by_setting.csv'),index=False)
    summary=pd.DataFrame([gate(detail,df,k) for k in arms if k!='G05']).sort_values('worst_setting_gain',ascending=False)
    summary.to_csv(OUT/(name+'_summary.csv'),index=False)
    print(name,summary.to_string(index=False),flush=True)
    return summary

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--confirmation-draws',type=int,default=128);ap.add_argument('--prefix',default='round2');args=ap.parse_args()
    pr,_,_,_,_,_,before,s,m=load();paths={'G05':G05}
    aliases={};seen={sha(G05):'G05'}
    for p in sorted((OUT/'candidates').glob('G*.csv')):
        digest=sha(p)
        if digest in seen:aliases[p.stem]=seen[digest];continue
        paths[p.stem]=p;seen[digest]=p.stem
    assert len(paths)>1
    protocol=dict(comparator='G05',comparator_public_score=79150812.58,development_draws=48,confirmation_draws=args.confirmation_draws,
        seed_development=202611022201,seed_confirmation=202611022202,settings=24,hazard_scales=[.5,1.,1.5],cost_cv=[0.,1.5],spatial_rho=[0.,.35],cell_m=250,
        gate='All 24 setting mean gains > 0, all scenarios feasible, and each forecast-family mean paired MC95 lower bound >0; must pass development and fresh confirmation.',
        note='Synthetic checks conditional on forecasts, not independent real-world validation. No candidate changes after confirmation.',
        sha256={k:sha(p) for k,p in paths.items()},duplicate_aliases=aliases,
        forecast_input_sha256={p.name:sha(p) for p in [INPUT/'CMS001_predictions_2027.csv',INPUT/'F168_curves_2027.npz']},
        code_sha256={p.name:sha(p) for p in [OUT/'assess.py',OUT/'fast_geometry.py',OUT/'larger_circles.py']},
        evaluation_cost_rule='round_to_cents(100 + sum(distinct all-contained surface rates)*area**0.85 + 200*unreplaced length)',
        future_public_annual_outcomes_used_as_forecast_inputs=False)
    save(args.prefix+'_protocol.json',protocol)
    f,fm=fit_fine(pr,2026,.5,.85);h=np.column_stack([f(y) for y in range(2027,2052)])
    fs=np.cumprod(1-h,axis=1);fs[pr.start]=0;fm[pr.start]=0
    families={'A_CMS001_F168':(s,m),'B_age_surface_historical_cost':(fs,fm)}
    _,region=np.unique(np.floor(pr.mid/250).astype(int),axis=0,return_inverse=True)
    arms={};audit={};rng=np.random.default_rng(202611022200)
    for k,p in paths.items():
        units=read(pr,p);covered=np.zeros(len(pr.p),bool)
        for u in units:covered[u[2]]=True
        assert not (pr.iron&~covered).any()
        arms[k]=packed(units)
        zero=np.zeros(len(pr.p),np.int64);first=np.full(len(pr.p),25,np.int64)
        a=run(*arms[k],pr.length,pr.start,pr.iron,first,zero);b=execute(pr,units)
        assert abs(a[0]/100-b['construction'])<.01 and a[4]==0 and a[3]>=0
        first=rng.integers(0,26,len(pr.p)).astype(np.int64);cost=rng.integers(0,10000000,len(pr.p)).astype(np.int64)
        a=run(*arms[k],pr.length,pr.start,pr.iron,first,cost);b=execute(pr,units,first,cost)
        assert abs(a[0]/100-b['construction'])<.01 and abs(a[1]/100-b['repair'])<.01
        audit[k]=dict(sha256=sha(p),uncovered_iron=0,rows=len(units))
        print('AUDITED',k,flush=True)
    save(args.prefix+'_audit.json',audit)
    dev=bank(pr,arms,families,region,protocol['seed_development'],48,args.prefix+'_development')
    selected=dev.loc[dev.gate_pass,'arm'].tolist()
    if not selected:
        save(args.prefix+'_accepted.json',[]);print('No candidate passed development; no submissions prepared.');return
    conf=bank(pr,{k:arms[k] for k in ['G05']+selected},families,region,protocol['seed_confirmation'],args.confirmation_draws,args.prefix+'_confirmation')
    accepted=[];(OUT/'submit').mkdir(exist_ok=True)
    for k in conf.loc[conf.gate_pass,'arm']:
        dest=OUT/'submit'/paths[k].name;shutil.copyfile(paths[k],dest)
        assert sha(dest)==protocol['sha256'][k]
        accepted.append(dict(candidate=k,file=str(dest.relative_to(OUT)),sha256=sha(dest),internal_comparator='G05',public_score=None))
    save(args.prefix+'_accepted.json',accepted)
    for k,p in paths.items():assert sha(p)==protocol['sha256'][k]
    print('ACCEPTED',[x['candidate'] for x in accepted],flush=True)

if __name__=='__main__':main()
