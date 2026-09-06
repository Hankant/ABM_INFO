---
title: AnyLogic 社会模拟研究与 LLM 集成证据记录
version: 0.1.0
date: 2026-09-06
status: 技术探索；未执行集成实验
---

# AnyLogic 社会模拟研究与 LLM 集成证据记录

## 1. 范围与证据说明

保存前两轮讨论的文献实现信息，并补充 AnyLogic 与 LLM 连接方法。本文是 AI 辅助检索与方法摘录，不改变研究基准或架构主文档的已记录决策。来源包括论文全文、作者公开仓库和产品文档；工程建议单独标注。未安装库、未调用付费模型、未运行 AnyLogic，也未取得下列论文的全部原始工程。

需要修正此前表述：2021 年移动应用论文第一作者为 Zhenyu Zhang，应写 Zhang et al.，此前一轮写成 Zhou et al. 不准确。此前“Python 不可被 AnyLogic 替代”的说法过强：Python 主控是本项目工程选择，不是 AnyLogic 无法实现日志、缓存或校验的能力结论。未找到源码只表示本次未取得，不能写成作者绝未公开。

## 2. 四项研究的实现摘录

### 2.1 Zhang et al. (2021)：移动应用扩散与网络共同演化

来源：[论文全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC8146323/)，DOI 10.3390/e23050521；重点为第 3、4 节。

- 环境：AnyLogic 8；People 是用户集合，每个 Person 对象具有 accept/reject 状态；随机选取初始采纳者。
- 每轮流程：计算当前决策效用、收集邻居信息 → 学习并决定下一轮采纳/拒绝 → 更新互动计数 → 判断断边、复边、新建边 → 同步数据、统计网络。
- 断边：原邻居长期没有单向或双向决策模仿，达到阈值后以 Disconnect 概率断开。
- 复边：历史邻居在当前时刻决策相同，以 Reconnect 概率恢复联系。
- 新边：原本不连接的用户多轮决策相同，达到阈值后以 Newconnect 概率建立联系。
- 软件操作：正文写作 Connectto/Disconnectto；这是论文所述连接操作，不保证其大小写就是当前可编译 API 签名。
- 文中示例参数：断边阈值 30 轮、建边阈值 70 轮；Disconnect=0.8、Reconnect=0.3、Newconnect=0.08。这些只属于原文情景。
- 效用与学习的完整微观规则沿用文献 [7]，本次未追溯核验该原始规则；不能据当前文字补造效用公式。作者承认模型缺乏充分经验数据支撑。

可借鉴：网络操作、轮次顺序与行为/网络反馈。采纳状态不能直接当成人类意见强度。本次未取得原始 .alp。

### 2.2 Nasrinpour et al. (2016)：Facebook 消息传播

来源：[作者预印本](https://arxiv.org/abs/1611.07454)，题名 An Agent-Based Model of Message Propagation in the Facebook Electronic Social Network；软件细节来自此前检索到的正文片段。

- 环境：Java-based AnyLogic 教学版，确切版本尚未确认。
- 网络：使用 Facebook 样本，结合 erased configuration model 与共同邻居信息修正缺失边。
- 过程：登录/退出、发帖、阅读与分享；帖子长度与吸引力评分影响传播。部分行为参数采用截断正态分布，Activity 与 Post Score 使用 [0,1] 均匀分布。
- 本次未完整核验所有转移方程、阅读/转发概率及源码；不可将口头流程描述当作完整复现规范。

可借鉴：信息暴露与分享事件建模。没有证据表明它实现了本项目所需的自然语言信息源与逐轮意见更新。

### 2.3 Khasawneh et al. (2022)：社交媒体挑战参与

来源：[期刊页面](https://doi.org/10.1007/s42001-022-00183-7)；[可检索作者版 PDF](https://www.sce.carleton.ca/faculty/wainer/papers/s42001-022-00183-7.pdf)。本次已获得方法片段，期刊正文需要订阅，作者版全文获取未完成。

- 环境：AnyLogic 8.5.1 University Researcher Edition，Java；child、father、mother、house、school 五类对象。
- 空间：100000 × 100000 二维环形空间；家庭和学校随机布置，儿童连接最近学校，并建立密友及 5–25 位同校朋友联系。
- 时间：按天更新属性；行为设计参考 Integrated Behavioral Model，结合此前调查研究。
- 具体意向函数、权重、阈值与联合分布仍需全文核对；目前不能给出可执行的参与概率公式。
- 期刊的数据声明为合理请求后向通讯作者获取；这不等于模型源码已公开。

可借鉴：调查参数、家庭/同伴联系和干预情景的实现结构。行为参与不是意见分布。

### 2.4 Lu & Liu (2024)：突发事件网络群体极化

来源：[论文全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC11182558/)，DOI 10.1371/journal.pone.0305552；第 3.4、4.2 节及表 2。

- 环境：AnyLogic 系统动力学；确切版本、求解器与步长本次未确认。
- 状态：P、PI、PIP、N、NI、NE、NIN 等群体人数存量；通过流率与微分方程改变各类人数。
- 一个明确的流率例子：NI 向 PI 的转移在文字中写为 V5 = NI(t) × λ2 / Tc；λ2 是作者设置的情绪引导参数，Tc 是转换时间。
- 表 2 设 Tc=2 天、Te=6 天、Tef=7 天、Tpi=3 天、Tni=1 天；这些不是本项目的经验估计。
- 复现疑点：公式 (1)(2) 出现 `//*` 等表达；解释文字写 N/P，而公式显示 N/(P+N)。公式 (4) 的流入项也需和状态图逐一核对。不能将这些表达直接作为合法 Java 或可靠数值实现。

可借鉴：存量流量和参数扫描；没有逐个用户的暴露集合，不能直接替代个体意见更新。搜索热度趋势与极端意见人数也不是相同测量对象。本次未取得原始工程。

## 3. AnyLogic 与 LLM 的已验证连接证据

### 3.1 发表论文：LLM 生成场景，再运行 AnyLogic

[Dengler et al. (2023), A Conversational Human-Computer Interface for Smart Energy System Simulation Environments, Winter Simulation Conference](https://www.informs-sim.org/wsc23papers/250.pdf)，重点第 1、3 节及图 2。

论文报告 GPT-4 系列的 ChatGPT 与 AnyLogic 8.7.12 University Researcher Version，通过 i7-AnyEnergy 连接。流程是自然语言场景 → 预先给定的 Python API 描述 → LLM 生成 Python 脚本 → Python 执行生成 CSV → AnyLogic 导入并运行 → 内置图形或 CSV 输出。底层框架地址为 https://github.com/cs7org/i7-AnyEnergy 。框架开源不等于本文全部对话集成资产已核验。

证据意义：存在明确的 AnyLogic + LLM 学术应用，但 LLM 在场景构造阶段发挥作用，没有展示 LLM 模拟人的逐轮意见更新。本文仅概括连接流程，未复现其脚本。

### 3.2 已发布集成案例：Pypeline + ChatGPT Bridge

[AnyLogic 发布的 Noorjax 客座案例，2024-04-25](https://www.anylogic.com/blog/use-chatgpt-for-data-analysis-make-your-anylogic-model-talk/)介绍安装 Pypeline 和 ChatGPT 库，并将聊天 agent 放入模型，用于查询、解释仿真输出。属于产品/开发者案例，不能作为同行评议社会模拟结果。

它证明有开发者实现过连接；当前 API 兼容性、库许可和维护状况仍需实际测试。文章中的旧模型名称和凭据配置教程不应直接作为新实现规范。

### 3.3 通用运行时工具：Pypeline

[AnyLogic-Pypeline 仓库](https://github.com/the-anylogic-company/AnyLogic-Pypeline)与 [Wiki](https://github.com/the-anylogic-company/AnyLogic-Pypeline/wiki)。

AnyLogic 调用本地 Python，允许使用 Python 库和传递数据。README 提供 JAR 安装、Python Communicator 和示例；声明不是主产品一部分、不保证未来支持，跨语言通信有开销。它是连接层，本身没有提供本项目的 LLM 社会行为模型。

本项目候选用法：AnyLogic 在轮次边界发送结构化状态给 Python；Python 调用来源 LLM，或在独立角色下调用模拟人的 LLM，校验后返回结果。该闭环是工程提案，未运行验证。

### 3.4 通用运行时工具：Alpyne

[Alpyne 仓库](https://github.com/the-anylogic-company/Alpyne)。

由 Python 控制从 AnyLogic RL experiment 导出的模型。README 要求配置 Configuration、Observation、Action 和停止条件，并在需要外部决策时调用 takeAction；Python 的 AnyLogicSim 可重置模型、查询状态、施加动作和取输出。README 标注 public beta、Python 3.10+，版本/许可限制需按实际安装检查。

本项目候选用法：把外部决策控制器接成 LLM 调用服务，不必因此把研究改成强化学习。需要验证字符串/文本载荷、批量 agent 状态、暂停同步与动作数据类型；可能将文本保存在 Python，由模型只交换 ID。该适配尚未实现。

### 3.5 其他候选与排除边界

- [anylogicPLE-mcp](https://github.com/umbaman/anylogicPLE-mcp)：第三方仓库，声明从自然语言生成 .alp；目前列出的模板主要是队列、工厂、仓库、医院，未核验生成社会 ABM 的能力。生成模型不等于运行中由 LLM 决策。
- [anylogic-mcp-server](https://github.com/kishorkukreja/anylogic-mcp-server)：第三方 Cloud API 包装，公开工具包含连接、运行与读取结果。仅审阅公开片段，未运行；不能据 README 判断工具链完整可靠。
- [LLMDrivenSimulation](https://github.com/YuchenXia/LLMDrivenSimulation)：公开 LLM 仿真参数探索代码；本次查看的主页未明确证明底层是 AnyLogic，暂不计入 AnyLogic 结合证据。
- [假新闻扩散工程](https://github.com/Faculty-of-information-studies/Fake-news-dissemination-modelling)：可作为后续 AnyLogic 工程审计对象，本次未运行，也不属于已验证 LLM 集成。

## 4. 本项目的可选连接设计（提案）

| 路线 | 控制方向 | 用途 | 未决验证 |
| --- | --- | --- | --- |
| Pypeline | AnyLogic → Python → LLM | GUI 驱动的小规模闭环原型 | 阻塞、超时、数据转换和依赖兼容 |
| Alpyne | Python → AnyLogic；状态返回 Python 决策 | Python 主控的可重复批量实验 | 轮次同步、文本传输、导出许可与版本 |
| 自建 HTTP/JSON 服务 | AnyLogic Java ↔ 本地 Python 服务 | 明确接口契约及独立服务部署 | 本项目自行开发、测试和维护 |
| CSV/JSON 离线回放 | Python 预生成 → AnyLogic 回放 | 演示、基线对照、时序调试 | 无在线反馈，不代表在线 LLM 闭环 |

建议先用固定假响应验证一个轮次闭环，再接真实 LLM；不要以连接成功当作人类行为有效性证明。

候选轮次协议：冻结 t 时刻状态 → 调用 f_message → 得到实际暴露集合 f_selection → 调用 f_update → 校验全部结果 → 一次提交 t+1 状态。允许的异步行为必须由研究设计指定，不能由网络响应先后偶然决定。

候选请求字段：run_id、round_id、agent_id、role、state_version、message_ids、payload；候选响应字段：request_id、status、validated_result、model_version、prompt_version。角色必须区分信息来源与模拟人，原文消息和意见数值分开保存。字段是提案，不是上列论文原始 API。

最小验证任务（仅计划）：使用测试用小网络和固定输入，对比两个引擎每轮状态；注入超时、重复回包和缺失回包；测试暂停期间时间是否推进；记录环境及许可证；完成后才评估真实 LLM 的成本、延迟与重复性。测试规模不固定正式研究的代理数和轮数。

## 5. 检索与版本记录

检索日期：2026-09-06。查询包括 AnyLogic LLM Pypeline ChatGPT github、AnyLogic LLM agents integration MCP。优先核验 WSC 原论文、开发者 GitHub 与 AnyLogic 发布案例。此次是定向技术探索，未做系统综述，不能推出全球不存在某种实现。

| 版本 | 日期 | 变更 |
| --- | --- | --- |
| 0.1.0 | 2026-09-06 | 保存四项社会模拟研究摘录及复现缺口；修正作者与能力表述；补充 WSC 论文、Pypeline、Alpyne、MCP 候选和本项目待验证协议 |
