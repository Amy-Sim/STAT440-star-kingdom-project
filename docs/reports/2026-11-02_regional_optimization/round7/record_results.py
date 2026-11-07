from pathlib import Path
from decimal import Decimal
import json,csv
import pandas as pd

OUT=Path(__file__).resolve().parent
METHODS={
'G22_Ryota_fixed3':'Ryota: Fixed order of 3-year cumulative risk',
'G23_Ryota_dynamic3':'Ryota: Dynamic limit update for initial 3 years + remaining fixed order',
'G24_Amy_annualBCR':'Amy: Annual BCR + cumulative pipe length progress',
'G25_Amy_submitted_order':'Ported Amy\'s 77.46M submission order (inherited Ryota\'s order)'}

def main():
    log=json.loads((OUT/'submission_log.json').read_text(encoding='utf8'))
    metrics=pd.read_csv(OUT/'method_comparison_summary.csv');rows=[]
    for r in log:
        name=r['candidate'];short=name.split('_')[0]
        with (OUT/f'official_{short}.csv').open(newline='') as f:a=list(csv.DictReader(f))
        assert [int(x['YEAR']) for x in a]==list(range(1,26))
        capex=sum(Decimal(x['CAPEX']) for x in a);opex=sum(Decimal(x['OPEX']) for x in a)
        score=Decimal(250000000)-capex-opex;s=metrics[metrics.arm==name].iloc[0]
        r.update(status='complete',method=METHODS[name],CAPEX=str(capex),OPEX=str(opex),public_score=str(score),delta_vs_G17=str(score-Decimal('79168928.88')),
            internal_mean_gain=float(s.mean_gain),internal_worst_setting_gain=float(s.worst_setting_gain),positive_settings=int(s.positive_settings),all_feasible=bool(s.all_feasible))
        rows.append(r)
    (OUT/'submission_log.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
    pd.DataFrame(rows).to_csv(OUT/'official_results.csv',index=False)
    best=max(rows,key=lambda r:Decimal(r['public_score']))
    lines=['# Amy / Ryota order × G17 circle arrangement','',
        'Based on circle in G17 (Public $79,168,928.88), we submitted four proposals that combined existing rearrangements. After completing the generation, inspection, and internal evaluation, we fixed the CSV and recorded the official results.','',
        '|Candidate|Order source|Public score( dollars)|Difference from G17( dollars)|Mean internal difference( dollars)|Internal settings with positive mean gain|',
        '|---|---|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"|{r['candidate'].split('_')[0]}|{r['method']}|{Decimal(r['public_score']):,.2f}|{Decimal(r['delta_vs_G17']):+,.2f}|{r['internal_mean_gain']:+,.2f}|{r['positive_settings']}/24|")
    lines+=['','## How to combine','',
        'For G22 to G24, only the ordering rules are ported, leak prediction is unified to F168, and conditional repair cost is unified to CMS001. This is not a re-learning reproduction of past Amy/Ryota prediction models. G25 made the order of the saved 77.46M submitted CSV correspond to the earliest order of the new circle exchange target. If multiple pipes result in the same new circle, place the circle at the position of the earliest pipe.','',
        'After reordering, calculate each row\'s newly replaced pipes and readjust center, radius, and splitting while covering their endpoints. All methods share a cap of 384 center positions per batch. Search same-year neighbors up to 350 m depending on local density; merge only groups reducing local expected costs. Computational limits are 16 circles/48 pipes; accepted group sizes depend on local costs.','',
        'Because geometry is also readjusted, public differences compare complete plans combining ordering and geometry; they are not causal effects of reordering alone.','',
        'Every variant preserves G17\'s union of replacement targets. Original coverage circles remain as a PU-only zero-cost suffix. The exported CSV was reloaded and checked for complete original-iron geometry, a $10M annual budget with carryover, and completion by 2051.','',
        'G24\'s original method concatenates annual plans as CSV sequences. Since the submitted CSV cannot directly specify the scheduled year, if there is a surplus of budget, the line for the next scheduled year can actually be executed earlier. Including this point, the final CSV was evaluated using the same sequential execution rules as the official one.','',
        '## Source and rating','',
        'Amy\'s 77.46M integrated cover proposal inherits Ryota\'s order. G24\'s alternate rules were ported from Amy\'s latest full-pipeline notebook\'s Economic Construction and Required Progress phases. The name of the person in charge is the source of the order, and the construction circle commonly uses the G17 series of Takito/Codex.','',
        '[Ryota\'s original code ](https://github.com/reinesana/STAT440-star-kingdom-project/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/submissions/2026-10-28_ryota_early3/early_three_years.py) / [Amy\'s original notebook ](https://github.com/reinesana/STAT440-star-kingdom-project/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/notebooks/Amy_Sim/star_kingdom_full_pipeline_AS.ipynb)','',
        'Internal evaluation compares against G17 using 24 settings: two forecast families, three leak-rate levels, two cost-dispersion levels, and two regional-correlation levels. Each uses 128 common-random-number scenarios, totaling 3,072, with fresh seed 202611027702. The internal key G05 is a legacy reference-arm name; the actual comparator is G17. This sensitivity analysis is conditional on existing forecasts and does not guarantee private outcomes.','',
        '![Internal evaluation for each forecast assumption ](internal_forecast_comparison.png)','',
        '## Conclusion','']
    if Decimal(best['public_score'])>Decimal('79168928.88'):
        lines.append(f"The highest public score in this round is{best['candidate'].split('_')[0]}'s{Decimal(best['public_score']):,.2f} dollars. Difference from G17:{Decimal(best['delta_vs_G17']):+,.2f} dollars. Internal results are reported alongside public gains to distinguish observed improvement from superiority on unknown data.")
    else:lines.append('None of these four candidates beat G17 publicly. G17 remained the highest-public-score candidate at that stage.')
    for r in rows:lines+=['',f"Official breakdown: [{r['candidate'].split('_')[0]}]({r['result_url']})"]
    (OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(pd.DataFrame(rows)[['candidate','public_score','delta_vs_G17','internal_mean_gain']].to_string(index=False))

if __name__=='__main__':main()
