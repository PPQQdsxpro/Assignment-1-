# 《活着》家珍搭配詞研究

CHI3242 作業 1。語料為余華《活着》，研究「家珍」姓名的搭配詞與人物空間。

**目前狀態：程式、三組結果及完整報告已完成。報告整合學生閱讀筆記與 Codex 補充撰寫，已列明 AI 使用範圍；提交前需由學生確認內容。尚未提交 Moodle。**

## 語料來源

- 作者：余華；書名：《活着》。
- 直接來源：教師提供之課堂 UTF-8 純文字檔案。學生確認此檔可用於本次作業；沒有可分享的獨立下載網址。
- 原檔末尾附帶來源線索：http://www.ixdzs.com 及 http://m.ixdzs.com 。這些僅為檔案內附地址，未獨立核實為本檔下載來源。
- 課程方法頁：https://mcjkurz.github.io/teaching/courses/2026-2027/CHI3242/notes/week-04/ （不是語料下載連結）。
- 原始檔：`data/huozhe_original.txt`，完整保留。原文權利歸原權利人；本倉庫不對小說另作開源授權。
- SHA-256：`1b5068f8aad70bc4fa22a86a5cc96f55ea3f02e93ae336c2490beb86d569ecbc`。

## 如何重做分析

使用 Python 3.12。於倉庫資料夾開啟終端機：

```text
python -m venv .venv
```

Windows：

```text
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run_all.py
```

macOS / Linux / Codespaces：

```text
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run_all.py
```

`run_all.py` 依序執行 `segment.py`、`collocates.py`、`verify.py`、`make_report.py`、`build_materials.py`。不會覆寫學生的報告文字。

如使用本次電腦已建立的環境，可在上一層課程資料夾執行：

```text
.venv-chi\Scripts\python huozhe-jiazhen\run_all.py
```

開啟 `output/results.html` 即可離線比較三組結果；點選詞語可查看對應設定的原文及前後句。`notes/reading_guide.html` 是十二段原文閱讀工作紙。

閱讀工作紙現包含每段在原始 TXT 的核心行數、前後句範圍及建議通讀範圍，另有逐段分析提示。`notes/project_walkthrough.html` 是給初學者的流程及文件導讀；兩頁皆有同名 Markdown 版本。`output/source_line_map.json` 保存全部句子 ID 至原始 TXT 行數的對應。

## 方法與產出

OpenCC t2s → 去除非正文資訊 → 按 。！？ 分句 → jieba（HMM=True，主要人物自訂詞典）→ 去標點 → 保留至少五詞的句子。停用詞與單字仍保留於句子中維持詞距；只透過 qhchina filters 從搭配詞結果排除。

三組皆以「家珍」為目標，`alternative="greater"`，`min_word_length=2`，`max_p=0.05`，並再確認 `p_value<0.05`。視窗大小分別為左右各五詞、十詞；另執行句子法。未截斷長句；未施加多重檢定校正。依 `obs_local` 降序排序，同次數按搭配詞字串排序以固定輸出。

| 設定 | 合格搭配詞數 | 檔案 |
|---|---:|---|
| 五詞視窗 | 78 | `output/collocates_jiazhen_window5.csv` |
| 十詞視窗 | 107 | `output/collocates_jiazhen_window10.csv` |
| 句子法 | 141 | `output/collocates_jiazhen_sentence.csv` |

其他紀錄：`corpus_stats.json`（語料規模）、`cleaning_log.json`（清理與疑似損壞處）、`sentences.jsonl`（原文定位）、`run_metadata.json`（參數與版本）、`verification.json`（獨立驗證）、`comparison.json`（前20名比較）、`segmentation_check.csv`（十句分詞抽查）。

`output/exploratory_baseline/` 保存第一次分詞設定有缺陷的初跑結果，**不得與正式結果混用**。詳見 `notes/experiment_log.md`。

## 報告與 PDF

學生先完成 `report.md` 的個人分析及待填段落，再執行：

```text
python render_report.py
```

此腳本由同一份 Markdown 產生 `report.html` 與 `report.pdf`；若仍有「待你」標記，PDF 明確顯示草稿狀態。PDF 輸出使用 ReportLab；Windows 優先使用微軟正黑體，其他環境可用環境變數 `CHI_FONT` 指向可嵌入的中文字體，否則使用內建 CJK 字體。

## AI 使用紀錄

本人使用 Codex 協助核對課程要求、編寫及除錯 Python 程式、建立比較頁、核驗統計、定位原文、整理方法說明與報告骨架。統計由本地 Python / qhchina 實際執行，並用獨立計數與 SciPy 核對。

本人負責閱讀原文、提出主要解釋與限制，並完成個人報告。本次未實際使用 GLM-5.3-Flash 產生研究結果，不將其列為已使用工具。
## 參考資料

- 課程作業 1、Week 3/4 講義及 Week 4 投影片。
- Woloch, Alex. *The One vs. the Many*. 
- https://www.qhchina.org/docs/collocations/find-collocates/
- https://www.qhchina.org/docs/helpers/load-stopwords/
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html



本篇完整報告由 Codex 依學生筆記與後續討論整合撰寫，含 AI 補充的論點與文字，詳見 report.md 末尾聲明。

