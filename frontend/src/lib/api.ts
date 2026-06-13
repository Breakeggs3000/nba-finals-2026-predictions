import type { PredictionsData } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchPredictions(): Promise<PredictionsData> {
  const res = await fetch(`${API_BASE}/api/predictions`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function retrain(): Promise<{ metrics: unknown; predictions: PredictionsData }> {
  const res = await fetch(`${API_BASE}/api/retrain`, { method: "POST" });
  if (!res.ok) throw new Error(`Retrain error: ${res.status}`);
  return res.json();
}
