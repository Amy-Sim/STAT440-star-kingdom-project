"""Record exact official results and the distinct surrogate / whole-plan checks."""
from pathlib import Path
import json,csv,sys
from decimal import Decimal
import pandas as pd

HERE=Path(__file__).resolve().parent

def main():
    out=HERE/sys.argv[1];log=json.loads((out/'submission_log.json').read_text(encoding='utf8'))
    metrics=pd.read_csv(out/'method_comparison_summary.csv');rows=[]
    for r in log:
        name=r['candidate'];short=name.split('_')[0]
        with (out/f'official_{short}.csv').open(newline='') as f:a=list(csv.DictReader(f))
        assert [int(x['YEAR']) for x in a]==list(range(1,26))
        c=sum(Decimal(x['CAPEX']) for x in a);o=sum(Decimal(x['OPEX']) for x in a);score=Decimal('250000000')-c-o
        r.update(status='complete',CAPEX=str(c),OPEX=str(o),public_score=str(score),delta_vs_G17=str(score-Decimal('79168928.88')))
        s=metrics[metrics.arm==name].iloc[0]
        r.update(internal_mean_gain=float(s.mean_gain),internal_worst_setting_gain=float(s.worst_setting_gain),internal_positive_settings=int(s.positive_settings),all_feasible=bool(s.all_feasible))
        rows.append(r)
    (out/'submission_log.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
    pd.DataFrame(rows).to_csv(out/'official_results.csv',index=False)
    nn=out.name=='round6'
    lines=['# Radius prediction by pipe and value prediction of circle candidates: Comparison of stacking','',
        'G17 held the highest existing public score at $79,168,928.88. The user explicitly authorized one submission per method for comparison, even with worse internal results, provided coverage, budget, and deadline requirements passed. The best existing submission was retained.','',
        '|Candidate|Origin and method|Public score( dollars)|Difference from G17( dollars)|Mean internal difference( dollars)|Internal settings with positive mean gain|',
        '|---|---|---:|---:|---:|---:|']
    for r in rows:
        short=r['candidate'].split('_')[0];role='User: per-pipe radius prediction' if short in ['G18','G20'] else 'Codex: circle candidate value prediction + update'
        lines.append(f"|{short}|{role}|{float(r['public_score']):,.2f}|{float(r['delta_vs_G17']):+,.2f}|{r['internal_mean_gain']:+,.2f}|{r['internal_positive_settings']}/24|")
    lines+=['','## Two methods implemented','',
        'The 166 pipe/neighborhood features include other-pipe counts/lengths by material and surface within 25/50/100/250 m, replaced fractions, coordinates, pipe length/orientation/age, CMS001 costs, and F168 probabilities. Official public annual breakdowns were not used to construct training targets.','',
        'The radius method compares circles enclosing 1/2/4/8 neighboring pipes with existing circles; the radius with the best local expected cost is the learning target. Stacking predicts per-pipe radius multipliers. Pipes are processed in the original priority order, using circles that contain both endpoints. Centers are selected from the midpoint and several perpendicular offsets; replaced pipes are skipped. Overly expensive circles fall back to single-pipe circles.','',
        'The candidate-value method uses 186 features: the same neighborhood inputs plus 20 circle-specific features, including radius, center displacement, contained pipes, all surfaces, replacement length, predicted costs, and probabilities. Stacking predicts local work value and ranks candidates within scheduled-year groups. Each acceptance updates neighboring candidates\' unreplaced pipes, lengths, and remaining values. Remaining value approximates the initial prediction using the unreplaced-risk fraction; the stack is not retrained at every step. Overly expensive circles fall back to single-pipe circles.','',
        'Both methods retain all existing circles as a suffix. The construction prefix replaces the original plan\'s entire target set, so the suffix contains only replaced pipes and meets geometric coverage at zero cost. The exported CSV was reloaded and checked for complete iron coverage, annual budget and carryover, and completion by 2051.','',
        '## Learning and evaluation','']
    lines.append('Base models are ExtraTrees, HistGradientBoosting, and standardized Ridge. Ridge combines three-fold OOF predictions split by 500 m cells.')
    if nn:
        lines.append('Extensions add a lightweight MLP (32 → 16 hidden units, at most 10,000 training rows and 100 iterations, with early stopping) plus a 64-component Nyström RBF approximation with Ridge. Standardization is fitted within each training split.')
        lines.append('Final neural networks contain 5,889 radius-model parameters and 6,529 candidate-value parameters. The radius network stopped after 59 iterations; the candidate-value network reached its 100-iteration cap, so convergence is unconfirmed. Neural networks and kernels were added together; public differences cannot be attributed to neural networks alone.')
    lines+=['','The northeast region was held out, with training locations at least 500 m from its boundary. This measures approximation to local targets derived from existing forecasts, not independent accuracy on future construction costs. Final models were then fitted across all regions.','',
        'Targets compare expected costs of grouped construction in the scheduled year with individual-pipe work three years later. The later single-pipe surface cost approximates only that pipe\'s surface and minimum radius; it is not an observed optimal-plan target. Both this approximation and conversion of local values into a budget-constrained global plan introduce error.','',
        'Compare the frozen CSVs against G17 across 24 settings: two forecast families, three leak rates, two cost-dispersion levels, and two regional-correlation levels, each with 128 common-random-number scenarios (3,072 total). G05 is a legacy internal reference-arm key; the actual comparator is G17, as recorded in the protocol.','',
        '## Conclusion','',
        'These results do not rule out stacking in general. Learning local approximations to radii or candidate values need not outperform existing geometry optimization and work ordering that account for budgets and leaks. Consider public and internal results together.','',
        'The folder contains submission CSVs, fitted models, generation code, feature lists, held-out-region approximation metrics, full-plan simulation summaries, and official annual breakdowns.']
    for r in rows:lines+=['',f"Official breakdown [{r['candidate'].split('_')[0]}]({r['result_url']})"]
    (out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(pd.DataFrame(rows)[['candidate','public_score','delta_vs_G17','internal_mean_gain']].to_string(index=False))

if __name__=='__main__':main()
