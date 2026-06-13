"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { SeriesOutcomeProbabilities } from "@/lib/types";

interface SeriesWinChartProps {
  probs: SeriesOutcomeProbabilities;
}

export function SeriesWinChart({ probs }: SeriesWinChartProps) {
  const data = [
    { name: "NYK in 5", value: probs.NYK_in_5 * 100, team: "NYK" },
    { name: "NYK in 6", value: probs.NYK_in_6 * 100, team: "NYK" },
    { name: "NYK in 7", value: probs.NYK_in_7 * 100, team: "NYK" },
    { name: "SAS in 6", value: probs.SAS_in_6 * 100, team: "SAS" },
    { name: "SAS in 7", value: probs.SAS_in_7 * 100, team: "SAS" },
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
        Series Outcome Breakdown
      </h2>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} barCategoryGap="25%">
          <XAxis
            dataKey="name"
            tick={{ fill: "#8b9cb3", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#8b9cb3", fontSize: 11 }}
            tickFormatter={(v) => `${v.toFixed(0)}%`}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip
            contentStyle={{
              background: "rgba(18,24,38,0.95)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "8px",
              color: "#f0f4fa",
              fontSize: "12px",
            }}
            formatter={(value) => [`${Number(value).toFixed(1)}%`, "Probability"]}
            cursor={{ fill: "rgba(255,255,255,0.04)" }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.team === "NYK" ? "#006BB6" : "#555"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
