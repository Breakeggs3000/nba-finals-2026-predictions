"use client";

interface EdgeBadgeProps {
  signal: "value" | "lean" | "neutral";
  edgePick: string;
  edgeMagnitude: number;
}

export function EdgeBadge({ signal, edgePick, edgeMagnitude }: EdgeBadgeProps) {
  const styles = {
    value: {
      background: "rgba(61,214,140,0.2)",
      color: "#3dd68c",
    },
    lean: {
      background: "rgba(245,132,38,0.2)",
      color: "#F58426",
    },
    neutral: {
      background: "rgba(139,156,179,0.2)",
      color: "#8b9cb3",
    },
  };

  return (
    <span
      className="inline-block rounded px-2 py-0.5 text-xs font-bold uppercase tracking-wide"
      style={styles[signal]}
    >
      {edgePick} edge {edgeMagnitude >= 0 ? "+" : ""}
      {(edgeMagnitude * 100).toFixed(1)}pp · {signal}
    </span>
  );
}
