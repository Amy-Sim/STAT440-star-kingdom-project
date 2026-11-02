"""Observed public and forecast-conditional internal differences, same dollar unit."""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

root=Path(__file__).resolve().parent
matplotlib.rcParams['font.family']=FontProperties(fname='C:/Windows/Fonts/YuGothR.ttc').get_name()
rows=[]
for d in ['round5','round6']:
    p=root/d/'submission_log.json'
    if p.exists():rows+=json.loads(p.read_text(encoding='utf8'))
rows=[r for r in rows if r.get('public_score') is not None]
if rows:
    fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained');y=np.arange(len(rows))
    public=np.array([float(r['delta_vs_G17']) for r in rows])/1e6
    internal=np.array([float(r['internal_mean_gain']) for r in rows])/1e6
    ax.barh(y-.17,public,height=.3,label='Publicの実測差',color='#227A78')
    ax.barh(y+.17,internal,height=.3,label='内部シミュレーションの平均差',color='#C47B36')
    ax.set_yticks(y,[r['candidate'].split('_')[0] for r in rows]);ax.invert_yaxis();ax.axvline(0,color='black',linewidth=1)
    ax.set_xlabel('G17からの差（百万ドル、右が良い）');ax.set_title('半径予測・候補価値予測：基本stackingと軽量NN追加版');ax.legend(loc='lower left')
    for yy,xx in zip(y-.17,public):ax.text(xx,yy,f' {xx:+.2f}',va='center',ha='left' if xx>=0 else 'right',fontsize=9)
    fig.savefig(root/'stacking_comparison.png',dpi=150)
