from pathlib import Path
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

out=Path(__file__).resolve().parent
s=pd.read_csv(out/'method_comparison_summary.csv')
matplotlib.rcParams['font.family']='DejaVu Sans'
fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained');y=np.arange(len(s))
ax.barh(y-.17,s.A_mean_gain/1e6,height=.3,label='CMS001 / F168 premise',color='#247F7C')
ax.barh(y+.17,s.B_mean_gain/1e6,height=.3,label='Fine-age risk and historical-cost assumptions',color='#C17B37')
ax.set_yticks(y,[x.split('_')[0] for x in s.arm]);ax.invert_yaxis();ax.axvline(0,color='black',linewidth=1)
ax.set_title('Ordering combined with G17 geometry: internal results by forecast family',pad=36)
ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),ncol=1,fontsize=9)
ax.set_xlabel('Average difference from G17 (million dollars, better on the right)')
fig.savefig(out/'internal_forecast_comparison.png',dpi=150)
