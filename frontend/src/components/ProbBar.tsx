"use client";

interface ProbBarProps {
  label: string;
  value: number;
  color: "nyk" | "sas" | "gold" | "market";
  delay?: number;
}

const colorMap = {
  nyk: "linear-gradient(90deg, #006BB6, #F58426)",
  sas: "linear-gradient(90deg, #555, #C4CED4)",
  gold: "linear-gradient(90deg, #d4af37, #f5d76e)",
  market: "linear-gradient(90deg, #4a5568, #718096)",
};

export function ProbBar({ label, value, color, delay = 0 }: ProbBarProps) {
  const pct = Math.round(value * 100 * 10) / 10;
  return (
    <div className="mb-2">
      <div className="mb-1 flex justify-between text-sm">
        <span style={{ color: "#f0f4fa" }}>{label}</span>
        <span
          style={{
            fontFamily: "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
            fontWeight: 700,
          }}
        >
          {pct.toFixed(1)}%
        </span>
      </div>
      <div
        className="h-2.5 overflow-hidden rounded-full"
        style={{ background: "rgba(30,42,62,0.9)" }}
      >
        <div
          className="animate-fill-bar h-full rounded-full"
          style={{
            width: `${pct}%`,
            background: colorMap[color],
            animationDelay: `${delay}s`,
          }}
        />
      </div>
    </div>
  );
}
