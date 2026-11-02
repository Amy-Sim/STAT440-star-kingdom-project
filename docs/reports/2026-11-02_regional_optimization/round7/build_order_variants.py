"""Transplant pinned Amy/Ryota ranking rules to G17 geometry and CMS001/F168.
No old prediction model is silently substituted; annual plans become fixed CSVs.
"""
from pathlib import Path
import sys,json,heapq,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'large_circle_round2'))
from fast_geometry import *
from optimize_geometry import optimize
from early_three_years import benefits

OUT=Path(__file__).resolve().parent
BASELINE=HERE/'round4/G17_single_merge.csv'

class BoundedSearch(Search):
    def at(self,centers,required,state,allowed,bound=np.inf):
        centers=np.asarray(centers).reshape(-1,2)
        if len(centers)>384:
            centers=centers[np.unique(np.linspace(0,len(centers)-1,384).astype(int))]
        return super().at(centers,required,state,allowed,bound)

def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=lambda a:a.item() if isinstance(a,np.generic) else str(a)),encoding='utf8')

def static(pr,base,predict,severity):
    value=benefits(predict,severity,2027,2029);value[pr.start]=0
    return sorted(range(len(base)),key=lambda j:(-float(value[base[j][2]].sum())/max(pr.cost(base[j],pr.start)/100,1),base[j][1],j)),[]

def dynamic(pr,base,predict,severity):
    incidence=[[] for _ in range(len(pr.p))]
    for j,u in enumerate(base):
        for i in u[2]:incidence[i].append(j)
    state=pr.start.copy();selected=[];audit=[];done=np.zeros(len(base),bool);versions=np.zeros(len(base),int);balance=0
    for year in range(2027,2030):
        balance+=1_000_000_000;value=benefits(predict,severity,year,2029);value[pr.start]=0;heap=[]
        def push(j):
            if done[j]:return
            ids=base[j][2][~state[base[j][2]]]
            if not len(ids) or not pr.iron[ids].any():return
            c=pr.cost(base[j],state);v=float(value[ids].sum())
            heapq.heappush(heap,(-v/max(c/100,1),j,int(versions[j]),c,v))
        for j in range(len(base)):push(j)
        while heap:
            neg,j,version,c,v=heapq.heappop(heap)
            if version!=versions[j] or done[j]:continue
            if c>balance:continue
            if v<=0:break
            ids=base[j][2][~state[base[j][2]]];selected.append(j);done[j]=True;balance-=c;state[ids]=True
            audit.append(dict(row=j,planned_year=year,cost=c/100,benefit=v))
            affected={k for i in ids for k in incidence[i]}
            for k in affected:versions[k]+=1;push(k)
    value=benefits(predict,severity,2030,2032);value[state]=0
    tail=[j for j in range(len(base)) if not done[j]]
    tail.sort(key=lambda j:(-float(value[base[j][2]].sum())/max(pr.cost(base[j],state)/100,1),base[j][1],j))
    return selected+tail,audit

def amy(pr,base,predict,severity):
    state=pr.start.copy();done=np.zeros(len(base),bool);selected=[];audit=[];balance=0
    totaliron=float(pr.length[pr.iron&~pr.start].sum())
    for year in range(2027,2052):
        balance+=1_000_000_000;value=predict(year)*severity;value[pr.start]=0
        candidates=[]
        for j,u in enumerate(base):
            if done[j]:continue
            ids=u[2][~state[u[2]]]
            if len(ids):candidates.append((float(value[ids].sum())/max(pr.cost(u,state)/100,1),j))
        candidates.sort(key=lambda x:(-x[0],x[1]))
        required=totaliron*(year-2026)/25
        for phase in ['Economic','Mandatory']:
            for initial,j in candidates:
                if phase=='Mandatory' and float(pr.length[pr.iron&~pr.start&state].sum())>=required:break
                if done[j] or (phase=='Economic' and initial<=1):continue
                u=base[j];ids=u[2][~state[u[2]]]
                if not len(ids) or (phase=='Mandatory' and not pr.iron[ids].any()):continue
                cost=pr.cost(u,state);bcr=float(value[ids].sum())/max(cost/100,1)
                if phase=='Economic' and bcr<=1:continue
                if cost>balance:continue
                selected.append(j);done[j]=True;balance-=cost;state[ids]=True
                audit.append(dict(row=j,planned_year=year,phase=phase,cost=cost/100,BCR=bcr))
    # Include remaining optional/noniron rows once, and preserve the full union.
    selected += [j for j in range(len(base)) if not done[j]]
    assert len(selected)==len(base)
    return selected,audit

def transferred(pr,base,predict,severity):
    reference=GEO/'reference_77_456.csv'
    old=read(pr,reference);_,_,assigned,_=shrink.trace(pr,old)
    rank=np.full(len(pr.p),len(pr.p)*2,int);k=0
    for ids in assigned:
        for i in ids:rank[i]=k;k+=1
    _,_,newassigned,_=shrink.trace(pr,base)
    # Group each latest circle at its earliest original, still-live target.
    order=sorted(range(len(base)),key=lambda j:(int(rank[newassigned[j]].min()) if len(newassigned[j]) else len(pr.p)*3,j))
    return order,[dict(reference=str(reference),sha256=sha(reference),mapping='Earliest rank among the latest circle original active assignment; no old circle radius is copied.')]

def main():
    _,_,_,_,_,_,before,s,mean=load();pr=FastProblem();units=read(pr,BASELINE)
    uy,py,active,total=shrink.trace(pr,units);n=sum(bool(len(x)) for x in active);base=units[:n];suffix=units[n:]
    prev=np.column_stack([np.ones(len(pr.p)),s[:,:-1]])
    hazards=np.clip(1-np.divide(s,prev,out=np.ones_like(s),where=prev>0),0,1);hazards[pr.start]=0
    predict=lambda year:hazards[:,year-2027]
    sources=[ROOT/'output/2026-11-02_circle_mix/source/submissions/2026-10-28_ryota_early3/early_three_years.py',ROOT/'output/2026-11-02_circle_mix/source/notebooks/Amy_Sim/star_kingdom_full_pipeline_AS.ipynb']
    save('protocol.json',dict(baseline='G17',baseline_sha256=sha(BASELINE),geometry='G17 circles; rerun center/radius/split for each reordered assignment',
        forecasts='All variants use frozen CMS001/F168; transplant ordering rules only, not historical Amy/Ryota models.',
        source_commit='ca6cdae4b859782e7a30d543fce686a30d52354c',source_sha256={p.name:sha(p) for p in sources},
        note='Amy 77.46M integrated coverage inherited Ryota order. The separate Amy rule comes from latest full-pipeline annual BCR plus iron progress notebook. CSV execution cannot explicitly pause between planned annual blocks.'))
    (OUT/'submit').mkdir(exist_ok=True)
    configs=[('G22_Ryota_fixed3',static),('G23_Ryota_dynamic3',dynamic),('G24_Amy_annualBCR',amy),('G25_Amy_submitted_order',transferred)]
    if '--only' in sys.argv:configs=[v for v in configs if v[0]==sys.argv[sys.argv.index('--only')+1]]
    for tag,fn in configs:
        start=time.time();order,audit=fn(pr,base,predict,mean)
        assert len(order)==n and len(set(order))==n
        ordered=[base[j] for j in order]
        print('ORDERED',tag,'rows',len(order),flush=True)
        out,moves,meta=optimize(ordered,pr,BoundedSearch(pr),True,tag)
        out=out[:meta['active_rows']]+suffix
        path=OUT/'submit'/(tag+'.csv');out=write_read(pr,out,path)
        validation=validate(path,pr.p,pr.hist,pr.a,pr.b,pr.mid,pr.length,pr.iron)
        save(tag+'_report.json',dict(source='G17',order_rule=tag,order_sha256=__import__('hashlib').sha256(np.array(order,dtype='<i8').tobytes()).hexdigest(),
            geometry_moves=len(moves),geometry_center_batch_cap=384,active_rows=meta['active_rows'],validation=validation,sha256=sha(path),public_score=None,seconds=time.time()-start))
        save(tag+'_order.json',order);save(tag+'_planning_audit.json',audit);save(tag+'_geometry_moves.json',moves)
        print('VALID',tag,validation['construction_cost'],validation['completion_year'],flush=True)

if __name__=='__main__':main()
