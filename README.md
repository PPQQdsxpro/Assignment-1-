# 《活着》家珍搭配詞分析

作者：余華。語料：教師提供的《活着》UTF-8 全文。原文保存在 data/huozhe_original.txt。

研究以「家珍」為目標，比較左右各五詞、十詞與句子法。使用 OpenCC 簡體正規化、jieba 分詞、qhchina Fisher 單尾 greater 檢定；候選詞至少兩字、排除停用詞、p < 0.05，按觀察共現次數排序。三組合格結果分別有 78、107、141 列。

## 執行方式

使用 Python 3.12，在獨立 Python 環境安裝套件：

```text
python -m pip install jieba==0.42.1 qhchina==0.2.7 opencc-python-reimplemented==0.1.7 scipy==1.18.1 pandas==3.0.6
python run_all.py
```

run_all.py 依序整理文本、計算搭配詞、獨立核對及產生結果頁，最後清除這些步驟的中間檔。保留三份 output/collocates_*.csv 與 output/results.html。單独執行各腳本時，請按相同順序；中間資料由 segment.py 及 collocates.py 自動生成。

report.pdf 是學生修改後提供的原始 PDF；report.md 由該 PDF 轉寫，文字內容一致，不重新生成或改寫 PDF。結果頁可以離線開啟。

## AI 使用聲明

使用 Codex 協助程式、統計核對、資料整理及論證補充，並依學生筆記整合撰寫初稿；本人其後加以修改。報告含 AI 協助生成及補充的文字與論點。統計由 Python 實際執行，未使用 GLM-5.3-Flash。

方法文件：https://www.qhchina.org/docs/collocations/find-collocates/ 及 https://www.qhchina.org/docs/helpers/load-stopwords/ 。
