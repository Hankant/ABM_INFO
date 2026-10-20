# V4 本地 SocioVerse2

## 从第20轮继续：4次生成策略（最新）

用户明确要求每次决策最多4次生成（首次+最多3次格式重试），并从第20轮继续。执行：

```powershell
./Continue-From-Tick20.ps1
```

此命令固定使用父运行`government-rumor-v4-openai-20261019-223648-884905`，检查并回放完整的第0—19轮。第20轮起重新进入决策阶段，完全相同输入的合法回答从缓存复用；已核对第20轮22个LLM回答都可复用。A0186第21轮失败计为第1次，最多再生成3次。不是重新花费从头跑20轮。

本次迁移只允许增加`format_max_attempts=4`；检查原材料、模型配置、核心环境model.py和审核后的目标代码哈希，迁移白名单为`retry4-migration.json`。新目录记录`policy_change.effective_from_tick=20`，不能宣称整条轨迹从第1轮就使用了相同重试政策。旧运行不改写。

格式重试使用完全相同的prompt和采样参数，不额外要求改变判断；只保留最终合法决策用于提交，所有失败响应与解析校验记录保留。4次上限跨恢复累计。语义错误（不可见证据、非法转发目标）不自动重抽；重复转发继续局部拒绝。HTTP429/额度、鉴权错误不做格式重试，临时传输错误另按最多一次重试处理，也计入总请求预算。

4次格式失败后保留检查点并停止。不要靠再次Resume绕过次数上限。本次续跑启动后，若额度暂停，使用`Resume-MiniMax-Simulation.ps1`恢复最新子运行，不重复执行固定父运行的Continue脚本。

验证：30项测试通过；离线重建原真实轨迹至tick19，确认tick20的22个成功回答可复用，且A0186在tick21的输入签名与失败请求一致。没有新增真实调用。Key仅存在用户PowerShell窗口，需在该窗口执行上述命令。

## 修复版与断点恢复（v4-recovery-2，以本节为准）

旧真实运行在第21轮出现明确的`repost:false`简写，并且历史记忆被字节预算过度裁剪。旧产物保留，不接续到修复版。第一次使用修复版必须新建实验：

```powershell
./Start-MiniMax-Simulation.ps1
```

额度/限流暂停后，等平台显示额度可用，在同一目录运行：

```powershell
./Resume-MiniMax-Simulation.ps1
# 多个实验时，明确指定要恢复的父运行目录：
./Resume-MiniMax-Simulation.ps1 -RunDirectory '完整运行目录'
```

关闭窗口或重启电脑后也可执行恢复脚本；Key不落盘，必要时重新隐藏输入。默认选择最新且有状态文件的真实运行；完成的运行拒绝重复恢复。每次恢复写入新目录并记录父运行，旧目录不覆盖。不要执行Start脚本来“恢复”，它会从头新建实验。

恢复保障：

- 每个完整tick额外保存582人的行动检查点及SHA256；只恢复连续且校验通过的完整轮次。通过官方action replay重建信念、已读、转发资格、公共内容和个人记忆，不再次调用已完成轮次。
- 未完成轮次的合法响应独立缓存；恢复后重新组装该轮，复用相同输入对应的合法回答，只请求尚未成功的用户。结构错误响应保留审计，但不作为成功缓存。
- 限流HTTP429、官方业务码1002/2056停止并标记`paused_quota`，不连续重试消耗额度，也不假设五小时后一定恢复（还可能有周额度）。需要用户在额度可用后执行Resume。
- 请求账本、检查点和状态采用写临时文件、flush/fsync后原子替换。恢复继承累计请求和预算；额度窗口刷新不会清零实验的12200次请求上限。
- Windows进程锁防止同时启动两个模拟。Ctrl+C会尽力保存已完成部分；强制关闭/断电后使用独立检查点，而非依赖未关闭的DuckDB。
- 如果断电发生在请求发送后、响应落盘前，会保留`pending_usage_unknown`，恢复停止并要求核查，不盲目重发。**无法保证服务端生成与本地落盘之间的网络请求恰好一次**。超时请求同样可能已计费，保留预留；不能声称所有失败请求都没有消耗。
- 代码、材料、参数、模型、服务地址不一致则拒绝恢复，避免混合条件。发生代码修复时需新版本，不能随意绕过哈希检查。

格式兼容只转换无歧义的“repost=false，且顶层target为空、text为空”为关闭转发对象，并保存`format_repairs`与原始回答；不为true简写推断目标，不编造行动。

输入限制现使用`tiktoken cl100k_base`估算，另留15%及64token余量，不再把UTF-8字节当token。**这仍非MiniMax官方分词器，不能宣称严格等于服务端4096tokens**。保留实际usage，记录被裁剪的记忆/帖子/评论数量及传入记忆轮次。仍按最旧记忆→评论→末尾帖子裁剪。代码不保证每次都能容纳5条完整经历。

验证：26项离线测试通过；582人先跑3轮再恢复至5轮的CLI测试通过。未发起新的真实模型请求。终端新增每次请求的tick、用户ID及记忆条数，完成轮次每轮打印。

## 已授权的真实工程首跑

用户在连接检查通过后已要求开始模拟。在保存Key的PowerShell窗口执行 `./Start-MiniMax-Simulation.ps1`：582人、40轮、305名真实LLM角色，使用`minimax.run.config.json`。该文件标为`authorized_engineering_run`，不是正式研究规则已确认。PBd=0、GT=.6、RF=.6、inside、tick20投放，沿用本文工程合同。最大12200请求，失败停止，无固定回答回退。

启动器使用`--token-plan-run`，仅接受MiniMax订阅Key和指定国内接口，表示授权使用套餐额度/积分，不声称已配置人民币费用上限，不切换按量Key。套餐限流或额度用完可能提前停止。Key留在当前PowerShell，助手的独立进程不能读取；启动脚本不把Key写入文件。

## MiniMax 接入（2026-10-19）

Token Plan订阅Key也使用相同的OpenAI兼容地址，不因订阅类型自动切换端点或普通付费Key。如果返回401，在已输入Key的同一窗口运行 `./.venv/Scripts/python.exe check_minimax_key.py`，只查询官方套餐状态接口，不生成文本、不输出Key。成功只证明套餐查询鉴权通过，不证明模型调用权限。依据：[官方订阅工具配置](https://platform.minimaxi.com/docs/token-plan/other-tools)、[官方订阅FAQ](https://platform.minimaxi.com/docs/token-plan/faq)。国内/海外Key需要匹配对应服务区域。

新增配置 `minimax.config.json`：`https://api.minimax.cn/v1`、`MiniMax-M3`。来源为[MiniMax官方兼容接口文档](https://platform.minimaxi.com/docs/api-reference/text-openai-api)，本次实际读取其`.md`版本。原V4材料和已有运行不变。

在本目录PowerShell中执行 `./Configure-MiniMax.ps1`，按隐藏提示输入你在MiniMax平台创建的API Key。Key仅保存在当前进程的`RUMOR_LLM_API_KEY`，不写入配置。没有调用或收费。

准备好后执行 `./.venv/Scripts/python.exe check_minimax.py`，只进行**一次可能计费的连接检查**，使用合成文本，不发送账户资料；检查返回合法JSON。也可直接使用 `./Configure-MiniMax.ps1 -TestConnection` 完成输入和检查。不要在聊天中提交Key。

该配置选择支持关闭thinking的M3，继续使用512输出token限制，开启reasoning_split。不发送文档中未明确保证的response_format；通过提示词要求JSON并在本地严格解析。保持temperature=.7、top_p=.8，不自动替换其他模型。更换到强制thinking的型号必须重新检查输出预算。

正式模拟使用 `run.py --live --config minimax.config.json --cost-limit-configured --max-requests 20`，但原行为合同仍标待确认，该命令在合同确认前会停止。连接检查不需要确认研究规则。费用上限标志只能在服务端实际设置额度后使用。连接检查通过也不等于完整V4决策已验证。

本次完成配置与离线测试，尚未持有用户Key，未执行真实连接检查。

本项目使用官方 SocioVerse2 引擎，独立实现V4环境、人群、混合决策和指标。权威材料是 `../../../TESTPROJECT/V4_四份交付文件/`；原始四文件不改写。本研究独立于总项目Paper1，不沿用旧二维移动模型。

## 启动

在本目录打开PowerShell：

```powershell
# 完整离线工程测试：582人、40轮，无API调用
./Start-Offline.ps1

# 打开本地官方查看面板，浏览器访问 http://127.0.0.1:8787
./Start-Dashboard.ps1

# 测试模型和核查最近一次离线运行的实际记录
./.venv/Scripts/python.exe -m pytest test_model.py -q
./.venv/Scripts/python.exe verify_run.py
```

若PowerShell本机策略阻止脚本，直接执行 `.venv/Scripts/python.exe run.py` 即可。面板只绑定本机127.0.0.1。停止面板：在启动终端按Ctrl+C；本次由助手后台启动的进程PID保存在日志目录的dashboard.pid。

官方本地版是研究查看面板，没有托管版聊天构建、余额或网页运行后台。运行与修改由本目录脚本完成，页面展示产物。无需访问官方托管平台，但真实LLM仍需可用的模型网关。

## 文件与位置

| 文件／目录 | 用途 |
|---|---|
| `model.py` | 四个已注册的原生provider：人口、环境、决策、指标 |
| `llm_client.py` | 可选真实调用、输入裁剪、预算、错误日志和成功响应缓存 |
| `run.py` | 冻结输入，组装官方引擎，独立运行目录，导出面板数据 |
| `test_model.py`、`verify_run.py` | 规则测试和实际轨迹不变量核查 |
| `Setup.ps1`、`requirements-lock.txt` | Python3.12隔离环境与依赖固定版本 |
| `../../../06_experiments/configs/socioverse2_v4/` | 每次运行的原始四文件副本、边表、目标名单、初态、合同及哈希 |
| `../../../06_experiments/results/socioverse2_v4/` | 每次运行的study、环境/人群配置、DuckDB、CSV、报告、状态 |
| `../../../06_experiments/logs/socioverse2_v4/` | 本地请求审计、预算账本、成功响应缓存；可能包含账户资料 |

每次运行创建新目录，不覆盖旧结果。`results/socioverse2_v4/latest.json`指向最近一次运行。`trajectory/panel.csv`包含tick0和之后每轮的每人状态，JSON列保留原始回答、执行回答、实际观察和概率抽样。`trajectory/study.duckdb`是官方引擎写出的数据库，`metrics_history.json`为逐轮指标。`status.json`明确区分离线完成、真实完成和中断。

## 按V4实现的内容

- 固定582个身份：305名LLM角色、277名规则角色，圈内82人、圈外500人。规则组不消耗模型调用。
- 8条同组＋2条跨组关注边，圈内额外关注SOURCE，共5902边；独立PCG64网络种子20261018。
- 全员每轮检查信息流，上限5帖，每帖最多2条评论；按时间倒序，同时间ID升序。每条投递只展示一次，同根的不同投递可以再次看到。
- P001在tick0发布，tick1开始展示。G001在tick20向40名圈内用户保证首位展示；投放种子20261019。不是全员广播，不增关注边。
- 同一轮统一观察后提交；新转发/评论下一轮可见。每人每个根内容全程最多成功转发一次。
- 固定persona、当前信念、最近5次成功个人经历和当前观察分开。初态unjudged，无预填真实评论、虚构习惯或心理属性。
- 重复转发只关闭repost，保留合法belief/comment；分别记录原始回答与执行结果。没有新内容就idle。
- 请求或解析失败停止本轮，不更新用户信念，不补造uncertain，不以固定回答代替。已完成轮次保留。

## 工程补充与待确认边界

以下**不是原稿已确认规则**。V4文件仍留空的行为合同，先作为离线工程条件实现，并在每次运行中标记`engineering_only_pending_confirmation`：

| 项目 | 当前工程条件 |
|---|---|
| 概率 | PBd=0、GT=.6、RF=.6，使用表中四舍五入值；PBd另支持.2/.4 |
| 多次接触 | 同轮每种处理路径只抽一次；有纠正时只执行纠正路径，不先执行谣言路径 |
| 谣言接触 | unjudged/uncertain执行PB；相信者满足资格时执行RC；规则reject不重新相信 |
| 纠正接触 | GT成功变reject，再按RF决定转发；失败保持原态；直接与转发纠正使用同一GT |
| 行为随机数 | PCG64，按行为seed20261020、tick、agent序号构造独立流；请求失败/顺序不改变规则抽样 |
| TBU候选 | 第19轮末相信者为固定队列；第20轮起首次reject的tick减20，对完成者取均值；无完成者null，允许等待0；uncertain不算完成 |
| 评论目标 | 原提示词未提供comment目标字段，明确将评论挂在本轮第一帖；已向提示词追加说明 |
| 实际请求并发 | 首版顺序调用，并发1，不超过V4上限5；不批量混合多用户回答 |
| 输入计数 | 网关未提供模型tokenizer；以UTF-8字节数+256作保守工程预算代理，**不是实际token数**。实际usage分开记录；正式研究需确认该服务分词计数 |

正式运行前需要确认上述合同，尤其是同轮纠正优先、规则用户不能重新相信、TBU口径。不能只改JSON中的规则文字：未实现的规则改动会被启动器拒绝。固定模板正文沿用V4，只追加重复转发资格和评论目标说明，不增加未经授权的心理构念。

离线LLM角色固定为“看到原帖相信并尝试转发，看到纠正不相信并尝试转发”，并生成测试评论。这是专门让传播、重复转发和政府排程充分被测试的程序，不是行为模型。所有相关运行标记dry_run，不可用于论证辟谣效果。

## 真实LLM检查与恢复

真实调用已实现，但默认不启动。没有静默换模型、换网关或规则回退。默认网关与模型名沿用V4，未验证服务可用性。迁移到本地不能保证消除网关570。

1. 确认工程合同后，将某次冻结的`behavior_contract.json`复制为新的配置，把`contract_status`改为`confirmed`；需要改变规则则先改实现和测试。
2. 在服务侧设置你接受的费用上限。令牌上限不等于货币预算。通过环境变量提供`RUMOR_LLM_API_KEY`，不要放入代码、命令历史或CSV。
3. 首次只检查最多20次真实请求（包含重试）：

```powershell
./.venv/Scripts/python.exe run.py --live --config ./confirmed_contract.json --cost-limit-configured --max-requests 20
```

20次预算耗尽通常会中断未完成轮次，这是预期的接口检查；不能说40轮已完成。正式首跑另行启动，最大请求可设12200。真实完成也只代表该假设情景的模型结果。

请求前持久化预留；SDK自动重试关闭，脚本只对明确临时错误最多重试一次。未知570不自动重试。失败用量保留为unknown；预留单位、实际input/output usage分别记录。日志不写key、完整响应头或原始异常正文。网关详细根因仍可能需要服务商提供请求追踪。

相同输入、模型、代码和合同可在**新运行目录**恢复：

```powershell
./.venv/Scripts/python.exe run.py --resume ../../../06_experiments/results/socioverse2_v4/某个离线运行目录
```

真实恢复还需同样的`--live --config --cost-limit-configured --max-requests`参数。恢复复用官方action replay，重建完整历史和记忆；继承预算账本，未完成轮次的成功回答从缓存读取。不保证跨不同网关/模型重跑一致，也不允许通过恢复清零预算。快照可能含失败轮的外生事件，因此恢复以数据库已完成行动为准。

## 数据与来源

账户资料与模拟输出均留在本地研究目录，已加入Git忽略；公开代码不含305名账户的资料行。假名ID不保证资料无法重识别，不将本地审计文件作为公开附件。使用材料不代表新增数据采集授权或伦理审查已完成。

官方源码：[sii-research/SocioVerse2](https://github.com/sii-research/SocioVerse2)，固定提交`9c3ac774816511c121184ca11f539dc398ba1544`。保留官方LICENSE/NOTICE，核心源码未修改。新增代码位于本目录；首次安装执行`Setup.ps1`，使用官方提交和依赖锁。G001是研究者实验性脚本，不能写成真实政府通告。


## Evidence validation repair (2026-10-19)

Continue-From-Tick22.ps1 is a one-time migration from government-rumor-v4-openai-20261019-231951-698018. It replays completed ticks through 21 into a new run and continues tick22. Inputs, network, model and budget remain unchanged. Displayed original text permits its root ID as evidence; unseen IDs remain invalid. New prompts list allowed_evidence_ids; existing requests retain exact old prompts and attempt counts to reuse responses. Evidence failures share the four-generation cap. Invisible repost targets still stop. The migration is recorded in provenance and is an engineering continuation, not an unchanged-code replication. After further pauses use Resume-MiniMax-Simulation.ps1. Key must be present in the launching PowerShell session.
