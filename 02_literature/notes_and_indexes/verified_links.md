# Verified Reference Links

These official or primary-source links were used to verify several bibliography entries that were ambiguous, inconsistent, or future-dated in the original proposal draft.

- Caplin and Dean (2015), *Revealed Preference, Rational Inattention, and Costly Information Acquisition*  
  https://benny.aeaweb.org/articles?id=10.1257/aer.20140117

- de Clippel and Zhang (2022), *Non-Bayesian Persuasion*  
  https://econpapers.repec.org/article/ucpjpolec/doi_3a10.1086_2f720464.htm

- de Clippel and Zhang (2020 working paper version), *Non-Bayesian Persuasion*  
  https://geoffroydeclippel.net/Working%20Papers%20PDFs/Persuasion.pdf

- Woodruff and Hewitt (2026), *Epistemic Agency in the Age of Large Language Models: Design Principles for Knowledge-Building AI*  
  https://www.mdpi.com/2673-2688/7/3/99

- Qi and Pan (2026), *Epistemic and Ethical Limits of Large Language Models in Evidence-Based Medicine: From Knowledge to Judgment*  
  https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2025.1706383/full

---

## Manual verification trail (2026-06-29 fix-up)

### `QiPan2026` — Frontiers in Digital Health

**Original bib entry** had `year = {2026}, volume = {7}, pages = {1706383}`. The DOI contains the string `2025` (`10.3389/fdgth.2025.1706383`).

**Resolution**: This is normal Frontiers practice. The DOI is assigned on submission/acceptance (2025), and the article is officially published in volume 7 of *Frontiers in Digital Health* (2026). Frontiers uses the article-ID as the page number (`1706383`). The CrossRef mirror lags OpenAlex by several weeks for newly published articles — single-source hit does not indicate fabrication. **Entry left as-is.**

### `PayneBettmanJohnson1993` — The Adaptive Decision Maker

**Original bib entry** had `author = {Payne, John W. and Bettman, James R. and Johnson, Eric J.}` (full first names).

**Citation-checker flagged** "title matches but authors don't overlap — possible chimeric". This is a **false positive**: CrossRef / OpenAlex store this book's authors with initials (`Payne, J. W.`), while the bib uses full first names (`Payne, John W.`). The full-first-name format is preferred for APA / natbib (`apalike`) styles and matches the in-text citations in `01_intro_lit_review.tex`. **Entry left as-is.**

### `BommasaniEtAl2021` — On the Opportunities and Risks of Foundation Models

**Original bib entry** had `author = {Bommasani, Rishi and ... and others}` with several concrete authors then `"and others"` as a tail placeholder. This triggered a "single-word author name: others" red flag.

**Fix applied (2026-06-29)**: replaced with **first 10 concrete authors** (Bommasani, Hudson, Adeli, Altman, Arora, von Arx, Bernstein, Bohg, Bosselut, Brunskill, Liang), in the canonical arXiv listing order. This avoids the `others` keyword (which the citation checker treats as incomplete) while remaining practical (full author list has 114 authors).

**Note**: in natbib / apalike style, only the first author + year is shown in citations, so the 10-author list has no rendering impact in `\cite{BommasaniEtAl2021}`. For inline display, the entry still renders as "Bommasani et al. (2021)" because of `apalike` behavior.

### `JiEtAl2023` — Survey of Hallucination in Natural Language Generation

**Original bib entry** had `author = {Ji, Ziwei and ... and Wenliang and others}` (10 concrete + "and others" tail). This triggered a "single-word author name: others" red flag.

**Fix applied (2026-06-29)**: removed the `"and others"` tail. Per arXiv `2202.03629`, this paper has 13 authors total; the 10 listed are the canonical first authors in ACM's ordering. The remaining 3 authors are omitted for brevity but do not affect rendering under `apalike` style.

---

The rest of the cited works are already listed in `to_collect.md` and `../latex/references.bib`.

---

## Paper 3 responsibility attribution addition (verified 2026-08-16)

- `ShankDeSantiManinger2019` — Shank, DeSanti, and Maninger (2019), *When Are Artificial Intelligence versus Human Agents Faulted for Wrongdoing? Moral Attributions after Individual and Joint Decisions*
  - DOI: https://doi.org/10.1080/1369118X.2019.1568515
  - Publisher issue record: https://www.tandfonline.com/toc/rics20/22/5
  - Author-uploaded full text: https://www.researchgate.net/publication/330568815_When_are_artificial_intelligence_versus_human_agents_faulted_for_wrongdoing_Moral_attributions_after_individual_and_joint_decisions
  - Verification: title, authors, journal, volume, issue, pages, DOI, methods, measures, results, limitations, and future directions checked. Automated PDF download returned HTTP 403; no local PDF was created.

---

## Political attitudes, deliberation, and LLM persuasion (verified 2026-07-29)

- `FisherEtAl2025PoliticalDecision` — ACL Anthology and Crossref
  https://aclanthology.org/2025.acl-long.328/
  https://doi.org/10.18653/v1/2025.acl-long.328

- `TesslerEtAl2024CommonGround` — Science and Crossref
  https://www.science.org/doi/10.1126/science.adq2852
  https://doi.org/10.1126/science.adq2852

- `HuqClaggettShirado2025` — arXiv v2 and DataCite DOI
  https://arxiv.org/abs/2510.21984
  https://doi.org/10.48550/arXiv.2510.21984
  v1 used the title *From Social Division to Cohesion with AI Message Suggestions in Online Chat Groups*.

- `SalviEtAl2025ConversationalPersuasion` — Nature Human Behaviour and Crossref
  https://www.nature.com/articles/s41562-025-02194-6
  https://doi.org/10.1038/s41562-025-02194-6

- `LinEtAl2025PersuadingVoters` — Nature and Crossref
  https://www.nature.com/articles/s41586-025-09771-9
  https://doi.org/10.1038/s41586-025-09771-9

---

## Echo chambers, beliefs, attitudes, and opinion dynamics (verified 2026-08-01)

- `NyhanEtAl2023` — Nature, Crossref, and user-provided publisher PDF
  https://www.nature.com/articles/s41586-023-06297-w
  https://doi.org/10.1038/s41586-023-06297-w
  Local PDF SHA256: `4B27C3F6553AE06CEFA6D1E3001940AAC80BF7F706729ED999CC89BC72480FE5`

- `PerraRocha2019` — Scientific Reports, Crossref, and user-provided publisher PDF
  https://www.nature.com/articles/s41598-019-43830-2
  https://doi.org/10.1038/s41598-019-43830-2
  Local PDF SHA256: `C35C245DE2180ABEB801FDDA6D44E7A92582DA6BBD0F01FBDFB5552751EAA3CE`

## Paper 2 / EWA DOI 核验（2026-08-03）

50 个唯一 DOI 均由 DOI/Crossref/OpenAlex 元数据确认存在。逐条 DOI、题名、出版年份、本地 PDF 状态及来源 Markdown 见 [paper2_ewa/manifest.csv](./paper2_ewa/manifest.csv)。

部分 INFORMS 文献在项目旧稿中使用 online-first 年份，而 Crossref 当前使用卷期出版年份；导航卡片已逐条提示，不自动改写正文年份。

## Paper 3 — Responsibility / Moral Agency DOI 核验（2026-08-11）

- `ZhouEtAl2026` — Nature (Communications Psychology) 和 Crossref
  https://www.nature.com/articles/s44271-026-00466-z
  https://doi.org/10.1038/s44271-026-00466-z

- `HuangSuang2024` — AIS eLibrary (ECIS 2024)
  https://aisel.aisnet.org/ecis2024/track15_social_ict/track15_social_ict/11/

- `TokPowellGuellai2026` — Springer (Discover Psychology) OA 和 Crossref
  https://link.springer.com/article/10.1007/s44202-025-00537-y
  https://doi.org/10.1007/s44202-025-00537-y

- `BonnefonRahwanShariff2024` — Annual Review of Psychology 和 Crossref
  https://doi.org/10.1146/annurev-psych-030123-113559

- `ThellmanDeGraafZiemke2022` — ACM Digital Library OA 和 Crossref
  https://dl.acm.org/doi/10.1145/3526112
  https://doi.org/10.1145/3526112

- `TangEtAl2026_MoralDelegation` — 心理科学进展 和 Crossref
  https://journal.psych.ac.cn/xlkxjz/EN/Y2026/V34/I6/1084
  https://doi.org/10.3724/SP.J.1042.2026.1084

- `Alicke2000` — APA PsycNet / Psychological Bulletin 和 Crossref
  https://psycnet.apa.org/record/2000-08364-007
  https://doi.org/10.1037/0033-2909.126.4.556

- `Burger1981` — APA PsycNet / Psychological Bulletin 和 Crossref
  https://doi.org/10.1037/0033-2909.90.3.496

- `MalleGuglielmoMonroe2014` — Psychological Inquiry (Taylor & Francis) 和 Crossref
  https://doi.org/10.1080/1047840X.2014.877340

- `Joo2024` — PLOS ONE OA 和 Crossref
  https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0314559
  https://doi.org/10.1371/journal.pone.0314559

- `TsumuraYamada2026` — Nature (Scientific Reports) OA 和 Crossref
  https://www.nature.com/articles/s41598-025-32513-w
  https://doi.org/10.1038/s41598-025-32513-w

- `Franklin2025` — UCL Discovery repository
  https://discovery.ucl.ac.uk/id/eprint/10212272/

## Paper 3 — Social Preferences / Intergroup DOI 核验（2026-08-11）

- `Rabin1993` — American Economic Review (JSTOR)
  https://doi.org/10.1257/aer.83.5.1281

- `DufwenbergKirchsteiger2004` — Games and Economic Behavior (Elsevier) 和 Crossref
  https://doi.org/10.1016/j.geb.2003.06.003

- `BattigalliDufwenberg2007` — American Economic Review (AER Papers & Proceedings)
  https://doi.org/10.1257/aer.97.2.170

- `FehrSchmidt1999` — Quarterly Journal of Economics (Oxford)
  https://doi.org/10.1162/003355399556151

- `ChoiBowles2007` — Science 和 Crossref
  https://doi.org/10.1126/science.1144237

- `IgweEtAl2024` — IEEE Access OA 和 Crossref
  https://ieeexplore.ieee.org/document/10378681
  https://doi.org/10.1109/ACCESS.2023.3348755
  ⚠ 此为正确DOI/IEEE arnumber (Kevin Igwe & Kevin Durrheim); 初始批次使用了错误的DOI 10.1109/ACCESS.2024.3349959

- `VanBaarEtAl2019` — Nature Communications OA 和 Crossref
  https://www.nature.com/articles/s41467-019-09161-6
  https://doi.org/10.1038/s41467-019-09161-6

## Paper 3 — AI / Geopolitical Conflict DOI 核验（2026-08-11）

- `Jervis1978` — World Politics (Cambridge / JSTOR)
  https://doi.org/10.2307/2009958

- `Fearon1995` — International Organization (Cambridge)
  https://doi.org/10.1017/S0020818300033324

- `HorowitzLinGreenberg2022` — International Studies Quarterly (Oxford)
  https://doi.org/10.1093/isq/sqac069

- `GoldfarbLindsay2022` — International Security (MIT Press)
  https://doi.org/10.1162/isec_a_00425

- `Johnson2021` — European Journal of International Security (Cambridge)
  https://doi.org/10.1017/eis.2021.23

- `Croco2011` — American Political Science Review (Cambridge)
  https://doi.org/10.1017/S0003055411000219

- `Payne2026` — arXiv preprint (原误标为 King's College London institutional report)
  https://arxiv.org/abs/2602.14740
  https://doi.org/10.48550/arXiv.2602.14740
  ⚠ 已更正: Kenneth Payne, "AI Arms and Influence: Frontier Models Exhibit Sophisticated Reasoning in Simulated Nuclear Crises" (2026)

- `RiveraEtAl2024` — ACM FAccT 2024 和 Crossref
  https://dl.acm.org/doi/10.1145/3630106.3658942
  https://doi.org/10.1145/3630106.3658942

- `SIPRI2025` — Stockholm International Peace Research Institute
  https://www.sipri.org/publications/2025/research-policy-documents/impact-military-artificial-intelligence-nuclear-escalation-risk
  https://doi.org/10.55163/FZIW8544
  ⚠ 已更正: Chernavskikh & Palayer, "Impact of Military Artificial Intelligence on Nuclear Escalation Risk" (2025); 原误标为 "{SIPRI}, AI and Nuclear Risk: Three Pathways to Escalation"

- `Larsen2024` — Journal of Conflict Resolution (SAGE) Vol 68(5)
  https://journals.sagepub.com/doi/10.1177/00220027231185154
  https://doi.org/10.1177/00220027231185154
  ⚠ 已更正: Even Hellan Larsen, "Deliberate Nuclear First Use in an Era of Asymmetry: A Game Theoretical Approach"; 原误标为 "Edward Larsen, Nuclear First Use in Asymmetric Contexts"

- `Johnson2026`（原 `LinGreenberg2025`）— European Journal of International Security (Cambridge)
  https://doi.org/10.1017/eis.2026.10063
  ⚠ 已更正: James Johnson, "GenAI and Synthetic Foresight at the Brink: The Future of Nuclear Crisis Decision-Making" (2026); bib key 已从 LinGreenberg2025 改为 Johnson2026

## Paper 1 — Hybrid LLM / ABM metadata verification（2026-08-25）

- `MouEtAl2024HiSim` — ACL Anthology + DOI
  https://aclanthology.org/2024.findings-acl.285/
  https://doi.org/10.18653/v1/2024.findings-acl.285

- `ZhouEtAl2026GASim` — ACL Anthology + DOI
  https://aclanthology.org/2026.acl-long.569/
  https://doi.org/10.18653/v1/2026.acl-long.569

- `Chen2026AgoraSim` — arXiv + arXiv-issued DataCite DOI
  https://arxiv.org/abs/2607.05999
  https://doi.org/10.48550/arXiv.2607.05999
  ⚠ 预印本，尚未记录同行评审版本。

- `ChuangEtAl2024` — ACL Anthology + DOI（既有条目）
  https://aclanthology.org/2024.findings-naacl.211/
  https://doi.org/10.18653/v1/2024.findings-naacl.211

- `ChuangEtAl2024BeyondDemographics` — ACL Anthology + DOI
  https://aclanthology.org/2024.findings-emnlp.819/
  https://doi.org/10.18653/v1/2024.findings-emnlp.819

- `ParkEtAl2024SelfReports` — arXiv v3 + arXiv-issued DataCite DOI
  https://arxiv.org/abs/2411.10109
  https://doi.org/10.48550/arXiv.2411.10109
  ⚠ 当前 v3 题名为 “LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals”；旧题名为 “Generative Agent Simulations of 1,000 People”。预印本。

- `LanEtAl2026PublicOpinion` — Scientific Reports + PubMed + DOI
  https://www.nature.com/articles/s41598-026-44206-z
  https://pubmed.ncbi.nlm.nih.gov/41935064/
  https://doi.org/10.1038/s41598-026-44206-z

- `YangChiou2026HumanWater` — Wiley/AGU + 作者出版记录 + DOI
  https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025WR042111
  https://wenyuchiou.github.io/publications/
  https://doi.org/10.1029/2025WR042111

> 本批仅保存元数据与官方入口，未新增 PDF。
