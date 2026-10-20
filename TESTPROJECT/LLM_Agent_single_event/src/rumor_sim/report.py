"""Self-contained, offline single-event report from committed simulation records.

No server, web libraries, or API calls are needed. Only simulated identifiers and
the already-whitelisted prompt fields are exported; donor identities stay local.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from .storage import read_json


def _jsonl(path):
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip(): yield json.loads(line)


def collect_report_data(run_path):
    run_path = Path(run_path).resolve()
    manifest = read_json(run_path / "manifest.json")
    initial = read_json(run_path / "initial.json.gz")
    status = read_json(run_path / "status.json")
    exports = run_path / "exports"
    summary = read_json(exports / "summary.json")
    if status["status"] != "completed":
        from .core import summarize
        journals = sorted((run_path / "rounds").glob("*.json.gz"))
        latest = read_json(journals[-1])["state"] if journals else initial
        summary = {**summarize(latest, manifest["config"]), **summary}
    agents = {aid: {"group": a["group"], "follows": a["follows"],
                   "profile": a.get("observed_profile", {}),
                   "behavior": a.get("empirical_behavior"), "states": [], "decisions": []}
              for aid, a in initial["agents"].items()}
    with (exports / "states.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            agents[row["agent_id"]]["states"].append([int(row["round"]),
                int(row["score"]) if row["score"] else None, row["state"], row["action"]])
    for row in _jsonl(exports / "decisions.jsonl"):
        d, view = row["decision"], row["view"]
        agents[row["agent_id"]]["decisions"].append({"round": row["round"],
            "before": view["previous_belief_score"], "score": d["belief_score"],
            "action": d["action"], "target": d["target_post_id"], "comment": d["comment"],
            "reason": d["reason"], "observations": view.get("social_observation", {}),
            "posts": [{"id": p["post_id"],
                       "relation": p.get("relationship"), "group_relation": p.get("author_group_relation")}
                      for p in view["visible_posts"]]})
    tbu = {}
    with (exports / "tbu_individual.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle): tbu[row["agent_id"]] = row
    exposure_counts = defaultdict(int)
    for row in _jsonl(exports / "exposures.jsonl"):
        exposure_counts[row["channel"]] += 1
    posts = list(_jsonl(exports / "posts.jsonl"))
    source = next(p for p in posts if p["kind"] == "rumor_original")
    official = next((p for p in posts if p["kind"] == "correction_original"), None)
    return {"run_id": manifest["run_id"], "mode": manifest["provider_mode"],
        "status": status["status"], "last_round": status.get("last_committed_round", 0),
        "source_text": source["text"], "correction_text": official["text"] if official else None,
        "config": manifest["config"], "policy": manifest["policy"],
        "summary": summary, "metrics": list(_jsonl(exports / "round_metrics.jsonl")),
        "agents": agents, "tbu": tbu, "exposure_counts": dict(exposure_counts),
        "profile_sampling": initial.get("profile_sampling", {}),
        "posts": {p["post_id"]: {"author": p["author_id"], "parent": p.get("parent_post_id"),
                    "round": p["created_round"], "kind": p["kind"], "text": p["text"],
                    "stance": p.get("public_stance"), "quote": p.get("quoted_context"),
                    "root_text": p.get("root_text"), "source_cue": p.get("source_cue"),
                    "root_evidence": p.get("root_evidence")} for p in posts}}


def build_report(run_path, output=None):
    run_path = Path(run_path).resolve()
    data = collect_report_data(run_path)
    output = Path(output).resolve() if output else run_path / "单事件过程展示.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    serialized = serialized.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    content = TEMPLATE.replace("__PAYLOAD__", serialized)
    output.write_text(content, encoding="utf-8")
    return {"report": str(output), "provider_mode": data["mode"], "status": data["status"],
            "last_committed_round": data["last_round"], "size_bytes": output.stat().st_size}


TEMPLATE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>一个事件：从谣言传播到政府纠正</title>
<style>
:root{--ink:#182b40;--muted:#546779;--line:#d9e1e8;--blue:#1765a5;--red:#c6433e;--green:#268074;--gold:#a77111;--gray:#929fae}
*{box-sizing:border-box}body{margin:0;background:#f3f6f8;color:var(--ink);font:16px/1.65 'Microsoft YaHei',Arial,sans-serif}main{max-width:1200px;margin:auto;padding:28px}h1{font-size:28px;margin:5px 0 16px}h2{font-size:20px;margin:0 0 12px}h3{font-size:17px;margin:0 0 8px}p{margin:7px 0 13px}section{background:white;padding:24px;margin:20px 0;border-radius:12px}.banner{padding:14px 18px;background:#fff1d1;border-left:5px solid var(--gold);font-weight:bold}.meta,.small{font-size:14px;color:var(--muted)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.chart{width:100%;height:auto;min-height:230px}label{display:block}select,input,button{font:inherit}select{max-width:100%;padding:7px}input[type=range]{width:100%;accent-color:var(--blue)}button{padding:7px 18px;border:1px solid var(--line);border-radius:6px;background:white;color:var(--ink)}.controls{display:flex;gap:16px;align-items:center;flex-wrap:wrap}.statline{display:flex;flex-wrap:wrap;gap:20px;padding:12px 0}.statline b{font-size:22px}.legend{display:flex;flex-wrap:wrap;gap:15px;font-size:14px}.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px}.thread{padding:10px 14px;margin:9px 0;background:#f4f7fa;border-left:3px solid var(--line);overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--muted)}.tablewrap{overflow:auto}.split{border-top:1px solid var(--line);margin-top:18px;padding-top:18px}.selected{background:#edf5fc}details{margin-top:12px}summary{cursor:pointer}.empty{color:var(--muted);padding:14px 0}.pill{padding:2px 8px;background:#e8eef3;border-radius:4px;font-size:13px}.caption{color:var(--muted);font-size:14px}svg text{font-family:'Microsoft YaHei',Arial,sans-serif;fill:var(--muted);font-size:13px}.stamp{font-size:15px;color:var(--gold)}@media(max-width:760px){main{padding:12px}.grid{grid-template-columns:1fr}section{padding:16px}h1{font-size:23px}.chart{min-height:180px}}
</style></head><body><main>
<div id="mode" class="banner"></div><h1>一个事件：从谣言传播到政府纠正</h1>
<p id="intro" class="meta"></p>
<section><h2>本次事件与模型设置</h2><p id="source"></p><div class="statline" id="parameters"></div><p class="caption">真实数据提供源帖、账号信息和公开发言特征；关注网络、圈内外分组及干预条件为实验设定。原始评论没有预先写入用户记忆。政府纠正为实验文本，未配入已核实的官方证据。</p>
<details><summary>查看纠正文本与数据使用方式</summary><p id="correction"></p><p id="sampling"></p><p>行为统计来自该事件完整观察期，是回顾性条件设定，不是事件前性格测量或模型微调。真实历史评论/转发仅在本地审阅文件中；运行时看到的同伴新帖来自本轮之前的模拟用户行为。</p></details></section>
<section><h2>1. 整体过程：先接触谣言，再接触纠正</h2><div class="grid"><div><h3>所有用户的信念状态</h3><div class="legend" id="state-legend"></div><svg id="overall" class="chart" role="img" aria-label="四种信念状态随仿真轮次的变化"></svg></div><div><h3>圈内与圈外相信谣言的比例</h3><div class="legend"><span><i class="dot" style="background:var(--red)"></i>圈内</span><span><i class="dot" style="background:var(--blue)"></i>圈外</span></div><svg id="groups" class="chart" role="img" aria-label="圈内外相信比例随仿真轮次的变化"></svg></div></div>
<label for="round">查看第 <b id="round-value"></b> 轮的状态（虚线为政府发布轮次）</label><input id="round" type="range" min="0" step="1" value="0"><div class="controls"><button id="play" type="button">播放过程</button><span id="round-summary" aria-live="polite"></span></div><p class="caption">一轮是模型更新单位，不等于现实中的一天或一小时。曲线按已完成轮次绘制。</p></section>
<section><h2>2. 社交信息如何进入判断</h2><div class="grid"><div><h3>本轮曝光渠道</h3><div id="channels"></div><p class="caption">同一用户一轮可能读取多条信息；这里是曝光次数，不是人数。</p></div><div><h3>截至已完成末轮的干预后观察</h3><div id="outcomes"></div><p class="caption">TBU只针对政府发布前一轮已相信谣言的用户。从政府发布起观察30轮；未拒绝者记为删失。单一过程曲线不能独立识别干预因果效应。</p></div></div></section>
<section><h2>3. 跟踪一个用户：看到了什么、为什么改变、说了什么</h2><div class="controls"><label for="agent">模拟用户 <select id="agent"></select></label><span id="agent-state" aria-live="polite"></span></div><p id="neighbors" class="small"></p><svg id="individual" class="chart" role="img" aria-label="所选用户的信念分数变化"></svg><details><summary>查看该用户的数据画像</summary><div id="profile"></div></details><div id="decision" class="split"></div><details><summary>查看该用户全部已完成决策（点击轮次定位）</summary><div id="history" class="tablewrap"></div></details></section>
<p class="small">完整核查文件：exports/states.csv、decisions.jsonl、exposures.jsonl、posts.jsonl、tbu_individual.csv。报告不发出任何网络请求。</p>
</main><script id="simulation-data" type="application/json">__PAYLOAD__</script><script>
'use strict';
const D=JSON.parse(document.getElementById('simulation-data').textContent),$=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
for(const a of Object.values(D.agents))for(const d of a.decisions)for(const p of d.posts)Object.assign(p,D.posts[p.id]);
const labels={accept:'相信',uncertain:'不确定',reject:'拒绝',unaware:'未接触'},actions={silent:'沉默',comment:'评论',repost:'转发',idle:'本轮无决策'},colors={accept:'#c6433e',uncertain:'#a77111',reject:'#268074',unaware:'#929fae'};
const channelNames={following:'关注用户的信息流',recommendation:'推荐信息',government_direct:'政府直接投送',thread_comment:'评论区 / 自己帖的回复',thread_repost:'同一话题的转发讨论'};
const relationNames={followed_peer:'已关注用户',unfollowed_peer:'未关注用户',official:'政府账号',source:'谣言源账号',same_group:'同圈',cross_group:'跨圈',non_peer:'发布账号'};
const policy=D.policy||{},tg=policy.government_round,N=Object.keys(D.agents).length,end=D.last_round,ids=Object.keys(D.agents).sort();let timer=null;
function node(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function num(v,d=1){return v===null||v===undefined?'尚无可用值':Number(v).toFixed(d)}
function el(tag,attrs={},text){const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
function chart(id,series,maxY,selected,percent=false){const svg=$(id);svg.replaceChildren();svg.setAttribute('viewBox','0 0 560 285');const x=t=>48+t/Math.max(end,1)*490,y=v=>239-v/maxY*200;
for(let k=0;k<=4;k++){let val=maxY*k/4;svg.append(el('line',{x1:48,x2:538,y1:y(val),y2:y(val),stroke:'#e1e7ed'}),el('text',{x:40,y:y(val)+4,'text-anchor':'end'},percent?Math.round(val*100)+'%':Math.round(val)));}
for(let k=0;k<=4;k++){let t=Math.round(end*k/4);svg.append(el('text',{x:x(t),y:262,'text-anchor':'middle'},t));}svg.append(el('text',{x:280,y:283,'text-anchor':'middle'},'仿真轮次'));
if(tg!==undefined&&tg<=end)svg.append(el('line',{x1:x(tg),x2:x(tg),y1:28,y2:239,stroke:'#526b80','stroke-dasharray':'5 4'}),el('text',{x:x(tg)+5,y:20},'政府发布'));
for(const s of series){let points='',has=false;for(const[t,v]of s.points){if(v===null){has=false;continue;}points+=(has?' L ':' M ')+x(t)+' '+y(v);has=true;}svg.append(el('path',{d:points,fill:'none',stroke:s.color,'stroke-width':2.6}));let p=s.points.find(p=>p[0]===selected);if(p&&p[1]!==null)svg.append(el('circle',{cx:x(p[0]),cy:y(p[1]),r:4,fill:s.color}));}svg.append(el('line',{x1:x(selected),x2:x(selected),y1:28,y2:239,stroke:'#bac5cf','stroke-width':1}));}
function countAt(t){let c={accept:0,uncertain:0,reject:0,unaware:0};for(const a of Object.values(D.agents)){let r=t===0?null:a.states.find(s=>s[0]===t);c[r?r[2]:'unaware']++;}return c;}
const totals=Array.from({length:end+1},(_,i)=>countAt(i));
$('mode').textContent=D.mode==='mock'?'离线流程演示 · 未调用真实 LLM · 曲线仅用于检查程序流程，不能作为研究结果':'真实 LLM 单事件实验 · 请结合请求日志和重复实验解释结果';
if(D.status!=='completed')$('mode').textContent+=' · 未完成：'+D.status+'（仅显示已提交轮次）';
$('intro').textContent='一个事件 / 一条连续轨迹 / '+N+'名用户 / 已完成'+end+'轮';$('source').textContent='待核实的源帖：'+D.source_text;
for(const text of [N+'名用户（'+D.config.population.n_inside+'圈内 / '+D.config.population.n_outside+'圈外）','第'+tg+'轮政府发布','定向'+(policy.recipients||[]).length+'名用户','GT = '+policy.credibility])$('parameters').append(node('span',text));
$('correction').textContent=D.correction_text||'尚未到达政府发布轮次。';$('sampling').textContent='本次画像池：'+D.profile_sampling.pool_size+'人；已分配'+D.profile_sampling.assigned+'个模拟身份。'+(D.profile_sampling.replacement?'画像不足时有放回补足，模拟身份彼此独立。':'');
for(const key of Object.keys(labels)){let span=node('span');let dot=node('i',undefined,'dot');dot.style.background=colors[key];span.append(dot,document.createTextNode(labels[key]));$('state-legend').append(span);}
for(const id of ids){let o=node('option',id+' · '+(D.agents[id].group==='inside'?'圈内':'圈外'));o.value=id;$('agent').append(o);}
const ranked=ids.slice().sort((a,b)=>{const score=id=>D.agents[id].decisions.length+30*D.agents[id].decisions.some(d=>d.posts.some(p=>p.author==='GOV'))+10*D.agents[id].decisions.some(d=>d.posts.some(p=>p.group_relation==='cross_group'));return score(b)-score(a);});$('agent').value=ranked[0]||'';$('round').max=end;$('round').value=Math.min(tg||1,end);
function render(){let t=Number($('round').value),id=$('agent').value,a=D.agents[id],c=totals[t];$('round-value').textContent=t;$('round-summary').textContent=Object.entries(c).map(([k,v])=>labels[k]+' '+v+'人').join(' / ');
chart('overall',Object.keys(labels).map(k=>({color:colors[k],points:totals.map((c,t)=>[t,c[k]])})),N,t);
chart('groups',[['inside','#c6433e'],['outside','#1765a5']].map(([g,color])=>({color,points:[[0,0],...D.metrics.map(m=>[m.round,m['accept_rate_'+g]])]})),1,t,true);
const metric=D.metrics.find(m=>m.round===t)||{};$('channels').replaceChildren();for(const[k,label]of Object.entries(channelNames))$('channels').append(node('p',label+'：'+(metric['exposures_'+k]||0)+'次'));
const s=D.summary;$('outcomes').replaceChildren();for(const text of ['干预前相信者：'+(end>=tg?s.risk_n+'人':'尚未到政府发布轮次'),'观察窗内首次拒绝：'+(s.updated_n??0)+'人','已观察到首次拒绝者平均 TBU：'+num(s.TBU_mean)+'轮','30轮内未转变 / 删失：'+(s.censored_n==null?'观察尚未完成':s.censored_n+'人')])$('outcomes').append(node('p',text));
if(!a)return;const row=t===0?null:a.states.find(r=>r[0]===t);$('agent-state').textContent=(row?labels[row[2]]:'未接触')+' · 信念分数 '+(row&&row[1]!==null?row[1]:'未形成');
let peers=a.follows.filter(x=>D.agents[x]);$('neighbors').textContent='该用户关注：'+a.follows.join('、')+'。同圈'+peers.filter(x=>D.agents[x].group===a.group).length+'人，跨圈'+peers.filter(x=>D.agents[x].group!==a.group).length+'人；他人的私下分数不会展示给该用户。';
chart('individual',[{color:'#1765a5',points:[[0,null],...a.states.map(r=>[r[0],r[1]])]}],100,t);
$('profile').replaceChildren();let b=a.behavior||{};for(const text of ['公开账号数据：粉丝 '+(a.profile.followers_count??'未知')+'；关注 '+(a.profile.following_count??'未知')+'；发帖 '+(a.profile.statuses_count??'未知'),'本事件已观察到评论 '+(b.comment_records??'未知')+'条，转发 '+(b.repost_records??'未知')+'条；公开发言中转发占比 '+(b.repost_fraction_among_observed_posts==null?'未知':num(100*b.repost_fraction_among_observed_posts)+'%'),'评论长度中位数：'+(b.median_comment_characters??'未知')+'字符；这是稀疏的观察记录，不是预设其必然评论或转发。'])$('profile').append(node('p',text));
$('decision').replaceChildren();const d=a.decisions.find(d=>d.round===t);if(!d){$('decision').append(node('p',t===0?'第0轮：谣言源发布，用户尚未接触。':'本轮没有可读曝光：不调用LLM，信念保持上一轮状态。','empty'));}else{
$('decision').append(node('h3','本轮实际看到了 '+d.posts.length+'条信息'));
for(const p of d.posts){const box=node('div',undefined,'thread');box.append(node('p',p.author+' · '+(relationNames[p.relation]||'用户')+' · '+(relationNames[p.group_relation]||'')+' · 公开立场 '+({support:'支持原主张',oppose:'反对原主张',uncertain:'不确定'}[p.stance]||'未明确表达'),'small'),node('p',p.text));
const context=node('details');context.append(node('summary','该条信息同时展示的引用和来源线索'));if(p.quote)context.append(node('p','直接引用 '+p.quote.author_id+'：'+p.quote.text));if(p.root_text&&p.root_text!==p.text)context.append(node('p','来源原文：'+p.root_text));if(p.source_cue)context.append(node('p','来源线索：'+p.source_cue));if(p.root_evidence)context.append(node('p','给定证据：'+p.root_evidence));box.append(context);
let post=D.posts[p.id];if(post&&post.parent){let chain=[],seen=new Set(),cursor=p.id;while(cursor&&D.posts[cursor]&&!seen.has(cursor)&&chain.length<8){seen.add(cursor);const q=D.posts[cursor];chain.unshift(q.author+'(第'+q.round+'轮)');cursor=q.parent;}box.append(node('p','传播链：'+(cursor?'… → ':'')+chain.join(' → '),'small'));}$('decision').append(box);}
$('decision').append(node('h3','信念分数：'+(d.before===null?'未形成':d.before)+' → '+d.score),node('p','行动：'+actions[d.action]+(d.comment?'；公开评论：'+d.comment:'')),node('p','简短判断依据：'+d.reason));}
$('history').replaceChildren();const table=node('table'),thead=node('thead'),tr=node('tr');for(const h of ['轮次','之前 → 当前分数','行动','简短依据'])tr.append(node('th',h));thead.append(tr);table.append(thead);const body=node('tbody');for(const h of a.decisions){let tr=node('tr');if(h.round===t)tr.className='selected';let td=node('td'),button=node('button',String(h.round));button.type='button';button.onclick=()=>{$('round').value=h.round;render();};td.append(button);tr.append(td,node('td',(h.before===null?'未形成':h.before)+' → '+h.score),node('td',actions[h.action]),node('td',h.reason));body.append(tr);}table.append(body);$('history').append(table);}
$('round').addEventListener('input',render);$('agent').addEventListener('change',render);$('play').onclick=()=>{if(timer){clearInterval(timer);timer=null;$('play').textContent='播放过程';return;}if(Number($('round').value)>=end)$('round').value=0;timer=setInterval(()=>{if(Number($('round').value)>=end){clearInterval(timer);timer=null;$('play').textContent='播放过程';return;}$('round').value=Number($('round').value)+1;render();},700);$('play').textContent='暂停';};render();
</script></body></html>'''
