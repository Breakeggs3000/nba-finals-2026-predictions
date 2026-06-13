"use client";

import type { GamePrediction, OddsComparison } from "@/lib/types";
import { ProbBar } from "./ProbBar";
import { EdgeBadge } from "./EdgeBadge";

interface NextGameCardProps {
  game: GamePrediction;
}

export function NextGameCard({ game }: NextGameCardProps) {
  const cmp: OddsComparison | null = game.odds_comparison;

  return (
    <section
      className="rounded-2xl border p-6 backdrop-blur-md"
      style={{
        background: "rgba(18,24,38,0.85)",
        borderColor: "rgba(245,132,38,0.3)",
        borderLeft: "4px solid #F58426",
      }}
    >
      {/* Title */}
      <div className="mb-1 flex items-center gap-3">
        <h2
          style={{
            fontFamily: "var(--font-bebas-neue), 'Bebas Neue', sans-serif",
            fontSize: "1.5rem",
            letterSpacing: "0.05em",
            color: "#F58426",
          }}
        >
          Game {game.game_number} — Next Up
        </h2>
        <span
          className="rounded-full px-2.5 py-0.5 text-xs font-bold uppercase tracking-wide"
          style={{
            background: "rgba(212,175,55,0.15)",
            color: "#f5d76e",
          }}
        >
          June 13, 2026
        </span>
      </div>
      <p className="mb-5 text-sm" style={{ color: "#8b9cb3" }}>
        {game.away_team} @ {game.home_team} · San Antonio
      </p>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        {/* Win probability */}
        <div>
          <h3
            className="mb-3 text-xs font-semibold uppercase tracking-widest"
            style={{ color: "#8b9cb3" }}
          >
            Win Probability
          </h3>
          <ProbBar
            label={`${game.away_team} (Away)`}
            value={game.away_win_prob}
            color={game.away_team === "NYK" ? "nyk" : "sas"}
            delay={0.2}
          />
          <ProbBar
            label={`${game.home_team} (Home)`}
            value={game.home_win_prob}
            color={game.home_team === "NYK" ? "nyk" : "sas"}
            delay={0.35}
          />
        </div>

        {/* Predicted score & spread */}
        <div>
          <h3
            className="mb-3 text-xs font-semibold uppercase tracking-widest"
            style={{ color: "#8b9cb3" }}
          >
            Predicted Score
          </h3>
          <div
            className="mb-3 text-center text-2xl font-bold"
            style={{
              fontFamily:
                "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
            }}
          >
            <span style={{ color: "#006BB6" }}>
              {game.away_team === "NYK"
                ? Math.round(game.predicted_away_score)
                : Math.round(game.predicted_home_score)}
            </span>
            <span className="mx-3" style={{ color: "#8b9cb3" }}>
              —
            </span>
            <span style={{ color: "#C4CED4" }}>
              {game.home_team === "SAS"
                ? Math.round(game.predicted_home_score)
                : Math.round(game.predicted_away_score)}
            </span>
          </div>
          <div
            className="mb-2 text-center text-sm"
            style={{ color: "#8b9cb3" }}
          >
            NYK {" "}
            {Math.round(
              game.away_team === "NYK"
                ? game.predicted_away_score
                : game.predicted_home_score
            )}{" "}
            · SAS{" "}
            {Math.round(
              game.home_team === "SAS"
                ? game.predicted_home_score
                : game.predicted_away_score
            )}
          </div>
          <div className="text-center text-xs" style={{ color: "#8b9cb3" }}>
            Spread:{" "}
            <span
              style={{
                fontFamily:
                  "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                fontWeight: 700,
                color: "#f0f4fa",
              }}
            >
              {game.predicted_margin > 0 ? "+" : ""}
              {game.predicted_margin.toFixed(1)} (home)
            </span>
          </div>
        </div>
      </div>

      {/* Model vs Market */}
      {game.market_home_prob != null && cmp && (
        <div
          className="mt-5 rounded-xl border p-4"
          style={{
            background: "rgba(30,42,62,0.9)",
            borderColor: "rgba(255,255,255,0.06)",
          }}
        >
          <div className="mb-3 flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: "#8b9cb3" }}>
              Model vs Market ({game.home_team})
            </span>
            <EdgeBadge
              signal={cmp.signal}
              edgePick={cmp.edge_pick}
              edgeMagnitude={cmp.edge_magnitude}
            />
          </div>
          <div className="grid grid-cols-3 gap-3 text-center text-sm">
            <div>
              <div className="text-xs" style={{ color: "#8b9cb3" }}>
                Model
              </div>
              <div
                className="font-bold"
                style={{
                  fontFamily:
                    "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                  color: "#f5d76e",
                }}
              >
                {(game.home_win_prob * 100).toFixed(1)}%
              </div>
            </div>
            <div>
              <div className="text-xs" style={{ color: "#8b9cb3" }}>
                Market
              </div>
              <div
                className="font-bold"
                style={{
                  fontFamily:
                    "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                }}
              >
                {(game.market_home_prob * 100).toFixed(1)}%
              </div>
            </div>
            <div>
              <div className="text-xs" style={{ color: "#8b9cb3" }}>
                Edge
              </div>
              <div
                className="font-bold"
                style={{
                  fontFamily:
                    "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                  color:
                    cmp.signal === "value"
                      ? "#3dd68c"
                      : cmp.signal === "lean"
                      ? "#F58426"
                      : "#8b9cb3",
                }}
              >
                {cmp.edge_pick} {cmp.home_edge >= 0 ? "+" : ""}
                {(
                  (cmp.edge_pick === game.home_team
                    ? cmp.home_edge
                    : cmp.away_edge) * 100
                ).toFixed(1)}
                pp
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
