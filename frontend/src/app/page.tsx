"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchPredictions } from "@/lib/api";
import type { PredictionsData } from "@/lib/types";

import { BgMesh } from "@/components/BgMesh";
import { HeroBanner } from "@/components/HeroBanner";
import { SeriesBanner } from "@/components/SeriesBanner";
import { ModelAccuracyCard } from "@/components/ModelAccuracyCard";
import { SeriesOutcomeCard } from "@/components/SeriesOutcomeCard";
import { SeriesWinChart } from "@/components/SeriesWinChart";
import { NextGameCard } from "@/components/NextGameCard";
import { OddsComparisonSection } from "@/components/OddsComparisonSection";
import { GameCard } from "@/components/GameCard";
import { RefreshButton } from "@/components/RefreshButton";

export default function HomePage() {
  const [data, setData] = useState<PredictionsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      const d = await fetchPredictions();
      setData(d);
      setLastFetch(new Date());
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Failed to connect to backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    // Auto-refresh every 60 seconds
    const interval = setInterval(load, 60_000);
    return () => clearInterval(interval);
  }, [load]);

  return (
    <>
      <BgMesh />

      <main className="relative z-10 mx-auto max-w-5xl px-4 pb-16">
        {/* Loading state */}
        {loading && !data && (
          <div className="flex min-h-screen flex-col items-center justify-center gap-4">
            <div
              className="h-12 w-12 animate-spin rounded-full border-4"
              style={{
                borderColor: "rgba(255,255,255,0.1)",
                borderTopColor: "#006BB6",
              }}
            />
            <p style={{ color: "#8b9cb3" }}>Loading predictions…</p>
          </div>
        )}

        {/* Error state */}
        {error && !data && (
          <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
            <div
              className="rounded-2xl border p-8"
              style={{
                background: "rgba(240,113,120,0.1)",
                borderColor: "rgba(240,113,120,0.3)",
              }}
            >
              <div className="mb-3 text-4xl">⚠️</div>
              <h2
                className="mb-2 text-lg font-bold"
                style={{ color: "#f07178" }}
              >
                Backend Unavailable
              </h2>
              <p
                className="mb-4 max-w-sm text-sm"
                style={{ color: "#8b9cb3" }}
              >
                {error}
              </p>
              <button
                onClick={load}
                className="rounded-xl px-5 py-2 text-sm font-semibold"
                style={{ background: "#006BB6", color: "#fff" }}
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Dashboard */}
        {data && (
          <div className="space-y-6">
            {/* Hero */}
            <HeroBanner oddsMeta={data.odds_meta} />

            {/* Series banner */}
            <SeriesBanner status={data.series_status} />

            {/* Next game spotlight */}
            {(() => {
              const nextGame = data.games.find((g) => !g.played);
              return nextGame ? <NextGameCard game={nextGame} /> : null;
            })()}

            {/* 2-col cards */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <ModelAccuracyCard metrics={data.model_metrics} />
              <SeriesOutcomeCard probs={data.series_outcome_probabilities} />
            </div>

            {/* Series win chart */}
            <SeriesWinChart probs={data.series_outcome_probabilities} />

            {/* Odds comparison */}
            <OddsComparisonSection soc={data.series_odds_comparison} />

            {/* All games */}
            <section>
              <h2
                className="mb-4"
                style={{
                  fontFamily:
                    "var(--font-bebas-neue), 'Bebas Neue', sans-serif",
                  fontSize: "1.75rem",
                  letterSpacing: "0.04em",
                  color: "#f0f4fa",
                }}
              >
                Game-by-Game Predictions
              </h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {data.games.map((game, i) => (
                  <GameCard
                    key={game.game_number}
                    game={game}
                    delay={0.65 + i * 0.08}
                  />
                ))}
              </div>
            </section>

            {/* Refresh button */}
            <RefreshButton
              lastUpdated={data.odds_meta.fetched_at}
              onRefreshed={load}
            />

            {/* Footer */}
            <footer
              className="border-t pt-6 text-center text-xs"
              style={{
                borderColor: "rgba(255,255,255,0.08)",
                color: "#8b9cb3",
              }}
            >
              Calibrated HistGradientBoosting + Logistic blend · Trained on
              2021–2025 playoffs ·{" "}
              {lastFetch
                ? `Refreshed ${lastFetch.toLocaleTimeString()}`
                : "—"}{" "}
              ·{" "}
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/predictions`}
                target="_blank"
                rel="noreferrer"
                style={{ color: "#f5d76e" }}
                className="hover:underline"
              >
                JSON API
              </a>
            </footer>
          </div>
        )}
      </main>
    </>
  );
}
