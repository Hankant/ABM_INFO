import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Paper 1 重构监管台",
  description: "Paper 1 各重构方案的动态比较与识别审查。",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
