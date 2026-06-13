"use client";

import { ProbBar } from "./ProbBar";
import type { SeriesOutcomeProbabilities } from "@/lib/types";

interface SeriesOutcomeCardProps {
  probs: SeriesOutcomeProbabilities;
}

export function SeriesOutcomeCard({ probs }: SeriesOutcomeCardProps) {
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
        Series Win Probability (Monte Carlo · 25k sims)
      </h2>

      <ProbBar
        label="Knicks win series"
        value={probs.NYK_wins_series}
        color="nyk"
        delay={0.2}
      />

      <div className="mb-4 mt-1 space-y-0.5">
        {[
          { label: "Knicks in 5", val: probs.NYK_in_5 },
          { label: "Knicks in 6", val: probs.NYK_in_6 },
          { label: "Knicks in 7", val: probs.NYK_in_7 },
        ].map((row) => (
          <div
            key={row.label}
            className="flex justify-between border-b py-1.5 text-sm last:border-0"
            style={{ borderColor: "rgba(255,255,255,0.05)" }}
          >
            <span style={{ color: "#f0f4fa" }}>{row.label}</span>
            <span
              style={{
                fontFamily:
                  "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                fontWeight: 700,
                color: "#F58426",
              }}
            >
              {(row.val * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>

      <ProbBar
        label="Spurs win series"
        value={probs.SAS_wins_series}
        color="sas"
        delay={0.4}
      />

      <div className="mt-1 space-y-0.5">
        {[
          { label: "Spurs in 6", val: probs.SAS_in_6 },
          { label: "Spurs in 7", val: probs.SAS_in_7 },
        ].map((row) => (
          <div
            key={row.label}
            className="flex justify-between border-b py-1.5 text-sm last:border-0"
            style={{ borderColor: "rgba(255,255,255,0.05)" }}
          >
            <span style={{ color: "#f0f4fa" }}>{row.label}</span>
            <span
              style={{
                fontFamily:
                  "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                fontWeight: 700,
                color: "#C4CED4",
              }}
            >
              {(row.val * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
