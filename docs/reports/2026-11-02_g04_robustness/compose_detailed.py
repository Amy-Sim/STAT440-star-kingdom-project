from pathlib import Path
import json
import pandas as pd
HERE=Path(__file__).resolve().parent
d=pd.read_csv(HERE/'evidence/absolute_metrics_summary.csv').set_index('arm')
order=['shana_20a','ryota_original','amy_integrated','takito_g04']
table=[['Metric / author and candidate','Shana / 20a','Ryota / reduced draft','Amy / integrated cover','Takito / G04'],
 ['Public score ($M)','74.03 *','77.29 **','77.4565','78.9910']]
for label,col,fmt in [('Repair-cost RMSE ($)','RMSE',',.2f'),('Repair-cost MAE ($)','MAE',',.2f'),
 ('Worst-year RMSE ($)','worst_year_RMSE',',.2f'),('Total prediction bias (%)','total_bias_pct','+.2f'),('Top-10% cost capture (%)','top10_cost_capture_pct','.2f')]:
 table.append([label]+[format(float(d.loc[k,col]),fmt) for k in order])
pages=json.loads((HERE/'detailed_content.json').read_text(encoding='utf8'))['pages']
pages[0]['table']=table
(HERE/'detailed_content.json').write_text(json.dumps(dict(pages=pages),ensure_ascii=False,indent=2),encoding='utf8')
md=[]
for i,page in enumerate(pages):
 md += [('# ' if i==0 else '## ')+page['title'],'']
 if i==0:
  md += [page['subtitle'],'','Current final selection: [G17](../2026-11-02_regional_optimization/G17/README.md).','',page['intro'],'','|'+'|'.join(table[0])+'|','|'+'|'.join(['---']*5)+'|']
  md += ['|'+'|'.join(r)+'|' for r in table[1:]]
  md += ['',page['table_note'],'']
 for section in page['sections']:
  md += ['### '+section['heading'],'']
  for text in section['paragraphs']:md += [text,'']
md += ['[Editable Word](G04_comparison_detailed.docx) / [PDF](paper.detailed.pdf) / [How to calculate indicators ](COST_METRICS.md) / [Implementation formulas and settings](ALGORITHM_DETAILS.md)','']
(HERE/'README.md').write_text('\n'.join(md),encoding='utf8')
print('Content composed: summary + two algorithm pages')
