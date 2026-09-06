# 代码材料说明

## `paper1-reconstruction-dashboard`

Paper 1 既有研究管理界面源码。已排除 `node_modules`、构建输出和本地 Git 元数据。依赖可依据 `package.json` 与锁文件重新安装。

## `third_party_reference/HiSim_source_audit`

HiSim/AgentVerse 的本地参考源码，用于检查混合 LLM-agent/规则-agent 架构与意见更新函数。该目录是第三方参考实现，不是本项目原创代码。原许可证和 README 已保留。

## `research_helpers`

既有 PDF 提取和 HiSim 文本审查辅助文件。

## 后续实现

`implementation` 已包含 [ARCHITECTURE_DESIGN.md](implementation/ARCHITECTURE_DESIGN.md)，用于记录混合 ABM 的模块、接口、AnyLogic 备选方案与架构版本。正式模拟器实现应放在该目录，并保持三函数接口、两类 LLM 角色、人类校准数据与模拟输出的分离。

相关文献与工具证据见 [AnyLogic 研究与 LLM 集成笔记](../01_research_notes/current_direction/AnyLogic_studies_and_LLM_integration.md)（v0.1.0，2026-09-06）。Pypeline、Alpyne 等方案目前处于技术探索阶段，尚未执行集成实验。
