from pathlib import Path
from decimal import Decimal
import json,hashlib

here=Path(__file__).resolve().parent;rows=[]
for p in [here/'official_results_G05_G06.json',here/'large_circle_round2/submission_log.json',*sorted(here.glob('round*/submission_log.json'))]:
    if not p.exists():continue
    data=json.loads(p.read_text(encoding='utf8'));data=data if isinstance(data,list) else [data]
    for r in data:
        score=r.get('public_score')
        if score is None:continue
        r=r.copy();r['folder']=p.parent.relative_to(here).as_posix();r['source_record']=p.relative_to(here).as_posix();rows.append(r)
rows.sort(key=lambda r:Decimal(str(r['public_score'])),reverse=True)
winner=rows[0];name=winner['candidate'];folder=here/winner['folder']
choices=[folder/'submit'/(name+'.csv'),folder/(name+'.csv')]
csv=next((p for p in choices if p.exists()),None)
if csv is not None:
    assert hashlib.sha256(csv.read_bytes()).hexdigest()==winner['sha256'].lower()
    csvlink=csv.relative_to(here).as_posix()
else:csvlink=winner.get('input_file','')
lines=['# 現在のPublic最高提出','',f"**{name}：{Decimal(str(winner['public_score'])):,.2f}ドル**",'',
    f'[提出CSV]({csvlink}) / [提出記録]({winner["source_record"]})','',
    'Publicの観測結果による順位。内部評価とPrivateでの優位は別に確認する。既存の提出は削除していない。','',
    '|候補|Public score（ドル）|','|---|---:|']
for r in rows:lines.append(f"|{r['candidate']}|{Decimal(str(r['public_score'])):,.2f}|")
(here/'LATEST_SUBMISSION.ja.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print('Current public leader:',name,winner['public_score'])
