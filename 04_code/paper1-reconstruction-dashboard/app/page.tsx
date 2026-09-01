import type { Metadata } from "next";
import Dashboard from "./dashboard";
import { dashboardData } from "./data/directions";

export const metadata: Metadata = {
  title: "Paper 1 重构监管台",
  description: "Paper 1 各重构方向的只读比较、识别审查与动态排序。",
  other: {
    "codex-preview": "development",
  },
};

export default function Home() {
  return <Dashboard data={dashboardData} />;
}
