"use client";

import { useMemo, useState } from "react";
import type { Direction, ScoreKey } from "./data/directions";
import { scoreLabels } from "./data/directions";

type DashboardData = {
  updatedAt: string;
  mode: string;
  scoringNote: string;
  headline: {
    currentBest: string;
    currentBestReason: string;
    upsideBest: string;
    upsideBestReason: string;
  };
  decisionRules: string[];
  directions: Direction[];
};

const weights: Record<ScoreKey, number> = {
  theory: 0.25,
  identification: 0.25,
  continuity: 0.2,
  aiSpecificity: 0.15,
  feasibility: 0.15,
};

const profileWeights: Record<string, Record<ScoreKey, number>> = {
  paper1: weights,
  theory: {
    theory: 0.7,
    identification: 0.1,
    continuity: 0,
    aiSpecificity: 0.15,
    feasibility: 0.05,
  },
  execution: {
    theory: 0.15,
    identification: 0.25,
    continuity: 0.25,
    aiSpecificity: 0.1,
    feasibility: 0.25,
  },
};

const profileLabels: Record<string, string> = {
  paper1: "Paper1 适配",
  theory: "理论上限",
  execution: "执行优先",
};

const statusClass: Record<Direction["status"], string> = {
  recommended: "tag tag-recommended",
  promising: "tag tag-promising",
  baseline: "tag tag-baseline",
  watch: "tag tag-watch",
  exclude: "tag tag-exclude",
};

function weightedScore(
  direction: Direction,
  activeWeights: Record<ScoreKey, number>,
) {
  const raw = (Object.keys(activeWeights) as ScoreKey[]).reduce(
    (sum, key) => sum + direction.scores[key] * activeWeights[key],
    0,
  );
  return Math.round(raw * 20);
}

function ScoreBars({ direction }: { direction: Direction }) {
  return (
    <div className="score-bars">
      {(Object.keys(scoreLabels) as ScoreKey[]).map((key) => (
        <div className="score-row" key={key}>
          <span>{scoreLabels[key]}</span>
          <div className="score-track" aria-hidden="true">
            <div
              className="score-fill"
              style={{ width: `${direction.scores[key] * 20}%` }}
            />
          </div>
          <strong>{direction.scores[key].toFixed(1)}</strong>
        </div>
      ))}
    </div>
  );
}

function DirectionDetail({ direction }: { direction: Direction }) {
  return (
    <article className="detail-card" id={`detail-${direction.id}`}>
      <div className="detail-head">
        <div>
          <span className={statusClass[direction.status]}>
            {direction.statusLabel}
          </span>
          <p className="eyebrow">{direction.subtitle}</p>
          <h3>{direction.title}</h3>
        </div>
        <div className="rank-mark">0{direction.rank}</div>
      </div>
      <p className="verdict">{direction.verdict}</p>
      <div className="detail-grid">
        <section>
          <h4>唯一理论矛盾</h4>
          <p>{direction.theoryTension}</p>
        </section>
        <section>
          <h4>分析单位</h4>
          <p>{direction.unit}</p>
        </section>
        <section className="wide">
          <h4>唯一主因果比较</h4>
          <p>{direction.causalComparison}</p>
        </section>
      </div>
      <div className="mechanism">
        <h4>机制链</h4>
        <ol>
          {direction.mechanism.map((step, index) => (
            <li key={step}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              {step}
            </li>
          ))}
        </ol>
      </div>
      <div className="audit-grid">
        <section>
          <h4>AI 不可替代性检验</h4>
          <p>{direction.aiTest}</p>
        </section>
        <section className="risk">
          <h4>失去贡献的结果</h4>
          <p>{direction.fatalResult}</p>
        </section>
        <section className="gate">
          <h4>下一道决策门</h4>
          <p>{direction.nextGate}</p>
        </section>
      </div>
      <div className="boundary">
        <span>证据边界</span>
        <p>{direction.evidenceBoundary}</p>
      </div>
      <footer>
        <span>依据</span>
        {direction.source}
      </footer>
    </article>
  );
}

export default function Dashboard({ data }: { data: DashboardData }) {
  const [profile, setProfile] = useState("paper1");
  const [visible, setVisible] = useState("core");
  const [activeId, setActiveId] = useState(data.directions[0].id);

  const ranked = useMemo(() => {
    const pool =
      visible === "all"
        ? data.directions
        : data.directions.filter((item) =>
            ["current", "ambitious", "baseline", "outside"].includes(item.lane) &&
            item.status !== "exclude",
          );
    return [...pool].sort(
      (a, b) =>
        weightedScore(b, profileWeights[profile]) -
        weightedScore(a, profileWeights[profile]),
    );
  }, [data.directions, profile, visible]);

  const active =
    data.directions.find((item) => item.id === activeId) ?? ranked[0];

  function selectProfile(key: string) {
    const nextTop = [...ranked].sort(
      (a, b) =>
        weightedScore(b, profileWeights[key]) -
        weightedScore(a, profileWeights[key]),
    )[0];
    setProfile(key);
    if (nextTop) setActiveId(nextTop.id);
  }

  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#top" aria-label="返回顶部">
          <span>P1</span>
          <div>
            <strong>RECONSTRUCTION CONTROL</strong>
            <small>Paper 1 重构监管台</small>
          </div>
        </a>
        <div className="top-meta">
          <span className="live-dot" />
          {data.mode}
          <span className="divider" />
          更新 {data.updatedAt}
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">SUPERVISOR VERDICT · ROUND 01</p>
          <h1>
            不是选“最宏大”的题，
            <br />
            而是选<span>最能被识别的理论矛盾</span>。
          </h1>
          <p className="hero-note">
            当前判断把“仍然是 Paper1”与“理论上限最高”分开。所有候选方案保持候选状态，
            不自动覆盖已确认基准稿。
          </p>
        </div>
        <div className="verdict-panel">
          <div className="verdict-item primary">
            <span>当前 Paper1 最优</span>
            <h2>{data.headline.currentBest}</h2>
            <p>{data.headline.currentBestReason}</p>
          </div>
          <div className="verdict-item">
            <span>理论上限最高</span>
            <h2>{data.headline.upsideBest}</h2>
            <p>{data.headline.upsideBestReason}</p>
          </div>
        </div>
      </section>

      <section className="rules">
        {data.decisionRules.map((rule, index) => (
          <div key={rule}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <p>{rule}</p>
          </div>
        ))}
      </section>

      <section className="comparison" id="ranking">
        <div className="section-head">
          <div>
            <p className="eyebrow">DYNAMIC RANKING</p>
            <h2>同一方案，在不同目标下会改变排序</h2>
          </div>
          <div className="controls">
            <div className="segmented" aria-label="切换评分视角">
              {Object.entries(profileLabels).map(([key, label]) => (
                <button
                  className={profile === key ? "active" : ""}
                  key={key}
                  onClick={() => selectProfile(key)}
                  type="button"
                >
                  {label}
                </button>
              ))}
            </div>
            <button
              className="text-button"
              onClick={() => setVisible(visible === "all" ? "core" : "all")}
              type="button"
            >
              {visible === "all" ? "收起次级方向" : "显示全部方向"}
              <span aria-hidden="true">↗</span>
            </button>
          </div>
        </div>

        <div className="ranking-layout">
          <div className="rank-list">
            {ranked.map((direction, index) => {
              const score = weightedScore(
                direction,
                profileWeights[profile],
              );
              return (
                <button
                  className={`rank-row ${active.id === direction.id ? "selected" : ""}`}
                  key={direction.id}
                  onClick={() => setActiveId(direction.id)}
                  type="button"
                >
                  <span className="rank-index">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className="rank-copy">
                    <strong>{direction.shortTitle}</strong>
                    <small>{direction.statusLabel}</small>
                  </span>
                  <span className="rank-meter">
                    <i style={{ width: `${score}%` }} />
                  </span>
                  <span className="rank-score">{score}</span>
                </button>
              );
            })}
            <p className="score-note">{data.scoringNote}</p>
          </div>
          <aside className="score-card">
            <div className="score-card-head">
              <div>
                <span className={statusClass[active.status]}>
                  {active.statusLabel}
                </span>
                <h3>{active.title}</h3>
              </div>
              <strong>
                {weightedScore(active, profileWeights[profile])}
                <small>/100</small>
              </strong>
            </div>
            <ScoreBars direction={active} />
            <a href={`#detail-${active.id}`}>查看完整识别审查 ↓</a>
          </aside>
        </div>
      </section>

      <section className="equation-section">
        <div>
          <p className="eyebrow">WHY THE AMBITIOUS ROUTE MATTERS</p>
          <h2>相关性不会改变个人方差，却会吞掉群体规模的收益</h2>
          <p>
            群体方向真正有价值的地方，不是“大家回答更像”，而是把理论结果写成误差协方差与有效独立样本量。
          </p>
        </div>
        <div className="equation-card">
          <span>群体均值误差方差</span>
          <p>
            Var(ē) = σ²[
            <strong>ρ</strong> + (1 − ρ) / N]
          </p>
          <small>
            当相关性 ρ 大于零，增加成员 N 无法像独立样本那样持续降低误差。
          </small>
        </div>
      </section>

      <section className="details" id="details">
        <div className="section-head">
          <div>
            <p className="eyebrow">DIRECTION LEDGER</p>
            <h2>方向账本：每项都要能被证伪</h2>
          </div>
          <p className="section-note">
            以下记录是监管判断，不代表相关任务已获准执行，也不构成对其他任务的干预。
          </p>
        </div>
        <div className="detail-stack">
          {data.directions.map((direction) => (
            <DirectionDetail direction={direction} key={direction.id} />
          ))}
        </div>
      </section>

      <section className="update-guide">
        <div>
          <p className="eyebrow">UPDATE PROTOCOL</p>
          <h2>以后如何更新这个看板</h2>
        </div>
        <ol>
          <li>
            <span>01</span>
            只更新 <code>app/data/directions.ts</code> 中的方向记录与日期。
          </li>
          <li>
            <span>02</span>
            新证据只能改变对应维度分数，必须同时写明证据边界或失败条件。
          </li>
          <li>
            <span>03</span>
            只有用户明确确认后，候选方案才能改成“已确认基准”。
          </li>
        </ol>
      </section>

      <footer className="page-footer">
        <div>
          <strong>PAPER 1 · RECONSTRUCTION CONTROL</strong>
          <span>Evidence → Search → Belief</span>
        </div>
        <p>Observer mode / no cross-task intervention</p>
      </footer>
    </main>
  );
}
