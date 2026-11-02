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
    lines=['# パイプ別半径予測と円候補の価値予測：stackingの比較','',
        '既存のPublic最高はG17の79,168,928.88ドル。今回は2手法を比較するため、内部評価が悪化しても被覆・予算・期限を満たせば各1案を提出することを、ユーザーが明示的に承認した。既存のベスト提出は削除していない。','',
        '|案|発案・方式|Public score（ドル）|G17との差（ドル）|内部の平均差（ドル）|内部で平均改善した条件|',
        '|---|---|---:|---:|---:|---:|']
    for r in rows:
        short=r['candidate'].split('_')[0];role='ユーザー：管ごとの半径予測' if short in ['G18','G20'] else 'Codex：円候補の価値予測＋更新'
        lines.append(f"|{short}|{role}|{float(r['public_score']):,.2f}|{float(r['delta_vs_G17']):+,.2f}|{r['internal_mean_gain']:+,.2f}|{r['internal_positive_settings']}/24|")
    lines+=['','## 実装した2つの方式','',
        '管・周辺特徴は166項目。25/50/100/250mでの材質・地表別の他管本数と延長、交換済み割合、座標、管の長さ・向き・年齢、CMS001修理費、F168漏水確率などを使った。教師データの公式Public年間内訳の使用はない。','',
        '半径方式：近隣1/2/4/8管の円と既存円を比較し、局所的な期待費用が最も良い半径を学習目標にした。stackingで管ごとの半径倍率を予測し、元の優先順に管を取り上げ、管の両端を含む円で採用する。中心は中点と垂直方向への数候補から選び、交換済み管は飛ばす。高すぎる円は単管円へ投影する。','',
        '候補方式：同じ近隣円候補に、半径・中心の移動量・含有管・全地表・交換長・予測費用と確率など20項目を加えた186項目を使う。stackingで局所的な工事の価値を予測し、予定年の範囲内で候補を順位付けする。採用するたびに周囲の候補の未交換管、交換長、残存価値を更新する。残存価値は予測した初期価値を未交換管の危険度比で配分する近似で、毎回stackingを再学習する方式ではない。高すぎる円は単管円へ投影する。','',
        '両方式とも既存の全円を末尾に残す。施工部分で元計画の交換対象をすべて交換するため、末尾は交換済み管だけとなり無料で幾何カバーを満たす。生成CSVを読み直し、全鉄管被覆・年次予算と繰越・2051年までの完了を検証した。','',
        '## 学習と評価','']
    lines.append('基本モデルはExtraTrees、HistGradientBoosting、標準化したRidge。500m区画による3分割のOOF予測をRidgeメタモデルで結合した。')
    if nn:
        lines.append('追加モデルは軽量MLP（32→16ユニット、最大10,000学習行、最大100反復、早期終了）と、Nyström近似RBFカーネル（64成分）＋Ridge。標準化は各学習分割の内側で行う。')
        lines.append('最終NNのパラメータ数は半径5,889・候補価値6,529。半径NNは59反復で停止、候補価値NNは100反復の計算上限に到達した。候補価値NNの完全収束は確認していない。NNとカーネルを同時追加しているため、Public差をNN単独の効果とは解釈しない。')
    lines+=['','北東地域を評価用に残し、学習側はその境界から500m以上離した。これは既存予測を使った局所的な教師への再現精度であり、実際の将来工事費の独立テストではない。確認後に全地域で最終モデルを学習した。','',
        '教師は「予定年にまとめて施工」と「3年後に単管で施工」の期待費用の差から作った。3年後の単管地表費は、その管自身の地表と最小半径による近似であり、最適な施工計画の実測正解ではない。この近似と、局所価値から予算制約下の全体計画への変換には誤差がある。','',
        '完成した固定CSVは、2種類の予測系統、漏水率3段階、費用のばらつき2段階、地域内の漏水相関2段階の24条件×128乱数＝3,072シナリオでG17と比較した。入力乱数は各候補で共通。内部表の参照腕名G05はコード上のキーで、実際の比較元はprotocolに記録したG17である。','',
        '## 結論','',
        '今回の結果だけでstacking全般の有効性を否定することはできない。ただし、局所的な半径・候補価値の近似を学習するだけでは、既存の幾何最適化と予算・漏水を考慮した修理順を上回るとは限らない。Public最高と内部評価を併記して判断する。','',
        '提出CSV・学習済みモデル・生成コード・特徴量一覧・地域外の近似精度・全体シミュレーション集計・公式年間内訳を同じフォルダに保存した。']
    for r in rows:lines+=['',f"公式内訳 [{r['candidate'].split('_')[0]}]({r['result_url']})"]
    (out/'README.ja.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(pd.DataFrame(rows)[['candidate','public_score','delta_vs_G17','internal_mean_gain']].to_string(index=False))

if __name__=='__main__':main()
