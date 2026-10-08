"""Reproducible preprocessing; keep stopwords in the counting corpus."""
from pathlib import Path
import csv
import hashlib
import json
import re
import sys
import unicodedata
import jieba
from opencc import OpenCC

ROOT = Path(__file__).resolve().parent
TARGET = '家珍'
CHARACTERS = ['家珍', '福贵', '凤霞', '有庆', '二喜', '苦根', '春生', '龙二', '老全', '长根']

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    original = ROOT / 'data/huozhe_original.txt'
    raw_bytes = original.read_bytes()
    raw = raw_bytes.decode('utf-8-sig')
    converter = OpenCC('t2s')
    normalized = converter.convert(raw.replace('\r\n', '\n'))
    baseline_name = list(jieba.cut(TARGET, HMM=False))
    # Preserve named characters consistently, including possible collocates.
    for name in CHARACTERS:
        jieba.add_word(name, freq=1000000)
    chapters = list(re.finditer(r'^第[一二三四五六七八九十百0-9]+章\s*$', normalized, re.M))
    if not chapters:
        raise ValueError('No chapter headings found; inspect the source before processing.')
    records, removed, suspect, bodies = [], [], [], []
    removed.append({'reason': 'front_matter', 'text': normalized[:chapters[0].start()].strip()})
    for ci, heading in enumerate(chapters):
        body = normalized[heading.end():chapters[ci + 1].start() if ci + 1 < len(chapters) else len(normalized)]
        if '=已完结=' in body:
            body, tail = body.split('=已完结=', 1)
            removed.append({'reason': 'end_marker_and_advertisement', 'text': '=已完结=' + tail})
        bodies.append(body.strip())
        chapter = heading.group().strip()
        # Sentence boundaries follow Week 4; paragraph breaks alone are not sentence ends.
        for local_id, match in enumerate(re.finditer(r'[^。！？]+[。！？]*', body), 1):
            text = re.sub(r'\s+', ' ', match.group()).strip()
            if not text or not any(c.isalnum() for c in text):
                continue
            tokens = [w.strip() for w in jieba.cut(text, HMM=True)
                      if w.strip() and any(unicodedata.category(c)[0] in 'LN' for c in w)]
            sid = f'C{ci+1:02d}-S{local_id:04d}'
            record = {'id': sid, 'chapter': chapter, 'text': text, 'tokens': tokens,
                      'kept': len(tokens) >= 5, 'target_tokens': tokens.count(TARGET)}
            records.append(record)
            if '*' in text or '\ufffd' in text:
                suspect.append({'id': sid, 'chapter': chapter, 'text': text,
                                'action': 'preserved, not guessed or silently corrected'})
    kept = [r for r in records if r['kept']]
    excluded = [r for r in records if not r['kept']]
    for r in records:
        if r['text'].count(TARGET) != r['target_tokens']:
            raise AssertionError(f'Target segmentation mismatch: {r["id"]}')
    (ROOT / 'sentences.txt').write_text(''.join(' '.join(r['tokens']) + '\n' for r in kept), encoding='utf-8')
    (output / 'sentences.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    (output / 'cleaned_text.txt').write_text('\n\n'.join(bodies), encoding='utf-8')
    write_json(output / 'cleaning_log.json', {'removed': removed, 'chapter_headings_excluded': [h.group().strip() for h in chapters],
        'suspected_corruption_preserved': suspect, 'baseline_target_segmentation': baseline_name,
        'custom_dictionary': {name: 1000000 for name in CHARACTERS}, 'jieba_HMM': True,
        'stopwords': 'Retained in sentences; filtered from collocation output only.'})
    corpus_text = '\n\n'.join(bodies)
    stats = {'source_sha256': hashlib.sha256(raw_bytes).hexdigest(), 'source_bytes': len(raw_bytes),
        'chapters': len(chapters), 'cleaned_characters_with_whitespace': len(corpus_text),
        'cleaned_characters_without_whitespace': len(re.sub(r'\s', '', corpus_text)),
        'cleaned_han_characters': len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]', corpus_text)),
        'sentences_before_short_filter': len(records), 'sentences_kept': len(kept),
        'sentences_excluded_short': len(excluded), 'tokens_kept': sum(len(r['tokens']) for r in kept),
        'target_raw_string_occurrences': raw.count(TARGET),
        'target_tokens_before_short_filter': sum(r['target_tokens'] for r in records),
        'target_tokens_kept': sum(r['target_tokens'] for r in kept),
        'target_tokens_excluded_short': sum(r['target_tokens'] for r in excluded),
        'target_sentences_kept': sum(r['target_tokens'] > 0 for r in kept),
        'maximum_sentence_tokens': max(len(r['tokens']) for r in kept),
        'suspected_corruption_sentences': len(suspect),
        'sentences_sha256': hashlib.sha256((ROOT / 'sentences.txt').read_bytes()).hexdigest()}
    write_json(output / 'corpus_stats.json', stats)
    targets = [r for r in kept if r['target_tokens']]
    sample = [targets[round(i*(len(targets)-1)/9)] for i in range(10)]
    with (output / 'segmentation_check.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f); writer.writerow(['id','chapter','text','tokens','target_count'])
        for r in sample: writer.writerow([r['id'],r['chapter'],r['text'],' / '.join(r['tokens']),r['target_tokens']])
    write_json(output / 'excluded_short_sentences.json', excluded)
    print(json.dumps(stats, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
