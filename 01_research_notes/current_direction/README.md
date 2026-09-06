# 当前研究笔记目录

当前研究以 [现行英文 RP](../../00_current_baseline/Paper1_Formal_RP_EN.tex) 为准：AI 如何改变人类群体的信息获取与意见形成。

## 新增方法与技术笔记

- [AnyLogic 研究与 LLM 集成笔记](AnyLogic_studies_and_LLM_integration.md)：v0.1.0（2026-09-06）；保存四项社会模拟研究的环境、规则及证据限制，补充 AnyLogic 与 LLM 的公开连接方法和待验证方案。
- [混合 ABM 架构设计](../../04_code/implementation/ARCHITECTURE_DESIGN.md)：模块、三函数接口、AnyLogic 备选方案及架构版本记录。

上述技术探索不代表正式研究已选定引擎或完成实验。

## 以下为迁移保留的历史说明

以下文字及 E 盘路径反映原目录的历史状态。“当前”“核心题目”等称谓仅适用于原记录日期，不作为 ABM_INFO 现行研究基准。保留原文供追溯。

### 第一篇：算法权威与信息校准（历史）

## 2026-08-24 重构方向

当前新增的正式研究计划为：

- `E:\Info_AI\主Agent\文章项目\01_算法权威与信息校准\Paper1_AI群体信息获取与意见形成_正式RP_2026-08-24.md`

该RP固定以下口径：

- 总主题：**AI如何改变人类群体的信息获取与意见形成？**
- 核心研究问题：**大语言模型如何改变群体意见分布？**
- 群体智慧仅作为可验证判断任务的补充理论与测量来源。

原“算法权威与信息校准”稿与“群体智慧方向”文件继续保留为历史基准，不由新RP改写。

## 文章身份

这是用户所说的“第一篇文章”。

核心题目：

**算法权威与信息校准：生成式 AI 如何改变额外搜索与信念更新**

英文标题建议：

**Algorithmic Authority and Information Calibration: How Generative AI Changes Additional Search and Belief Updating under Uncertainty**

注意：早期材料中曾使用 **Double Bayesian Distortion / 双重贝叶斯偏离** 作为标题或核心框架，但当前版本已经改为“算法权威与信息校准”。`double Bayesian distortion` 最多作为可能的经验结果或后验偏离模式出现，不能作为当前 PPT 或讲稿的主标题。

## 核心问题

在初始 summary 内容相同、额外搜索成本相同的条件下，AI 来源标签是否改变用户对额外证据价值、主观信息获得感、epistemic ownership 和后续信念更新的判断？

## 核心机制

1. 信息呈现阶段：AI summary 将多个原始证据压缩为一个总结式回答，改变用户对当前信息充分性的判断。
2. 来源标签阶段：同一段 summary 被标注为 AI 生成时，可能改变用户对额外证据价值和搜索必要性的判断。
3. 后验更新阶段：用户的 reported posterior 与 conditional / full-information Bayesian benchmark 之间可能出现不同类型的偏离。
4. 主观校准阶段：用户的 objective performance 与 subjective mastery / epistemic ownership 可能发生错配。

## 关键设计

- same-summary source-label design
- no-summary control / unlabeled summary / AI-labeled summary
- representative summary / incomplete summary
- 固定证据库
- likelihood ratio
- conditional Bayesian deviation
- full-information deviation

## 主要材料入口

- 当前基准稿：`E:\Info_AI\主Agent\文章项目\01_算法权威与信息校准\当前第一章_算法权威与信息校准_基准稿.md`
- 文献批判备忘：`E:\Info_AI\主Agent\文章项目\01_算法权威与信息校准\文献批判靶子_自动化偏差与信息校准_2026-07-05.md`
- 英文表格版：`E:\Info_AI\主Agent\文章项目\01_算法权威与信息校准\Literature_Targets_Automation_Bias_and_Information_Calibration_2026-07-05.md`
- `E:\Info_AI\修改版本.md`
- `E:\Info_AI\dd636486-c2c3-485e-a8b5-0ec083e806dd_修改版｜算法权威与信息校准：生成式_AI_如何改变额外搜索与信念更新.pdf`
- `E:\Info_AI\defense_project\latex\main.tex`
- `E:\Info_AI\defense_project\latex\sections\01_intro_lit_review.tex`
- `E:\Info_AI\defense_project\latex\sections\02_framework_questions_hypotheses.tex`
- `E:\Info_AI\defense_project\latex\sections\03_research_design_and_studies.tex`
- `E:\Info_AI\defense_project\latex\sections\04_empirics_contributions_governance.tex`

## 已有答辩 PPT

已有一套较完整的英文 20 页答辩 PPT，但其标题和部分内容是旧口径。可以参考美术风格和版式节奏，不要直接沿用内容：

- `E:\Info_AI\outputs\019e9e26-a704-79e1-8478-8a7f65a6f8d3\presentations\defense-project\output\algorithmic-authority-defense-deck.pptx`
- `E:\Info_AI\outputs\019e9e26-a704-79e1-8478-8a7f65a6f8d3\presentations\defense-project\output\speech_script_en.md`
- `E:\Info_AI\outputs\019e9e26-a704-79e1-8478-8a7f65a6f8d3\presentations\defense-project\preview\contact-sheet.png`

2026-07-01 新生成的中文 12 页版本位于：

- `E:\Info_AI\主Agent\答辩材料\第一章_双重贝叶斯偏离_PPT初版.pptx`

该中文版本是压缩草稿，且仍有旧口径。后续正式 PPT 应以本目录的“当前第一章_算法权威与信息校准_基准稿.md”为内容基准，以“算法权威与信息校准”为主线重做内容。
