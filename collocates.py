"""Three preregistered settings for Jia Zhen; qhchina performs the statistics."""
from pathlib import Path
import hashlib
import importlib.metadata
import inspect
import json
import platform
import sys
from qhchina.analytics.collocations import find_collocates
from qhchina.helpers.texts import load_stopwords

ROOT = Path(__file__).resolve().parent
RUNS = [('window5', 'window', 5), ('window10', 'window', 10), ('sentence', 'sentence', None)]

def main():
    sentences = [line.split() for line in (ROOT / 'sentences.txt').read_text(encoding='utf-8').splitlines() if line.strip()]
    stopwords = sorted(load_stopwords())
    assert '家珍' not in stopwords
    output = ROOT / 'output'
    (output / 'stopwords_used.txt').write_text('\n'.join(stopwords) + '\n', encoding='utf-8')
    runs = []
    for run_id, method, horizon in RUNS:
        kwargs = dict(target_words='家珍', method=method, alternative='greater',
                      filters={'stopwords': stopwords, 'min_word_length': 2, 'max_p': 0.05},
                      correction=None, sort_by='obs_local', ascending=False,
                      max_sentence_length=None, return_type='dataframe')
        if horizon is not None:
            kwargs['horizon'] = horizon
        df = find_collocates(sentences, **kwargs)
        # Assignment explicitly requests strictly below .05, even if API uses <=.
        df = df.loc[df['p_value'] < 0.05].copy()
        df = df.sort_values(['obs_local','collocate'], ascending=[False,True], kind='stable').reset_index(drop=True)
        assert all(len(w) >= 2 and w not in stopwords for w in df['collocate'])
        assert (df['p_value'] < 0.05).all()
        path = output / f'collocates_jiazhen_{run_id}.csv'
        df.to_csv(path, index=False, encoding='utf-8-sig')
        # Avoid embedding a huge stopword list in every run's metadata.
        kwargs['filters']['stopwords'] = 'output/stopwords_used.txt'
        runs.append({'id':run_id, 'parameters':kwargs, 'rows':len(df),
                     'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'top20':df.head(20).to_dict('records')})
        print('\n' + run_id + ' rows=' + str(len(df)))
        print(df.head(20).to_string(index=False))
    metadata = {'python':platform.python_version(),
        'packages':{p:importlib.metadata.version(p) for p in ['qhchina','jieba','opencc-python-reimplemented','scipy','pandas']},
        'function_signature':str(inspect.signature(find_collocates)),
        'sentences_sha256':hashlib.sha256((ROOT/'sentences.txt').read_bytes()).hexdigest(),
        'stopwords_sha256':hashlib.sha256((output/'stopwords_used.txt').read_bytes()).hexdigest(),
        'runs':runs}
    (output/'run_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
