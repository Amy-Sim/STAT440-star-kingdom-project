from pathlib import Path
import json,shutil,hashlib
import pandas as pd
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
REPO_URL='https://github.com/reinesana/STAT440-star-kingdom-project'
BRANCH='takito/g04-robustness-paper-2026-11-02'
REL='docs/reports/2026-11-02_g04_robustness'
PAPER_URL=f'{REPO_URL}/blob/{BRANCH}/{REL}/README.ja.md'
df=pd.read_csv(HERE/'evidence/summary.csv').set_index('arm')
order=['shana_20a','ryota_original','amy_integrated','takito_g04']
headers=['指標 / 作成者・候補','Shana / 20a','Ryota / 縮小原案','Amy / 統合カバー','Takito / G04']
def fmt(key,col):return f"{df.loc[key,col]:+.3f}" if key!='amy_integrated' else '0（基準）'
table=[headers,
 ['Public score ($M)','74.03 *','77.29 **','77.4565','78.9910'],
 ['内部A：平均差 ($M)']+[fmt(k,'A_mean_gain_M') for k in order],
 ['内部B：平均差 ($M)']+[fmt(k,'B_mean_gain_M') for k in order]]

title='G04はPublic最高だが、内部優位は将来の仮定で変わる'
lead='G04のPublicは78.991Mで、Amy案を1.534M上回る。一方、別の漏水・費用仮定ではAmyより平均0.228M低い。Publicの結果と内部評価を分けて、最終提出を判断する。'
note='内部差はAmy案とのスコア差で、正は改善、負は悪化。1M＝100万ドル。* ShanaのPublicは旧評価ルールの参考値。** Ryota原案は幾何カバー不足のため、内部値は診断用で、有効計画の順位には含めない。補修版の比較は付録。'
method='内部A：CMS001の修理費＋F168の漏水予測。内部B：別の年齢ベース漏水予測＋材質・地表別の歴史的平均修理費。漏水量・費用のばらつき・地域ショックを変えた24条件を各256回、同じ乱数で全案に与えた。全案の内部計算には現行の工事費ルールを使い、候補を再調整せず比較した。'
finding='読み方：G04は内部Aで強いが、内部BではAmyをわずかに下回る。Shanaも内部では有力で、Public順と内部順は一致しない。つまり、G04の優位は「どんな将来を想定するか」に依存している。'
steps=[
 '順番を引き継ぐ：CMS001（金額）とF168（時期）で作った修理順序を土台に、各工事で新たに交換する管を取り出す。',
 '円を動かす・分ける：管の両端を覆うことを守り、中心・半径・分割を比較する。地表は交換済み管も含めて集計し、単価が高い別地表を外せる位置を探す。',
 '近隣の円をまとめる：同じ予定年の2-3円を比較。漏水によって各円がPUだけになり無料でスキップできる機会もF168で見積もり、統合後の期待工事費が下がる組を採る。',
 '全鉄管のカバーを残す：元の円は末尾に置く。交換後はPUだけを含むため無料で処理でき、小さい施工円と全鉄管の幾何カバーを両立する。']
example='具体例（G04の前段G02で採用）：水面＋建物を含む半径32.83mの円をずらし、同じ交換対象を水面だけの半径22.11mの円で囲んだ。地表単価は32＋50＝82から32になり、その工事で約$65,688削減した。最終G04では、この後さらに近隣円を統合する。'
limits='判定の限界：これは選択済み計画の感度分析で、未使用の実データによる独立テストではない。過去の年やPublicは既にモデル・候補選択に使われている。新しい乱数でもその選択バイアスは消えず、Privateでの優位や「過学習なし」は断定できない。'
decision='現時点の最終提出はG04を維持する。現行Public最高で、内部Aでも強く、全鉄管カバーと予算条件を満たすため。課題ルールも、残した提出のPublic最高案のPrivate scoreを採点する。一方、内部BではAmyが優位なので、G04のPrivate最良は保証せず、Amy・Shanaも代替候補として保存する。'
sources=[
 ('候補・入力ハッシュ・全24条件・再現コード','METHODS.ja.md'),
 ('Ryota原案とカバー不足の記録',f'{REPO_URL}/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/reports/2026-10-28_ryota_geometry_comparison.md'),
 ('Amy案・公式内訳',f'{REPO_URL}/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/submissions/2026-10-30_integrated_coverage/official_results.json'),
 ('採点対象のルール',f'{REPO_URL}/blob/ca6cdae4b859782e7a30d543fce686a30d52354c/docs/assignment_2026-10-14.md')]

md=[f'# {title}','',f'2026-11-02 | 日本語版 | 作成・集計：Takito（AI補助）','',f'**{lead}**','',
 '|'+ '|'.join(table[0])+'|','|'+'|'.join(['---']*len(headers))+'|']
md += ['|'+'|'.join(row)+'|' for row in table[1:]]
md += ['',note,'','## 同じ条件での内部評価','',method,'',finding,'','## G04はどう作ったか','']
md += [f'{i+1}. {s}' for i,s in enumerate(steps)]
md += ['',example,'','## 結論：最終提出はG04を維持する','',decision,'',f'**{limits}**','','出典・詳細：'+ ' / '.join(f'[{name}]({url})' for name,url in sources),
        '', '[A4・1ページPDF](paper.ja.pdf) / [数値表](evidence/summary.csv)','']
(HERE/'README.ja.md').write_text('\n'.join(md),encoding='utf8')

pdfmetrics.registerFont(TTFont('Jp','C:/Windows/Fonts/YuGothR.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('JpBold','C:/Windows/Fonts/YuGothB.ttc',subfontIndex=0))
normal=ParagraphStyle('Body',fontName='Jp',fontSize=10.5,leading=14.7,spaceAfter=7,wordWrap='CJK',textColor=colors.HexColor('#152331'))
small=ParagraphStyle('Small',parent=normal,fontSize=8.3,leading=11.2,spaceAfter=5)
head=ParagraphStyle('Heading',parent=normal,fontName='JpBold',fontSize=10.5,leading=14,spaceBefore=7,spaceAfter=4)
big=ParagraphStyle('Title',parent=head,fontSize=15,leading=20,spaceBefore=0,spaceAfter=5)
cell=ParagraphStyle('Cell',parent=normal,fontSize=9.3,leading=12.4,spaceAfter=0,alignment=1)
cellhead=ParagraphStyle('CellH',parent=cell,fontName='JpBold',textColor=colors.white)
story=[Paragraph(title,big),Paragraph('2026-11-02  |  日本語版  |  作成・集計：Takito（AI補助）',small),Paragraph(lead,normal),Spacer(1,4)]
rows=[]
for i,row in enumerate(table):rows.append([Paragraph(x,cellhead if i==0 else cell) for x in row])
t=Table(rows,colWidths=[135,95,95,95,95],hAlign='LEFT')
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#243f54')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
 ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
 ('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#243f54')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#cbd3d9')),
 ('BACKGROUND',(-1,1),(-1,-1),colors.HexColor('#eaf3f7'))]))
story += [t,Spacer(1,5),Paragraph(note,small),Paragraph('同じ条件での内部評価',head),Paragraph(method,normal),Paragraph(finding,normal),Paragraph('G04はどう作ったか',head)]
story += [Paragraph(f'{i+1}. {s}',normal) for i,s in enumerate(steps)]
story += [Paragraph(example,normal),Paragraph('結論：最終提出はG04を維持する',head),Paragraph(decision,normal),Paragraph(limits,small),
 Paragraph(f'出典・再現：<link href="{PAPER_URL}"><u>GitHubの本文・付録・入力CSV</u></link>。Publicは提出記録とユーザー提供の年間内訳、内部値は保存したシミュレーションから集計。担当者名はチーム内の方案名で、共同開発部分を含む。',small)]
doc=SimpleDocTemplate(str(HERE/'paper.ja.pdf'),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=30,bottomMargin=28,
 title=title,author='Takito / AI-assisted analysis')
doc.build(story)
r=PdfReader(HERE/'paper.ja.pdf');assert len(r.pages)==1,f'Paper has {len(r.pages)} pages'
text=''.join(p.extract_text() for p in r.pages)
assert all(s in text for s in ['Shana','Ryota','Amy','Takito','78.9910','過学習'])
print('ONE-PAGE PDF VERIFIED',len(text))
