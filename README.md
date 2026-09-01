# ABM_INFO

本目录是 Paper 1 后续研究与实现的工作目录。

## 当前研究主线

总主题：**AI 如何改变人类群体的信息获取与意见形成？**

核心研究问题：

> How do large language models change group opinion distributions?

三个子问题构成同一过程链：

1. SQ1：LLM 如何改变群体中的信息暴露与信息传播？
2. SQ2：信息暴露与传播的变化如何影响个体意见更新和群体意见演化？
3. SQ3：如果上述群体意见演化现象存在，LLM 侧的技术调整能否抑制该现象？

当前方法为混合 ABM。规则代理与 LLM 代理共享 `f_message`、`f_selection` 和 `f_update` 三个接口。LLM 在研究中有两个需要分开的角色：

- 信息来源：向群体提供政策信息；
- LLM agent：依据真人数据构造的资料模拟部分成员的表达和意见更新。

SQ1 的基准比较是传统搜索引擎信息获取与 LLM 信息获取。共享人工简报只用于检验共同信息输入这一替代解释。SQ3 的候选干预是来自不同模型家族或供应商的独立随机路由，且只改变信息来源模型。

## 当前基准

- `00_current_baseline/Paper1_Formal_RP_EN.tex`：迁移时的现行英文 LaTeX，后续研究内容和方法实现以此为准。
- `00_current_baseline/Paper1_Formal_RP_CN_2026-08-24.md`：中文正式研究计划，用于追溯构念与研究逻辑。
- `00_current_baseline/Paper1_Formal_RP_EN_2026-08-25.md`：英文 Markdown 基准，用于对照。
- `00_current_baseline/Paper1_content_changes_2026-08-30.md`：最近一次研究内容修订记录。
- `00_current_baseline/Paper1_latest_available_PDF_2026-08-30.pdf`：迁移时可用的最新 PDF。该 PDF 早于 2026-08-31 的最终英文语言修订，不能替代现行 `.tex`。

迁移时源文件与目标 `.tex` 的 SHA-256 均为：

```text
7CEE0A17AB779D12628BD6D9FC27C626DD76A3BA7E3C9411F11BD768EFD08059
```

## 目录结构

```text
ABM_INFO/
├── 00_current_baseline/              # 当前 RP 与变更记录
├── 01_research_notes/                # 当前研究方向的理论、方法与文献笔记
├── 02_literature/                    # 文献索引、BibTeX 与本地论文
├── 03_presentations/                 # 原始 PPT、英文稿与历史展示版本
├── 04_code/                          # dashboard 源码、HiSim 参考源码与辅助脚本
├── 05_reviews_and_revision_history/  # 对齐审查、diff 与历史快照
├── 99_historical_directions/         # 已退出当前主线的旧 Paper 1 方向
├── tools/                            # 资料收集脚本
├── SOURCE_MANIFEST.csv               # 每个复制文件的原始路径与哈希
└── PROJECT_INVENTORY.csv              # 目标目录的文件清单与哈希
```

## 使用边界

- `99_historical_directions` 中的算法权威、搜索停止和群体智慧稿均为历史材料，不是现行 RP。
- `01_research_notes/current_direction` 中仍可能包含候选设计。候选不因迁移而自动变成已确认方案。
- 当前分析单位是具有信息传播网络的统计群体，不是正式组织团队。
- `opinion` 指具体公共政策议题上的立场，不等同于事实信念、稳定意识形态或判断准确率。
- 具体政策场景、目标人群、数据来源、网络、主结果、空消息更新和部分实现参数仍待确定。
- ABM 结果属于经验约束下的模拟，不能在缺少真实群体轨迹验证时表述为现实社会的长期定量预测。

## 本次整理范围

已纳入正式稿、研究笔记、相关文献、PPT、方法审查、修订记录、dashboard 源码和 HiSim 参考源码。没有迁移 `node_modules`、Git 内部目录、构建输出、LaTeX 编译中间文件、Python 缓存、Office 临时锁文件或 PPT 渲染缓存。这些文件均可由源代码或正式文件重新生成。

本目录尚未初始化为 Git 仓库。
