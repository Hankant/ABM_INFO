# 群体信息同质化、共享 LLM 与 LLM-ABM 文献清单

更新日期：2026-07-29  
增量更新：2026-08-01  
对应研究问题：当群体成员独立研究同一项开放性或争议性问题时，共享或高度相似的大语言模型是否会提高信息样本与判断误差的相关性，进而削弱认知多样性和集体判断质量？

## 1. 入库范围与核验口径

本清单收录本轮讨论中实际出现、且能够支撑以下四个环节的 41 篇文献：

1. LLM 输出同质性、算法单一化与群体智慧；
2. 共享信息、相关误差与群体聚合；
3. 意见动力学和认识论网络的 ABM；
4. LLM 社会仿真的可行性、效度边界与报告规范。

每条正式记录至少经过两类来源交叉核验：Crossref 与期刊/会议官网，或 arXiv 与会议、项目页、正式论文库。预印本保留预印本标识。无法确认的 DOI 没有写入。开放获取原文按 BibTeX key 命名；付费墙文献只登记元数据与权威链接。

入库结果：41 条 BibTeX；28 份开放原文；13 篇暂为元数据记录。

## 2. 直接相关的实验与理论

| Key | 文献 | 研究设计与本项目关系 | 识别边界 | 原文 |
|---|---|---|---|---|
| `JiangEtAl2025ArtificialHivemind` | Jiang et al. (2025), *Artificial Hivemind: The Open-Ended Homogeneity of Language Models* | 大规模比较开放式生成，显示不同模型在输出空间中存在系统性同质化；给出“共同模型先验”的直接测量框架。 | 测量模型输出，未识别人类判断或群体绩效的因果效应。 | [OpenReview](https://openreview.net/forum?id=saDOrrnNTz) · [PDF](./papers_originals/collective_intelligence_homogeneity/JiangEtAl2025ArtificialHivemind.pdf) |
| `FugenerGrahlGuptaKetter2021` | Fügener et al. (2021), *Will Humans-in-the-Loop Become Borgs? Merits and Pitfalls of Working with AI* | 分析模型、实验和模拟共同表明：AI 建议可提高个人准确率，同时使选择趋同、减少独特人类知识，并可能在较大群体中损害群体智慧；个性化建议能够缓解风险。 | 任务和建议结构有边界；其“相关判断—聚合损失”机制与本项目最接近。 | [DOI](https://doi.org/10.25300/MISQ/2021/16553) · [PDF](./papers_originals/collective_intelligence_homogeneity/FugenerGrahlGuptaKetter2021.pdf) |
| `DoshiHauser2024` | Doshi & Hauser (2024), *Generative AI Enhances Individual Creativity but Reduces the Collective Diversity of Novel Content* | 随机实验显示生成式 AI 提高个人创作表现，同时降低群体产出的内容多样性。 | 创意写作任务；尚未直接测量事实性判断误差相关性。 | [DOI](https://doi.org/10.1126/sciadv.adn5290) · [PDF](./papers_originals/collective_intelligence_homogeneity/DoshiHauser2024.pdf) |
| `AndersonShahKreminski2024` | Anderson et al. (2024), *Homogenization Effects of Large Language Models on Human Creative Ideation* | 人机创意实验直接观察 LLM 辅助导致的创意收敛。 | 创意构思场景，不能直接外推到政策判断准确率。 | [DOI](https://doi.org/10.1145/3635636.3656204) · [PDF](./papers_originals/collective_intelligence_homogeneity/AndersonShahKreminski2024.pdf) |
| `BommasaniCreelKumarEtAl2022` | Bommasani et al. (2022), *Picking on the Same Person: Does Algorithmic Monoculture Lead to Outcome Homogenization?* | 形式化算法单一化如何让不同决策者产生相关结果，并将局部模型偏差放大为系统风险。 | 重点是算法决策系统；人类对话式搜索需要新增行为环节。 | [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2022/hash/17a234c91f746d9625a75cf8a8731ee2-Abstract-Conference.html) · [PDF](./papers_originals/collective_intelligence_homogeneity/BommasaniCreelKumarEtAl2022.pdf) |
| `StasserTitus1985` | Stasser & Titus (1985), *Pooling of Unshared Information in Group Decision Making* | 隐藏信息范式说明群体讨论会偏向共享信息，独特信息难以进入集体判断。 | 共享信息偏差发生在群体讨论阶段；本项目关注独立研究阶段的共同信息源。 | [DOI](https://doi.org/10.1037/0022-3514.48.6.1467) · 暂无开放原文 |
| `LorenzRauhutSchweitzerHelbing2011` | Lorenz et al. (2011), *How Social Influence Can Undermine the Wisdom of Crowd Effect* | 实验表明社会影响压缩意见多样性，并可能削弱群体智慧。 | 操纵成员间直接社会信息；共享 LLM 属于共同中介来源。 | [DOI](https://doi.org/10.1073/pnas.1008636108) · 暂无开放原文 |
| `BaiVoelkelMuldowneyEtAl2025` | Bai et al. (2025), *LLM-Generated Messages Can Persuade Humans on Policy Issues* | 证明 LLM 生成信息能够改变政策态度，为政治议题上的行为反应提供实验依据。 | 识别说服效应，未识别群体误差相关性或聚合绩效。 | [DOI](https://doi.org/10.1038/s41467-025-61345-5) · [PDF](./papers_originals/collective_intelligence_homogeneity/BaiVoelkelMuldowneyEtAl2025.pdf) |
| `BurtonEtAl2024` | Burton et al. (2024), *How Large Language Models Can Reshape Collective Intelligence* | 系统梳理 LLM 对群体组成、互动、协调、聚合与多样性的潜在影响。 | 综述与研究议程，不能充当本项目的因果证据。 | [DOI](https://doi.org/10.1038/s41562-024-01959-9) · 暂无开放原文 |
| `PescetelliRutherfordRahwan2021` | Pescetelli et al. (2021), *Modularity and Composite Diversity Affect the Collective Gathering of Information Online* | 在线实验说明网络模块化与来源多样性会影响集体信息搜集和最终表现。 | 研究网络搜索结构，尚未引入生成式共同信息源。 | [DOI](https://doi.org/10.1038/s41467-021-23424-1) · [PDF](./papers_originals/collective_intelligence_homogeneity/PescetelliRutherfordRahwan2021.pdf) |
| `KimGargPengGarg2025` | Kim et al. (2025), *Correlated Errors in Large Language Models* | 在 350 余个模型上测量错误相关性，直接支持“模型多样性不能由供应商数量替代”的测量问题。 | 模型层误差结构；转化为群体层效应仍需人机交互实验。 | [PMLR](https://proceedings.mlr.press/v267/kim25e.html) · [PDF](./papers_originals/collective_intelligence_homogeneity/KimGargPengGarg2025.pdf) |
| `AshkinazeEtAl2025` | Ashkinaze et al. (2025), *How AI Ideas Affect the Creativity, Diversity, and Evolution of Human Ideas* | 大型动态实验发现更高 AI 暴露在部分条件下提高集体创意多样性，构成重要反向证据。 | 表明“AI 暴露必然导致同质化”不能成立；效应取决于提示、任务、选择和扩散机制。 | [DOI](https://doi.org/10.1145/3715928.3737481) · [PDF](./papers_originals/collective_intelligence_homogeneity/AshkinazeEtAl2025.pdf) |
| `KleinbergRaghavan2021` | Kleinberg & Raghavan (2021), *Algorithmic Monoculture and Social Welfare* | 理论模型说明多个决策者依赖同一算法时，错误会相关化，个体改进与社会福利可能分离。 | 算法筛选场景；需要把“同一算法”转写为“共享生成信息分布”。 | [DOI](https://doi.org/10.1073/pnas.2018340118) · 暂无开放原文 |

## 3. 意见动力学、社会学习与 ABM 基础

| Key | 文献 | 可用于本项目的组件 | 原文 |
|---|---|---|---|
| `LazerFriedman2007` | Lazer & Friedman (2007), *The Network Structure of Exploration and Exploitation* | 解释高连通网络为何快速收敛并损失长期探索收益，可对应共享模型引发的共同信息暴露。 | [DOI](https://doi.org/10.2189/asqu.52.4.667) · 暂无开放原文 |
| `Zollman2007` | Zollman (2007), *The Communication Structure of Epistemic Communities* | 认识论网络模型显示有限连接有时有助于维持有价值的异质信念。 | [DOI](https://doi.org/10.1086/525605) · 暂无开放原文 |
| `GolubJackson2010` | Golub & Jackson (2010), *Naïve Learning in Social Networks and the Wisdom of Crowds* | 提供网络权重、影响力集中与群体学习有效性的形式条件。 | [DOI](https://doi.org/10.1257/mic.2.1.112) · [PDF](./papers_originals/opinion_dynamics_abm/GolubJackson2010.pdf) |
| `HegselmannKrause2002` | Hegselmann & Krause (2002), *Opinion Dynamics and Bounded Confidence Models* | 提供有界信任、极化、簇形成与共识的基础更新规则。 | [JASSS](https://www.jasss.org/5/3/2.html) · [PDF](./papers_originals/opinion_dynamics_abm/HegselmannKrause2002.pdf) |
| `DeGroot1974` | DeGroot (1974), *Reaching a Consensus* | 提供线性意见平均与影响权重矩阵的基准模型。 | [DOI](https://doi.org/10.1080/01621459.1974.10480137) · 暂无开放原文 |
| `PirolliCard1999` | Pirolli & Card (1999), *Information Foraging* | 支撑用户在成本、信息气味和收益预期下选择查询与追问路径。 | [DOI](https://doi.org/10.1037/0033-295X.106.4.643) · 暂无开放原文 |
| `GrimEtAl2024Juries` | Grim et al. (2024), *The Epistemic Role of Diversity in Juries: An Agent-Based Model* | 直接建模证据多样性、成员异质性与集体裁决质量，可作为群体判断模块的最近邻 ABM。 | [DOI](https://doi.org/10.18564/jasss.5304) · [PDF](./papers_originals/opinion_dynamics_abm/GrimEtAl2024Juries.pdf) |

## 4. LLM 代理与大规模社会仿真

| Key | 文献 | 对可行性的支持及限制 | 原文 |
|---|---|---|---|
| `ArgyleEtAl2023` | Argyle et al. (2023), *Out of One, Many* | 证明条件化语言模型可复现部分群体响应分布；身份条件化也可能把模型偏差包装成群体差异。 | [DOI](https://doi.org/10.1017/pan.2023.2) · [PDF](./papers_originals/llm_social_simulation/ArgyleEtAl2023.pdf) |
| `ParkEtAl2023GenerativeAgents` | Park et al. (2023), *Generative Agents* | 提供记忆、反思、计划和互动架构，支持多轮代理行为。 | [DOI](https://doi.org/10.1145/3586183.3606763) · [PDF](./papers_originals/llm_social_simulation/ParkEtAl2023GenerativeAgents.pdf) |
| `ChuangEtAl2024` | Chuang et al. (2024), *Simulating Opinion Dynamics with Networks of LLM-Based Agents* | 直接展示网络化 LLM 代理的意见更新、共识与极化仿真。 | [ACL](https://aclanthology.org/2024.findings-naacl.211/) · [PDF](./papers_originals/llm_social_simulation/ChuangEtAl2024.pdf) |
| `LiuEtAl2024FakeNews` | Liu et al. (2024), *From Skepticism to Acceptance* | 将 LLM 代理用于虚假新闻态度动力学，支持议题暴露—信念更新的实现路线。 | [IJCAI PDF](https://www.ijcai.org/proceedings/2024/0873.pdf) · [本地 PDF](./papers_originals/llm_social_simulation/LiuEtAl2024FakeNews.pdf) |
| `TangEtAl2025GenSim` | Tang et al. (2025), *GenSim* | 提供通用 LLM 社会仿真平台与可扩展系统结构。 | [ACL](https://aclanthology.org/2025.naacl-demo.15/) · [PDF](./papers_originals/llm_social_simulation/TangEtAl2025GenSim.pdf) |
| `ParkEtAl2024SelfReports` | Park et al. (2024), *Generative Agent Simulations of 1,000 People* | 以真实访谈和自我报告为代理背景，提供人口校准与外部比较思路。 | [arXiv](https://arxiv.org/abs/2411.10109) · [PDF](./papers_originals/llm_social_simulation/ParkEtAl2024SelfReports.pdf) |
| `VezhnevetsEtAl2023Concordia` | Vezhnevets et al. (2023), *Generative Agent-Based Modeling ... Using Concordia* | 提供可复现的生成式 ABM 组件、环境与行动机制。 | [arXiv](https://arxiv.org/abs/2312.03664) · [PDF](./papers_originals/llm_social_simulation/VezhnevetsEtAl2023Concordia.pdf) |
| `PiaoEtAl2025AgentSociety` | Piao et al. (2025), *AgentSociety* | 展示大规模 LLM 代理社会仿真的工程可行性。其社会科学效度仍需独立验证。 | [arXiv](https://arxiv.org/abs/2502.08691) · [PDF](./papers_originals/llm_social_simulation/PiaoEtAl2025AgentSociety.pdf) |
| `ZhangEtAl2025SocioVerse` | Zhang et al. (2025), *SocioVerse* | 展示以大规模用户池条件化社会代理的路线。人口代表性和行为有效性不能由规模自动保证。 | [arXiv](https://arxiv.org/abs/2504.10157) · [PDF](./papers_originals/llm_social_simulation/ZhangEtAl2025SocioVerse.pdf) |

## 5. 仿真效度、偏差与报告规范

| Key | 文献 | 对本项目的约束 | 原文 |
|---|---|---|---|
| `BisbeeEtAl2024` | Bisbee et al. (2024), *Synthetic Replacements for Human Survey Data?* | LLM 可复制均值模式，同时扭曲异质性、相关结构和不确定性；不能直接用合成代理替代人口推断。 | [DOI](https://doi.org/10.1017/pan.2024.5) · [PDF](./papers_originals/simulation_validation/BisbeeEtAl2024.pdf) |
| `WangMorgensternDickerson2025` | Wang et al. (2025), *Large Language Models That Replace Human Participants Can Harmfully Misportray and Flatten Identity Groups* | 说明身份条件化 LLM 会压平群体内部差异，并可能制造表面稳定的群体画像。 | [DOI](https://doi.org/10.1038/s42256-025-00986-z) · [PDF](./papers_originals/simulation_validation/WangMorgensternDickerson2025.pdf) |
| `GrimmEtAl2020ODD` | Grimm et al. (2020), *The ODD Protocol ...* | 要求明确目的、实体、状态变量、过程、调度、初始化、输入数据与子模型，构成本项目的最低报告规范。 | [DOI](https://doi.org/10.18564/jasss.4259) · [PDF](./papers_originals/simulation_validation/GrimmEtAl2020ODD.pdf) |
| `NudoEtAl2025` | Nudo et al. (2025), *Generative Exaggeration in LLM Social Agents* | 检验代理的一致性、夸张、偏差和毒性，提示多轮互动可能累积模型特有偏差。 | [arXiv](https://arxiv.org/abs/2507.00657) · [PDF](./papers_originals/simulation_validation/NudoEtAl2025.pdf) |
| `NeumannDeArteagaFazelpour2026` | Neumann et al. (2026), *Should You Use LLMs to Simulate Opinions?* | 提供意见仿真的质量检查，并强调早期探索、机制敏感性分析与人口预测之间的效度差异。 | [DOI](https://doi.org/10.1609/aaai.v40i46.41254) · [PDF](./papers_originals/simulation_validation/NeumannDeArteagaFazelpour2026.pdf) |

## 6. 对 Paper 1 的累积结论

### 6.1 理论矛盾

共同或高度相似的 AI 信息源可能提高个人层面的平均信息质量，同时提高成员间信息样本和判断误差的相关性。个人改进与群体聚合收益因此可能发生分离。Fügener et al. (2021)、Kleinberg and Raghavan (2021) 与 Kim et al. (2025) 提供了这条逻辑链最强的现有依据。

### 6.2 反向机制

用户条件化生成可能根据成员初始立场、身份与追问路径提供不同证据，使意见分化。Ashkinaze et al. (2025) 的结果也说明 AI 暴露能够在特定结构下增加集体多样性。因此，主张应写成条件性命题：共享模型先验提高潜在输出相关性；实际的人类收敛程度取决于个性化、提示异质性、选择行为、网络扩散和任务结构。

### 6.3 仍然存在的研究缺口

现有研究尚未完成以下单一因果比较：在个体层边际信息质量和平均准确率大致匹配时，外生改变群体成员所获信息及其误差的相关性，并观察群体认知多样性、误差相关性和聚合判断质量。单个政治题无法稳定估计误差相关结构，需要跨多个可验证政策任务重复测量。

### 6.4 ABM 的可行边界

LLM-ABM 可以用于机制探索、尺度扩展和反事实敏感性分析。模型中的核心状态变量应包括初始立场、置信度、信息搜索策略、来源权重、记忆、网络位置、信息样本和任务误差。LLM 负责生成或评估查询响应，意见更新和群体聚合应由透明规则控制。

该仿真不能单独识别真实人口中的因果效应。最低可信路径包括：

1. 用小规模人类实验估计查询、采纳和更新参数；
2. 用独立人类样本验证代理的条件响应分布、组内异质性和跨任务稳定性；
3. 对模型、提示、温度、记忆和网络结构做系统敏感性分析；
4. 按 ODD 协议报告全部代理规则；
5. 将共享人工简报作为非 AI 对照，以检验效应究竟来自共同信息源，还是生成式、交互式与用户条件化机制。

## 7. 当前入库状态

- 已写入主 Bib：41/41。
- 已获取并验证开放 PDF：28/41。
- 暂无开放 PDF：`StasserTitus1985`、`LorenzRauhutSchweitzerHelbing2011`、`BurtonEtAl2024`、`KleinbergRaghavan2021`、`LazerFriedman2007`、`Zollman2007`、`DeGroot1974`、`PirolliCard1999`、`FisherEtAl2025PoliticalDecision`、`TesslerEtAl2024CommonGround`、`HuqClaggettShirado2025`、`SalviEtAl2025ConversationalPersuasion`、`LinEtAl2025PersuadingVoters`。
- 预印本：`ParkEtAl2024SelfReports`、`VezhnevetsEtAl2023Concordia`、`PiaoEtAl2025AgentSociety`、`ZhangEtAl2025SocioVerse`、`NudoEtAl2025`。
- 关键实验定位：`FugenerGrahlGuptaKetter2021`。
- 关键模型输出基准：`JiangEtAl2025ArtificialHivemind`。
- 关键反向证据：`AshkinazeEtAl2025`。

## 8. 补充检索：政治态度、群体共识与 LLM 说服

本节记录随后针对“政治态度、价值判断或政策偏好”补充检索的 8 篇近邻研究。前三篇已在上文入库；其余五篇于本次增量加入主 Bib。

| Key | 文献 | 主要证据 | 与本项目的边界 |
|---|---|---|---|
| `FisherEtAl2025PoliticalDecision` | Fisher et al. (2025), *Biased LLMs Can Influence Political Decision-Making* | 两项交互实验随机分配自由对话中的自由派偏向、保守派偏向和中性 LLM。参与者的政治意见与资源分配会向模型偏向移动，模型偏向与参与者原有党派立场相反时仍可观察到影响。 | 证明共同偏向的模型能推动个人态度；没有比较同一群体成员的回答相关性，也没有测量群体分布。 |
| `TesslerEtAl2024CommonGround` | Tessler et al. (2024), *AI Can Help Humans Find Common Ground in Democratic Deliberation* | Habermas Machine 综合小组成员的个人意见和批评，生成并迭代群体陈述。英国超过 5,000 名参与者的实验显示，AI 调解提高陈述认可度并降低组内分歧，同时保留部分少数意见。 | 直接说明“收敛”可能代表有效调解。评价危害需要同时测量观点覆盖、少数意见保留和判断质量。 |
| `HuqClaggettShirado2025` | Huq et al. (2025), *AI-Mediated Communication Reshapes Social Structure in Opinion-Diverse Groups* | 预注册在线实验包含 557 人、60 个讨论场次。个体立场条件化建议提高同类立场聚集；纳入群体成员视角的关系型建议形成更异质的联系。 | 为“个性化导致分化”的竞争机制提供直接证据。当前为预印本；研究对象是群际连边和沟通结构。 |
| `SalviEtAl2025ConversationalPersuasion` | Salvi et al. (2025), *On the Conversational Persuasiveness of GPT-4* | 900 人参与预注册的 2×2×3 辩论实验，操纵人类或 GPT-4 对手、是否获得人口统计信息以及议题强度。个性化 GPT-4 的说服力高于人类对手。 | 说明用户条件化会改变说服效力；一对一辩论没有群体层因变量。 |
| `LinEtAl2025PersuadingVoters` | Lin et al. (2025), *Persuading Voters Using Human–Artificial Intelligence Dialogues* | 美国、加拿大和波兰的预注册实验随机分配参与者与支持不同候选人的 AI 对话，观察到候选人偏好变化；马萨诸塞州公投议题也出现政策支持变化。论文同时发现部分生成事实不准确。 | 最接近真实选举态度，但仍估计个人平均处理效应，没有检验共享模型是否压缩群体差异。 |
| `BaiVoelkelMuldowneyEtAl2025` | Bai et al. (2025), *LLM-Generated Messages Can Persuade Humans on Policy Issues* | 多项随机实验显示 LLM 生成信息可以改变公共政策态度。 | 已入库。说明政策态度可被影响；没有群体误差相关性和聚合结果。 |
| `FugenerGrahlGuptaKetter2021` | Fügener et al. (2021), *Will Humans-in-the-Loop Become Borgs?* | AI 建议可能提高个人表现，同时提高成员选择的相关性并削弱较大群体中的群体智慧；个性化建议可缓解。 | 已入库。提供最接近的“个人收益—群体损失”机制，政治态度外推仍需新证据。 |
| `JiangEtAl2025ArtificialHivemind` | Jiang et al. (2025), *Artificial Hivemind* | 测量多个语言模型在开放式生成中的输出同质性。 | 已入库。提供模型输出层测量，不识别人类态度与集体结果。 |

### 本轮检索后的判断

现有研究分别证明了三件事：

1. LLM 对话可以改变政治与政策态度；
2. AI 调解可以促成有价值的共识；
3. 个体条件化建议也可能加剧立场聚集。

仍未发现直接完成以下比较的研究：随机分配群体成员使用同一模型或多样化模型，在个体平均信息质量大致匹配时，比较成员间信息相关性、态度分布和群体判断结果。因此，本轮文献收缩了因果主张的范围，也保留了原问题的识别空间。研究问题、假设和模型仍处于待定状态。

## 9. 补充入库：信息暴露、信念、态度与意见动力学（2026-08-01）

| Key | 文献 | 构念与方法贡献 | 使用边界 | 原文 |
|---|---|---|---|---|
| `NyhanEtAl2023` | Nyhan et al. (2023), *Like-Minded Sources on Facebook Are Prevalent but Not Polarizing* | 将同立场来源暴露、平台互动、事实性信念和政治态度分开测量；大规模现场实验显示减少同立场暴露没有可测量地改变八项预注册态度结果。 | 研究 Facebook 信息流，不包含 LLM，也不检验群体智慧；其价值在于构念分层和反对“暴露必然改变信念或态度”的自动因果链。 | [DOI](https://doi.org/10.1038/s41586-023-06297-w) · [PDF](./papers_originals/collective_intelligence_homogeneity/NyhanEtAl2023.pdf) |
| `PerraRocha2019` | Perra & Rocha (2019), *Modelling Opinion Dynamics in the Age of Algorithmic Personalisation* | 将代理状态设为 A/B 二元意见，并按时间线中 A/B 内容比例随机更新；比较随机、时间排序、偏好排序和集中助推对意见分布、极化与回音室的影响。 | `opinion` 是抽象状态，论文没有将其经验校准为事实信念或具体政策态度；可借用更新机制，不能直接借用构念含义。 | [DOI](https://doi.org/10.1038/s41598-019-43830-2) · [PDF](./papers_originals/opinion_dynamics_abm/PerraRocha2019.pdf) |

详细的构念证据与 Paper 1 使用边界见 `belief_attitude_opinion_construct_evidence_2026-08-01.md`。
