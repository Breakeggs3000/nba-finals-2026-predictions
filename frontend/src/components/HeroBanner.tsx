"use client";

import type { OddsMeta } from "@/lib/types";

interface HeroBannerProps {
  oddsMeta: OddsMeta;
}

export function HeroBanner({ oddsMeta }: HeroBannerProps) {
  const isLive = oddsMeta.mode === "live";

  return (
    <section className="animate-fade-in text-center px-4 pb-2 pt-10">
      {/* Finals badge */}
      <div
        className="animate-glow-pulse mx-auto mb-4 inline-flex items-center gap-2 rounded-full border px-4 py-1.5"
        style={{
          background: "linear-gradient(135deg, rgba(212,175,55,0.2), rgba(212,175,55,0.05))",
          borderColor: "rgba(212,175,55,0.35)",
          color: "#f5d76e",
        }}
      >
        <svg viewBox="0 0 24 24" className="h-4 w-4 fill-[#d4af37]">
          <path d="M12 2L15 8.5L22 9.5L17 14.5L18 22L12 18.5L6 22L7 14.5L2 9.5L9 8.5L12 2Z" />
        </svg>
        <span className="text-xs font-semibold tracking-widest uppercase">
          2026 NBA Finals
        </span>
      </div>

      {/* Title */}
      <h1
        className="animate-slide-up mb-2 leading-none"
        style={{
          fontFamily: "var(--font-bebas-neue), 'Bebas Neue', sans-serif",
          fontSize: "clamp(2.5rem, 8vw, 4.5rem)",
          letterSpacing: "0.04em",
          animationDelay: "0.1s",
        }}
      >
        <span style={{ color: "#f5d76e" }}>FINALS</span> PREDICTIONS
      </h1>

      {/* Subtitle */}
      <p
        className="animate-slide-up text-base"
        style={{ color: "#8b9cb3", animationDelay: "0.2s" }}
      >
        Machine learning model · Historical playoff data · Monte Carlo series
        simulation
      </p>

      {/* Odds mode badge */}
      <div
        className="animate-slide-up mt-3 inline-flex items-center gap-1.5 rounded-md border px-3 py-1 text-xs font-bold uppercase tracking-wider"
        style={{
          animationDelay: "0.3s",
          background: isLive
            ? "rgba(61,214,140,0.15)"
            : "rgba(245,132,38,0.15)",
          borderColor: isLive
            ? "rgba(61,214,140,0.3)"
            : "rgba(245,132,38,0.3)",
          color: isLive ? "#3dd68c" : "#F58426",
        }}
      >
        <span
          className="animate-glow-pulse h-1.5 w-1.5 rounded-full"
          style={{ background: "currentColor" }}
        />
        {isLive ? "Live Odds" : "Demo Odds"}
        {!oddsMeta.api_key_configured && !isLive && (
          <span className="ml-1 opacity-70">· Set ODDS_API_KEY for live lines</span>
        )}
      </div>
    </section>
  );
}
