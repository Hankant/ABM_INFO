import copy
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from model import V4Environment, normalize_answer, dump, digest
from llm_client import LiveClient, QuotaPause, UncertainRequest, prepare_prompt
from run import SOURCE, defaults, make_bundles, prepare_replay


def observation(tmp_path):
    _, eb, _, _ = make_bundles(SOURCE / '01_Agent基础信息表.csv', SOURCE / '02_Prompt固定提示词.md', defaults(), tmp_path)
    env = V4Environment(eb)
    env.reset(1)
    return env.observe('A0002', 1)


def client(tmp_path, monkeypatch):
    monkeypatch.setenv('RUMOR_LLM_API_KEY', 'test-not-real')
    return LiveClient(defaults(), tmp_path)


def response(answer):
    return SimpleNamespace(model='fake', usage=SimpleNamespace(prompt_tokens=100, completion_tokens=20),
        choices=[SimpleNamespace(finish_reason='stop', message=SimpleNamespace(content=json.dumps(answer)))])


def valid():
    return {'belief':'reject', 'comment':{'enabled':False,'text':''},
            'repost':False,'target_content_id':None,'text':'','evidence_ids':['P001']}


def test_false_shorthand_preserves_raw_and_rejects_ambiguous(tmp_path):
    ob=observation(tmp_path); raw=valid(); original=copy.deepcopy(raw)
    result=normalize_answer(raw,ob.local_information['posts'],[],[])
    assert result['repost']['enabled'] is False and result['format_repairs']
    assert raw==original
    raw['repost']=True
    with pytest.raises(ValueError): normalize_answer(raw,ob.local_information['posts'],[],[])


def test_memory_is_actually_in_prompt(tmp_path):
    ob=observation(tmp_path)
    ob.local_physical['memory']=[{'tick':0,'observed_posts':copy.deepcopy(ob.local_information['posts']),
        'belief_before':'unjudged','belief_after':'uncertain','comment':{'enabled':False,'text':''},
        'repost':{'enabled':False,'target_content_id':None,'text':''}}]
    template=(SOURCE/'02_Prompt固定提示词.md').read_text(encoding='utf-8').split('```text')[1].split('```')[0]
    prompt, feed, memory, estimate=prepare_prompt(template,ob)
    assert len(memory)==1 and 'belief_before' in prompt and estimate<=4096


def test_quota_pause_resume_reuses_success_and_budget(tmp_path,monkeypatch):
    c=client(tmp_path,monkeypatch); ob=observation(tmp_path)
    calls=[]
    def create(**kwargs): calls.append(1);return response(valid())
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    c.decide(ob,'{当前观察}')
    second=copy.deepcopy(ob);second.agent_id='A0003'
    class Limit(Exception): status_code=429;code='rate_limit'
    def limit(**kwargs): calls.append(1);raise Limit()
    c.client.chat.completions.create=limit
    with pytest.raises(QuotaPause): c.decide(second,'{当前观察}')
    assert len(calls)==2
    # New client emulates a new process after the window resets.
    resumed=client(tmp_path,monkeypatch)
    resumed.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    answer,_,meta=resumed.decide(ob,'{当前观察}')
    assert meta['cached'] and len(calls)==2
    resumed.decide(second,'{当前观察}')
    assert len(calls)==3 and resumed.budget['requests']==3


def test_invalid_response_never_becomes_success_cache(tmp_path,monkeypatch):
    c=client(tmp_path,monkeypatch); ob=observation(tmp_path)
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **k:response({'belief':'invented'}))))
    with pytest.raises(ValueError):c.decide(ob,'{当前观察}')
    assert not list(c.cache.glob('*.json'))
    assert c.budget['requests']==4


def test_format_retry_identical_input_then_success(tmp_path,monkeypatch):
    c=client(tmp_path,monkeypatch); ob=observation(tmp_path); calls=[]
    def create(**kwargs):
        calls.append(kwargs)
        return response({'belief':'bad'}) if len(calls)<4 else response(valid())
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    answer,_,meta=c.decide(ob,'{当前观察}')
    assert len(calls)==4 and all(k==calls[0] for k in calls)
    assert answer['belief']=='reject' and meta['attempt']==4
    assert len(list((tmp_path/'validation').glob('*.json')))==3


def test_four_failures_remain_exhausted_after_restart(tmp_path,monkeypatch):
    from llm_client import FormatAttemptsExhausted
    c=client(tmp_path,monkeypatch); ob=observation(tmp_path)
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **k:response({'belief':'bad'}))))
    with pytest.raises(FormatAttemptsExhausted): c.decide(ob,'{当前观察}')
    resumed=client(tmp_path,monkeypatch)
    with pytest.raises(FormatAttemptsExhausted): resumed.decide(ob,'{当前观察}')
    assert resumed.budget['requests']==4


def test_saved_bad_json_consumes_first_attempt(tmp_path,monkeypatch):
    c=client(tmp_path,monkeypatch); ob=observation(tmp_path)
    c.cfg['format_max_attempts']=1
    def broken(**kwargs):
        r=response(valid());r.choices[0].message.content='{"belief": "reject", "text": "bad"quote"}'
        return r
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=broken)))
    with pytest.raises(ValueError): c.decide(ob,'{当前观察}')
    resumed=client(tmp_path,monkeypatch)
    resumed.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **k:response(valid()))))
    _,_,meta=resumed.decide(ob,'{当前观察}')
    assert meta['attempt']==2 and resumed.budget['requests']==2


def test_invisible_target_never_format_retried(tmp_path,monkeypatch):
    c=client(tmp_path,monkeypatch);ob=observation(tmp_path)
    raw=valid();raw['repost']={'enabled':True,'target_content_id':'future','text':''}
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **k:response(raw))))
    with pytest.raises(ValueError,match='invisible'):c.decide(ob,'{当前观察}')
    assert c.budget['requests']==1


def test_pending_request_blocks_blind_reissue(tmp_path,monkeypatch):
    c=client(tmp_path,monkeypatch); ob=observation(tmp_path)
    def killed(**kwargs):raise KeyboardInterrupt()
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=killed)))
    with pytest.raises(KeyboardInterrupt):c.decide(ob,'{当前观察}')
    resumed=client(tmp_path,monkeypatch)
    with pytest.raises(UncertainRequest):resumed.decide(ob,'{当前观察}')
    assert resumed.budget['requests']==1


def test_checkpoint_rejects_corruption_and_ignores_partial_tick(tmp_path):
    parent=tmp_path/'parent';dest=tmp_path/'new';dest.mkdir()
    actions=[{'agent_id':f'A{i:04d}','step':1,'action_kind':'idle','action_payload':{}} for i in range(1,583)]
    dump(parent/'checkpoints/tick-001.json',{'actions':actions,'sha256':digest(actions)})
    dump(parent/'checkpoints/tick-003.json',{'actions':[],'sha256':digest([])})
    completed,_=prepare_replay(parent,dest)
    assert completed==1
    dump(parent/'checkpoints/tick-001.json',{'actions':actions[:-1],'sha256':digest(actions)})
    with pytest.raises(ValueError):prepare_replay(parent,dest)

def test_root_evidence_requires_displayed_text(tmp_path):
    from model import allowed_evidence_ids
    ob=observation(tmp_path); feed=copy.deepcopy(ob.local_information['posts'])
    feed[0]['content_id']='repost'; feed[0]['root_content_id']='root'
    assert 'root' in allowed_evidence_ids(feed, [])
    assert 'root' in allowed_evidence_ids([], [{'observed_posts':feed}])
    raw=valid(); raw['evidence_ids']=['root']; normalize_answer(raw,feed,[],[])
    feed[0]['text']=''
    with pytest.raises(ValueError,match='evidence'): normalize_answer(raw,feed,[],[])
    assert 'future' not in allowed_evidence_ids(feed, [])


def test_invisible_evidence_four_attempts(tmp_path,monkeypatch):
    from llm_client import FormatAttemptsExhausted
    c=client(tmp_path,monkeypatch); ob=observation(tmp_path)
    raw=valid(); raw['evidence_ids']=['future']
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **k:response(raw))))
    with pytest.raises(FormatAttemptsExhausted): c.decide(ob,'{当前观察}')
    assert c.budget['requests']==4
    with pytest.raises(FormatAttemptsExhausted): c.decide(ob,'{当前观察}')
    assert c.budget['requests']==4


def test_legacy_response_reused_without_request(tmp_path,monkeypatch):
    from llm_client import prepare_prompt, request_options
    c=client(tmp_path,monkeypatch); ob=observation(tmp_path); template='{当前观察}'
    prompt,*_=prepare_prompt(template,ob,include_evidence=False)
    sig=digest({'prompt':prompt,'model':c.cfg['model'],'base_url':c.cfg['base_url'],
        'request_options':request_options(c.cfg),'agent_id':ob.agent_id,'step':ob.step})
    dump(tmp_path/'request-000001.json',{'prompt_sha256':sig,'status':'response_received','finish_reason':'stop','raw_response':json.dumps(valid())})
    def forbidden(**k): raise AssertionError('must reuse')
    c.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=forbidden)))
    answer,_,meta=c.decide(ob,template)
    assert meta['cached'] and answer['belief']=='reject'
    assert 'allowed_evidence_ids=' in prepare_prompt(template,ob)[0]
