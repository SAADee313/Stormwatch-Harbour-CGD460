"""Test whether the original movement tie-break produces a concentrated corridor.
Alternative: when two cells make equal progress, prefer less-visited cells.
"""
import csv, os, statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.simulation import Harbour, WIDTH, HEIGHT, distance
class BalancedHarbour(Harbour):
    def _step_toward(self,w,dest,occupancy):
        x,y=w.pos
        candidates=[p for p in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)] if 0<=p[0]<WIDTH and 0<=p[1]<HEIGHT and occupancy.get(p,0)<3 and distance(p,dest)<distance(w.pos,dest)]
        if not candidates:return
        p=min(candidates,key=lambda p:(self.heatmap[p[1]][p[0]],occupancy.get(p,0),p[1],p[0]))
        occupancy[w.pos]-=1;w.pos=p;occupancy[p]=occupancy.get(p,0)+1
os.makedirs('results',exist_ok=True)
rows=[]
for seed in range(1,11):
    for variant,cls in [('original',Harbour),('balanced',BalancedHarbour)]:
        h=cls('utility',seed);result=h.run()
        visits=sum(sum(r) for r in h.heatmap)
        corridor=sum(h.heatmap[y][0]+h.heatmap[y][1] for y in range(HEIGHT))
        rows.append({'seed':seed,'variant':variant,'cargo_delivered':result['cargo_delivered'],'western_corridor_share':round(corridor/visits,5),'storm_knockouts':result['storm_knockouts']})
with open('results/emergence_10_seeds.csv','w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
for metric in ['cargo_delivered','western_corridor_share']:
    print(metric,[(v,round(statistics.mean(r[metric] for r in rows if r['variant']==v),4)) for v in ['original','balanced']])
fig,ax=plt.subplots(figsize=(7,4))
for variant in ['original','balanced']:
    subset=[r for r in rows if r['variant']==variant]
    ax.plot([r['seed'] for r in subset],[r['western_corridor_share'] for r in subset],marker='o',label=variant)
ax.set(xlabel='Development seed',ylabel='Fraction of worker-ticks in columns 0–1',title='Corridor concentration: original vs balanced tie-break')
ax.legend();fig.tight_layout();fig.savefig('results/emergence_comparison.png',dpi=160)
print('Saved emergence experiment to results/')
