"""Render the student's Markdown into matching HTML/PDF, with visible draft status."""
from pathlib import Path
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html import escape
import markdown
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle

ROOT=Path(__file__).resolve().parent

def main():
    md=(ROOT/'report.md').read_text(encoding='utf-8')
    draft='待你' in md
    body=markdown.markdown(md,extensions=['tables'])
    banner='草稿：個人分析尚未完成，請勿提交' if draft else '《活着》家珍搭配詞研究'
    (ROOT/'report.html').write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>家珍人物空間研究</title><style>body{max-width:820px;margin:40px auto;padding:0 24px;font:17px/1.9 "Microsoft JhengHei",sans-serif;color:#263b37}blockquote{background:#fff0d7;padding:8px 20px}h1{font-size:28px}h2{font-size:21px}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #ccc}a{overflow-wrap:anywhere}</style>'+body+'</html>',encoding='utf-8')
    font_path=os.environ.get('CHI_FONT','C:/Windows/Fonts/msjh.ttc')
    if Path(font_path).exists():
        pdfmetrics.registerFont(TTFont('Chinese',font_path,subfontIndex=0))
        font='Chinese'
    else:
        pdfmetrics.registerFont(UnicodeCIDFont('MSung-Light'));font='MSung-Light'
    pdfmetrics.registerFontFamily(font,normal=font,bold=font,italic=font,boldItalic=font)
    base=ParagraphStyle('Body',fontName=font,fontSize=10.5,leading=17,spaceAfter=9,wordWrap='CJK',textColor=colors.HexColor('#243b36'))
    h1=ParagraphStyle('Title',parent=base,fontSize=19,leading=28,spaceAfter=20)
    h2=ParagraphStyle('Heading',parent=base,fontSize=13,leading=21,spaceBefore=13,spaceAfter=8,keepWithNext=True)
    note=ParagraphStyle('Note',parent=base,fontSize=9.5,leading=15,backColor=colors.HexColor('#fff0d7'),borderPadding=8,spaceAfter=14)
    def para(text,style=base):return Paragraph(escape(text).replace('\n','<br/>'),style)
    flows=[]
    root=ET.fromstring('<root>'+body+'</root>')
    for el in root:
        content=''.join(el.itertext()).strip()
        if el.tag=='h1':flows.append(para(content,h1))
        elif el.tag in ('h2','h3'):flows.append(para(content,h2))
        elif el.tag=='blockquote':flows.append(para(content,note))
        elif el.tag in ('ul','ol'):
            for i,item in enumerate(el):flows.append(para(('• ' if el.tag=='ul' else f'{i+1}. ')+''.join(item.itertext())))
        elif el.tag=='table':
            rows=[[para(''.join(c.itertext())) for c in row] for row in el.findall('.//tr')]
            if rows:
                table=Table(rows,colWidths=[(A4[0]-100)/len(rows[0])]*len(rows[0]),repeatRows=1)
                table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eeea')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#b8c9bf')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
                flows += [table,Spacer(1,10)]
        elif content:flows.append(para(content))
    def page(canvas,doc):
        canvas.setFont(font,8);canvas.setFillColor(colors.HexColor('#7b6251' if draft else '#5b7469'))
        canvas.drawString(50,A4[1]-30,banner)
        canvas.drawRightString(A4[0]-50,27,str(doc.page))
    SimpleDocTemplate(str(ROOT/'report.pdf'),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=54,bottomMargin=45,
                      title='從搭配詞看《活着》中家珍的人物空間',author='').build(flows,onFirstPage=page,onLaterPages=page)
    maintext=md.split('## 參考資料與AI使用聲明')[0]
    check={'status':'draft_not_ready' if draft else 'requires_final_review','han_characters_before_references':len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]',maintext)),
           'nonwhitespace_characters_before_references':len(re.sub(r'\s','',maintext)),
           'pending_markers':md.count('待你'),'note':'Character counts include headings/placeholders; final prose must be reviewed against the 2500–3000 requirement.'}
    (ROOT/'output/report_status.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(check,ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
