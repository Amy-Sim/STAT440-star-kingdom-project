"""Larger, locally selected construction circles starting from submitted G05.
Spatial proposals only; public annual outcomes are kept out of this program.
"""
from fast_geometry import *
from scipy.spatial import cKDTree
from itertools import combinations
import argparse,time

OUT=Path(__file__).resolve().parent
SOURCE=HERE/'submit/R05_regional6.csv'

def save(name,x):
    (OUT/name).write_text(json.dumps(x,indent=2,ensure_ascii=False,default=lambda a:a.item() if isinstance(a,np.generic) else str(a)),encoding='utf8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);ap.add_argument('--distance',type=float,default=250)
    ap.add_argument('--neighbors',type=int,default=32);ap.add_argument('--max-circles',type=int,default=6)
    ap.add_argument('--max-pipes',type=int,default=24);ap.add_argument('--adaptive',action='store_true');ap.add_argument('--source',type=Path,default=SOURCE)
    ap.add_argument('--year-window',type=int,default=0)
    ap.add_argument('--robust',action='store_true')
    a=ap.parse_args();pr0,_,_,_,_,_,before,survival,mean=load();pr=FastProblem()
    assert np.array_equal(pr.p['Pipe ID'].values,pr0.p['Pipe ID'].values)
    units=read(pr,a.source);uy,py,active,total=shrink.trace(pr,units)
    n=sum(bool(len(x)) for x in active);base=units[:n];suffix=units[n:]
    assert all(len(x) for x in active[:n]) and all(not len(x) for x in active[n:])
    firstrow=np.full(len(pr.p),n,int);firstrow[pr.start]=-1
    for j,rep in enumerate(active[:n]):firstrow[rep]=j
    sr=Search(pr);proposals=[];seen=set();considered=tested=0;start=time.time()
    density=cKDTree(pr.mid).query_ball_point(np.array([u[0] for u in base]),100,return_length=True)
    sizes={};cache={}
    # Expected fixed cost and survival at each pipe's original planned year.
    original_prob=np.zeros(len(pr.p));old_expected=np.zeros(n)
    for j in range(n):
        original_prob[active[j]]=before[active[j],uy[j]-2027]
        old_expected[j]=(1-np.prod(1-original_prob[active[j]]))*base[j][3]
    if a.robust:
        from early_three_years import fit_fine
        predict,mean2=fit_fine(pr,2026,.5,.85)
        sv2=np.cumprod(1-np.column_stack([predict(y) for y in range(2027,2052)]),axis=1)
        sv2[pr.start]=0;before2=np.column_stack([(~pr.start).astype(float),sv2[:,:-1]])
        original_prob2=np.zeros(len(pr.p));old_expected2=np.zeros(n)
        for j in range(n):
            original_prob2[active[j]]=before2[active[j],uy[j]-2027]
            old_expected2[j]=(1-np.prod(1-original_prob2[active[j]]))*base[j][3]
    for year in sorted(set(uy)-{-1}):
        ii=np.flatnonzero(uy[:n]==year)
        pool=np.flatnonzero((uy[:n]>=year)&(uy[:n]<=year+a.year_window))
        xy=np.array([base[i][0] for i in pool]);tree=cKDTree(xy)
        dd,near=tree.query(np.array([base[i][0] for i in ii]),k=min(a.neighbors+1,len(pool)))
        if near.ndim==1:near=near[:,None];dd=dd[:,None]
        p=before[:,year-2027]
        olde=old_expected
        def attempt(group):
            nonlocal considered,tested
            group=tuple(sorted(set(group)))
            if len(group)<2 or len(group)>a.max_circles:return None
            if group in cache:return cache[group]
            considered+=1
            rep=np.unique(np.concatenate([active[j] for j in group]));oldfixed=sum(base[j][3] for j in group);oe=olde[list(group)].sum()
            if len(rep)>a.max_pipes:cache[group]=None;return None
            pts=np.vstack([pr.a[rep],pr.b[rep]])
            lb_r=max(np.ptp(pts[:,0]),np.ptp(pts[:,1]),pr.length[rep].max())/2
            rate=sum(RATES[s] for s in set(pr.surface[rep]));work=1-np.prod(1-p[rep])
            # Earlier replacement avoids some leaks but also sacrifices the
            # chance natural leak repairs would remove the replacement charge.
            advance_gain=(p[rep]-original_prob[rep])@(mean[rep]-200*pr.length[rep])
            if a.robust:
                p2=before2[rep,year-2027];work2=1-np.prod(1-p2);oe2=old_expected2[list(group)].sum()
                advance2=(p2-original_prob2[rep])@(mean2[rep]-200*pr.length[rep])
            lower=100+rate*(np.pi*lb_r*lb_r)**.85
            if oldfixed-lower<25 or oe-work*lower+advance_gain<10:cache[group]=None;return None
            if a.robust and oe2-work2*lower+advance2<10:cache[group]=None;return None
            c,r=enclosing(pts);lower=100+rate*(np.pi*r*r)**.85
            if oldfixed-lower<25 or oe-work*lower+advance_gain<10:cache[group]=None;return None
            if a.robust and oe2-work2*lower+advance2<10:cache[group]=None;return None
            state=firstrow<group[0];new=sr.group(rep,state,rep,deep=True);tested+=1
            if new is None:cache[group]=None;return None
            saving=oldfixed-new[3];gain=oe-work*new[3]+advance_gain
            if a.robust:gain=min(gain,oe2-work2*new[3]+advance2)
            if saving<25 or gain<10:cache[group]=None;return None
            ans=(float(gain),float(saving),group,new);cache[group]=ans;proposals.append(ans)
            return ans
        for k,i0 in enumerate(ii):
            i=int(i0)
            # Smooth density-based reach; sparse long pipes can search farther.
            reach=a.distance if not a.adaptive else min(a.distance,max(100.,2.5*base[i][1]+250./np.sqrt(max(density[i],1)/30.)))
            js=[int(pool[col]) for d,col in zip(dd[k],near[k]) if col<len(pool) and pool[col]!=i and d<=reach]
            if not js:continue
            anchors=[]
            for j in js:
                result=attempt([i,j])
                if result is not None:anchors.append(result)
            # Test every prefix size, letting local expected costs determine the
            # best number rather than requiring a globally fixed group size.
            for size in range(3,min(a.max_circles,len(js)+1)+1):attempt([i]+js[:size-1])
            # Surface-aligned prefixes avoid crossing costly boundaries merely
            # because a geometrically closer, different-surface pipe intervenes.
            surf=set(pr.surface[active[i]])
            same=[j for j in js if set(pr.surface[active[j]])<=surf]
            for size in range(3,min(a.max_circles,len(same)+1)+1):attempt([i]+same[:size-1])
            for group in combinations(js[:4],2):attempt([i,*group])
            if a.adaptive:
                # Greedily grow two promising local seeds; stop when no next
                # circle has positive incremental expected fixed-cost benefit.
                for seed in sorted(anchors,key=lambda x:-x[0])[:2]:
                    current=seed
                    while len(current[2])<a.max_circles:
                        best=current
                        for j in js:
                            if j in current[2]:continue
                            result=attempt([*current[2],j])
                            if result is not None and result[0]>best[0]+10:best=result
                        if best is current:break
                        current=best
        print(a.tag,year,'considered',considered,'tested',tested,'proposals',len(proposals),'seconds',round(time.time()-start),flush=True)
        # Cache only avoids duplicate work within year; all proposals retained.
        cache.clear()
    used=set();replace={};removed=set();audit=[]
    for gain,saving,group,new in sorted(proposals,key=lambda v:(-v[0],v[2])):
        if any(j in used for j in group):continue
        used.update(group);replace[group[0]]=new;removed.update(group[1:])
        audit.append(dict(rows=list(group),year=int(uy[group[0]]),expected_local_total_saving=gain,nominal_fixed_saving=saving,
            merged_circles=len(group),new_radius_m=new[1],old_radii_m=[base[j][1] for j in group],
            new_surfaces=sorted(set(pr.surface[new[2]])),target_pipes=len(np.unique(np.concatenate([active[j] for j in group])))))
    out=[replace.get(j,u) for j,u in enumerate(base) if j not in removed]+suffix
    (OUT/'candidates').mkdir(exist_ok=True);path=OUT/'candidates'/(a.tag+'.csv');out=write_read(pr,out,path)
    ny,npy,na,nt=shrink.trace(pr,out)
    if a.year_window==0:assert np.all(npy<=py)
    assert nt<=total and np.all(npy[pr.iron&~pr.start]<2052)
    check=validate(path,pr.p,pr.hist,pr.a,pr.b,pr.mid,pr.length,pr.iron)
    save(a.tag+'_moves.json',audit)
    save(a.tag+'_report.json',dict(configuration=vars(a),source_sha256=sha(a.source),candidate_sha256=sha(path),mergers=len(audit),
        nominal_saving=sum(v['nominal_fixed_saving'] for v in audit),expected_local_total_saving=sum(v['expected_local_total_saving'] for v in audit),
        merged_size_counts=pd.Series([v['merged_circles'] for v in audit]).value_counts().to_dict(),
        max_adopted_radius=max([v['new_radius_m'] for v in audit],default=0),tested=tested,considered=considered,
        nominal_delayed_pipes=int(((py<2052)&(npy>py)).sum()),validation=check,seconds=time.time()-start,public_score=None))
    print('DONE',a.tag,'mergers',len(audit),'saving',sum(v['nominal_fixed_saving'] for v in audit),flush=True)

if __name__=='__main__':main()
