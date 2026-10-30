import csv, statistics, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.simulation import Harbour

os.makedirs('results',exist_ok=True)
policies=['baseline','reflex','model','utility']
metrics=['cargo_delivered','avg_ship_wait','crowding_violations','storm_knockouts']
rows=[]
for seed in range(11,41):
    for agent in policies:
        h=Harbour(agent,seed)
        rows.append({'seed':seed,'agent':agent,**h.run()})
with open('results/evaluation_30_seeds.csv','w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['seed','agent']+metrics);writer.writeheader();writer.writerows(rows)
summary=[]
for agent in policies:
    subset=[r for r in rows if r['agent']==agent]
    out={'agent':agent}
    for metric in metrics:
        values=[r[metric] for r in subset]
        out[metric+'_mean']=round(statistics.mean(values),3)
        out[metric+'_sd']=round(statistics.stdev(values),3)
    summary.append(out)
with open('results/summary.csv','w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
fig,axes=plt.subplots(2,2,figsize=(12,8))
for ax,metric in zip(axes.flat,metrics):
    means=[s[metric+'_mean'] for s in summary]
    sds=[s[metric+'_sd'] for s in summary]
    ax.bar(policies,means,yerr=sds,capsize=4)
    ax.set_title(metric.replace('_',' ').title()+' (mean ± SD)')
    ax.tick_params(axis='x',rotation=20)
fig.tight_layout();fig.savefig('results/comparison_30_seeds.png',dpi=160);plt.close(fig)
print('30-seed evaluation complete. Files saved to results/')
for s in summary:
    print(s['agent'], 'cargo mean',s['cargo_delivered_mean'],'SD',s['cargo_delivered_sd'])
print('Paired cargo differences against reflex (mean ± SD across same seeds):')
for agent in ['baseline','model','utility']:
    differences=[next(r['cargo_delivered'] for r in rows if r['seed']==seed and r['agent']==agent)-next(r['cargo_delivered'] for r in rows if r['seed']==seed and r['agent']=='reflex') for seed in range(11,41)]
    print(agent,round(statistics.mean(differences),2),round(statistics.stdev(differences),2))
