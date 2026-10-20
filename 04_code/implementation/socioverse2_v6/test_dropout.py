import json
from types import SimpleNamespace
import pytest
from socioverse.schemas import Action
from model import V4Environment, V4Decision, V4Metrics
from llm_client import AgentRequestFailure, QuotaPause
from run import make_bundles, SOURCE, defaults

def setup(tmp_path):
    _,b,_,_=make_bundles(SOURCE/'01_Agent基础信息表.csv', SOURCE/'02_Prompt固定提示词.md',defaults(),tmp_path)
    e=V4Environment(b);e.reset(1);e.advance_to(1)
    aid=next(a for a,r in e.by_id.items() if r['decision_mode']=='llm' and e.observe(a,1).local_information['posts'])
    return e,aid

def test_dropout_commit_idempotent_and_replay(tmp_path):
    e,aid=setup(tmp_path)
    a=Action(agent_id=aid,step=1,kind='idle',source='rule',payload={'decision_status':'technical_dropout','failure_reason':'AgentRequestFailure'})
    e.apply([a]);e.apply([a])
    assert len(e.offline)==1 and e.beliefs[aid]=='unjudged' and not e.memory[aid]
    e.advance_to(2); assert not e.observe(aid,2).local_information['posts']
    restored,_=setup(tmp_path);restored.apply([a]);restored.advance_to(2)
    assert restored.offline==e.offline
    m=V4Metrics().collect(e,[],2)
    assert m['remaining_agents']==581 and m['remaining_llm']==304 and m['remaining_rule']==277

def test_dropout_only_eligible_failure(tmp_path):
    e,aid=setup(tmp_path)
    d=V4Decision(defaults(),SOURCE/'02_Prompt固定提示词.md',tmp_path,'scripted');d.mode='openai'
    def fail(*args): raise AgentRequestFailure('test')
    d.client=SimpleNamespace(decide=fail)
    actions=d.decide_batch([e.observe(aid,1)],None)
    assert actions[0].payload['decision_status']=='technical_dropout'
    assert not e.offline
    e.apply(actions);assert aid in e.offline
    e2,aid2=setup(tmp_path)
    def quota(*args): raise QuotaPause('test')
    d.client=SimpleNamespace(decide=quota)
    with pytest.raises(QuotaPause): d.decide_batch([e2.observe(aid2,1)],None)
    assert not e2.offline


def test_event_hooks_record_phase_without_headers(tmp_path,monkeypatch):
    from llm_client import LiveClient
    import httpx
    monkeypatch.setenv('RUMOR_LLM_API_KEY','test-secret-not-real')
    c=LiveClient(defaults(),tmp_path)
    c.on_request(httpx.Request('POST','https://example.org',headers={'Authorization':'secret'}))
    c.on_response(httpx.Response(200,headers={'Set-Cookie':'secret'}))
    text=(tmp_path/'request-events.jsonl').read_text()
    assert 'http_dispatch' in text and 'response_headers_received' in text
    assert 'secret' not in text and 'Authorization' not in text
    c.client.close()
