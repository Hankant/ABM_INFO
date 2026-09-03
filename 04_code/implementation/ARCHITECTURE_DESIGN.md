---
document_id: ABM-ARCH
title: ABM_INFO 混合 ABM 架构设计与版本记录
version: 0.1.0
status: DRAFT
created: 2026-09-03
last_updated: 2026-09-03
current_research_baseline: ../../00_current_baseline/Paper1_Formal_RP_EN.tex
---

# ABM_INFO 混合 ABM 架构设计与版本记录

## 1. 文档目的与约束

本文档记录 ABM_INFO 项目的混合 Agent-Based Model（ABM）架构、模块边界、接口、待确认选择与后续修改。它是工程设计主文档，不替代现行研究基准：

`../../00_current_baseline/Paper1_Formal_RP_EN.tex`

当前版本是设计草案，不代表下列待定事项已经获得确认：具体研究场景、人群、数据来源、网络、模型池、LLM 代理比例、模拟轮次、主结果、意见更新规则、空暴露行为和参数分布。

如果未来的架构修改改变研究问题、理论构念、分析层级、识别逻辑或结论强度，必须先由用户确认，并在 `../../05_reviews_and_revision_history/` 单独保存研究内容变更说明。本文档中的工程变更记录不能替代该程序。

## 2. 状态标签

| 标签 | 含义 |
| --- | --- |
| `FIXED` | 来自现行研究基准或项目规则；未经用户确认不得改变 |
| `PROVISIONAL` | 当前推荐的工程方案；可通过设计评审修改 |
| `TBD` | 尚未确定；不得在实现中自行固定 |
| `REJECTED` | 已识别为不适合本项目或会破坏可识别性的做法 |

## 3. 版本规则

本文档采用语义化版本号 `MAJOR.MINOR.PATCH`：

- `MAJOR`：研究边界、分析单位、核心过程接口或总体耦合方向发生变化；必须有用户确认和 `05_reviews_and_revision_history` 记录。
- `MINOR`：增加模块、修改模块责任、运行顺序、数据契约、验证门槛或引擎策略。
- `PATCH`：不改变含义的文字澄清、链接修复、示例补充或格式调整。

每次修改必须同步更新文档头部的 `version`、`last_updated` 和第 16 节版本历史。

## 4. 当前研究边界

| 项目 | 当前定义 | 状态 |
| --- | --- | --- |
| 总主题 | AI 如何改变人类群体的信息获取与意见形成 | `FIXED` |
| 核心问题 | How do large language models change group opinion distributions? | `FIXED` |
| 分析单位 | 具有信息传播网络的统计群体，不直接外推为正式组织团队 | `FIXED` |
| 研究顺序 | SQ1 信息暴露与传播；SQ2 意见更新与群体演化；SQ3 条件式技术抑制 | `FIXED` |
| SQ1 对比 | 传统搜索引擎信息获取与 LLM 信息获取 | `FIXED` |
| 共享人工简报 | 仅作为替代来源检查，不替代传统搜索条件 | `FIXED` |
| SQ3 前提 | 只有 SQ2 出现稳定群体演化模式后才执行 | `FIXED` |
| 群体结果边界 | 模型输出相似不能直接解释为人类意见收敛 | `FIXED` |
| 长期结果边界 | 无现实群体验证时，只称经验约束下的模型涌现或反事实模拟 | `FIXED` |

## 5. 核心构念与观测边界

本节只记录现行设计已经使用的过程对象，不增加新的理论构念。

| 原始术语 | 来源 | 定义与排除项 | 分析层级 | 模型位置 | 经验对应 | 能区分的竞争解释 |
| --- | --- | --- | --- | --- | --- | --- |
| Message function / `f_message` | Mou et al. (2024) 的函数分解；现行 RP | 将来源状态转成可传播消息；不等于接收者实际看到该消息 | 消息—发送者—轮次 | 信息生成过程 | 原始文本、立场、主张、来源、表达不确定性 | 输出相似来自信息生成，还是来自后续选择 |
| Selection function / `f_selection` | Mou et al. (2024) 的函数分解；现行 RP | 从候选消息形成实际暴露集合；不等于潜在网络连接，也不等于接受 | 接收者—消息—轮次 | 暴露机制 | 被呈现、打开或阅读的消息记录 | 网络可达与实际注意选择 |
| Sharing and diffusion path | 现行 RP | 消息被再次传播的行为和路径；不等于首次暴露或意见接受 | 关系／网络—轮次 | 传播机制 | 分享、转发、回复事件及边 | 信息被看到与信息继续扩散 |
| Update function / `f_update` | Mou et al. (2024) 的函数分解；现行 RP | 暴露后个体意见状态的变化；不由公开文本自动反推 | 个体—轮次 | 微观状态转移 | 暴露前后意见、更新方向与幅度 | 未暴露、已暴露但未接受、接受后更新 |
| Group opinion distribution | 现行 RP 的群体结果 | 群体成员意见的分布特征；不自动等于判断质量或社会福利 | 群体—轮次 | 结果 | 均值、方差、分位数、聚类、双峰性和轨迹 | 共同移动、收敛、分化和分群等不同分布变化 |

## 6. 总体架构：5 层、13 个模块

一般 ABM 用较少模块即可运行；本项目还需要自然语言、LLM 角色分离、人类校准和审计，因此按 5 层、13 个功能模块设计。模块是独立责任，不等于 13 个 Agent 类型或 13 个代码文件。

```text
场景与运行配置
       │
人口初始化 ── 代理状态 ── 环境与潜在网络
       │
候选消息 f_message
       │
实际暴露 f_selection
       │
意见更新 f_update ── 分享与扩散 f_sharing
       │
规则代理／LLM代理内核
       │
同步调度与轮次提交
       │
文本编码 ── 校准验证 ── 日志回放与评估
```

### 6.1 第一层：研究与实验定义

| ID | 模块 | 责任 | 主要输入 | 主要输出 | 状态 |
| --- | --- | --- | --- | --- | --- |
| M01 | Scenario and Run Configuration | 声明情境、条件、轮次、模型版本、随机种子和停止规则 | 经确认的实验设计 | `ScenarioConfig`、`RunManifest` | `PROVISIONAL`；具体值 `TBD` |

### 6.2 第二层：模拟世界

| ID | 模块 | 责任 | 主要输入 | 主要输出 | 状态 |
| --- | --- | --- | --- | --- | --- |
| M02 | Population Initializer | 从真实样本或声明分布联合生成群体，不独立拼接相关人口变量 | 初始化数据、抽样规则 | 初始代理集合 | `PROVISIONAL`；数据源 `TBD` |
| M03 | Agent State | 保存每个成员的显式状态、历史、暴露和行为 | 初始代理、每轮提交 | `AgentState(t)` | 边界 `FIXED`；具体字段部分 `TBD` |
| M04 | Environment and Network | 保存外部信息环境、潜在连接和可达关系 | 网络数据或生成规则 | 候选接触集合 | 两层记录原则 `FIXED`；网络类型 `TBD` |

### 6.3 第三层：行为过程

| ID | 模块 | 责任 | 主要输入 | 主要输出 | 状态 |
| --- | --- | --- | --- | --- | --- |
| M05 | Message Function | 生成可传播的候选消息 | 来源状态、历史、情境 | `Message[]` | 接口 `FIXED`；生成规则 `TBD` |
| M06 | Selection Function | 从可达候选消息形成实际暴露 | 网络、候选消息、选择参数 | `ExposureBundle` | 接口 `FIXED`；选择规则 `TBD` |
| M07 | Sharing Function | 决定分享、回复、引用或沉默及传播目标 | 状态、暴露包、分享参数 | `ShareEvent[]` | 独立接口 `PROVISIONAL` |
| M08 | Update Function | 依据当前状态和实际暴露生成下一期意见 | `AgentState(t)`、`ExposureBundle` | `StateTransition` | 接口 `FIXED`；主更新式 `TBD` |

### 6.4 第四层：混合代理与执行

| ID | 模块 | 责任 | 主要输入 | 主要输出 | 状态 |
| --- | --- | --- | --- | --- | --- |
| M09 | Agent Kernels and Role Router | 让规则代理与模拟人类的 LLM 代理实现相同数据契约，并区分 LLM 角色 | 代理类型、模型配置 | 更新和行为决策 | 角色分离 `FIXED`；代理比例 `TBD` |
| M10 | Scheduler and Round Engine | 按声明顺序执行一轮，使用同步快照并统一提交 `t+1` | 当前快照、四个行为接口 | 下一轮快照 | 同步主设计 `PROVISIONAL` |

### 6.5 第五层：经验约束与审计

| ID | 模块 | 责任 | 主要输入 | 主要输出 | 状态 |
| --- | --- | --- | --- | --- | --- |
| M11 | Text Encoder and Measurement | 把自然语言编码为声明字段，并保存人工分歧和测量误差 | 原始消息、编码规范 | `EncodedMessage` | 与生成器分离 `FIXED`；编码方案 `TBD` |
| M12 | Calibration and Validation | 估计参数、恢复参数并做保留样本微观和宏观验证 | 人类数据、模拟输出 | 参数、验证报告 | 顺序 `FIXED`；数据与阈值 `TBD` |
| M13 | Logger, Replay and Evaluation | 保存完整路径、随机状态、模型调用和结果指标，支持离线回放 | 全部事件 | 事件日志、快照、评估结果 | 完整可追溯原则 `FIXED` |

## 7. 核心数据契约

以下字段名是工程标识，不是新增理论构念。

### 7.1 AgentState

```text
AgentState
  agent_id
  agent_kind                 # rule | llm_human_sim
  issue_id
  round_id
  opinion_position
  opinion_certainty          # 仅在人类数据支持时启用
  factual_beliefs            # 仅在研究材料包含可核查命题时启用
  memory_refs
  exposure_refs
  action_refs
```

政策支持、事实可信度、公开表达和情绪不得合并为一个 `opinion` 字段。

### 7.2 Message

```text
Message
  message_id
  issue_id
  round_id
  sender_id
  source_role
  raw_text
  action_type
  parent_message_id
  created_at_simulation
  encoding_status
```

文本编码后的立场、主张、来源和不确定性另存为 `EncodedMessage`，不得覆盖原始消息。

### 7.3 ExposureRecord

```text
ExposureRecord
  receiver_id
  message_id
  reachable
  selected
  exposure_order
  exposure_probability
  selection_seed
```

`reachable` 与 `selected` 必须分开，以区分潜在网络和实际暴露。

### 7.4 StateTransition

```text
StateTransition
  agent_id
  issue_id
  round_id
  state_before
  exposure_bundle_id
  proposed_state_after
  committed_state_after
  update_kernel
  parameter_set_id
  raw_llm_response_ref
  validation_status
```

### 7.5 RunManifest

```text
RunManifest
  run_id
  architecture_version
  scenario_config_hash
  code_commit
  dataset_versions
  network_seed
  selection_seed
  rule_update_seed
  llm_generation_seed
  model_provider
  model_name
  model_version
  prompt_version
  sampling_parameters
  start_time
  end_time
```

不得把网络、选择、规则更新和 LLM 生成共用一个无法拆分的随机状态。

## 8. 三种 LLM 角色

| 角色 | 在研究中的位置 | 允许做什么 | 不允许做什么 | 状态 |
| --- | --- | --- | --- | --- |
| 被研究的 LLM 信息源 | SQ1 的处理条件 | 回答成员查询并产生候选信息 | 同时扮演模拟人类代理或最终文本编码器 | `FIXED` |
| 模拟人类的 LLM 代理 | 混合 ABM 的代理实现 | 根据资料、显式状态、记忆和暴露包返回结构化状态转移与行为 | 把自身输出偏好直接解释为真实人类机制 | `FIXED` |
| 文本编码器 | 测量模块 | 编码立场、主张、来源和表达不确定性 | 用同一生成偏误替代人工验证 | `FIXED` |

最低记录要求包括角色、模型供应商、模型名称、模型版本、提示版本、温度、其他采样参数、调用时间、原始请求、原始响应和解析结果。

## 9. 一轮模拟的推荐顺序

主设计采用同步快照；异步顺序仅作为预先声明的敏感性检查。

```text
1. 冻结 t 时点代理状态、网络和外部输入
2. 生成候选信息和成员消息：f_message
3. 根据潜在网络形成每名代理的实际暴露包：f_selection
4. 规则代理依据同一 t 快照计算拟议状态转移：f_update
5. LLM 代理读取结构化暴露包并返回拟议状态转移
6. 两类代理依据已声明规则产生分享／回复／沉默：f_sharing
7. 校验全部结构化输出；无效输出不得静默写入状态
8. 同时提交 t+1 状态、消息、传播边和记忆
9. 写入事件日志、快照和本轮指标
```

规则代理的信息必须能够进入 LLM 代理的下一轮暴露包；LLM 代理的信息也必须能够进入规则代理暴露包。

## 10. 更新函数的当前位置

主更新式尚未确认。当前只记录候选位置，不固定最终选择：

| 候选 | 当前角色 | 使用条件 | 状态 |
| --- | --- | --- | --- |
| 现行 RP 的锚定更新结构 | 最小主模型候选 | 参数能够由人类意见转移数据估计并在保留议题验证 | `PROVISIONAL` |
| Bounded-confidence 类规则 | 透明竞争基线 | 人类数据支持意见距离阈值 | `PROVISIONAL` |
| Social Judgment | 检验远距信息是不更新还是反向移动 | 人类数据观察到排斥更新，而非只有拒绝 | `TBD` |
| Relative Agreement | 同时建模意见位置与确定程度 | 取得联合前后测意见与确定程度 | `TBD` |
| Lorenz 类多机制规则 | 稳健性或敏感性分析 | 参数可识别且每个保留项有经验对应 | `TBD` |

不得为了复现 HiSim 而直接复制其公式、参数表或公开代码。论文定义、原始理论、人类测量和实现测试必须共同决定最终版本。

## 11. 从 HiSim 继承与拒绝的内容

### 11.1 可以继承

- 少量 LLM 代理与大量规则代理构成混合模拟的总体工程思路；
- `f_message`、`f_selection`、`f_update` 的过程分解；
- 人口、代理、环境、调度、行为与评估的模块化结构；
- 微观行为和宏观轨迹同时评估；
- 把模型采样参数纳入敏感性分析。

### 11.2 必须修改后使用

- 增加规则代理到 LLM 代理的可读信息通道；
- 使用同步快照，避免规则层更新后再覆盖 LLM 镜像所形成的时序滞后；
- 把网络可达、实际暴露和分享路径分别记录；
- 把公开文本与潜在意见状态分开；
- 分别估计 LLM 生成随机性和规则层随机性。

### 11.3 明确拒绝

- `REJECTED`：使用 `eval()` 解析模型输出；
- `REJECTED`：用情感强度直接覆盖潜在意见；
- `REJECTED`：把沉默自动写成中立意见或数值 `0`；
- `REJECTED`：让 LLM 自行修改已声明的选择、分享或网络规则；
- `REJECTED`：用同一个 LLM 同时承担信息源、模拟人类代理和最终测量；
- `REJECTED`：只拟合宏观均值而不验证微观状态转移；
- `REJECTED`：把流畅的自然语言解释当作人类心理机制证据。

第三方 HiSim 源码继续保存在 `../third_party_reference/`，不得移除其许可证或作者信息。

## 12. 仿真引擎策略

### 12.1 当前建议

采用引擎无关的数据契约和行为接口：

```text
ABM_INFO domain and interfaces
        ├── Python reference engine
        └── Optional AnyLogic adapter
```

Python 参考引擎作为可审计、可测试和 Git 友好的科学内核；AnyLogic 可作为后续调度、实验与可视化后端，但不能成为唯一的数据和规则来源。

### 12.2 AnyLogic 可承担的模块

- 人口和代理实例化；
- 潜在网络与消息传递；
- 同步轮次调度；
- 参数变化和重复运行；
- 网络传播和群体状态可视化。

LLM 信息源、模拟人类的 LLM 调用、文本编码、提示版本、调用缓存、校准和最终验证建议保留在外部 Python 服务。两边通过版本化 JSON 契约交换暴露包和状态转移。

官方能力参考：

- AnyLogic Agent-Based Modeling: <https://anylogic.help/anylogic/agentbased/index.html>
- Agent networks: <https://anylogic.help/anylogic/agentbased/connections-and-networks.html>
- Agent communication: <https://anylogic.help/anylogic/agentbased/communication.html>
- Parameter variation: <https://anylogic.help/anylogic/experiments/parameter-variation.html>
- Python/Pypeline integration: <https://anylogic.help/advanced/code/pypeline.html>
- Editions and PLE limitations: <https://anylogic.help/anylogic/ui/editions.html>

Pypeline 是可选连接工具，官方文档不承诺持续兼容。正式接口优先采用可测试的本地服务协议；不得在 GUI 事件中逐代理同步调用在线模型并让网络延迟改变模拟时序。

## 13. 日志、目录和数据边界

建议实现目录：

```text
04_code/implementation/
├── ARCHITECTURE_DESIGN.md
├── abm_info/
│   ├── domain/
│   ├── interfaces/
│   ├── agents/
│   ├── sources/
│   ├── opinion_models/
│   ├── encoding/
│   ├── engine/
│   ├── calibration/
│   ├── evaluation/
│   └── logging/
└── tests/
```

实验资产遵循项目目录规则：

- 配置：`../../06_experiments/configs/`
- 输出：`../../06_experiments/results/`
- 日志：`../../06_experiments/logs/`

这些目录首次实际使用时再创建。新的人类数据不得与公开代码、示例配置或可共享输出混放；在收集前需建立数据使用、伦理和匿名化说明。不得提交 API key、模型凭据、参与者身份信息、受限数据或本地缓存。

## 14. 实施阶段与质量门槛

| 阶段 | 内容 | 进入下一阶段的门槛 | 状态 |
| --- | --- | --- | --- |
| P0 | 冻结架构数据契约和模块设计卡 | 13 个模块的输入、输出、责任和待定项完成评审 | 当前阶段 |
| P1 | Python 纯规则最小引擎 | 更新方向测试、同步顺序测试和固定种子回放通过 | 未开始 |
| P2 | 使用缓存 LLM 输出的混合纵向切片 | 无在线调用也能完整回放，双向信息接口通过 | 未开始 |
| P3 | 接入被研究的 LLM 信息源与模拟人类的 LLM 代理 | 三种 LLM 角色、提示和日志完全分离 | 未开始 |
| P4 | 接入人类校准数据 | 参数恢复通过，估计、选择和保留验证数据分离 | 未开始 |
| P5 | 宏观群体实验 | 微观意见转移和分享行为先通过保留样本验证 | 未开始 |
| P6 | AnyLogic 适配与可视化 | 与 Python 参考引擎在同一缓存输入下产生一致的规则层结果 | 可选、未开始 |

工程纵向切片可以暂用少量代理和少量轮次做测试，但这些数字只用于软件验证，不得进入正式研究设计或结果解释。

## 15. 待决策登记表

| 决策 ID | 问题 | 为什么必须确认 | 当前状态 |
| --- | --- | --- | --- |
| D-001 | 具体研究场景和议题是什么？ | 决定信息、意见尺度和外部效度 | `TBD` |
| D-002 | 目标群体与数据来源是什么？ | 决定初始化和验证对象 | `TBD` |
| D-003 | 主更新函数是什么？ | 决定微观机制与参数需求 | `TBD` |
| D-004 | 空暴露时状态如何转移？ | 空集合不能在更新式中静默处理 | `TBD` |
| D-005 | 潜在网络来自真实记录还是生成模型？ | 决定可达关系与网络外推边界 | `TBD` |
| D-006 | `f_selection` 如何生成实际暴露？ | 决定网络效应与注意选择能否区分 | `TBD` |
| D-007 | 分享由人类估计、规则函数还是 LLM 决定？ | 决定传播机制的识别 | `TBD` |
| D-008 | 哪些节点由 LLM 模拟人类？ | 影响计算架构和反事实含义 | `TBD` |
| D-009 | LLM 节点比例与抽样规则是什么？ | 不得观察结果后选择 | `TBD` |
| D-010 | 使用哪些信息源模型和模型池？ | 决定 SQ1 与 SQ3 条件 | `TBD` |
| D-011 | 主群体分布结果是什么？ | 需要在确证性分析前固定 | `TBD` |
| D-012 | 实际轮次、终止规则和时间映射是什么？ | 决定动态解释和计算规模 | `TBD` |
| D-013 | AnyLogic 是否进入主执行链？ | 决定部署、许可和跨引擎验证成本 | `TBD` |

## 16. 版本历史

| 版本 | 日期 | 状态 | 变更 | 研究基准是否改变 |
| --- | --- | --- | --- | --- |
| 0.1.0 | 2026-09-03 | DRAFT | 首次汇总 HiSim 架构拆解、5 层 13 模块、数据契约、双向同步轮次、引擎策略、质量门槛和待决策表 | 否 |

## 17. 后续变更记录模板

复制以下模板追加到本节下方，并同时更新第 16 节：

```markdown
### Change ABM-ARCH-YYYYMMDD-NN

- Previous version:
- New version:
- Date:
- Requested by:
- Status: PROPOSED | APPROVED | REJECTED | IMPLEMENTED | VERIFIED
- Affected modules:
- Problem being changed:
- Evidence or reason:
- Exact design change:
- Research meaning changed: yes | no
- Baseline change record required: yes | no
- Files changed:
- Tests or validation:
- Remaining uncertainty:
```

## 18. 当前下一步

当前处于 P0。下一步应为 13 个模块逐一建立模块设计卡，至少填写：

```text
模块目的
输入
内部状态
输出
分析层级
经验数据来源
关键假设
待定选择
失败行为
单元测试
与其他模块的接口
```

在 D-001 至 D-013 未逐步审议前，不进入正式大规模编码。

## 参考与追溯

- Mou, X., Wei, Z., & Huang, X. (2024). *Unveiling the Truth and Facilitating Change: Towards Agent-based Large-scale Social Movement Simulation*. Findings of ACL 2024. <https://doi.org/10.18653/v1/2024.findings-acl.285>
- 本项目 HiSim 方法拆解：`../../01_research_notes/current_direction/Paper1_HiSim混合ABM方法拆解_2026-08-25.md`
- 本项目现行研究基准：`../../00_current_baseline/Paper1_Formal_RP_EN.tex`
- HiSim 第三方代码审计副本：`../third_party_reference/HiSim_source_audit/`
- 交互式知识图谱：`../../01_research_notes/literature_knowledge_graphs/hisim-2024-abm-knowledge-graph.html`
