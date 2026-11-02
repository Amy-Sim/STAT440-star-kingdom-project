"""Two distinct learned geometry policies, trained on forecast-based local rollout costs.
Teacher values are not observed optimal construction plans or official futures.
"""
from pathlib import Path
import sys,json,time,heapq,os
os.environ.setdefault('LOKY_MAX_CPU_COUNT','2')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'large_circle_round2'))
from fast_geometry import *
from scipy.spatial import cKDTree
from sklearn.ensemble import ExtraTreesRegressor,HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error,mean_squared_error
import joblib
from sklearn.neural_network import MLPRegressor
from sklearn.kernel_approximation import Nystroem
from light_models import CappedRegressor
from threadpoolctl import threadpool_limits
threadpool_limits(limits=2)

OUT=Path(__file__).resolve().parent
BASELINE=HERE/'round4/G17_single_merge.csv'

def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=lambda a:a.item() if isinstance(a,np.generic) else str(a)),encoding='utf8')

def preparation():
    _,_,_,_,_,_,before,surv,mean=load();pr=FastProblem();base=read(pr,BASELINE)
    uy,py,active,total=shrink.trace(pr,base);n=sum(bool(len(a)) for a in active)
    first=np.full(len(pr.p),n,int);first[pr.start]=-1
    for j,ids in enumerate(active[:n]):first[ids]=j
    targets=np.flatnonzero((first>=0)&(first<n));order=targets[np.lexsort((-mean[targets]*(1-surv[targets,1]),first[targets]))]
    f=pd.read_csv(HERE/'pipe_neighborhood_features.csv').set_index('pipe_id').loc[pr.p['Pipe ID']].reset_index()
    f=f.drop(columns=['pipe_id','planned_year_G04'])
    f=pd.get_dummies(f,columns=['material','surface'],dtype=float)
    v=pr.b-pr.a;f['orientation_sin2']=2*v[:,0]*v[:,1]/np.maximum(pr.length**2,1e-9)
    f['orientation_cos2']=(v[:,0]**2-v[:,1]**2)/np.maximum(pr.length**2,1e-9)
    f['planned_year_context']=np.where(py<2052,py,2051)
    X=f.to_numpy(np.float32);assert np.isfinite(X).all()
    save('feature_manifest.json',dict(columns=list(f.columns),features=len(f.columns),pipe_count=len(pr.p),target_count=len(targets),
        source_sha256=sha(BASELINE),teacher='Expected cost of immediate grouped work versus separate work three years later; frozen CMS001/F168, no official outcome inputs.',
        initial_state='2027, historical leaks and initial PU excluded',validation='Northeast spatial quadrant holdout, 500m buffer from its edges; inner 500m block grouped OOF stacking.'))
    return pr,base,n,first,targets,order,X,before,surv,mean

def action_features(pr,u,anchor,X,before,surv,mean,year):
    ids=u[2][~pr.start[u[2]]];yi=int(np.clip(year-2027,0,24));later=min(yi+3,24)
    p=before[ids,yi];q=surv[ids,max(later-1,0)]
    # Delayed separate replacements use each pipe's minimum disk as a cost proxy.
    solo=100+np.array([RATES[s] for s in pr.surface[ids]])*(np.pi*(pr.length[ids]/2)**2)**.85
    gross=float((p-q)@(mean[ids]-200*pr.length[ids])+q@solo)
    work=1-np.prod(1-p);expected=work*u[3]+200*(p@pr.length[ids])
    score=(gross-work*u[3])/max(expected,100)**.85
    sf=set(pr.surface[u[2]])
    extra=[u[1],u[3],len(ids),len(u[2]),pr.length[ids].sum(),len(sf),
        mean[ids].sum(),float(p.sum()),float(q.sum()),float(work),float(pr.age[ids].mean()),
        float(np.sum(mean[ids]*(p-q))),float(np.linalg.norm(u[0]-pr.mid[anchor])),year]
    extra += [float(s in sf) for s in RATES]
    return np.r_[X[anchor],extra].astype(np.float32),gross,score

def make_data(pr,base,n,first,targets,order,X,before,surv,mean):
    pool=[];anchors=[];features=[];gross=[];radius_y=np.zeros(len(pr.p));year=np.full(len(pr.p),2051,int)
    uy,py,aa,total=shrink.trace(pr,base)
    for i in targets:year[i]=uy[first[i]]
    tree=cKDTree(pr.mid[targets]);_,nn=tree.query(pr.mid[targets],k=8)
    seen={};start=time.time()
    for k,i in enumerate(targets):
        near=targets[np.atleast_1d(nn[k])];near=near[np.linalg.norm(pr.mid[near]-pr.mid[i],axis=1)<=100]
        candidates=[base[first[i]]]
        for size in [1,2,4,8]:
            ids=near[:size]
            if len(ids):candidates.append(pr.unit(ids))
        best=(-np.inf,None)
        for u in candidates:
            feat,g,s=action_features(pr,u,int(i),X,before,surv,mean,int(year[i]))
            if s>best[0]:best=(s,u)
            key=(tuple(u[0]),u[1],int(year[i]))
            if key not in seen:
                seen[key]=len(pool);pool.append(u);anchors.append(int(i));features.append(feat);gross.append(g)
        radius_y[i]=np.log(max(best[1][1]/max(pr.length[i]/2,.001),1.))
        if k%4000==0:print('teacher',k,'/',len(targets),'actions',len(pool),'seconds',round(time.time()-start),flush=True)
    joblib.dump(dict(pool=pool,anchors=np.array(anchors),features=np.array(features),gross=np.array(gross),radius_y=radius_y,year=year),OUT/'teacher.joblib',compress=3)
    return pool,np.array(anchors),np.array(features),np.array(gross),radius_y,year

def models():
    return [ExtraTreesRegressor(n_estimators=64,min_samples_leaf=10,max_features=.75,n_jobs=2,random_state=440),
        HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=23,l2_regularization=10,random_state=440),
        make_pipeline(StandardScaler(),Ridge(alpha=50)),
        CappedRegressor(make_pipeline(StandardScaler(),MLPRegressor(hidden_layer_sizes=(32,16),alpha=.1,batch_size=256,max_iter=100,early_stopping=True,n_iter_no_change=8,random_state=440)),max_rows=10000),
        make_pipeline(StandardScaler(),Nystroem(kernel='rbf',gamma=1/180,n_components=64,random_state=440),Ridge(alpha=10))]

def fit_stack(X,y,groups,label):
    estimators=models();oof=np.zeros((len(y),len(estimators)))
    for fold,(tr,va) in enumerate(GroupKFold(3).split(X,y,groups)):
        for j,est in enumerate(estimators):
            fitted=clone(est).fit(X[tr],y[tr]);oof[va,j]=fitted.predict(X[va])
        print(label,'OOF',fold,len(tr),len(va),flush=True)
    meta=make_pipeline(StandardScaler(),Ridge(alpha=10)).fit(oof,y)
    fitted=[clone(est).fit(X,y) for est in estimators]
    return dict(base=fitted,meta=meta)

def predict(stack,X):return stack['meta'].predict(np.column_stack([m.predict(X) for m in stack['base']]))

def train(pr,targets,X,anchors,actionX,gross,radius_y):
    xy=pr.mid;xm,ym=np.median(xy[targets],axis=0)
    held=(xy[:,0]>=xm)&(xy[:,1]>=ym)
    trainmask=(xy[:,0]<xm-500)|(xy[:,1]<ym-500)
    coords=np.floor(xy/500).astype(int);_,groups=np.unique(coords,axis=0,return_inverse=True)
    rng=np.random.default_rng(202611025500);sample=np.sort(rng.choice(len(anchors),min(36000,len(anchors)),replace=False))
    jobs=[('radius',X[targets],radius_y[targets],targets),
          ('action',actionX[sample],np.sign(gross[sample])*np.log1p(np.abs(gross[sample])),anchors[sample])]
    metrics=[];stacks={}
    for name,xx,yy,ids in jobs:
        tr=np.flatnonzero(trainmask[ids]);va=np.flatnonzero(held[ids]);assert len(tr)>100 and len(va)>100
        # Every validation anchor is >=500m from every allowed training anchor.
        assert cKDTree(xy[ids[tr]]).query(xy[ids[va]])[0].min()>=500-1e-6
        st=fit_stack(xx[tr],yy[tr],groups[ids[tr]],name+'_spatial_train')
        pred=predict(st,xx[va]);basepred=np.column_stack([m.predict(xx[va]) for m in st['base']])
        metrics.append(dict(task=name,holdout_rows=len(va),training_rows=len(tr),target_scale='log radius ratio' if name=='radius' else 'signed log gross value',
            RMSE=float(np.sqrt(mean_squared_error(yy[va],pred))),MAE=float(mean_absolute_error(yy[va],pred)),
            base_RMSE=[float(np.sqrt(mean_squared_error(yy[va],basepred[:,j]))) for j in range(basepred.shape[1])],
            note='Surrogate teacher prediction in unseen region; not observed future repair cost or whole-plan validation.'))
        stacks[name]=fit_stack(xx,yy,groups[ids],name+'_all_regions')
        joblib.dump(stacks[name],OUT/(name+'_stack.joblib'),compress=3)
    save('spatial_model_metrics.json',metrics)
    return stacks

def emit(pr,units,tag,baseline):
    folder=OUT/'submit';folder.mkdir(exist_ok=True);path=folder/(tag+'.csv');units=write_read(pr,units,path)
    check=validate(path,pr.p,pr.hist,pr.a,pr.b,pr.mid,pr.length,pr.iron)
    assert check['uncovered_iron_count']==0 and check['completed_by_2051']
    save(tag+'_report.json',dict(method=tag,sha256=sha(path),baseline_sha256=sha(BASELINE),validation=check,public_score=None))
    print('VALID',tag,check['construction_cost'],check['completion_year'],flush=True)
    return units

def build_radius(pr,base,n,first,targets,order,X,stack):
    ratios=np.exp(np.clip(predict(stack,X[targets]),0,np.log(8)));ratio=np.ones(len(pr.p));ratio[targets]=ratios
    state=pr.start.copy();units=[]
    for k,i in enumerate(order):
        if state[i]:continue
        half=pr.length[i]/2;r=float(np.round(min(max(half+1e-6,half*ratio[i]+1e-6),120),9))
        d=(pr.b[i]-pr.a[i])/max(pr.length[i],1e-6);normal=np.array([-d[1],d[0]])
        best=None
        for shift in [0.,-.15,.15,-.3,.3]:
            center=np.round(pr.mid[i]+normal*r*shift,9)
            if max(np.linalg.norm(pr.a[i]-center),np.linalg.norm(pr.b[i]-center))>r:continue
            near=pr.grid.query(center,r);ids=near[(np.linalg.norm(pr.a[near]-center,axis=1)<=r)&(np.linalg.norm(pr.b[near]-center,axis=1)<=r)]
            fixed=100+sum(RATES[s] for s in set(pr.surface[ids]))*(np.pi*r*r)**.85
            u=(center,r,ids,float(fixed))
            if best is None or pr.cost(u,state)<pr.cost(best,state):best=u
        assert best is not None and i in best[2]
        # Hard feasibility projection: don't spend more than separate minimum
        # disks for the live pipes this predicted circle would newly replace.
        live=best[2][~state[best[2]]]
        separate=sum(100+RATES[pr.surface[j]]*(np.pi*(pr.length[j]/2)**2)**.85+200*pr.length[j] for j in live)
        if pr.cost(best,state)/100>separate*1.05:
            best=pr.unit([i])
        units.append(best);state[best[2]]=True
    assert state[targets].all()
    return emit(pr,units+base, 'G20_user_radius_NN_stack',base)

def build_action(pr,base,n,first,targets,order,pool,anchors,actionX,gross,year,stack,surv,mean):
    z=predict(stack,actionX);values=np.sign(z)*np.expm1(np.minimum(np.abs(z),18))
    weights=np.maximum(mean*(1-surv[:,min(2,surv.shape[1]-1)]),1.)
    inverse=[[] for _ in range(len(pr.p))];state=pr.start.copy();versions=np.zeros(len(pool),int);heap=[]
    initial=np.zeros(len(pool));current=np.zeros(len(pool));costlength=np.zeros(len(pool));counts=np.zeros(len(pool),int)
    for j,u in enumerate(pool):
        ids=u[2][~state[u[2]]];initial[j]=current[j]=weights[ids].sum();costlength[j]=pr.length[ids].sum();counts[j]=len(ids)
        for i in ids:inverse[i].append(j)
    def key(j):
        if counts[j]==0:return -np.inf
        u=pool[j];benefit=values[j]*current[j]/max(initial[j],1)-u[3]
        return benefit/max(u[3]+200*costlength[j],100)**.85
    for j in range(len(pool)):heapq.heappush(heap,(int(year[anchors[j]]),-key(j),j,0))
    units=[];covered=0
    while heap:
        context_year,score,j,version=heapq.heappop(heap)
        if version!=versions[j] or counts[j]==0:continue
        u=pool[j];live=u[2][~state[u[2]]]
        if not len(live):continue
        separate=sum(100+RATES[pr.surface[i]]*(np.pi*(pr.length[i]/2)**2)**.85+200*pr.length[i] for i in live)
        if pr.cost(u,state)/100>separate*1.05:
            # The learned score ranks proposals, but cannot override the hard
            # construction-cost projection shared with the radius policy.
            anchor=int(live[np.argmax(weights[live])]);u=pr.unit([anchor]);live=u[2][~state[u[2]]]
        units.append(u);state[live]=True;affected=set()
        for i in live:
            for k in inverse[i]:current[k]-=weights[i];costlength[k]-=pr.length[i];counts[k]-=1;affected.add(k)
        for k in affected:
            versions[k]+=1
            if counts[k]:heapq.heappush(heap,(int(year[anchors[k]]),-key(k),k,versions[k]))
        if len(units)%3000==0:print('dynamic candidate stack',len(units),'remaining',int((~state[targets]).sum()),flush=True)
        if state[targets].all():break
    assert state[targets].all()
    return emit(pr,units+base,'G21_candidate_NN_stack',base)

def main():
    pr,base,n,first,targets,order,X,before,surv,mean=preparation()
    if (OUT/'teacher.joblib').exists():
        data=joblib.load(OUT/'teacher.joblib');pool,anchors,actionX,gross,ry,year=[data[k] for k in ['pool','anchors','features','gross','radius_y','year']]
    else:pool,anchors,actionX,gross,ry,year=make_data(pr,base,n,first,targets,order,X,before,surv,mean)
    if (OUT/'radius_stack.joblib').exists() and (OUT/'action_stack.joblib').exists():stacks={k:joblib.load(OUT/(k+'_stack.joblib')) for k in ['radius','action']}
    else:stacks=train(pr,targets,X,anchors,actionX,gross,ry)
    if '--action-only' not in sys.argv:build_radius(pr,base,n,first,targets,order,X,stacks['radius'])
    build_action(pr,base,n,first,targets,order,pool,anchors,actionX,gross,year,stacks['action'],surv,mean)

if __name__=='__main__':main()
