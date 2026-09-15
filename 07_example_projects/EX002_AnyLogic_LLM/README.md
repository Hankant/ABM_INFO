# EX002 · AnyLogic 与 LLM 集成候选

版本：0.1.0；更新：2026-09-15；状态：候选集合，尚未运行。

## 已有材料

[AnyLogic 研究与 LLM 集成笔记](../../01_research_notes/current_direction/AnyLogic_studies_and_LLM_integration.md)保存研究来源、方法摘录、接口候选和证据缺口。其检索日期为 2026-09-06，本次整理没有重新验证外部仓库的更新状态。

| 候选 | 已有笔记中的用途 | 下一项工程核验 |
| --- | --- | --- |
| WSC 2023 对话式能源仿真 | LLM → Python 场景 → CSV → AnyLogic | 区分底层框架与论文完整实现；查找场景生成入口 |
| Pypeline / ChatGPT Bridge | AnyLogic 调 Python、查询结果 | 库版本、接口和兼容环境 |
| Alpyne | Python 读取 AnyLogic 状态、发送动作 | RL experiment 导出、暂停和轮次同步 |
| 自建 HTTP/JSON | 本项目工程备选 | 仅为提案，不能登记为外部样例已实现 |

## 与正式架构的关系

参见 [架构设计第 12 节](../../04_code/implementation/ARCHITECTURE_DESIGN.md#12-仿真引擎策略与-anylogicanalogic备选架构)。是否采用某个后端仍需环境、固定响应测试、异常处理和实验一致性验证。当前没有在线 LLM 闭环运行记录。

选定具体实现后建立独立样例档案，使用 [模板](../templates/EXAMPLE_TEMPLATE.md)，登记源码版本与复现实验；这份候选索引继续保留来源关系。

## 版本记录

- 0.1.0（2026-09-15）：建立候选入口并链接既有笔记。
