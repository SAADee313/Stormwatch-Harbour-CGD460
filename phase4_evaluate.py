"""Run five paired seeds, preserving actual measurements."""
import csv, json, statistics, time
from pathlib import Path
from src.simulation import Harbour
from src.harbour_master import run_llm

Path('results').mkdir(exist_ok=True)
rows=[]
for seed in range(11,16):
    for policy in ('utility','llm'):
        print(f'Running {policy} seed {seed}...',flush=True)
        start=time.perf_counter()
        result=run_llm(seed) if policy=='llm' else Harbour(policy,seed).run()
        row={'seed':seed,'agent':policy,**result,'wall_seconds':round(time.perf_counter()-start,2)}
        rows.append(row)
        with open('results/phase4_llm_comparison.jsonl','a',encoding='utf8') as f: f.write(json.dumps(row)+'\n')
        print(json.dumps(row),flush=True)
fields=list(dict.fromkeys(k for row in rows for k in row))
with open('results/phase4_llm_comparison.csv','w',newline='',encoding='utf8') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
for policy in ('utility','llm'):
    data=[r for r in rows if r['agent']==policy]
    print(policy,{k:round(statistics.mean(r[k] for r in data),3) for k in ('cargo_delivered','avg_ship_wait','crowding_violations','storm_knockouts')})
print('Saved results/phase4_llm_comparison.csv')
