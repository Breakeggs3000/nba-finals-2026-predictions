"use client";

import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { retrain } from "@/lib/api";

interface RefreshButtonProps {
  lastUpdated: string | null;
  onRefreshed: () => void;
}

export function RefreshButton({ lastUpdated, onRefreshed }: RefreshButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleRetrain() {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await retrain();
      setSuccess(true);
      onRefreshed();
      setTimeout(() => setSuccess(false), 3000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Retrain failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border p-5 backdrop-blur-md"
      style={{
        background: "rgba(18,24,38,0.85)",
        borderColor: "rgba(255,255,255,0.08)",
      }}
    >
      <div>
        <div className="mb-0.5 text-sm font-semibold" style={{ color: "#f0f4fa" }}>
          Retrain Models
        </div>
        <div className="text-xs" style={{ color: "#8b9cb3" }}>
          {lastUpdated
            ? `Last updated: ${lastUpdated.slice(0, 16).replace("T", " ")} UTC`
            : "Fetches fresh NBA API data and retrains"}
        </div>
        {error && (
          <div className="mt-1 text-xs" style={{ color: "#f07178" }}>
            {error}
          </div>
        )}
        {success && (
          <div className="mt-1 text-xs" style={{ color: "#3dd68c" }}>
            Models retrained successfully!
          </div>
        )}
      </div>
      <button
        onClick={handleRetrain}
        disabled={loading}
        className="flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all hover:opacity-90 disabled:opacity-50"
        style={{
          background: "linear-gradient(135deg, #006BB6, #F58426)",
          color: "#fff",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        <RefreshCw
          className={`h-4 w-4 ${loading ? "animate-spin" : ""}`}
        />
        {loading ? "Retraining…" : "Retrain Now"}
      </button>
    </div>
  );
}
