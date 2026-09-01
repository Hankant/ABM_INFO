# Paper 1：混合 LLM–ABM 相关文献元数据与 DeepSeek 摘录指令

更新日期：2026-08-25  
入库范围：规则型代理与 LLM agent 共存、LLM 意见动力学、真实人类数据驱动的代理构建。  
本批状态：仅保存元数据、官方入口与研究相关性；未下载新 PDF。

## 一、术语边界

相关论文实际使用的名称包括：

- **hybrid framework for social media user simulation**：Mou et al. (2024)。
- **graph-accelerated hybrid multi-agent framework**：Zhou et al. (2026)。
- **hybrid agent-based modeling framework**：Chen (2026)。
- **LLM-driven ABM**：Yang and Chiou (2026)。

“混合 LLM–ABM”在本项目中暂作方法描述，指同一模拟系统中同时存在由显式规则更新的代理和由 LLM 生成判断或行为的代理。它不是本项目新提出的理论构念。

## 二、已记录文献

### 1. `MouEtAl2024HiSim`

Mou, X., Wei, Z., & Huang, X. (2024). Unveiling the truth and facilitating change: Towards agent-based large-scale social movement simulation. *Findings of the Association for Computational Linguistics: ACL 2024*, 4789–4809. https://doi.org/10.18653/v1/2024.findings-acl.285

- 发表状态：同行评审会议论文。
- 官方入口：https://aclanthology.org/2024.findings-acl.285/
- 代理构成：核心用户由 LLM 驱动；普通用户由演绎式 ABM 驱动。
- 数据基础：真实 Twitter 用户资料、历史推文、初始态度和关注网络。
- 与本研究关系：目前最接近“部分节点使用 LLM、其余节点使用意见动力学规则”的直接先例。
- 已识别边界：文本由立场识别和情感分析转成态度分数；普通用户对核心用户的反向影响未被纳入。

### 2. `ZhouEtAl2026GASim`

Zhou, X., Sun, Y., Yao, H., He, A., Zhang, Y., & Liu, W. (2026). GASim: A graph-accelerated hybrid framework for social simulation. *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 12510–12528. https://doi.org/10.18653/v1/2026.acl-long.569

- 发表状态：同行评审会议长文。
- 官方入口：https://aclanthology.org/2026.acl-long.569/
- 代理构成：LLM 核心代理与图消息传递驱动的普通代理共存。
- 主要目标：降低大规模混合社会模拟的延迟和 token 成本。
- 与本研究关系：为大规模混合计算架构提供直接参照；理论结果仍需由意见动力学与群体意见分布界定。

### 3. `Chen2026AgoraSim`

Chen, C.-C. (2026). AgoraSim: A hybrid agent-based modeling framework. *arXiv preprint arXiv:2607.05999*. https://doi.org/10.48550/arXiv.2607.05999

- 发表状态：预印本。
- 官方入口：https://arxiv.org/abs/2607.05999
- 代理构成：可按比例混合 LLM、视觉语言模型、外部端点、随机代理和经典代理。
- 主要特点：不同类型代理使用共同的结构化决策对象和行动空间，并可与匹配的经典模型运行比较。
- 与本研究关系：支持操纵 LLM 节点比例和比较全规则基线；当前证据不支持将其视为成熟的实证验证框架。

### 4. `ChuangEtAl2024`

Chuang, Y.-S., Goyal, A., Harlalka, N., et al. (2024). Simulating opinion dynamics with networks of LLM-based agents. *Findings of the Association for Computational Linguistics: NAACL 2024*, 3326–3346. https://doi.org/10.18653/v1/2024.findings-naacl.211

- 发表状态：同行评审会议论文。
- 官方入口：https://aclanthology.org/2024.findings-naacl.211/
- 代理构成：LLM-based agents 组成的网络。
- 主要发现：模型存在趋向事实共识的偏向；通过提示诱导确认偏差后，模拟出现意见碎片化。
- 与本研究关系：直接说明 LLM 的更新倾向可能决定群体意见轨迹，也说明提示构造不能被当作中性的技术细节。

### 5. `ChuangEtAl2024BeyondDemographics`

Chuang, Y.-S., Nirunwiroj, K., Studdiford, Z., et al. (2024). Beyond demographics: Aligning role-playing LLM-based agents using human belief networks. *Findings of the Association for Computational Linguistics: EMNLP 2024*, 14010–14026. https://doi.org/10.18653/v1/2024.findings-emnlp.819

- 发表状态：同行评审会议论文。
- 官方入口：https://aclanthology.org/2024.findings-emnlp.819/
- 数据基础：人类调查中的 64 个议题和 9 个潜在信念因素。
- 主要发现：人口统计信息本身没有使 LLM 意见充分贴近人类；加入一个经验观测到的相关信念后，相关议题的拟合改善。
- 与本研究关系：支持使用真实初始意见或信念关系校准代理，人口统计 persona 只能承担有限作用。

### 6. `ParkEtAl2024SelfReports`

Park, J. S., Zou, C. Q., Kamphorst, J., et al. (2024; arXiv v3, 2026). LLM agents grounded in self-reports enable general-purpose simulation of individuals. *arXiv preprint arXiv:2411.10109*. https://doi.org/10.48550/arXiv.2411.10109

- 发表状态：预印本。
- 当前官方入口：https://arxiv.org/abs/2411.10109
- 题名说明：旧题名为 *Generative Agent Simulations of 1,000 People*；2026 年 v3 已更名。
- 数据基础：1,052 名美国参与者的半结构化访谈、调查或两者结合。
- 与本研究关系：为使用真实问卷或访谈数据构建个体代理提供依据；该研究没有建立网络中的长期意见传播模型。

### 7. `LanEtAl2026PublicOpinion`

Lan, H., Hu, H., Guo, P. C., & Huang, Q. (2026). Public opinion dissemination simulation based on large language model multi-agent systems. *Scientific Reports, 16*(1), 16231. https://doi.org/10.1038/s41598-026-44206-z

- 发表状态：同行评审期刊论文。
- 官方入口：https://www.nature.com/articles/s41598-026-44206-z
- 数据基础：使用真实微博互动数据校准行为频率，并用概率模型约束行为和议题分布。
- 代理构成：LLM 负责关键语义内容，概率模型控制行为频率和部分结构化决策。
- 与本研究关系：提供“宏观统计约束 + 微观语言生成”的相邻架构，但没有建立两类节点长期共存的严格混合人口。

### 8. `YangChiou2026HumanWater`

Yang, Y. C. E., & Chiou, W. (2026). Leveraging large language models for agent-based simulation of human–water system interactions. *Water Resources Research, 62*(6), e2025WR042111. https://doi.org/10.1029/2025WR042111

- 发表状态：同行评审期刊论文。
- 官方入口：https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025WR042111
- 代理构成：比较传统随机 ABM 与 LLM-driven ABM，并讨论在关键决策时调用 LLM、其他状态由规则更新的混合方式。
- 数据基础：论文的示范案例使用合成数据，作者明确将其界定为方法验证，未声称行为预测效度。
- 与本研究关系：支持在同一代理内部划分规则更新与 LLM 推理的架构，也提供了结构不确定性和验证边界的写法。

## 三、当前入库判断

- 严格结构先例：`MouEtAl2024HiSim`。
- 大规模计算扩展：`ZhouEtAl2026GASim`。
- 可调混合人口框架：`Chen2026AgoraSim`，预印本。
- 意见动力学行为边界：`ChuangEtAl2024`。
- 真实人类数据校准：`ChuangEtAl2024BeyondDemographics` 与 `ParkEtAl2024SelfReports`。
- 概率规则和 LLM 语义生成结合：`LanEtAl2026PublicOpinion`。
- 同一代理内部的规则—LLM 分工：`YangChiou2026HumanWater`。

现有文献已经覆盖“混合 LLM 与规则型代理”的基本架构。本项目需要把贡献放在研究对象、因果比较、真实人类数据校准、双向交互转换和群体意见分布结果上。

## 四、交给 DeepSeek 的检索与摘录指令

```text
你是一名计算社会科学与意见动力学方向的文献研究助理。请围绕“规则型代理与 LLM agent 共存的混合 ABM，以及真实人类数据驱动的意见形成模拟”执行一次可核查的文献检索和全文摘录。

一、必须先核对的种子文献
1. Mou, Wei, and Huang (2024), Unveiling the Truth and Facilitating Change: Towards Agent-Based Large-Scale Social Movement Simulation. DOI: 10.18653/v1/2024.findings-acl.285
2. Zhou et al. (2026), GASim: A Graph-Accelerated Hybrid Framework for Social Simulation. DOI: 10.18653/v1/2026.acl-long.569
3. Chen (2026), AgoraSim: A Hybrid Agent-Based Modeling Framework. arXiv:2607.05999
4. Chuang et al. (2024), Simulating Opinion Dynamics with Networks of LLM-Based Agents. DOI: 10.18653/v1/2024.findings-naacl.211
5. Chuang et al. (2024), Beyond Demographics: Aligning Role-Playing LLM-Based Agents Using Human Belief Networks. DOI: 10.18653/v1/2024.findings-emnlp.819
6. Park et al. (2024; current arXiv v3), LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals. arXiv:2411.10109。注意旧题名为 Generative Agent Simulations of 1,000 People。
7. Lan et al. (2026), Public Opinion Dissemination Simulation Based on Large Language Model Multi-Agent Systems. DOI: 10.1038/s41598-026-44206-z
8. Yang and Chiou (2026), Leveraging Large Language Models for Agent-Based Simulation of Human–Water System Interactions. DOI: 10.1029/2025WR042111

二、扩展检索范围
检索 2023—2026 年直接相关研究，关键词至少组合以下术语：
- "hybrid agent-based model" AND LLM
- "hybrid social simulation" AND large language model
- "LLM agent" AND "opinion dynamics"
- "rule-based agents" AND "LLM agents"
- "human-grounded agents" AND survey
- "mixed population" AND "large language model agents"

优先检索 ACL Anthology、ACM Digital Library、IEEE Xplore、Springer Nature、Wiley、PNAS、JASSS 和 arXiv。搜索结果页和二手解读不能作为结论依据。必须打开论文全文、出版社页面或官方预印本。

三、纳入标准
满足下列至少一项：
A. 同一模拟人口中同时存在规则型代理和 LLM agent；
B. 同一代理的不同决策阶段分别由显式规则和 LLM 完成；
C. 使用真实调查、访谈、社交媒体行为或真实网络数据构建或校准 LLM agent；
D. 使用 LLM agent 模拟意见、态度或信念在网络中的多轮更新。

排除：仅讨论通用多智能体协作、没有社会模拟对象、只让 LLM 帮助编写 ABM 代码、没有实际模型或实验的产品宣传文章。概念论文可以保留，但必须单列为“立场/方法论文”。

四、每篇文献必须摘录的内容
1. 完整书目信息：题名、全部作者、年份、期刊或会议、卷期页码、DOI或arXiv号、发表状态。
2. 原文使用的架构名称。不得自行制造术语。
3. Agent构成：代理种类、数量、LLM节点比例、LLM节点选择方式。
4. 状态变量：opinion、attitude、belief、action或其他变量的原文名称和定义。
5. 更新规则：谁接收什么信息，如何更新状态，是否使用DeGroot、bounded confidence、Bayesian updating、概率规则或自定义函数。
6. 自然语言接口：文本如何转换为数值意见或行动；数值状态如何转换为文本；转换是单向还是双向。
7. 真实数据：数据来源、样本量、抽样方式、用于初始化、参数估计、校准还是验证。
8. 验证方法：个体层验证、群体分布验证、时间轨迹验证、消融实验和基线模型。
9. 作者实际报告的主要发现。
10. 作者明确承认的局限。
11. 与本项目的关系：完全重合、部分重合或仅提供方法支撑，并说明判断依据。

五、证据要求
- 每个重要判断都标注论文页码、章节名、公式号、表号或图号。
- 每篇保留3—6段关键原文摘录。每段不超过两句话，并附中文直译。
- 严格区分“作者原文”“根据方法作出的推论”“你的评价”。
- 无法读取全文时写“全文未取得”，不得根据摘要补写方法细节。
- 预印本必须标注“未经同行评审”；若存在正式版本，优先使用正式版本并说明版本关系。
- 不得虚构DOI、样本量、模型名称、结果或页码。
- 避免使用“不是……而是……”句式，避免空泛评价。

六、输出格式
输出一个Markdown文件，结构如下：

# 混合 LLM–ABM 与意见动力学文献全文摘录
## 1. 检索记录
## 2. 纳入与排除标准
## 3. 文献总表
## 4. 逐篇全文摘录卡片
### 4.1 文献题名
- 核验后的引用
- 原始术语
- Agent构成
- 状态变量与更新规则
- 文本—数值转换
- 人类数据与校准
- 验证方法
- 作者发现
- 作者局限
- 原文摘录与页码
- 与本项目的重合边界
## 5. 跨文献比较矩阵
## 6. 仍未被解决的研究缺口
## 7. 无法核验或被排除的条目

跨文献比较矩阵至少包含：规则型节点、LLM节点、混合比例、真实人类数据、网络交互、意见更新、自然语言传播、双向转换、个体验证、群体验证、同行评审状态。
```

## 五、后续待办

1. DeepSeek 返回全文摘录后，逐篇核对其页码、公式、样本量与作者原话。
2. 确认需要保留的论文后再下载 PDF，并以 BibTeX key 命名。
3. PDF 完成核验后再更新知识图谱中的 `has_pdf` 与本地路径字段。
