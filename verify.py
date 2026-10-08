"""Independent count/Fisher checks against every saved collocate."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import sys
import pandas as pd
from scipy.stats import fisher_exact

ROOT=Path(__file__).resolve().parent
def count_table(sentences, mode, horizon=None):
    glob, local = Counter(), Counter()
    total=context=0
    for words in sentences:
        if mode=='sentence':
            unique=set(words); total+=1; glob.update(unique)
            if '家珍' in unique:
                context+=1; local.update(unique-{'家珍'})
        else:
            positions=[i for i,w in enumerate(words) if w=='家珍']
            glob.update(words)
            for i,w in enumerate(words):
                if w=='家珍': continue
                total+=1
                # Union of window positions: overlaps counted once per target type.
                if any(abs(i-j)<=horizon for j in positions):
                    context+=1;local[w]+=1
    return glob,local,total,context

def main():
    out=ROOT/'output'
    ss=[x.split() for x in (ROOT/'sentences.txt').read_text(encoding='utf-8').splitlines()]
    stops=set((out/'stopwords_used.txt').read_text(encoding='utf-8').splitlines())
    summary=[]; example=[]
    for run,mode,h in [('window5','window',5),('window10','window',10),('sentence','sentence',None)]:
        df=pd.read_csv(out/f'collocates_jiazhen_{run}.csv')
        glob,local,total,context=count_table(ss,mode,h)
        max_p_difference=0.0
        for row in df.to_dict('records'):
            w=row['collocate'];a=local[w];b=context-a;c=glob[w]-a;d=total-a-b-c
            assert min(a,b,c,d)>=0
            expected=context*glob[w]/total
            p=fisher_exact([[a,b],[c,d]],alternative='greater').pvalue
            assert row['obs_local']==a and row['obs_global']==glob[w],(run,w,'count')
            assert math.isclose(row['exp_local'],expected,rel_tol=1e-10),(run,w,'E')
            # qhchina's compiled Fisher routine and SciPy differ at ~1e-10 absolute.
            max_p_difference=max(max_p_difference,abs(row['p_value']-float(p)))
            assert math.isclose(row['p_value'],p,rel_tol=1e-6,abs_tol=1e-9),(run,w,row['p_value'],p)
            assert len(w)>=2 and w not in stops and p<.05
        assert df['obs_local'].is_monotonic_decreasing
        for w in ['凤霞','有庆','床上','衣服','商量','春生','眼泪']:
            a=local[w];b=context-a;c=glob[w]-a;d=total-a-b-c
            p=fisher_exact([[a,b],[c,d]],alternative='greater').pvalue
            example.append({'run':run,'word':w,'a':a,'b':b,'c':c,'d':d,'N':total,'R1':context,
                'expected':context*glob[w]/total,'p_value':float(p),'passes_p':bool(p<.05)})
        summary.append({'run':run,'verified_rows':len(df),'N':total,'R1':context,
                        'max_absolute_p_difference_vs_scipy':max_p_difference,'absolute_p_tolerance':1e-9})
    (out/'verification.json').write_text(json.dumps({'status':'passed','independent_method':'Python position union + scipy.stats.fisher_exact',
        'checks':summary,'examples':example},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
