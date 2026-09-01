# PDF 归档清单（仅清单，未执行文件移动）

> 生成日期：2026-08-17。本次遍历全项目，检测到文献 PDF 散落在 3 处（标准目录 `papers_originals/` 之外）：
> 1. 项目根目录 `behavioral_economics_belief_search_literature/pdf/`（5 个文件名与内容不符）
> 2. `tmp/`（正确内容 PDF 待归档 + 损坏文件 + 重复文件）
> 3. 项目根目录散落的一份论文修改稿
>
> 按用户要求，本文件**只列清单，不动任何文件**。待确认后再执行移动 / 删除 / 重下。

---

## 一、需重新下载的 PDF（文件名 ≠ 实际内容，5 个）

来源：`behavioral_economics_belief_search_literature/pdf/`。这 5 个文件的文件名声称是某一篇论文，但打开后实际内容是另一篇，属于历史下载错误。对应 bib 条目已入库，但 `note` 已标记 `mislabeled — needs re-download`。

| # | 当前文件（错误） | 文件名声称的论文（应下载） | 实际内容（误下） | 目标 DOI / 位置 |
|---|---|---|---|---|
| 1 | `2006_Gabaix_Costly_Information_Acquisition.pdf` | Gabaix et al. (2006), AER 96(4):1043–1068 | Hoff & Stiglitz (2005), NBER "Creation of the Rule of Law" | `10.1257/aer.96.4.1043` |
| 2 | `2011_Caplin_Search_and_Satisficing.pdf` | Caplin, Dean & Martin (2011), AER 101(7):2899–2922 | Chetty et al., NBER | `10.1257/aer.101.7.2899` |
| 3 | `2019_Fryer_Updating_Beliefs.pdf` | Fryer, Harms & Jackson (2013), NBER w19114 | Stanley & Doucouliagos, IZA | `10.3386/w19114` |
| 4 | `2023_Haaland_Designing_Information_Provision_Experiments.pdf` | Haaland, Roth & Wohlfart (2023), JEL 61(1):3–40 | Agan / Doleac / Harvey, NBER | `10.1257/jel.20211658` |
| 5 | `2024_Graeber_Stories_Statistics_and_Memory.pdf` | Graeber, Roth & Zimmermann (2024), QJE 139(4):2181–2225 | Kumar et al., NBER | `10.1093/qje/qjae020` |

**建议动作**：重新下载这 5 篇的正确版本；误下的 5 篇内容如仍需保留，先单独归类到 `papers_originals/` 对应主题，否则删除。

---

## 二、内容正确、待归档到 `papers_originals/` 的 PDF

这些 PDF 内容已核验正确，只是还躺在 `tmp/` 里，建议移动到标准三层的第 3 层。

| # | 当前文件 | 实际论文 | 目标目录（建议） |
|---|---|---|---|
| 1 | `tmp/hyndman_hose.pdf` | Hyndman, Özbay, Schotter & Ehrblatt (2012), JEEA 10(3):573–604（内容已确认） | `papers_originals/information_acquisition/HyndmanOzbaySchotterEhrblatt2012.pdf` |
| 2 | `tmp/pdfs/Qin_2025_AI_Aversion_Appreciation.pdf` | Qin et al. (2025), Psychological Bulletin 151(5):580–599（内容已确认） | `papers_originals/algorithm_aversion/QinEtAl2025.pdf` |

> 注：目标目录 `information_acquisition/` 在 `papers_originals/` 下尚不存在，需新建。

---

## 三、损坏文件（建议删除）

| # | 文件 | 问题 |
|---|---|---|
| 1 | `tmp/hyndman_ter_vak.pdf` | 仅 12 KB，实际是 HTML 而非 PDF，无法解析 |

---

## 四、重复 / 冗余 PDF（建议去重，保留 1 份）

| # | 文件 | 说明 | 保留版本 |
|---|---|---|---|
| 1 | `tmp/camerer_ho_1999.pdf` | Camerer & Ho (1999) EWA，与已归档版本重复 | `papers_originals/paper2_ewa/Camerer1999.pdf` |
| 2 | `tmp/camerer_ho_caltech.pdf` | 同上，Caltech 来源副本 | 同上 |
| 3 | `tmp/Artificial_Hivemind_NeurIPS_2025.pdf` | 与已归档 `JiangEtAl2025ArtificialHivemind.pdf` 重复 | `papers_originals/collective_intelligence_homogeneity/JiangEtAl2025ArtificialHivemind.pdf` |
| 4 | `tmp/Artificial_Hivemind_arXiv_2510.22954.pdf` | 同上，arXiv 版 | 同上 |
| 5 | `tmp/artificial_hivemind_2510.22954.pdf` | 同上，arXiv 版（另一个文件名） | 同上 |

---

## 五、非文献 PDF（保留原位，不纳入文献库）

这些是论文写作 / 申请 / 产出物，不属于文献库，建议留在原地。

| # | 位置 | 类型 |
|---|---|---|
| 1 | `dd636486-…_修改版｜算法权威与信息校准….pdf`（根目录） | 论文修改稿，建议移入 `defense_project/` 或 `outputs/` 版本区 |
| 2 | `defense_project/latex/*.pdf` | 论文正文 / 研究计划编译产物 |
| 3 | `outputs/**/*.pdf` | 历史产出 / 会议包 |
| 4 | `tmp/gz_edu_grant/*.pdf` | 广州市教育局课题申报材料 |
| 5 | `tmp/docs/rendered_feedback/feedback_review.pdf` | 反馈评审 |
| 6 | `tmp/academic_ppt_master_projects/**/local_formulas.pdf` | PPT 公式子图 |

---

## 六、汇总统计

- **标准库内 PDF**：`papers_originals/` 下 13 个主题目录，共 54 个（含本次已归档的 Bigman/DongBocian/Joo/Nyilasy）
- **待处理 PDF**：重下 5 + 归档 2 + 删除 1 + 去重 5 = 13 个
- **非文献 PDF**：6 处（保持不动）

## 七、执行建议（待确认后再做）

1. 优先：重下第 1 节 5 篇正确论文（信息获取主题），归档到新建的 `papers_originals/information_acquisition/`。
2. 归档第 2 节 2 篇已验证 PDF。
3. 删除第 3 节损坏文件。
4. 去重第 4 节 5 个 `tmp/` 副本。
5. 第 5 节非文献 PDF 保持不动（如需归位，单独讨论）。

以上均未执行，等你确认。
