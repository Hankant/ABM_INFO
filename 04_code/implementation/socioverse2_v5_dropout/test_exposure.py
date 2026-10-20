import copy
from model import exposure_summary, V4Decision
from test_model import bundles, env
from llm_client import render_prompt


def test_counts_distinguish_authors_ticks_and_roots():
    history={'p1':{'root_content_id':'r','author_id':'a','tick':1}}
    feed=[{'content_id':'p2','root_content_id':'r','author_id':'a'},
          {'content_id':'p3','root_content_id':'r','author_id':'b'},
          {'content_id':'c','root_content_id':'correction','author_id':'gov'}]
    summary=exposure_summary(history,feed,3)
    assert summary['r']==dict(observed_post_count=3,distinct_author_count=2,exposure_tick_count=2,first_seen_tick=1,last_seen_tick=3)
    assert summary['correction']['observed_post_count']==1
    assert len(history)==1
    assert exposure_summary(history,feed+feed,3)==summary


def test_history_survives_memory_and_idempotent_commit(env,bundles):
    dec=V4Decision(**bundles[3].decision_args);aid='A0002'
    author=next(a for a in env.following[aid] if a!='SOURCE')
    for t in range(1,8):
        if t>1:
            env.posts[f'extra{t}']={**env.posts['P001'],'content_id':f'extra{t}','author_id':author,'published_tick':t,'available_tick':t}
        env.advance_to(t)
        ob=env.observe(aid,t)
        actions=dec.decide_batch([ob],{})
        before=copy.deepcopy(env.exposure_history[aid])
        assert env.exposure_history[aid]==before
        env.apply(actions);stored=copy.deepcopy(env.exposure_history[aid]);env.apply(actions)
        assert env.exposure_history[aid]==stored
    assert len(env.memory[aid])==5
    assert env.agent_state(aid)['exposure_summary']['P001']['observed_post_count']==7
    assert env.snapshot()['exposure_history'][aid]==stored


def test_trimmed_feed_not_in_prompt_count(env,bundles):
    ob=env.observe('A0002',1);feed=ob.local_information['posts']
    prompt=render_prompt('{当前观察}',ob,[],[])
    assert 'observed_post_count' not in prompt
    prompt=render_prompt('{当前观察}',ob,feed,[])
    assert 'observed_post_count' in prompt


def test_rule_reconsideration_and_corrected_boundary(env,bundles):
    dec=V4Decision(**bundles[3].decision_args)
    ob=env.observe('A0002',1);ob.local_physical['current_belief']='reject'
    _,draws=dec._rule(ob)
    assert any(d['name']=='PB' for d in draws)
    ob.local_physical['rule_corrected']=True
    ans,draws=dec._rule(ob)
    assert ans['belief']=='reject' and not draws
    ob.local_physical['rule_corrected']=False;dec.cfg['rule_reconsider_rumor']=False
    _,draws=dec._rule(ob)
    assert not draws
