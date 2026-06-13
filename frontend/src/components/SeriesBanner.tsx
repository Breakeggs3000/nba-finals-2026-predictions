"use client";

import Image from "next/image";
import type { SeriesStatus } from "@/lib/types";

const KNICKS_LOGO =
  "https://cdn.nba.com/logos/nba/1610612752/global/L/logo.svg";
const SPURS_LOGO =
  "https://cdn.nba.com/logos/nba/1610612759/global/L/logo.svg";

const NYK_PLAYERS = [
  { id: "1628973", name: "Jalen Brunson" },
  { id: "1626157", name: "Karl-Anthony Towns" },
  { id: "1628384", name: "OG Anunoby" },
];
const SAS_PLAYERS = [
  { id: "1641705", name: "Victor Wembanyama" },
  { id: "1628368", name: "De'Aaron Fox" },
  { id: "1630170", name: "Devin Vassell" },
];

interface SeriesBannerProps {
  status: SeriesStatus;
}

export function SeriesBanner({ status }: SeriesBannerProps) {
  return (
    <div className="animate-slide-up space-y-4" style={{ animationDelay: "0.35s" }}>
      {/* Score banner */}
      <div
        className="mx-auto flex max-w-2xl items-center justify-center gap-8 rounded-2xl border p-6 backdrop-blur-md"
        style={{
          background: "rgba(18,24,38,0.85)",
          borderColor: "rgba(255,255,255,0.08)",
        }}
      >
        {/* NYK */}
        <div className="flex flex-1 flex-col items-center gap-2 text-center">
          <div className="group relative h-20 w-20 transition-transform hover:scale-110">
            <Image
              src={KNICKS_LOGO}
              alt="New York Knicks"
              fill
              className="object-contain drop-shadow-xl"
              unoptimized
            />
          </div>
          <div
            style={{
              fontFamily: "var(--font-bebas-neue), 'Bebas Neue', sans-serif",
              fontSize: "1.4rem",
              letterSpacing: "0.05em",
              color: "#F58426",
            }}
          >
            Knicks
          </div>
          <div
            style={{
              fontFamily: "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
              fontSize: "clamp(2.5rem,8vw,3.5rem)",
              fontWeight: 700,
              lineHeight: 1,
              color: "#f0f4fa",
            }}
          >
            {status.nyk_wins}
          </div>
        </div>

        {/* Center */}
        <div className="text-center" style={{ color: "#8b9cb3" }}>
          <div className="mb-1 text-xs font-semibold uppercase tracking-widest">
            Best of 7
          </div>
          <div
            className="text-sm font-semibold"
            style={{ color: "#f5d76e" }}
          >
            {status.leader === "NYK" ? "NYK" : "SAS"} leads{" "}
            {status.nyk_wins}–{status.sas_wins}
          </div>
          <div className="mt-2 text-xs" style={{ color: "#8b9cb3" }}>
            Game 5 · Jun 13
          </div>
        </div>

        {/* SAS */}
        <div className="flex flex-1 flex-col items-center gap-2 text-center">
          <div className="group relative h-20 w-20 transition-transform hover:scale-110">
            <Image
              src={SPURS_LOGO}
              alt="San Antonio Spurs"
              fill
              className="object-contain drop-shadow-xl"
              unoptimized
            />
          </div>
          <div
            style={{
              fontFamily: "var(--font-bebas-neue), 'Bebas Neue', sans-serif",
              fontSize: "1.4rem",
              letterSpacing: "0.05em",
              color: "#C4CED4",
            }}
          >
            Spurs
          </div>
          <div
            style={{
              fontFamily: "var(--font-jetbrains-mono), 'JetBrains Mono', monospace",
              fontSize: "clamp(2.5rem,8vw,3.5rem)",
              fontWeight: 700,
              lineHeight: 1,
              color: "#f0f4fa",
            }}
          >
            {status.sas_wins}
          </div>
        </div>
      </div>

      {/* Player headshots row */}
      <div className="flex flex-wrap justify-center gap-8">
        {/* NYK players */}
        <div className="flex flex-col items-center gap-3">
          <span
            className="text-xs font-semibold uppercase tracking-widest"
            style={{ color: "#F58426" }}
          >
            New York Knicks
          </span>
          <div className="flex gap-2">
            {NYK_PLAYERS.map((p) => (
              <div
                key={p.id}
                title={p.name}
                className="group relative h-14 w-14 cursor-pointer overflow-hidden rounded-full border-2 transition-all hover:-translate-y-1"
                style={{
                  borderColor: "rgba(255,255,255,0.15)",
                  background: "rgba(30,42,62,0.9)",
                }}
              >
                <Image
                  src={`https://cdn.nba.com/headshots/nba/latest/260x190/${p.id}.png`}
                  alt={p.name}
                  fill
                  className="object-cover object-top"
                  unoptimized
                />
                <div
                  className="absolute inset-x-0 bottom-0 text-center"
                  style={{
                    background: "rgba(0,0,0,0.75)",
                    fontSize: "0.45rem",
                    padding: "1px 0",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {p.name.split(" ").pop()}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SAS players */}
        <div className="flex flex-col items-center gap-3">
          <span
            className="text-xs font-semibold uppercase tracking-widest"
            style={{ color: "#C4CED4" }}
          >
            San Antonio Spurs
          </span>
          <div className="flex gap-2">
            {SAS_PLAYERS.map((p) => (
              <div
                key={p.id}
                title={p.name}
                className="group relative h-14 w-14 cursor-pointer overflow-hidden rounded-full border-2 transition-all hover:-translate-y-1"
                style={{
                  borderColor: "rgba(255,255,255,0.15)",
                  background: "rgba(30,42,62,0.9)",
                }}
              >
                <Image
                  src={`https://cdn.nba.com/headshots/nba/latest/260x190/${p.id}.png`}
                  alt={p.name}
                  fill
                  className="object-cover object-top"
                  unoptimized
                />
                <div
                  className="absolute inset-x-0 bottom-0 text-center"
                  style={{
                    background: "rgba(0,0,0,0.75)",
                    fontSize: "0.45rem",
                    padding: "1px 0",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {p.name.split(" ").pop()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
