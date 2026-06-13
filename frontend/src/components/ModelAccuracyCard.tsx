"use client";

import type { ModelMetrics } from "@/lib/types";

interface ModelAccuracyCardProps {
  metrics: ModelMetrics;
}

export function ModelAccuracyCard({ metrics }: ModelAccuracyCardProps) {
  const rows = [
    {
      label: "Cross-val (training)",
      value:
        metrics.cv_accuracy_mean != null
          ? `${(metrics.cv_accuracy_mean * 100).toFixed(1)}%`
          : "—",
    },
    {
      label: "2026 Playoffs holdout",
      value:
        metrics.validation_2026_playoffs_accuracy != null
          ? `${(metrics.validation_2026_playoffs_accuracy * 100).toFixed(1)}%`
          : "—",
    },
    {
      label: "Finals G1–4 backtest",
      value:
        metrics.finals_played_games_accuracy != null
          ? `${(metrics.finals_played_games_accuracy * 100).toFixed(1)}%`
          : "—",
    },
    {
      label: "Training games",
      value: metrics.train_games != null ? String(metrics.train_games) : "—",
    },
  ];

  return (
    <div
      className="rounded-2xl border p-5 backdrop-blur-md"
      style={{
        background: "rgba(18,24,38,0.85)",
        borderColor: "rgba(255,255,255,0.08)",
      }}
    >
      <h2
        className="mb-4 text-xs font-semibold uppercase tracking-widest"
        style={{ color: "#8b9cb3" }}
      >
        Model Accuracy
      </h2>
      <div className="space-y-0">
        {rows.map((row, i) => (
          <div
            key={i}
            className="flex justify-between border-b py-2 text-sm last:border-0"
            style={{ borderColor: "rgba(255,255,255,0.05)" }}
          >
            <span style={{ color: "#f0f4fa" }}>{row.label}</span>
            <span
              style={{
                fontFamily:
                  "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                fontWeight: 700,
              }}
            >
              {row.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
