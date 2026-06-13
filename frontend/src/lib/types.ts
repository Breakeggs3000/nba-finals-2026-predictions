export interface OddsComparison {
  home_team: string;
  away_team: string;
  model_home_prob: number;
  market_home_prob: number;
  home_edge: number;
  away_edge: number;
  edge_pick: string;
  edge_magnitude: number;
  signal: "value" | "lean" | "neutral";
}

export interface GamePrediction {
  game_number: number;
  date: string;
  home_team: string;
  away_team: string;
  played: boolean;
  actual_home_pts: number | null;
  actual_away_pts: number | null;
  home_win_prob: number;
  away_win_prob: number;
  predicted_winner: string;
  predicted_margin: number;
  predicted_home_score: number;
  predicted_away_score: number;
  spread_probs: Record<string, number>;
  market_home_prob: number | null;
  market_away_prob: number | null;
  odds_source: string | null;
  odds_comparison: OddsComparison | null;
}

export interface ModelMetrics {
  cv_accuracy_mean?: number;
  validation_2026_playoffs_accuracy?: number;
  finals_played_games_accuracy?: number;
  train_games?: number;
  [key: string]: unknown;
}

export interface SeriesStatus {
  nyk_wins: number;
  sas_wins: number;
  leader: string;
}

export interface SeriesOutcomeProbabilities {
  NYK_in_5: number;
  NYK_in_6: number;
  NYK_in_7: number;
  SAS_in_6: number;
  SAS_in_7: number;
  NYK_wins_series: number;
  SAS_wins_series: number;
}

export interface SeriesOddsComparison {
  NYK: OddsComparison;
  model_NYK_series_prob: number;
  market_NYK_series_prob: number;
  market_SAS_series_prob: number;
  odds_source: string;
  is_demo: boolean;
}

export interface OddsMeta {
  mode: "live" | "demo";
  api_key_configured: boolean;
  fetched_at: string | null;
  live_event: unknown;
}

export interface PredictionsData {
  series_status: SeriesStatus;
  model_metrics: ModelMetrics;
  odds_meta: OddsMeta;
  series_outcome_probabilities: SeriesOutcomeProbabilities;
  series_odds_comparison: SeriesOddsComparison;
  games: GamePrediction[];
  spread_lines: number[];
}
