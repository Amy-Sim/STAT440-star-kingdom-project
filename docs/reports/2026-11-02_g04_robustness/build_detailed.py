from pathlib import Path
import json,zipfile
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
from docx import Document
from docx.shared import Pt,Mm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE=Path(__file__).resolve().parent
pages=json.loads((HERE/'detailed_content.json').read_text(encoding='utf8'))['pages']
FONT_DIR=Path('/usr/share/fonts/truetype/dejavu')
if (FONT_DIR/'DejaVuSans.ttf').exists():
 pdfmetrics.registerFont(TTFont('ReportSans',str(FONT_DIR/'DejaVuSans.ttf')))
 pdfmetrics.registerFont(TTFont('ReportSansBold',str(FONT_DIR/'DejaVuSans-Bold.ttf')))
 BODY_FONT,HEADING_FONT='ReportSans','ReportSansBold'
else:
 BODY_FONT,HEADING_FONT='Helvetica','Helvetica-Bold'
body=ParagraphStyle('Body',fontName=BODY_FONT,fontSize=10.2,leading=14.2,spaceAfter=7)
small=ParagraphStyle('Small',parent=body,fontSize=8,leading=10.8,spaceAfter=5)
title=ParagraphStyle('Title',parent=body,fontName=HEADING_FONT,fontSize=14.5,leading=20,spaceAfter=7)
head=ParagraphStyle('Head',parent=body,fontName=HEADING_FONT,fontSize=11.2,leading=15,spaceBefore=7,spaceAfter=4)
cell=ParagraphStyle('Cell',parent=body,fontSize=9.1,leading=12,spaceAfter=0,alignment=1)
cellh=ParagraphStyle('CellH',parent=cell,fontName=HEADING_FONT,textColor=colors.white)
story=[]
for pi,page in enumerate(pages):
 if pi:story.append(PageBreak())
 story.append(Paragraph(page['title'],title))
 if pi==0:
  story += [Paragraph(page['subtitle'],small),Paragraph(page['intro'],body)]
  data=[[Paragraph(v,cellh if i==0 else cell) for v in row] for i,row in enumerate(page['table'])]
  t=Table(data,colWidths=[135,95,95,95,95])
  t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#243f54')),
    ('BACKGROUND',(-1,1),(-1,-1),colors.HexColor('#edf4f7')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#ccd3da')),
    ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
  story += [t,Spacer(1,5),Paragraph(page['table_note'],small)]
 for s in page['sections']:
  story.append(Paragraph(s['heading'],head))
  story.extend(Paragraph(p,body) for p in s['paragraphs'])
pdf=HERE/'paper.detailed.pdf'
SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=40,rightMargin=40,topMargin=30,bottomMargin=28,
                  title=pages[0]['title'],author='Takito').build(story)
assert len(PdfReader(pdf).pages) > 0

doc=Document();sec=doc.sections[0];sec.page_width=Mm(210);sec.page_height=Mm(297)
sec.top_margin=Mm(13);sec.bottom_margin=Mm(13);sec.left_margin=Mm(15);sec.right_margin=Mm(15)
for name in ['Normal','Title','Heading 1','Heading 2']:
 st=doc.styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
 st.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Calibri')
 st.paragraph_format.space_before=Pt(0);st.paragraph_format.space_after=Pt(5)
normal=doc.styles['Normal'];normal.font.size=Pt(10);normal.paragraph_format.line_spacing=Pt(14)
for name,size in [('Title',14.5),('Heading 1',11.2)]:
 st=doc.styles[name];st.font.size=Pt(size);st.font.bold=True
 st.paragraph_format.line_spacing=Pt(size+4);st.paragraph_format.space_before=Pt(5 if name=='Heading 1' else 0)
 st.paragraph_format.keep_with_next=True
def para(text,style=None,small=False):
 p=doc.add_paragraph(text,style=style)
 if small:
  p.paragraph_format.line_spacing=Pt(10.2)
  for r in p.runs:r.font.size=Pt(7.8)
 return p
for pi,page in enumerate(pages):
 if pi:doc.add_page_break()
 para(page['title'],style='Title' if pi==0 else 'Heading 1')
 if pi==0:
  para(page['subtitle'],small=True);para(page['intro'])
  t=doc.add_table(rows=0,cols=5);t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
  widths=[48,33,33,33,33]
  for i,w in enumerate(widths):t.columns[i].width=Mm(w)
  for ri,row in enumerate(page['table']):
   cells=t.add_row().cells
   for ci,text in enumerate(row):
    c=cells[ci];c.width=Mm(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p=c.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=Pt(11.5)
    r=p.add_run(text);r.font.size=Pt(8.7);r.bold=ri==0
    if ri==0:r.font.color.rgb=RGBColor(255,255,255)
    pr=c._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'243F54' if ri==0 else ('EDF3F7' if ri%2 else 'FFFFFF'));pr.append(sh)
    mar=OxmlElement('w:tcMar')
    for edge in ['top','bottom','left','right']:
     x=OxmlElement('w:'+edge);x.set(qn('w:w'),'80');x.set(qn('w:type'),'dxa');mar.append(x)
    pr.append(mar);b=OxmlElement('w:tcBorders')
    for edge in ['top','bottom','left','right']:
     x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');b.append(x)
    pr.append(b)
   tr=t.rows[ri]._tr.get_or_add_trPr();tr.append(OxmlElement('w:cantSplit'))
   if ri==0:tr.append(OxmlElement('w:tblHeader'))
  para(page['table_note'],small=True)
 for s in page['sections']:
  para(s['heading'],style='Heading 1')
  for text in s['paragraphs']:para(text)
for root in [doc.styles.element,doc.element]:
 for b in list(root.xpath('.//w:pBdr')):b.getparent().remove(b)
doc.core_properties.title=pages[0]['title'];doc.core_properties.author='Takito'
word=HERE/'G04_comparison_detailed.docx';doc.save(word)
# Normalize unused default-template font metadata to English names too.
import re
with zipfile.ZipFile(word) as source:
 entries={item.filename:(item,source.read(item.filename)) for item in source.infolist()}
with zipfile.ZipFile(word, 'w') as target:
 for name,(item,data) in entries.items():
  if name.endswith('.xml'):
   text=data.decode('utf8')
   text=re.sub(r'(["\'])([^"\']*[\u3040-\u30ff\u3400-\u9fff][^"\']*)\1',lambda m:m[1]+'Calibri'+m[1],text)
   data=text.encode('utf8')
  target.writestr(item,data)
with zipfile.ZipFile(word) as z:
 x=z.read('word/document.xml').decode();settings=z.read('word/settings.xml').decode()
 assert 'w:documentProtection' not in settings and '<w:drawing' not in x
 assert all(s in x for s in ['Shana','Ryota','Amy','Takito','P1'])
print(f'Created {len(PdfReader(pdf).pages)}-page English report and editable Word document')
