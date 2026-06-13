"use client";

import { ProbBar } from "./ProbBar";
import { EdgeBadge } from "./EdgeBadge";
import type { SeriesOddsComparison } from "@/lib/types";

interface OddsComparisonSectionProps {
  soc: SeriesOddsComparison;
}

export function OddsComparisonSection({ soc }: OddsComparisonSectionProps) {
  return (
    <section
      className="rounded-2xl border p-6 backdrop-blur-md"
      style={{
        background: "rgba(18,24,38,0.85)",
        borderColor: "rgba(212,175,55,0.2)",
      }}
    >
      <h2
        style={{
          fontFamily: "var(--font-bebas-neue), 'Bebas Neue', sans-serif",
          fontSize: "1.5rem",
          letterSpacing: "0.05em",
          color: "#f5d76e",
          marginBottom: "0.25rem",
        }}
      >
        Model vs Market
      </h2>
      <p className="mb-5 text-xs" style={{ color: "#8b9cb3" }}>
        Series championship odds · {soc.odds_source}
      </p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {/* NYK */}
        <div
          className="rounded-xl p-4"
          style={{ background: "rgba(30,42,62,0.9)" }}
        >
          <h3
            className="mb-3 text-xs font-semibold uppercase tracking-widest"
            style={{ color: "#8b9cb3" }}
          >
            Knicks Win Series
          </h3>
          <ProbBar
            label="Model"
            value={soc.model_NYK_series_prob}
            color="gold"
            delay={0.3}
          />
          <ProbBar
            label="Market"
            value={soc.market_NYK_series_prob}
            color="market"
            delay={0.5}
          />
          <div className="mt-3">
            <EdgeBadge
              signal={soc.NYK.signal}
              edgePick={soc.NYK.edge_pick}
              edgeMagnitude={
                soc.NYK.edge_pick === "NYK"
                  ? soc.NYK.home_edge
                  : soc.NYK.away_edge
              }
            />
          </div>
        </div>

        {/* SAS */}
        <div
          className="rounded-xl p-4"
          style={{ background: "rgba(30,42,62,0.9)" }}
        >
          <h3
            className="mb-3 text-xs font-semibold uppercase tracking-widest"
            style={{ color: "#8b9cb3" }}
          >
            Spurs Win Series
          </h3>
          <ProbBar
            label="Model"
            value={1 - soc.model_NYK_series_prob}
            color="gold"
            delay={0.35}
          />
          <ProbBar
            label="Market"
            value={soc.market_SAS_series_prob}
            color="market"
            delay={0.55}
          />
          <div
            className="mt-3 flex justify-between border-t pt-3 text-sm"
            style={{ borderColor: "rgba(255,255,255,0.05)" }}
          >
            <span style={{ color: "#8b9cb3" }}>Edge magnitude</span>
            <span
              style={{
                fontFamily:
                  "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
                fontWeight: 700,
              }}
            >
              {(soc.NYK.edge_magnitude * 100).toFixed(1)}pp
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
