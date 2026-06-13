"use client";

import { EdgeBadge } from "./EdgeBadge";
import type { GamePrediction } from "@/lib/types";

interface GameCardProps {
  game: GamePrediction;
  delay?: number;
}

const SPREAD_DISPLAY_LINES = [-3.5, -2.5, -1.5, 1.5, 2.5, 3.5];

export function GameCard({ game, delay = 0 }: GameCardProps) {
  const isPlayed = game.played;

  return (
    <div
      className="animate-slide-up rounded-2xl border p-5 backdrop-blur-md"
      style={{
        background: "rgba(18,24,38,0.85)",
        borderColor: "rgba(255,255,255,0.08)",
        borderLeft: isPlayed
          ? "3px solid #3dd68c"
          : "3px solid #f5d76e",
        animationDelay: `${delay}s`,
      }}
    >
      {/* Header */}
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <span className="text-base font-bold" style={{ color: "#f0f4fa" }}>
          Game {game.game_number}
        </span>
        <span
          className="rounded-full px-2.5 py-0.5 text-xs font-bold uppercase tracking-wide"
          style={
            isPlayed
              ? {
                  background: "rgba(61,214,140,0.15)",
                  color: "#3dd68c",
                }
              : {
                  background: "rgba(212,175,55,0.15)",
                  color: "#f5d76e",
                }
          }
        >
          {isPlayed ? "Final" : "Upcoming"}
        </span>
      </div>

      {/* Matchup info */}
      <div className="mb-1 text-sm" style={{ color: "#f0f4fa" }}>
        {game.away_team} @ {game.home_team} —{" "}
        <span style={{ color: "#8b9cb3" }}>{game.date}</span>
      </div>

      {isPlayed && (
        <div
          className="mb-1 text-sm"
          style={{
            fontFamily:
              "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
            color: "#3dd68c",
          }}
        >
          Final: {game.away_team} {game.actual_away_pts} — {game.home_team}{" "}
          {game.actual_home_pts}
        </div>
      )}

      <div
        className="mb-3 text-sm"
        style={{
          fontFamily:
            "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
          color: "#8b9cb3",
        }}
      >
        Predicted: {game.away_team} {Math.round(game.predicted_away_score)} —{" "}
        {game.home_team} {Math.round(game.predicted_home_score)}
        <span className="ml-2">
          ({game.predicted_margin > 0 ? "+" : ""}
          {game.predicted_margin.toFixed(1)})
        </span>
      </div>

      {/* Win prob boxes */}
      <div className="mb-3 grid grid-cols-2 gap-2">
        <div
          className="rounded-xl p-3 text-center"
          style={{ background: "rgba(30,42,62,0.9)" }}
        >
          <div className="text-xs" style={{ color: "#8b9cb3" }}>
            {game.away_team}
          </div>
          <div
            className="text-xl font-bold"
            style={{
              fontFamily:
                "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
              color: game.away_team === "NYK" ? "#006BB6" : "#C4CED4",
            }}
          >
            {(game.away_win_prob * 100).toFixed(1)}%
          </div>
        </div>
        <div
          className="rounded-xl p-3 text-center"
          style={{ background: "rgba(30,42,62,0.9)" }}
        >
          <div className="text-xs" style={{ color: "#8b9cb3" }}>
            {game.home_team}
          </div>
          <div
            className="text-xl font-bold"
            style={{
              fontFamily:
                "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
              color: game.home_team === "NYK" ? "#006BB6" : "#C4CED4",
            }}
          >
            {(game.home_win_prob * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Market odds comparison */}
      {game.market_home_prob != null && game.odds_comparison && (
        <div className="mb-3 grid grid-cols-3 gap-2 text-xs">
          <div
            className="rounded-lg p-2 text-center"
            style={{ background: "rgba(255,255,255,0.04)" }}
          >
            <div className="mb-0.5" style={{ color: "#8b9cb3" }}>
              Model {game.home_team}
            </div>
            <div
              style={{
                fontFamily:
                  "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                fontWeight: 700,
              }}
            >
              {(game.home_win_prob * 100).toFixed(1)}%
            </div>
          </div>
          <div
            className="rounded-lg p-2 text-center"
            style={{ background: "rgba(255,255,255,0.04)" }}
          >
            <div className="mb-0.5" style={{ color: "#8b9cb3" }}>
              Market {game.home_team}
            </div>
            <div
              style={{
                fontFamily:
                  "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                fontWeight: 700,
              }}
            >
              {(game.market_home_prob * 100).toFixed(1)}%
            </div>
          </div>
          <div
            className="rounded-lg p-2 text-center"
            style={{ background: "rgba(255,255,255,0.04)" }}
          >
            <div className="mb-0.5" style={{ color: "#8b9cb3" }}>
              Edge
            </div>
            <div
              style={{
                fontFamily:
                  "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                fontWeight: 700,
                color:
                  game.odds_comparison.signal === "value"
                    ? "#3dd68c"
                    : game.odds_comparison.signal === "lean"
                    ? "#F58426"
                    : "#8b9cb3",
              }}
            >
              {game.odds_comparison.edge_pick}{" "}
              {game.odds_comparison.edge_magnitude > 0 ? "+" : ""}
              {(game.odds_comparison.edge_magnitude * 100).toFixed(1)}pp
            </div>
          </div>
        </div>
      )}

      {/* Pick */}
      <div className="mb-2 text-sm" style={{ color: "#8b9cb3" }}>
        Pick:{" "}
        <strong style={{ color: "#f0f4fa" }}>{game.predicted_winner}</strong>
      </div>

      {/* Odds comparison badge */}
      {game.odds_comparison && (
        <div className="mb-3">
          <EdgeBadge
            signal={game.odds_comparison.signal}
            edgePick={game.odds_comparison.edge_pick}
            edgeMagnitude={game.odds_comparison.edge_magnitude}
          />
        </div>
      )}

      {/* Spread cover probs */}
      <div className="text-xs" style={{ color: "#8b9cb3" }}>
        Home team spread cover probability
      </div>
      <div className="mt-1.5 flex flex-wrap gap-1.5">
        {SPREAD_DISPLAY_LINES.map((line) => {
          const key = `home_${line > 0 ? "+" : ""}${line.toFixed(1)}`;
          const prob = game.spread_probs[key];
          if (prob == null) return null;
          return (
            <div
              key={key}
              className="rounded-md px-2 py-1.5 text-center"
              style={{
                background: "rgba(30,42,62,0.9)",
                minWidth: "64px",
              }}
            >
              <div style={{ color: "#8b9cb3", fontSize: "0.65rem" }}>
                {game.home_team} {line > 0 ? "+" : ""}
                {line.toFixed(1)}
              </div>
              <div
                style={{
                  fontFamily:
                    "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                  fontWeight: 700,
                  fontSize: "0.9rem",
                }}
              >
                {Math.round(prob * 100)}%
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
