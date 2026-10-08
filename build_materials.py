"""Generate factual reading materials; never generate the student's interpretation."""
from pathlib import Path
import json
import sys
import re
import markdown
import pandas as pd
from opencc import OpenCC

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
('C08-S0242','距離：關鍵話是否落在視窗內','本句其實含有「家珍」。分別檢查五詞、十詞及整句的範圍：引語中的「命」「还」是否被納入？單字篩選又會排除甚麼？'),
('C03-S0017','眼淚：反例','這裏流淚的是誰？為何不能把所有眼淚都歸給家珍？'),
('C02-S0119','床上：反例','這裏躺在床上的是誰？共現與人物屬性有何差別？')]

def main():
    out=ROOT/'output'; notes=ROOT/'notes';notes.mkdir(exist_ok=True)
    records=[json.loads(x) for x in (out/'sentences.jsonl').read_text(encoding='utf-8').splitlines()]
    idx={r['id']:i for i,r in enumerate(records)}
    # Match every processed sentence back to the unchanged original physical lines.
    source_lines=(ROOT/'data/huozhe_original.txt').read_text(encoding='utf-8-sig').splitlines()
    converter=OpenCC('t2s'); compact=[]; line_numbers=[]
    for n,line in enumerate(source_lines,1):
        value=re.sub(r'\s+','',converter.convert(line))
        compact.append(value);line_numbers.extend([n]*len(value))
    source=''.join(compact);cursor=0; locations={}
    for r in records:
        needle=re.sub(r'\s+','',r['text']);pos=source.find(needle,cursor)
        if pos<0: raise AssertionError('Cannot locate original sentence: '+r['id'])
        locations[r['id']]=[line_numbers[pos],line_numbers[pos+len(needle)-1]]
        cursor=pos+len(needle)
    (out/'source_line_map.json').write_text(json.dumps(locations,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
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
             '行數以未修改的 `data/huozhe_original.txt` 為準，與你 Downloads 裏的原始《余华_活着.txt》相同。從第一行起算，空白行也算一行；編輯器的自動折行不另算行數。不是 sentences.txt 的行數。',
             '「核心」定位本頁核心引文；「摘錄」涵蓋本頁前句、核心、後句；「建議通讀」再向兩邊各延伸八行，供你理解情節，並非引文精確範圍。',
             '**更正先前工作紙：** C08-S0242 明確含有「家珍在里面哭了」，不能用它證明整句沒有姓名而被漏掉。以下改為檢查視窗距離及單字篩選；這項更正不改變統計結果。',
             '| 段落 | 句子 ID | 核心原文行數 | 摘錄行數 | 建議通讀行數 |','|---|---|---|---|---|']
    ranges={}
    for sid,title,_ in SELECTION:
        i=idx[sid];r=records[i];a,b=locations[sid]
        before=records[i-1] if i and records[i-1]['chapter']==r['chapter'] else r
        after=records[i+1] if i+1<len(records) and records[i+1]['chapter']==r['chapter'] else r
        c,d=locations[before['id']][0],locations[after['id']][1]
        e,f=max(1,c-8),min(len(source_lines),d+8)
        ranges[sid]=(a,b,c,d,e,f)
        text.append(f'| {title} | {sid} | {a}–{b} | {c}–{d} | {e}–{f} |')
    text += ['## 分析時的五個動作',
             '1. **辨認人物：** 圈出誰說話、誰行動、誰被描述；把「我」「她」「我娘」還原成具體人物。\n2. **找細節：** 寫下動作、物件及語氣，不先貼「賢妻良母」等標籤。\n3. **提出解釋：** 這些細節如何讓讀者看見家珍？哪些來自她的直接話語，哪些來自福貴的評價？\n4. **找相反證據：** 同一詞在另一場景是否有不同意思？一段重要情節能否代表全書？\n5. **返回研究問題：** 統計把你的注意力帶到哪裏？原文又補上了哪些統計看不到的內容？',
             '每段可先填：「這裏的行動者是＿＿；我注意到＿＿（原文字詞）；可能表示＿＿；但＿＿使我不能直接斷定＿＿。」',
             '以下問題都是可探索的方向，並非預定答案。不同結論只要有原文支持都可以。']
    prompts=[
        '比較「旗袍／粗布」及「喘不過氣／笑盈盈」兩組對照。福貴能直接知道她的內心嗎？微笑還可能表示甚麼？留意後句有損壞字串，勿猜補。',
        '先查清送走鳳霞的原因，再看穿衣的動作與落淚。連續的「她」各指誰？這一幕是否同時包含照料、貧困與無奈？不要把所有眼淚直接歸給母親。',
        '把「背」的施受關係寫出來。家珍既接受照料又評價女兒，這對「她只有母職功能」的說法有甚麼補充或挑戰？',
        '查前文米從哪裏來，以及為甚麼要藏。這裏的衣服是身份標記，還是生存行動的工具？能否與第一段形成變化？',
        '分開記錄身體限制、針線勞動及福貴的期待。床上出現頻繁是否足以推出「被動」？哪些句子支持，哪些反駁？',
        '誰安排鞋子？誰被細寫外貌？家珍在婚事中有沒有說話或決策，要再看後文。敘述她的外貌不一定等於讓她表達自己的想法。',
        '區分「參與商量」與「擁有相同決定權」。有沒有她的直接回答？鳳霞與有慶被如何取捨？目前摘錄能支持到哪一步？',
        '比較家珍的直接質問與福貴退錢的動作。她的話是否改變他人的行為？再想：只有一次衝突，是否足以推論她在全書中的權力？',
        '回看有慶之死及春生目前的困境。把「拒收錢」與「你要活着」放在一起，可能是態度轉變、堅持同一價值，或兩者兼有嗎？',
        '「欠命／還命」把生存說成甚麼關係？這是否等於原諒？先不要定論。這句有姓名，句子法可以納入；然而統計不理解比喻或倫理判斷。',
        '把「我娘」與「家珍」分清楚。這一條能推翻「每個眼淚都描寫家珍」，但能否因此否定所有眼淚的結果？這兩種主張強度不同。',
        '床上屬於父親，家珍則在灶間。比較窄視窗與整句：範圍擴大會增加哪些關係，也可能混入哪些人物？實際查表後再下結論。']
    for selection_index,(sid,title,question) in enumerate(SELECTION):
        i=idx[sid];r=records[i]
        a,b,c,d,e,f=ranges[sid]
        text += [f"### {title}｜{r['chapter']} {sid}",
                 f'**TXT 定位：核心第 {a}–{b} 行；本頁摘錄第 {c}–{d} 行；建議通讀第 {e}–{f} 行。**',
                 '**前句：** '+(records[i-1]['text'] if i else ''),
                 '**核心原文：** '+r['text'],
                 '**後句：** '+(records[i+1]['text'] if i+1<len(records) else ''),
                 '**思考：** '+question,
                 '**分析提示：** '+prompts[selection_index],
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
    walkthrough=notes/'project_walkthrough.md'
    if walkthrough.exists():
        header=page[:page.index('<h1>')].replace('<title>家珍研究閱讀材料</title>','<title>這份研究是怎樣完成的？</title>')
        body=markdown.markdown(walkthrough.read_text(encoding='utf-8'),extensions=['tables'])
        (notes/'project_walkthrough.html').write_text(header+body+'</html>',encoding='utf-8')
    print('Reading guide created with 12 located passages.')

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
