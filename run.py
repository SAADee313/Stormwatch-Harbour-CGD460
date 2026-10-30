import argparse,json
from src.simulation import Harbour
from src.harbour_master import run_llm

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--agent',choices=['baseline','reflex','model','utility','llm'],required=True)
    p.add_argument('--seed',type=int,required=True)
    p.add_argument('--model',default='qwen2.5:3b')
    p.add_argument('--temperature',type=float,default=0)
    p.add_argument('--replay',action='store_true')
    p.add_argument('--approve-dangerous',action='store_true',help='For explicit supervised testing only')
    a=p.parse_args()
    if a.agent=='llm':
        result=run_llm(a.seed,a.model,a.temperature,a.replay,a.approve_dangerous)
    else: result=Harbour(a.agent,a.seed).run()
    print(json.dumps(result,separators=(',',':')))
if __name__=='__main__': main()
