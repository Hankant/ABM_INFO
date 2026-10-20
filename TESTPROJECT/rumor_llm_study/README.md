# 谣言茧房 LLM Agent 仿真程序

这是一套可执行的 Python 程序，包含真实Excel导入、用户画像赋值、关注网络、信息流、LLM决策、同步状态更新、政府干预、TBU计算、完整日志和断点恢复。核心仿真只用Python标准库；重新读取原始Excel时才需要额外依赖。

当前研究配置为82名圈内用户和500名圈外用户。`T_G = 10, 20, 30, 40, 50`，所有轨迹运行至第80轮，以便最晚干预仍有最长30轮的随访。窗口包含两个端点；同轮更新为0，第T_G+30轮更新为30。

逐项参数和每轮交互顺序见 [MODEL_GUIDE.md](MODEL_GUIDE.md)，已执行的检查见 [verification/TEST_REPORT.md](verification/TEST_REPORT.md)。要修改参数，请编辑 `config/research.json`，并在命令中显式加入 `--config config/research.json`；没有该选项时程序读取 `config.py` 内置默认值。例如：`python run.py run --config config/research.json --event data/imported/event_052/event.json --provider mock --tg 50 --output outputs/edited_config`。

## 先运行这三条命令

进入解压后的项目目录，使用Python 3.11或更高版本。Windows也可双击 `开始离线验证.cmd`。

```powershell
python test_all.py
python run.py check --event data/imported/event_052/event.json
python run.py run --event data/imported/event_052/event.json --provider mock --tg 50 --output outputs/my_offline_check
```

第三条命令使用真实事件及画像，运行582人、80轮的一条无干预轨迹和一条T_G=50政策轨迹；决策器为明确标记的Mock，仅验证程序，**不产生可用于论文的LLM研究结果**。输出中的`provider_mode`记录实际使用的决策器。

2026-10-12已切换到ZetaTechs并完成一次成功的真实接口测试：`https://api.zetatechs.com/v1/chat/completions` 返回合法六字段JSON，响应模型为 `deepseek-v4-flash`。该平台模型列表使用这个名称；旧平台的 `deepseek-ai/DeepSeek-V4-Flash` 在新平台返回无可用通道，因此改用列表中的对应名称。接口已连通，但尚未执行完整真实LLM研究轨迹。

## 已导入的数据

`data/imported`包含原目录的125个事件：75个有源帖正文，50个正文为空。原Excel没有改写。全量导入有效评论21,832条、转发21,901条，去重并移除源账号自身互动后，事件内画像池合计38,753份；跨事件可能是相同账号，不能解释为38,753个独立真人。

- `data/imported/ready_events.json`：75个有正文事件的批量列表。
- `data/imported/missing_source_text.csv`：50个待补正文事件。
- `data/imported/event_index.csv`：125个事件ID与原工作簿文件名的对应表。
- `data/imported/event_052/event.json`：一个可检查的事件输入示例。
- `data/imported/event_052/profiles.jsonl`：该事件305份去重公开画像。
- `data/imported/import_report.json`：逐事件记录数与导入状态。

表2与表3先按真实用户ID去重，再生成不可直接识别的donor_id。赋值使用粉丝数、关注数、累计发博数三项实测字段；原评论、转发文字、情感类别和后验立场不放入初始记忆、信念或信任。昵称、原用户ID与主页不进入模型输入。原始溯源资料只保存在本机导入目录的`_private`，不收入下载代码包。

画像先无放回抽取，人数不足时再有放回补至582人。重复使用的只是画像模板，每个Agent的信念、记忆和互动状态都是独立对象。不同d_seed和政策分支使用相同seed时保持相同画像赋值。圈内外身份、关注边、活动概率、分享倾向、原有政府信任与初始倾向仍属于实验设定；不能把它们写成真实关注关系或问卷测量值。

75个“有正文”不等于已经逐条核实其真假和完整性。`original_claim`目前保存源帖原文，部分原文有省略或包含多个陈述，事件文件标记为待内容检查。正式研究前可在这些JSON中进一步明确唯一待判断主张；程序不会根据文件名补造文本。

## 政府纠正的实际实现

按本次确认，没有外部官方纠正文件，使用统一实验刺激模板：

> 针对网上流传的“原始主张”，本账号澄清：这一说法不属实。请勿继续传播未经核实的信息。

每个事件中保存`correction_mode=scripted_no_evidence`、`correction_origin=experimental_script`、`evidence_text=""`、`evidence_status=not_provided`。这不是采集到的官方辟谣，也不代表程序替现实事件判定真假。各政策分支正文完全相同，只改变时点、40名投送对象以及2/10、6/10、10/10的虚拟来源线索。不得将空证据伪装成官方调查或事实证明。

## 连接你的API

已配置端点`https://api.zetatechs.com/v1`和模型`deepseek-v4-flash`。`/keys`是密钥管理页面，不是模型请求地址。密钥不在任何交付文件中。双击 `开始API测试.cmd`，在隐藏输入中提供新Key；每次主动测试都最多发送一次新请求，不使用缓存冒充接口连通，单次不做修复重试。所有后续真实调用仍使用严格JSON校验，最多初始请求加2次修复。

命令行也可以这样设置当前会话的Key，输入内容不会显示：

```powershell
$secureKey = Read-Host "API Key" -AsSecureString
$keyPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try { $env:RUMOR_LLM_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPtr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPtr) }
python tools/probe_api.py
```

以下命令启动真实模型轨迹。20是这个输出目录的**累计HTTP请求上限**，含失败及重试，通常不足以完成完整研究轨迹，达到上限会明确停止并保存完整轮末快照。需要更大额度时，由你自行修改上限；重启不会清空已消耗的预算。

```powershell
python run.py run --event data/imported/event_052/event.json --provider http --tg 50 --max-api-requests 20 --output outputs/real_event052
```

默认请求发送temperature=0.7、top_p=0.8、max_tokens=384、JSON输出和`thinking={"type":"disabled"}`，不发送Qwen专用参数。本次成功探测使用了这些字段；这证明该请求获接受并返回合规结果，不能证明服务端内部执行了每个参数。程序不会静默删除参数、更换模型或改用Mock。实际请求参数、返回model、usage、原始输出和重试原因会留痕；模型服务的内部权重版本无法由客户端独立核实。

401/403立即停止；重定向被拒绝，密钥不会随跳转发送给其他站点。预算记录在`outputs/对应目录/provider/budget.json`。接口探测的独立预算域是`outputs/api_verification/provider`；不同输出目录分别计数，跨目录测试的总预算需同时核对。

## 批量运行

先查看数量和保守调用上界，不会调用API：

```powershell
python run.py estimate --events 1
python run.py estimate --events 75
```

每事件3种d_seed × 5种T_G × 3种定向 × 3种GT × 3种子，共405条政策轨迹，另有9条无纠正父轨迹，合计414条。75个事件合计31,050条逻辑轨迹。并未在交付时运行完整真实实验；可先用单事件评估实际token量和耗时。

```powershell
# 一个事件的完整网格；默认仍是离线Mock
python run.py grid --event data/imported/event_052/event.json --provider mock --output outputs/offline_grid

# 全部75事件，只有显式指定http才调用真实模型
python run.py grid --event-list data/imported/ready_events.json --provider http --max-api-requests 20 --output outputs/batch_real

# 单独无纠正传播
python run.py parent --event data/imported/event_052/event.json --provider mock --output outputs/no_correction
```

真实批处理使用同一个provider预算域，预算不会在每个事件或分支开始时重置。输入缺失事件会在第一次模型调用前报错，不会跳过后假装完整成功。

## 如何恢复和核查

正常中断或达到请求上限后，重新执行相同命令、使用相同输出目录即可恢复。每个成功轮次用一个原子写入的压缩文件保存完整状态及日志；失败的一轮不提交。该轮已成功的模型请求按相同run、主体、轮次、输入、提示版本和参数缓存，恢复时可重用；不同政策后缀不会互相冒充新的随机调用。

前置历史由同一无纠正父轨迹复用。T_G=50分支复制第49轮末状态；所有分支PBd继承第5轮值。CSV导出自动拼接父轨迹前缀和分支后缀，582人×80轮应有46,560条状态行，不重复计算前缀。修改代码、模型参数、事件文本或研究配置后，应使用新的输出目录；程序拒绝混用不一致的实验版本。只有预算和超时可以不改变行为版本而调整。

每条轨迹的`exports`目录提供：

| 文件 | 内容 |
| --- | --- |
| summary.json | PBd、风险集、更新比例、TBU、80轮终点及累计指标 |
| tbu_individual.csv | 风险集每人的event、duration与首次拒绝轮 |
| states.csv | 全部主体逐轮信念和动作 |
| exposures.jsonl | 实际阅读、来源渠道、重复计数 |
| posts.jsonl | 所有创建的源帖、政府帖、评论和转发 |
| decisions.jsonl | 六字段决策及实际provider审计记录 |
| round_metrics.jsonl | 每轮接受比例、动作和曝光统计 |

`rounds/*.json.gz`是权威恢复记录，`exports`是可重新生成的派生文件。无风险集时TBU和更新率都为null；有风险集但无人更新时TBU为null、更新率为0。删失者duration=30、event=0，不能当成观测到TBU=30。最新真实接口成功记录见`verification/api_probe_result.json`，平台模型列表见`verification/gateway_models.json`；旧平台403仅保留为`api_probe_previous_gateway.json`历史记录。此次截至交付累计4次请求：旧平台1次、新平台错误旧名称1次、模型列表1次、新名称成功1次。

## 代码对应表

| 文件 | 实现内容 |
| --- | --- |
| src/rumor_sim/config.py | 唯一配置来源与启动前校验 |
| src/rumor_sim/import_data.py | 三表读取、无表头处理、统计尾行过滤、用户去重 |
| src/rumor_sim/core.py | 人口、网络、信息流、同步状态机、PBd、TBU |
| src/rumor_sim/provider.py | 真实模型请求、严格输出、重试、预算与缓存 |
| src/rumor_sim/runner.py | 真实画像赋值、父轨迹与政策分支调度 |
| src/rumor_sim/storage.py | 原子快照、校验哈希、完整导出与恢复 |
| src/rumor_sim/cli.py | 单事件、批量、检查、估算和导入命令 |

重新导入Excel：

```powershell
python -m pip install -r requirements.txt
python run.py import-data --source "原Excel文件夹路径" --output data/reimported
```

原始工作簿不会被修改。首次导入时，42张无表头转发表已保留第一行；末尾29行评论统计和117行转发统计未错误当作用户。

接口字段参考：DeepSeek官方[Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)与[Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)。实际第三方接口以真实调用返回为准。
