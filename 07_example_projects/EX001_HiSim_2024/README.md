# EX001 · HiSim 2024

版本：0.1.0；更新：2026-09-15。

## 文献与材料入口

- 文献标识：2024.findings-acl.285；[出版页面](https://aclanthology.org/2024.findings-acl.285/)（公开入口，本次目录整理未重新联网核验）。
- [本地 PDF 原文](../../02_literature/user_supplied_originals/MouEtAl2024_HiSim_2024.findings-acl.285.pdf)：仅本地保存，不随公开库同步。
- [方法拆解](../../01_research_notes/current_direction/Paper1_HiSim混合ABM方法拆解_2026-08-25.md)。
- [交互知识图谱](../../01_research_notes/literature_knowledge_graphs/hisim-2024-abm-knowledge-graph.html) · [在线图谱](https://hankant.github.io/ABM_INFO/)。
- [第三方参考源码](../../04_code/third_party_reference/HiSim_source_audit/)：原 README、作者与许可证保留在该目录。
- [本项目架构设计](../../04_code/implementation/ARCHITECTURE_DESIGN.md)：用于对照，不视为 HiSim 原始设计。

## 原文核对

2026-09-15 对以下两个文件实际计算 SHA-256，结果一致：

- 根目录用户新放入文件：`2024.findings-acl.285 (1).pdf`。
- 已有归档文件：`02_literature/user_supplied_originals/MouEtAl2024_HiSim_2024.findings-acl.285.pdf`。

```text
9F12D10B60D363F79E226D8606516C6BED6AA9DFBA4D7AE67D96BBE50AA681D2
```

因此使用已有归档文件作为本地阅读入口；根目录副本保持原样，未删除或移动。

## 工程设计与复现任务

已有方法拆解和源码作为分析材料。后续补齐下表时，应引用源码文件/行号或论文页码；本次只建立管理结构。

| 项目 | 当前材料或状态 | 后续记录 |
| --- | --- | --- |
| 智能体、环境、状态与更新机制 | 方法拆解笔记已有入口 | 逐项关联代码类和函数 |
| 调度与信息流 | 待本库形成完整代码调用顺序 | 初始化、每轮顺序、结束条件 |
| 函数与参数 | 待逐项核验 | 输入、输出、公式、参数依据、异常行为 |
| 源码版本 | 本地目录存在 | 上游 URL、commit/tag、是否有本地改动 |
| 环境 | 尚未登记可运行环境 | Python/依赖版本、安装方式、服务需求 |
| 最小运行 | 本库无运行证据 | 命令、配置、种子、日志和输出路径 |
| 结果复现 | 未验证 | 原论文目标、复现数值、差异及解释 |

借鉴评审按 `f_message`、`f_selection`、`f_update` 记录；特别核查信息来源 LLM 与模拟人的 LLM 是否承担不同职责。样例的状态、参数和更新规则不会因入库自动成为本项目设定。

## 版本记录

- 0.1.0（2026-09-15）：登记现有材料、PDF 重复核对结果和复现待办。
