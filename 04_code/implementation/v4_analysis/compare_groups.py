import csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[3]
name='government-rumor-v4-openai-20261020-004902-188523'
run=ROOT/'06_experiments/results/socioverse2_v4'/name
cfg=ROOT/'06_experiments/configs/socioverse2_v4'/name
rows=list(csv.DictReader((cfg/'01_Agent基础信息表.csv').open(encoding='utf-8-sig')))
mode={r['agent_id']:r['decision_mode'] for r in rows};group={r['agent_id']:r['group'] for r in rows}
state={a:'unjudged' for a in mode};reposted=defaultdict(set);seen=defaultdict(set)
first=defaultdict(Counter);exposed=defaultdict(set);shared=defaultdict(set);events=defaultdict(Counter);snap={};cohort={};hashes={}
for t in range(1,23):
 p=run/'checkpoints'/f'tick-{t:03d}.json'; d=json.loads(p.read_text(encoding='utf-8'));hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
 assert hashlib.sha256(json.dumps(d['actions'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()==d['sha256']
 assert len(d['actions'])==582 and len({a['agent_id'] for a in d['actions']})==582
 for action in d['actions']:
  if action['action_kind']=='idle':continue
  aid=action['agent_id'];m=mode[aid];x=action['action_payload'];ans=x['answer'];posts=x['observed_posts']; roots={p['root_content_id'] for p in posts};before=state[aid];after=ans['belief']
  phase='correction' if 'G001' in roots else 'rumor';key=(m,phase)
  events[key]['decisions']+=1; events[key]['comments']+=bool(ans['comment']['enabled']);events[key]['before_'+before]+=1
  events[key]['transition_'+before+'_'+after]+=1
  if phase not in seen[aid]:
   for g in ('all',group[aid]):
    f=first[(m,phase,g)];f['n']+=1;f[after]+=1;f['before_'+before]+=1;f['repost']+=bool(ans['repost']['enabled'])
   seen[aid].add(phase)
  for root in roots:
   exposed[(m,root)].add(aid)
   if root not in reposted[aid]: events[(m,root)]['eligible_decisions']+=1
  if ans['repost']['enabled']:
   target=next(p for p in posts if p['content_id']==ans['repost']['target_content_id']);root=target['root_content_id']
   assert root not in reposted[aid]
   reposted[aid].add(root);shared[(m,root)].add(aid)
   events[(m,root)]['share_belief_'+after]+=1
  state[aid]=after
 if t in (19,20,21,22):snap[t]={m:dict(Counter(state[a] for a in mode if mode[a]==m)) for m in ('llm','rule')}
 if t==19:cohort={a for a,s in state.items() if s=='believe'}
out={'run':name,'through_tick':22,'snapshot':snap,'first_exposure':{'|'.join(k):dict(v) for k,v in first.items()},'events':{'|'.join(k):dict(v) for k,v in events.items()},'exposed':{'|'.join(k):len(v) for k,v in exposed.items()},'shared':{'|'.join(k):len(v) for k,v in shared.items()},'cohort19':{m:{'n':sum(mode[a]==m for a in cohort),'reject_at22':sum(mode[a]==m and state[a]=='reject' for a in cohort)} for m in ('llm','rule')},'group_composition':{m:dict(Counter(group[a] for a in mode if mode[a]==m)) for m in ('llm','rule')},'checkpoint_sha256':hashes}
dest=ROOT/'06_experiments/results/v4_analysis'/f'{name}-through22';dest.mkdir(parents=True,exist_ok=True)
(dest/'comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='checkpoint_sha256'},ensure_ascii=False,indent=2))
