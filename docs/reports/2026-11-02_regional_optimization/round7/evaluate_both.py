"""Two user-authorized method comparisons, regardless of score gate; feasibility mandatory."""
from pathlib import Path
import sys,json
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[0]/'round4'))
import assess as e
e.OUT=OUT

def main():
    paths={'G05':OUT.parents[0]/'round4/G17_single_merge.csv'}
    paths.update({p.stem:p for p in sorted((OUT/'submit').glob('G*.csv'))})
    assert len(paths)==5,paths
    protocol=dict(comparator='G17',internal_reference_key='G05',public_baseline=79168928.88,
        seed=202611027702,draws_per_setting=128,settings=24,
        user_requested_Amy_Ryota_order_comparison=True,
        rule='All four plans must satisfy geometry, annual budget/carry and completion by 2051. Internal score differences are reported, not hidden.',
        forecast_note='Frozen forecast-based synthetic scenarios, not unseen real-world outcomes.',sha256={k:e.sha(p) for k,p in paths.items()})
    (OUT/'comparison_protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    pr,_,_,_,_,_,before,s,m=e.load()
    f,fm=e.fit_fine(pr,2026,.5,.85);h=e.np.column_stack([f(y) for y in range(2027,2052)])
    fs=e.np.cumprod(1-h,axis=1);fs[pr.start]=0;fm[pr.start]=0
    _,region=e.np.unique(e.np.floor(pr.mid/250).astype(int),axis=0,return_inverse=True)
    arms={};rng=e.np.random.default_rng(202611025500)
    for name,path in paths.items():
        units=e.read(pr,path);covered=e.np.zeros(len(pr.p),bool)
        for u in units:covered[u[2]]=True
        assert not (pr.iron&~covered).any()
        arms[name]=e.packed(units)
        first=e.np.full(len(pr.p),25,e.np.int64);zero=e.np.zeros(len(pr.p),e.np.int64)
        a=e.run(*arms[name],pr.length,pr.start,pr.iron,first,zero);b=e.execute(pr,units)
        assert a[4]==0 and a[3]>=0 and abs(a[0]/100-b['construction'])<.01
        first=rng.integers(0,26,len(pr.p)).astype(e.np.int64);cost=rng.integers(0,10000000,len(pr.p)).astype(e.np.int64)
        a=e.run(*arms[name],pr.length,pr.start,pr.iron,first,cost);b=e.execute(pr,units,first,cost)
        assert abs(a[0]/100-b['construction'])<.01 and abs(a[1]/100-b['repair'])<.01
        print('AUDITED',name,flush=True)
    e.bank(pr,arms,{'A_CMS001_F168':(s,m),'B_age_surface_historical_cost':(fs,fm)},region,protocol['seed'],128,'method_comparison')
    for name,path in paths.items():assert e.sha(path)==protocol['sha256'][name]

if __name__=='__main__':main()
