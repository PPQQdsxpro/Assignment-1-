"""Generate factual reading materials; never generate the student's interpretation."""
from pathlib import Path
import json
import sys
import markdown
import pandas as pd

ROOT=Path(__file__).resolve().parent
SELECTION=[
('C03-S0148','衣服：身份變化','衣服在此只是物品，還是把家珍的生活變化具體化？'),
('C04-S0230','衣服：母女關係','家珍如何行動？鳳霞如何回應？為何舊旗袍被改作衣服？'),
('C05-S0184','鳳霞：照料方向的改變','這次誰照顧誰？能否只把家珍概括成照顧者？'),
('C06-S0196','衣服：攜帶食物','先讀前後文。這個衣服的用途與前兩段有何不同？'),
('C07-S0178','床上：疾病與勞動','身体受到限制，是否就等於完全沒有行動？'),
('C08-S0003','床上：相親場景','外貌、衣服、床與家庭活動如何組合？'),
('C04-S0208','商量：家庭決策','誰提出送走鳳霞？「商量」是否足以證明決策權平等？'),
('C07-S0204','拒絕春生的錢','家珍是否只服從福貴？福貴接下來怎樣反應？'),
('C08-S0241','勸春生活下去','她的說話是否與小說「活着」的問題有關？怎樣用原文支持？'),
('C08-S0242','代詞：一句關鍵話的遗漏','本句以「她」延續家珍的說話，沒有「家珍」姓名；姓名搭配詞會漏掉甚麼？'),
('C03-S0017','眼淚：反例','這裏流淚的是誰？為何不能把所有眼淚都歸給家珍？'),
('C02-S0119','床上：反例','這裏躺在床上的是誰？共現與人物屬性有何差別？')]

def main():
    out=ROOT/'output'; notes=ROOT/'notes';notes.mkdir(exist_ok=True)
    records=[json.loads(x) for x in (out/'sentences.jsonl').read_text(encoding='utf-8').splitlines()]
    idx={r['id']:i for i,r in enumerate(records)}
    verification=json.loads((out/'verification.json').read_text(encoding='utf-8'))
    examples=verification['examples']
    text=['# 家珍研究：閱讀材料與你的分析筆記',
        '> 這是閱讀工作紙，不是可提交的報告。統計數據已完成；文學論點需要你閱讀後自行提出。',
        '## 已確認的資料',
        '正式語料：74,916 個正文漢字；保留 2,411 句、49,097 詞；「家珍」保留 577 次，出現在 461 句。依課堂規則排除 49 個少於五詞的句子，其中含三次「家珍」。',
        '結果列數：五詞視窗 78；十詞視窗 107；句子法 141。數量增加不代表後者更正確。',
        '## 六個詞的三組結果',
        '下表每格為「觀察值 O；p 值」。視窗 O 與句子 O 的單位不同。標示未通過者只是用來解釋設定差異，不在正式合格 CSV 中。',
        '| 詞 | 左右五詞 | 左右十詞 | 同一句 |','|---|---|---|---|']
    for w in ['凤霞','有庆','床上','衣服','商量','春生']:
        cells=[]
        for run in ['window5','window10','sentence']:
            e=next(e for e in examples if e['word']==w and e['run']==run)
            cells.append(f"{e['a']}；{e['p_value']:.4g}"+('（未通過）' if not e['passes_p'] else ''))
        text.append('| '+w+' | '+' | '.join(cells)+' |')
    text += ['','數據表的 p 值使用獨立 SciPy 核對值；與 qhchina 的差異小於 10⁻⁹，不影響是否通過 .05 的判斷。正式 CSV 保留 qhchina 原始輸出。',
             '## 十二段原文：按順序讀',
             '每段先讀前後文，再用自己的話回答問題。章節標題沿用這份教師語料的分章。']
    for sid,title,question in SELECTION:
        i=idx[sid];r=records[i]
        text += [f"### {title}｜{r['chapter']} {sid}",
                 '**前句：** '+(records[i-1]['text'] if i else ''),
                 '**核心原文：** '+r['text'],
                 '**後句：** '+(records[i+1]['text'] if i+1<len(records) else ''),
                 '**思考：** '+question,
                 '**你的筆記：** ＿＿＿＿＿＿＿＿＿＿＿＿']
    text += ['## 請你最後回答三個問題',
        '1. 綜合「衣服」「床上」及母女關係段落，你認為福貴如何呈現家珍？請指出兩個句子 ID，並說明不是每一個共現都能直接歸於家珍。',
        '2. 比較「商量」、拒收金錢與勸春生活下去的段落，你認為家珍只是襯托福貴，還是有自己的判斷？你也可以提出其他解釋。請用具體原文說明。',
        '3. 哪一項結果或反例最能說明搭配詞的限制？比較三種設定後，你會怎樣限定自己的結論？',
        '請先寫自己的閱讀判斷，不用追求漂亮句子。我會幫你檢查它們是否被數據及原文支持。']
    md='\n\n'.join(text)
    # Repair Markdown table continuity (blank lines must not split rows).
    md=md.replace('|\n\n|','|\n|')
    (notes/'reading_guide.md').write_text(md+'\n',encoding='utf-8')
    content=markdown.markdown(md,extensions=['tables'])
    page='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>家珍研究閱讀材料</title><style>body{max-width:960px;margin:40px auto;padding:0 24px;color:#203a36;background:#f7f4ed;font:17px/1.85 "Microsoft JhengHei",sans-serif}h1{font-size:30px}h2{margin-top:40px;border-bottom:2px solid #adc5b7}h3{margin-top:35px;color:#236453}table{border-collapse:collapse;width:100%;background:white}td,th{padding:9px;border:1px solid #cdd7ce}blockquote{background:#fff0c8;padding:6px 18px;margin:0}p{overflow-wrap:anywhere}@media print{body{background:white;font-size:11pt}h3{break-after:avoid}table{font-size:10pt}}</style>'+content+'</html>'
    (notes/'reading_guide.html').write_text(page,encoding='utf-8')
    print('Reading guide created with 12 located passages.')

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
