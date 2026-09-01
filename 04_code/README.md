# 代码材料说明

## `paper1-reconstruction-dashboard`

Paper 1 既有研究管理界面源码。已排除 `node_modules`、构建输出和本地 Git 元数据。依赖可依据 `package.json` 与锁文件重新安装。

## `third_party_reference/HiSim_source_audit`

HiSim/AgentVerse 的本地参考源码，用于检查混合 LLM-agent/规则-agent 架构与意见更新函数。该目录是第三方参考实现，不是本项目原创代码。原许可证和 README 已保留。

## `research_helpers`

既有 PDF 提取和 HiSim 文本审查辅助文件。

## 后续实现

Paper 1 的正式模拟器尚未在本次迁移中创建。后续代码应放入新的 `implementation` 子目录，并保持三函数接口、两类 LLM 角色、人类校准数据与模拟输出的分离。
