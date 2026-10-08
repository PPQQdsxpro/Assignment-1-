"""Run analysis, verify results, and retain only required submission outputs."""
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parent
for name in ['segment.py','collocates.py','verify.py','make_report.py']:
    subprocess.run([sys.executable,str(root/name)],cwd=root,check=True)
intermediates=['sentences.txt','output/cleaned_text.txt','output/cleaning_log.json','output/comparison.json','output/corpus_stats.json','output/excluded_short_sentences.json','output/run_metadata.json','output/segmentation_check.csv','output/sentences.jsonl','output/stopwords_used.txt','output/verification.json']
for name in intermediates:
    p=(root/name).resolve()
    assert p.is_relative_to(root)
    p.unlink(missing_ok=True)
