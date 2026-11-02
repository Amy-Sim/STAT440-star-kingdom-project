from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
GEO=ROOT/'output/2026-11-02_geometry_optimization'
sys.path.insert(0,str(GEO))
from optimize_geometry import Problem,Search,read,write_read,shrink,RATES,sha,validate

BASE=GEO/'delivery/G04_economic_triples.csv'
INPUT=ROOT/'output/2026-11-02_robustness_paper/inputs'

def load():
    pr=Problem();units=read(pr,BASE)
    assert sha(BASE)=='3e240e4122be8e69e6f9ede23c7bb042c215a84d853815bd0d372d999aa5ecc4'
    for name in ['pipes.csv','train.csv']:
        a=pd.read_csv(ROOT/'data'/name);b=pd.read_csv(ROOT/'output/2026-11-02_circle_mix/source/data'/name)
        pd.testing.assert_frame_equal(a,b)
    uy,py,active,total=shrink.trace(pr,units)
    n=json.loads((GEO/'G04_economic_triples_report.json').read_text())['active_rows']
    assert sum(bool(len(x)) for x in active)==n
    with np.load(INPUT/'F168_curves_2027.npz') as z:
        ids=z['pipe_id'].astype(str);sv=z['survival'].astype(float)
    positions=pd.Index(pr.p['Pipe ID']).get_indexer(ids);assert (positions>=0).all()
    survival=np.ones((len(pr.p),25));survival[positions]=sv;survival[pr.start]=0
    c=pd.read_csv(INPUT/'CMS001_predictions_2027.csv')
    mean=pr.p['Pipe ID'].map(c.set_index('pipe_id').predicted_repair_cost).fillna(float(c.predicted_repair_cost.median())).to_numpy();mean[pr.start]=0
    before=np.column_stack([(~pr.start).astype(float),survival[:,:-1]])
    return pr,units,n,uy,py,active,before,survival,mean

def save_json(name,data):
    (HERE/name).write_text(json.dumps(data,indent=2,ensure_ascii=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),encoding='utf8')
