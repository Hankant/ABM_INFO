# Reference Materials (文献库)

> 答辩项目所有文献资料统一管理入口。

---

## 一、文献库结构（三层）

文献库分为 **bib 索引层**、**总结/分类文档层**、**论文原文献层**。三者通过 BibTeX key 关联。

```
defense_project/
├── latex/
│   ├── references.bib           # ⭐ bib 索引层（与 LaTeX 共用，natbib 引用）
│   ├── main.tex
│   ├── sections/*.tex
│   └── 04_research_plan.tex
│
└── reference_materials/         # 本目录：总结文档 + 原文献
    ├── README.md                # 本文件（结构 + 入库流程）
    │
    ├── paper_research_summaries.md       # 核心 20 篇深度综述（研究方法/问题/理论/发现/Gap）
    ├── self_vs_ai_literature_review_2026-06-29.md   # Self vs AI 文献库（22 篇新文献）
    ├── to_collect.md                     # 与 references.bib 对应的待入库清单
    ├── verified_links.md                 # 已核对过的官方/原始链接（含可疑条目的核查结果）
    ├── citation_health_report_2026-06-29.md          # 引用核查健康报告
    │
    ├── ai_human_interaction_literature_map_2026-06-15.md
    ├── ai_behavioral_econ_review_framework_cn_2026-06-15.md
    ├── ai_20_papers_gap_logic_progression_cn_2026-06-15.md
    ├── ai_behavior_expansion_notes_2026-06-15.md
    │
    ├── knowledge_graph/        # ⭐⭐ 机器可读导出（供其他 agent 构建知识图谱）
    │   ├── README.md           #   Schema 与构建指南
    │   ├── papers.json         #   68 篇完整元数据
    │   ├── papers.csv          #   扁平表格（pandas 可读）
    │   ├── concepts.json       #   概念 → 论文映射（184 个概念）
    │   ├── categories.json     #   类别 → 论文映射（10 个类别）
    │   ├── citations_in_thesis.csv    #   论文 → 引用位置
    │   └── edges_cocitation.csv       #   共被引边（thesis 内部）
    │
    └── papers_originals/                # ⭐ 论文原文献层（按主题分子目录）
        ├── foundational_theory/          #  基础理论（Bayesian Persuasion / RI / EWA）
        ├── information_acquisition/      #  信息获取与信念更新
        ├── algorithms_trust_hci/         #  算法信任 / HCI / 反算法厌恶
        ├── recommender_genai/            #  推荐系统与生成式 AI
        ├── narrative_epistemic/          #  叙事、心智代理、医疗 AI
        ├── newly_added_candidates/       #  新增候选引用
        ├── advice_taking/                #  2026-06-29 批次
        ├── self_serving_attribution/     #  2026-06-29 批次
        ├── overconfidence_control/       #  2026-06-29 批次
        ├── algorithm_aversion/           #  2026-06-29 批次
        └── _unverified/                  #  ⛔ 核查失败 / 无法定位 / 暂存
```

---

### Paper 2 / EWA 可点击子集合（2026-08-03）

- [中文总结与原文导航](../../主Agent/文章项目/02_AI授权_EWA/Paper2_EWA_参考文献导航.md)
- [批次状态清单](./paper2_ewa/manifest.csv)
- [批次入库记录](./paper2_ewa/batch_2026-08-03_summary.md)
- [本地 PDF 目录](./papers_originals/paper2_ewa/)

本批覆盖 50 个唯一 DOI，12 篇已有本地 PDF，其余条目保留 DOI/出版社入口。原 Paper 2 Markdown 的参考文献行已可直接跳转到中文卡片与原文。

---

## 二、入库流程（每次拿到新摘要时执行）

> 触发条件：你给我一段文献摘要 / 标题 / 作者 / DOI / 链接，要求"入库"。

```
                       ┌─────────────────────────────┐
                       │ 1. 核查存在性              │
                       │   python citation_checker.py│
                       │   → CrossRef / S2 / OpenAlex│
                       └──────────────┬──────────────┘
                                      │ 状态
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
        verified (≥2)         suspicious (1)         not_found (0)
        → 入正式子目录        → 人工二次核查           → _unverified/
                                若通过 → 入正式
                                若失败 → _unverified/
                                      │
                                      ▼
                       ┌─────────────────────────────┐
                       │ 2. 加入 references.bib       │
                       │   • key 必须唯一、与正文一致 │
                       │   • DOI/eprint 必填          │
                       │   • 字段完整（author/year/journal│
                       │     /volume/pages 或等价项）  │
                       └──────────────┬──────────────┘
                                      │
                                      ▼
                       ┌─────────────────────────────┐
                       │ 3. 查找 / 下载原文献 PDF    │
                       │   • 优先 OA（arXiv / 期刊官网）│
                       │   • DOI 解析                │
                       │   • 备份到 papers_originals/ │
                       │     对应主题子目录            │
                       │   • 文件命名: <key>.pdf      │
                       └─────────────────────────────┘
```

### 关键约定

- **bib key 与 PDF 文件名一致**：例如 `KamenicaGentzkow2011.pdf` 对应 `references.bib` 中的 `@article{KamenicaGentzkow2011,...}`。
- **`_unverified/` 是隔离区**：核查失败或付费墙无法下载的，先入此目录附 `.note.txt` 说明原因；不要直接进主题子目录。
- **更新三个索引文件**：
  - `references.bib`（机器可读，LaTeX 直接读）
  - `to_collect.md`（人类可读，与 bib 一一对应）
  - `verified_links.md`（可疑/年份未来的条目，把官方原始链接写在这里作为佐证）
- **如果用户在 `04_research_plan.tex` 中新增 `\cite{...}`** 而 bib 缺失，需要立即补 bib 条目，避免编译失败。

---

## 三、常用命令

### 核查全部 bib 条目
```bash
PYTHONIOENCODING=utf-8 py -3 -u \
  "C:/Users/69596/.claude/skills/claude-skill-citation-checker/scripts/citation_checker.py" \
  "e:/Info_AI/defense_project/latex/references.bib"
```

### 核查并输出 JSON（便于脚本处理）
```bash
PYTHONIOENCODING=utf-8 py -3 -u \
  ".../citation_checker.py" "e:/Info_AI/defense_project/latex/references.bib" --json \
  > /tmp/cite_report.json
```

### 找出 LaTeX 中引用了但 bib 缺失的 key
```bash
# 提取 \cite{...} 的 key 列表
grep -ohE '\\cite[a-z]*\{[^}]+\}' \
  e:/Info_AI/defense_project/latex/sections/*.tex \
  | sed -E 's/\\cite[a-z]*\{//; s/\}//' \
  | tr ',' '\n' | sort -u > /tmp/cited_keys.txt
```

---

## 四、当前状态（动态更新）

> 索引重建：2026-08-01（在 2026-07-29 的 39 条批次基础上，新增信息暴露—信念—态度与意见动力学核心文献 2 条）。
>
> 最近一次全库 citation checker 快照：2026-07-06；下表中的 verified/suspicious 数量仍对应当时的 79 条基线。

| 项目 | 数量 |
|------|------|
| `references.bib` 条目总数 | **166** |
| ✅ Verified (≥2 sources) | **48***（2026-07-06 全库快照；2026-07-29 新增 39 条另经官方来源交叉核验） |
| ⚠️ Suspicious (1 source) | **30***（2026-07-06 全库快照） |
| ❌ Not found (0 source) | **0**\* |
| 已下载 PDF | **49** |
| 🚩 红旗告警 | **0**（全部修复） |
| 类别 | **15** |
| 唯一概念标签 | **302** |
| 在 thesis 中被引用 | **29** |

\* 第一轮运行（无 API 限流）测得的稳定值。后续因为 Semantic Scholar 限流，verified/suspicious 数字有较大波动。**not_found 始终为 0** 是核心不变信号。

### 基线 PDF 示例（10 篇；完整 38 篇清单见 `knowledge_graph/papers.json`）

```
Vaswani2017 (recommender_genai)
Brown2020 (recommender_genai)
Ouyang2022 (recommender_genai)
BommasaniEtAl2021 (recommender_genai)
Bender2021 (algorithms_trust_hci)
QiPan2026 (narrative_epistemic)
Shanahan2024 (narrative_epistemic)
HicksHumphriesSlater2024 (algorithms_trust_hci)
VodrahalliEtAl2021 (algorithms_trust_hci)
PrahlVanSwol2017 (algorithm_aversion)
```

\* 第一轮运行（无 API 限流）测得的稳定值。后续两次运行因为 Semantic Scholar 限流，verified/suspicious 数字有较大波动（17/30/2 → 3/42/4），但 **not_found 始终为 0**，说明无编造文献。

### 🚩 红旗告警（1 处未修复，2 处已修复）

| Bib key | 状态 | 说明 |
|---------|------|------|
| ~~`BommasaniEtAl2021`~~ | ✅ **已修复** | 改成前 10 位作者，去掉 "and others" 占位符（详见 `verified_links.md`）|
| ~~`JiEtAl2023`~~ | ✅ **已修复** | 去掉 "and others" 占位符，保留前 10 位作者（详见 `verified_links.md`）|
| `PayneBettmanJohnson1993` | ⚠️ **误报保留** | chimeric 警告是 CrossRef 与 bib 作者名格式差异（full vs initials）导致。真实文献，字段无误。 |
| `QiPan2026` | ⚠️ **误报保留** | 2026 未来年份 + 单源命中。Frontiers DOI 含 2025 是正常模式（DOI 在 2025 分配，期刊卷号 2026）。 |

### ⚠️ Suspicious 列表（单源命中，标题 100% 匹配）

下列 18 条均"标题 100% 匹配，仅 1 个数据库返回"，绝大多数是真实的经典文献。第一轮运行的稳定快照：

```
ParasuramanRiley1997, LeeSee2004, Dietvorst2015, Brown2020,
CaplinDean2015, PayneBettmanJohnson1993, LordRossLepper1979,
ReevesNass1996, Waytz2010, Bender2021, QiPan2026,
BommasaniEtAl2021, Gabaix2019, Grether1980,
KahnemanTversky1973, PuringtonEtAl2017, SundarNass2000,
WingerterStraubSchweitzer2025
```

### ⚠️ 重要：citation checker 的非确定性

多次运行同一份 bib，verified/suspicious/not_found 的数字会有较大波动：

| 运行 | Verified | Suspicious | Not found |
|------|----------|------------|-----------|
| 第 1 轮（fresh）| 31 | 18 | 0 |
| 第 2 轮 | 17 | 30 | 2 |
| 第 3 轮 | 3 | 42 | 4 |

**核心结论**：**not_found 始终 = 0**，因此本项目 bib 中不存在 AI 编造的虚假文献。  
但 verified/suspicious 的边界会因为 Semantic Scholar 的限流（每 5 分钟 100 次）而漂移。  
**推荐做法**：以**第一轮**（或间隔 5 分钟重跑后）测得的 verified 为准；suspicious 列表中的项目直接看 DOI 即可确认。

> 完整报告归档：`/tmp/cc.out`（首轮）、`/tmp/cc2.out`（二轮）、`/tmp/cc3.out`（三轮）。
