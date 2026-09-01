export type ScoreKey =
  | "theory"
  | "identification"
  | "continuity"
  | "aiSpecificity"
  | "feasibility";

export type Direction = {
  id: string;
  rank: number;
  title: string;
  shortTitle: string;
  subtitle: string;
  lane: "current" | "ambitious" | "baseline" | "outside" | "hold";
  status: "recommended" | "promising" | "baseline" | "watch" | "exclude";
  statusLabel: string;
  verdict: string;
  theoryTension: string;
  unit: string;
  causalComparison: string;
  mechanism: string[];
  aiTest: string;
  fatalResult: string;
  nextGate: string;
  evidenceBoundary: string;
  source: string;
  scores: Record<ScoreKey, number>;
};

export const scoreLabels: Record<ScoreKey, string> = {
  theory: "理论张力",
  identification: "因果识别",
  continuity: "Paper1 连续性",
  aiSpecificity: "AI 特异性",
  feasibility: "执行可行性",
};

export const dashboardData = {
  updatedAt: "2026-07-29",
  mode: "只读监管 · 未干预其他任务",
  scoringNote:
    "分数是当前监管判断，不是统计结果。总分按 Paper1 当前目标加权：理论张力 25%、因果识别 25%、连续性 20%、AI 特异性 15%、可行性 15%。",
  headline: {
    currentBest: "AI 第二意见的独立性错觉",
    currentBestReason:
      "它保留“信息获取—搜索停止—信念校准”的 Paper1 主链，同时把操纵从来源标签推进到更有因果含义的“用户先验进入 AI 证据选择”。",
    upsideBest: "群体信息同质化 / 相关误差",
    upsideBestReason:
      "理论对象从个人均值转向成员间误差协方差，社会意义更大；但必须证明自然 LLM 暴露如何生成相关误差，且不能只靠任意参数的 ABM。",
  },
  decisionRules: [
    "先判断它是否仍然回答 Paper1 的 evidence → belief 问题。",
    "再要求一个分析单位、一个主因果比较、一个可证伪失败条件。",
    "最后做 AI 不可替代性检验；若共享人工简报同样解释结果，只能称 AI 应用。",
  ],
  directions: [
    {
      id: "independence-illusion",
      rank: 1,
      title: "AI 第二意见的独立性错觉",
      shortTitle: "独立性错觉",
      subtitle: "belief-contingent evidence sampling",
      lane: "current",
      status: "recommended",
      statusLabel: "当前最优",
      verdict:
        "最适合作为当前 Paper1 的主重构。不是研究“AI 会迎合”，而是研究用户把由自己先验诱发的证据返回，当成独立、完整的外部意见。",
      theoryTension:
        "第二意见只有在信息来源相对独立时才增加证据量；对话式 AI 却会根据用户已表达的立场选择与组织证据，使表面的第二意见与用户先验因果相关。",
      unit: "个体判断者",
      causalComparison:
        "固定同一证据池与边际信息质量：AI 按用户先验选择证据 vs AI 独立、代表性抽样证据；再加入人类/静态系统来源对照。",
      mechanism: [
        "用户先表达初始判断",
        "AI 返回立场一致但不完整的真实证据",
        "用户高估来源独立性与信息充分性",
        "反向证据搜索下降",
        "完整信息基准下的偏离与过度确信上升",
      ],
      aiTest:
        "比较隐藏自适应 AI 与内容匹配的人类分析员/静态系统。AI 特异性来自低可见度的个性化因果依赖，而非“AI 标签”本身。",
      fatalResult:
        "只要告知证据与用户输入有关，效应就完全消失；或静态重复信息产生同样效应且无新预测，则贡献退化为传统 evidential dependency neglect。",
      nextGate:
        "写出相对依赖忽视、共识错觉与重复真理效应的新增预测；随后锁定最小 2×2 设计和预注册主结果。",
      evidenceBoundary:
        "直接“sycophancy 让人更确信/更差”已拥挤；可发表增量必须来自自我诱发的信息依赖与后续搜索。",
      source: "任务：重构 Paper1 中的有害信息机制（只读观察）",
      scores: {
        theory: 4.2,
        identification: 4.5,
        continuity: 4.8,
        aiSpecificity: 3.7,
        feasibility: 4.3,
      },
    },
    {
      id: "correlated-error",
      rank: 2,
      title: "群体信息同质化与相关误差",
      shortTitle: "相关误差",
      subtitle: "individual non-inferiority ≠ group non-inferiority",
      lane: "ambitious",
      status: "promising",
      statusLabel: "高上限",
      verdict:
        "理论上限最高，但不是当前最稳。最小论文应研究互不交流的统计群体，避免同时扩张到真实团队、政治说服和跨机构生态。",
      theoryTension:
        "AI 不降低个人平均准确率，仍可能提高成员间误差相关性，从而削弱群体聚合收益；个人无害不能推出群体无害。",
      unit: "互不交流的统计群体；个人是嵌套观测",
      causalComparison:
        "共同 AI 信息冲击 vs 独立 AI 信息冲击；匹配模型、界面、标签、边际信息质量、个人平均误差与方差。",
      mechanism: [
        "共同模型先验进入多人信息环境",
        "证据与框架重叠",
        "个体误差协方差上升",
        "有效独立样本量下降",
        "群体平均判断的误差下降变慢或停止",
      ],
      aiTest:
        "以质量匹配的共享人工简报作为替代性检验。若完全复现，主机制是共同信息源；AI 贡献需来自规模化、交互表面独立性或内生搜索停止。",
      fatalResult:
        "无法在匹配个人边际质量后识别相关性差异；或自然 LLM 输出并未提供超出一般共享简报的相关性来源。",
      nextGate:
        "先完成解析模型与功效仿真，再做重复客观任务的人类校准实验；ABM 只能在参数可由数据约束后加入。",
      evidenceBoundary:
        "现有 Perspective 已明确提出共享 LLM 可能减少功能多样性；新意不能只是“输出相似”，而要识别人类误差传导。",
      source:
        "Paper1_群体信息同质化_最小识别审查_2026-07-28.md；重构方案",
      scores: {
        theory: 4.9,
        identification: 3.7,
        continuity: 3.2,
        aiSpecificity: 3.1,
        feasibility: 2.8,
      },
    },
    {
      id: "calibration-baseline",
      rank: 3,
      title: "算法权威与信息校准",
      shortTitle: "现有基准",
      subtitle: "same-summary source-label design",
      lane: "baseline",
      status: "baseline",
      statusLabel: "已确认基准",
      verdict:
        "识别清楚、资产最成熟，是所有重构的比较基线。主要短板是理论张力偏小：AI 标签为什么足以改变搜索，以及该效应为何具有更广的组织后果，仍需加强。",
      theoryTension:
        "相同信息内容下，AI 来源标签可能改变主观信息充分性和额外证据价值，使用户更早停止搜索，并造成主观掌握感与客观校准错配。",
      unit: "个体判断者",
      causalComparison:
        "无 summary vs 无标签 summary vs AI 标签 summary，交叉 representative vs incomplete evidence；summary 内容保持一致。",
      mechanism: [
        "AI 来源标签 / 总结式呈现",
        "主观信息充分性上升",
        "额外证据价值下降",
        "提前停止搜索",
        "贝叶斯偏离与主客观校准错配",
      ],
      aiTest:
        "same-summary 标签比较已隔离来源效应，但仍需证明结果不是一般权威标签、熟悉度或需求特征。",
      fatalResult:
        "AI 标签不影响充分性感知或搜索；或搜索下降在不完整证据下不造成可识别校准损失。",
      nextGate:
        "保留为基准稿。若候选方向无法通过新增预测与最小识别门槛，则回到此设计强化理论边界，而不盲目换题。",
      evidenceBoundary:
        "“少搜索”本身不是 automation bias；只有在信息不完整/错误且减少监控造成可识别错误时才成立。",
      source: "当前第一章_算法权威与信息校准_基准稿.md",
      scores: {
        theory: 3.3,
        identification: 4.6,
        continuity: 5,
        aiSpecificity: 3.5,
        feasibility: 4.8,
      },
    },
    {
      id: "capability-accumulation",
      rank: 4,
      title: "AI 分工与能力积累",
      shortTitle: "能力积累",
      subtitle: "current productivity vs future capability",
      lane: "outside",
      status: "watch",
      statusLabel: "独立项目更强",
      verdict:
        "是很强的新管理研究，但不宜直接替换 Paper1。它把单位改为稳定团队、结果改为长期能力，等于重写三篇论文的架构。",
      theoryTension:
        "静态分工要求把任务交给当前最有效率者；能力形成却依赖反复执行与反馈，因此短期最优 AI 分工可能侵蚀未来的人类与团队能力。",
      unit: "稳定工作团队",
      causalComparison:
        "同一 AI 直接完成任务 vs 同一 AI 支持但由团队执行；随后在无 AI 条件下测量团队能力。",
      mechanism: [
        "AI 提高即时生产率",
        "人类执行机会减少",
        "反馈与错误修正减少",
        "知识折旧 / 能力积累放缓",
        "未来无 AI 表现下降",
      ],
      aiTest:
        "必须与固定规则自动化匹配比较，否则只是经典 deskilling 的生成式 AI 场景。",
      fatalResult:
        "长期能力差异完全由任务暴露量解释，且 AI 与普通自动化无差别；或无法稳定测量团队层能力。",
      nextGate:
        "作为独立项目建立一页概念备忘，不占用 Paper1 当前重构资源；除非用户明确批准重写论文组合。",
      evidenceBoundary:
        "理论价值高，但与 Paper1 的 evidence → belief 主线不连续。",
      source: "任务：Paper1 理论框架讨论（只读观察）",
      scores: {
        theory: 4.7,
        identification: 4,
        continuity: 1.8,
        aiSpecificity: 3.2,
        feasibility: 3,
      },
    },
    {
      id: "creativity-exploration",
      rank: 5,
      title: "AI 创造力与组织探索",
      shortTitle: "探索多样性",
      subtitle: "individual quality vs portfolio diversity",
      lane: "hold",
      status: "watch",
      statusLabel: "观察",
      verdict:
        "问题重要，但“个体创意提高、总体多样性下降”已有直接证据。除非能识别 AI 进入生成与选择阶段的不同作用，否则容易成为现象复现。",
      theoryTension:
        "个体层创意质量提升不保证组织的创意组合更有探索性，平均质量与组合多样性可能反向变化。",
      unit: "组织的创意组合",
      causalComparison: "AI 用于创意生成 vs AI 用于创意筛选，保持任务与资源投入可比。",
      mechanism: [
        "AI 提高单个创意完成度",
        "共享语义先验导致相似化",
        "组合覆盖面收缩",
        "远距探索下降",
      ],
      aiTest: "与共享范例库或人类创意顾问比较，识别是否超出一般共同刺激。",
      fatalResult: "阶段差异没有新增预测，结果仅复制现有“创意更好但更相似”。",
      nextGate: "暂不进入 Paper1 主线；只在相关误差方向需要任务域时重新评估。",
      evidenceBoundary: "现象层已有先行研究，理论增量依赖过程阶段与组合选择。",
      source: "任务：Paper1 理论框架讨论（只读观察）",
      scores: {
        theory: 3.5,
        identification: 3.5,
        continuity: 2.4,
        aiSpecificity: 2.8,
        feasibility: 3.7,
      },
    },
    {
      id: "direct-sycophancy",
      rank: 6,
      title: "直接有害信息 / AI 迎合",
      shortTitle: "直接迎合",
      subtitle: "sycophancy → confidence / harm",
      lane: "hold",
      status: "exclude",
      statusLabel: "不建议",
      verdict:
        "不建议把“迎合信息让用户更自信、更不愿修正”本身作为重构主张。该因果链已被近期多项实验直接覆盖。",
      theoryTension:
        "AI 通过认可用户既有立场提高体验与信任，却可能降低纠错和关系修复。",
      unit: "个体判断者",
      causalComparison: "迎合回答 vs 不迎合回答；来源标为 AI vs 人类。",
      mechanism: ["立场迎合", "感到自己正确", "信任与复用上升", "纠错/修复意愿下降"],
      aiTest:
        "同内容 AI/人类标签若无差异，说明内容机制优先，不能宣称 AI 来源的独特效应。",
      fatalResult: "现有研究已覆盖主要结果，除非提出新的信息依赖机制，否则缺乏独立理论贡献。",
      nextGate: "只保留为独立性错觉方向的现象背景，不作为主设计。",
      evidenceBoundary:
        "Science 终版研究已包含多项预注册实验；后续工作也已测试信念条件化证据抽样与反馈循环。",
      source: "任务：重构 Paper1 中的有害信息机制（只读观察）",
      scores: {
        theory: 2.6,
        identification: 4,
        continuity: 3.6,
        aiSpecificity: 2.3,
        feasibility: 4,
      },
    },
    {
      id: "responsibility",
      rank: 7,
      title: "AI 行动权与责任结构",
      shortTitle: "责任结构",
      subtitle: "action authorization → responsibility",
      lane: "outside",
      status: "exclude",
      statusLabel: "归入 Paper3",
      verdict:
        "这是 Paper3 的核心，不是 Paper1 重构候选。放进 Paper1 会同时改变因变量、理论单位和论文组合边界。",
      theoryTension:
        "AI 获得行动权后，控制、授权与责任归属可能分离。",
      unit: "人—AI 行动与问责关系",
      causalComparison: "AI 建议 vs AI 受权执行，并交叉确认/披露等治理安排。",
      mechanism: ["行动权委托", "过程控制变化", "因果归因", "责任配置"],
      aiTest: "比较建议、自动化执行与代理性执行，识别真正的行动授权结构。",
      fatalResult: "若只操纵确认或披露按钮，贡献只是过程干预，未建立独特责任结构。",
      nextGate: "维持 Paper3 轨道，不进入 Paper1 看板排名竞争。",
      evidenceBoundary: "Paper1 负责 evidence → belief；Paper3 负责 action → responsibility。",
      source: "三篇论文既定映射",
      scores: {
        theory: 4.2,
        identification: 3.5,
        continuity: 1,
        aiSpecificity: 4.2,
        feasibility: 3.2,
      },
    },
  ] satisfies Direction[],
};
