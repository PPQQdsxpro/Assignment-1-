"""Build a self-contained, offline comparison and concordance page."""
from pathlib import Path
import html
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent
LABELS = {'window5':'左右各 5 詞','window10':'左右各 10 詞','sentence':'同一句子'}

def main():
    out = ROOT/'output'
    frames = {k:pd.read_csv(out/f'collocates_jiazhen_{k}.csv') for k in LABELS}
    records = [json.loads(line) for line in (out/'sentences.jsonl').read_text(encoding='utf-8').splitlines()]
    contexts = []
    for i,r in enumerate(records):
        if r['kept'] and r['target_tokens']:
            contexts.append({**r,
                'before':records[i-1]['text'] if i and records[i-1]['chapter']==r['chapter'] else '',
                'after':records[i+1]['text'] if i+1<len(records) and records[i+1]['chapter']==r['chapter'] else ''})
    tops = {k:set(f.head(20)['collocate']) for k,f in frames.items()}
    comparison = {'top20_common_all': sorted(set.intersection(*tops.values())),
        'pairs':{f'{a}_vs_{b}': {'shared':sorted(tops[a]&tops[b]), 'only_first':sorted(tops[a]-tops[b]),
            'only_second':sorted(tops[b]-tops[a])} for a,b in [('window5','window10'),('window5','sentence'),('window10','sentence')]}}
    (out/'comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    payload = {'runs':{k:f.to_dict('records') for k,f in frames.items()}, 'labels':LABELS,
               'contexts':contexts,'stats':json.loads((out/'corpus_stats.json').read_text(encoding='utf-8')),
               'comparison':comparison}
    serialized=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')
    page='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>《活着》家珍：搭配詞與原文</title><style>
:root{color-scheme:light}body{margin:0;background:#f5f2eb;color:#253c39;font:16px/1.65 "Microsoft JhengHei",sans-serif}main{max-width:1380px;margin:auto;padding:32px}h1{font-size:30px;margin-bottom:6px}h2{font-size:21px}p{margin:8px 0 18px}.tag{color:#697771;font-size:13px;letter-spacing:1px}.cards{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}.card{background:white;border:1px solid #ddd9ce;border-radius:12px;padding:14px 20px}.card b{display:block;font-size:24px}select,input,button{font:inherit;padding:8px;border:1px solid #aab5b0;border-radius:6px;background:white}label{margin-right:16px}.grid{display:grid;grid-template-columns:minmax(580px,1.2fr) minmax(320px,1fr);gap:22px}.panel{background:white;border-radius:12px;padding:20px;border:1px solid #ddd9ce;min-width:0}.scroll{overflow:auto;max-height:680px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;border-bottom:1px solid #e4e8e5;padding:8px;white-space:nowrap}th{position:sticky;top:0;background:#eaf0ec}tr.pick{cursor:pointer}tr.pick:hover,tr.selected{background:#fff0ca}mark{background:#ffe8a0;color:#223b36}.context{border-bottom:1px solid #ddd;padding:14px 0}.muted{color:#737d79;font-size:14px}.anchor{font-weight:bold;color:#236753}details{margin:20px 0}a{color:#246d63}#status{font-size:14px}footer{font-size:13px;margin-top:22px;color:#6a746f}@media(max-width:1000px){.grid{grid-template-columns:1fr}main{padding:16px}}
</style><main><div class="tag">CHI3242 · 可重現文本分析 · 研究結果與閱讀工作台</div><h1>《活着》中的家珍</h1><p>比較姓名周圍的詞語，再回到原文判斷它們描寫了誰、甚麼行動與關係。這個頁面呈現統計結果，不代替文學論證。</p>
<div class="cards" id="cards"></div><div class="panel"><label>分析範圍 <select id="run"><option value="window5">左右各 5 詞</option><option value="window10">左右各 10 詞</option><option value="sentence">同一句子</option></select></label><label>搜尋搭配詞 <input id="search" placeholder="例如：凤霞、说话"></label><label><input type="checkbox" id="top">只看前 20 名</label><p id="status"></p><a id="download">下載這組完整 CSV</a></div>
<div class="grid" style="margin-top:22px"><section class="panel"><h2>搭配詞結果</h2><p class="muted">按共現次數降序排列；點選任何詞語查看相同設定下的原文。</p><div class="scroll"><table><thead><tr><th>排名</th><th>搭配詞</th><th>觀察值 O</th><th>期望值 E</th><th>O/E</th><th>p 值</th></tr></thead><tbody id="rows"></tbody></table></div></section><section class="panel"><h2 id="ctitle">點選左側搭配詞</h2><p id="csummary" class="muted">原文以簡體保留。淡色文字是前後句，黃色是姓名及搭配詞。</p><div class="scroll" id="contexts"></div></section></div>
<details class="panel" open><summary>三組前 20 名的共同詞與差異</summary><div id="comparison"></div></details>
<details class="panel"><summary>方法、欄位與解讀限制</summary><p>三組均以「家珍」為目標，Fisher 單尾 greater，p &lt; 0.05，候選詞至少兩字。停用詞只從結果排除，保留原本位置。句子按 。！？ 分隔，去標點，保留至少五詞，未截斷長句。</p><p>視窗的 O 是目標語境中候選詞的位置數；句子法的 O 是同時含兩詞的句子數，因此不能直接比較兩種 O 的大小。原文面板按句顯示；一個句子可提供多個視窗共現位置，所以原文句數未必等於 O。</p><p>p 值不是解釋正確的概率；O/E 也不是文學重要性的排名。沒有多重檢定校正。姓名分析會漏掉代詞與其他稱呼，附近的詞也可能描述其他人物。疑似原文損壞內容保留並記錄於 cleaning_log.json。</p></details>
<footer>全文與程式在同一作業資料夾；本頁可離線使用。數據由 qhchina 實際計算。<br>閱讀筆記：記下句子 ID、行動者、說話者、你的解釋及反例。</footer></main>
<script>const DATA=__DATA__;
const $=id=>document.getElementById(id);let chosen='';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=x=>Number(x).toLocaleString('en-US',{maximumFractionDigits:2});
$('cards').innerHTML=[['正文漢字',DATA.stats.cleaned_han_characters],['保留句子',DATA.stats.sentences_kept],['家珍詞次',DATA.stats.target_tokens_kept],['含家珍句子',DATA.stats.target_sentences_kept]].map(([l,v])=>`<div class="card">${l}<b>${num(v)}</b></div>`).join('');
function matches(r,w,key){if(key==='sentence')return r.tokens.includes(w);let h=key==='window5'?5:10;return r.tokens.some((t,i)=>t==='家珍'&&r.tokens.slice(Math.max(0,i-h),i+h+1).includes(w));}
function mark(s,w){let a=esc(s);for(let t of ['家珍',w]){if(t)a=a.split(esc(t)).join('<mark>'+esc(t)+'</mark>')}return a;}
function showContexts(w){chosen=w;let key=$('run').value;let rows=DATA.contexts.filter(r=>matches(r,w,key));$('ctitle').textContent='「'+w+'」的原文語境';$('csummary').textContent=DATA.labels[key]+'：'+rows.length+' 個匹配句子。先讀前後文，再判斷誰在說話、誰在行動。';$('contexts').innerHTML=rows.map(r=>`<article class="context"><div class="anchor">${esc(r.chapter)} · ${r.id}</div><div class="muted">${esc(r.before)}</div><p>${mark(r.text,w)}</p><div class="muted">${esc(r.after)}</div></article>`).join('');}
function draw(){let key=$('run').value,all=DATA.runs[key],q=$('search').value.trim(),arr=all.map((r,i)=>({...r,rank:i+1})).filter(r=>(!$('top').checked||r.rank<=20)&&r.collocate.includes(q));$('status').textContent=`完整合格結果 ${all.length} 詞；目前顯示 ${arr.length} 詞。所有 p 值均小於 0.05。`;$('download').href=`collocates_jiazhen_${key}.csv`;$('rows').innerHTML=arr.map(r=>`<tr class="pick" tabindex="0" data-word="${esc(r.collocate)}"><td>${r.rank}</td><td><b>${esc(r.collocate)}</b></td><td>${num(r.obs_local)}</td><td>${num(r.exp_local)}</td><td>${num(r.ratio_local)}</td><td>${Number(r.p_value).toExponential(3)}</td></tr>`).join('');document.querySelectorAll('tr.pick').forEach(el=>{el.onclick=()=>showContexts(el.dataset.word);el.onkeydown=e=>{if(e.key==='Enter')showContexts(el.dataset.word)}});if(chosen)showContexts(chosen);else if(arr.length)showContexts(arr[0].collocate);}
$('run').onchange=draw;$('search').oninput=draw;$('top').onchange=draw;
$('comparison').innerHTML='<p><b>三組共同：</b>'+DATA.comparison.top20_common_all.map(esc).join('、')+'</p>'+Object.entries(DATA.comparison.pairs).map(([k,v])=>{let [a,b]=k.split('_vs_');return `<p><b>${DATA.labels[a]} 與 ${DATA.labels[b]}</b><br>只在前者前20：${v.only_first.map(esc).join('、')||'無'}<br>只在後者前20：${v.only_second.map(esc).join('、')||'無'}</p>`}).join('');draw();</script></html>'''
    (out/'results.html').write_text(page.replace('__DATA__',serialized),encoding='utf-8')
    print(json.dumps(comparison,ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8'); main()
