"""EDA-guided neighborhood recombination beyond G04's 2/3-circle, row-gap search.
Same no-future-leak planned year, adaptive spatial extent, 2..6 old circles.
Do not use official Public scores or official annual leak outcomes in proposals.
"""
from common import *
from itertools import combinations
from scipy.spatial import cKDTree
import argparse,time

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--max-group',type=int,default=4);ap.add_argument('--tag',default='R02_regional4');args=ap.parse_args()
    pr,original,n,oldyears,oldpy,_,before,survival,mean=load()
    source=HERE/'delivery/R01_2D_centers.csv';units=read(pr,source)
    base=units[:n];suffix=units[n:];uy,py,active,total=shrink.trace(pr,base)
    firstrow=np.full(len(pr.p),n,int);firstrow[pr.start]=-1
    for j,rep in enumerate(active):firstrow[rep]=j
    sr=Search(pr);proposals=[];seen=set();tested=0;considered=0;start=time.time()
    features=pd.read_csv(HERE/'G04_circle_features.csv').set_index('row')
    for year in sorted(set(uy)-{-1}):
        ii=np.flatnonzero(uy==year);xy=np.array([base[i][0] for i in ii]);tree=cKDTree(xy)
        distances,near=tree.query(xy,k=min(13,len(ii)))
        if near.ndim==1:near=near[:,None];distances=distances[:,None]
        p=before[:,year-2027]
        for k,i in enumerate(ii):
            # Sparse regions permit a wider search; dense regions still search
            # every neighbor within 100m up to the neighbor-count cap.
            density=float(features.loc[i,'neighborhood_count100'])
            radius=100 if density>=75 else 175
            js=[int(ii[col]) for d,col in zip(distances[k],near[k]) if col<len(ii) and d<=radius and ii[col]!=i]
            groups=[tuple(sorted([int(i),j])) for j in js[:10]]
            for size in range(3,args.max_group+1):
                # Connected prefixes plus nearest-neighbor triples/quadruples.
                if len(js)>=size-1:groups.append(tuple(sorted([int(i)]+js[:size-1])))
                if size<=4:groups.extend(tuple(sorted([int(i)]+list(cc))) for cc in combinations(js[:4],size-1))
            for group in groups:
                if group in seen:continue
                seen.add(group);considered+=1
                rep=np.unique(np.concatenate([active[j] for j in group]))
                if len(rep)>16:continue
                oldfixed=sum(base[j][3] for j in group)
                pts=np.vstack([pr.a[rep],pr.b[rep]])
                # A cheap valid lower bound prevents expensive geometry work.
                radius_lb=max(np.ptp(pts[:,0]),np.ptp(pts[:,1]),np.max(pr.length[rep]))/2
                rate=sum(RATES[s] for s in set(pr.surface[rep]))
                lower=100+rate*(np.pi*radius_lb**2)**.85
                oldexpected=sum((1-np.prod(1-p[active[j]]))*base[j][3] for j in group)
                newprob=1-np.prod(1-p[rep])
                if oldfixed-lower<25 or oldexpected-newprob*lower<10:continue
                minimal=pr.unit(rep)
                lower=100+rate*(np.pi*minimal[1]**2)**.85
                if oldfixed-lower<25 or oldexpected-newprob*lower<10:continue
                state=firstrow<min(group)
                new=sr.group(rep,state,rep,deep=True);tested+=1
                if new is None:continue
                saving=oldfixed-new[3];gain=oldexpected-newprob*new[3]
                if saving<25 or gain<10:continue
                proposals.append((gain,saving,group,new))
        print(args.tag,year,'considered',considered,'geometry',tested,'proposals',len(proposals),'seconds',round(time.time()-start),flush=True)
    # Independent set selection of nonoverlapping local changes.
    used=set();replace={};removed=set();audit=[]
    for gain,saving,group,new in sorted(proposals,key=lambda t:(-t[0],t[2])):
        if any(j in used for j in group):continue
        used.update(group);replace[min(group)]=new;removed.update(group[1:])
        audit.append(dict(rows=list(group),year=int(uy[group[0]]),nominal_saving=saving,expected_fixed_saving=gain,
            old_circle_count=len(group),old_surfaces=[sorted(set(pr.surface[base[j][2]])) for j in group],
            new_surfaces=sorted(set(pr.surface[new[2]])),radius_m=new[1],pipe_count=len(np.unique(np.concatenate([active[j] for j in group])))))
    merged=[replace.get(j,u) for j,u in enumerate(base) if j not in removed]
    # Every noninitial pipe contained by a proposed circle must belong to this
    # group's assigned target union or have already been processed.
    output=merged+suffix;path=HERE/'delivery'/(args.tag+'.csv');output=write_read(pr,output,path)
    ny,npy,aa,newtotal=shrink.trace(pr,output)
    delays=int(((oldpy<2052)&(npy>oldpy)).sum())
    assert delays==0,('Unintended nominal timing delays',delays)
    assert newtotal<=total
    check=validate(path,pr.p,pr.hist,pr.a,pr.b,pr.mid,pr.length,pr.iron)
    save_json(args.tag+'_moves.json',audit)
    save_json(args.tag+'_report.json',dict(mergers=len(audit),max_group=args.max_group,considered=considered,geometry_tested=tested,
        active_circles=len(merged),nominal_fixed_saving=sum(a['nominal_saving'] for a in audit),
        F168_expected_fixed_saving=sum(a['expected_fixed_saving'] for a in audit),no_future_leak_delayed_pipes=delays,
        seconds=time.time()-start,base_sha256=sha(BASE),source_sha256=sha(source),candidate_sha256=sha(path),validation=check,public_score=None))
    print('DONE',args.tag,len(audit),'saving',sum(a['nominal_saving'] for a in audit),flush=True)

if __name__=='__main__':main()
