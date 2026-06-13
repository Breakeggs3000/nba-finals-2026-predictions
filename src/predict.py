"""Generate game-by-game and series-level predictions for the 2026 NBA Finals."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.data_loader import (
    FEATURE_COLUMNS,
    FINALS_TEAMS,
    VALIDATION_SEASON,
    _h2h_win_rate,
    _series_wins_before,
    _team_history_before,
    _team_points_for_against,
    _team_recent_stats,
    _team_win_rate,
    _rest_days,
    load_or_fetch_data,
)
from src.odds import compare_model_vs_market, get_odds_comparison

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
WINNER_MODEL_PATH = MODEL_DIR / "winner_model.joblib"
MARGIN_MODEL_PATH = MODEL_DIR / "margin_model.joblib"
METRICS_PATH = MODEL_DIR / "training_metrics.json"

FINALS_SCHEDULE = [
    {"game": 1, "date": "2026-06-03", "home": "SAS", "away": "NYK", "played": True},
    {"game": 2, "date": "2026-06-05", "home": "SAS", "away": "NYK", "played": True},
    {"game": 3, "date": "2026-06-08", "home": "NYK", "away": "SAS", "played": True},
    {"game": 4, "date": "2026-06-10", "home": "NYK", "away": "SAS", "played": True},
    {"game": 5, "date": "2026-06-13", "home": "SAS", "away": "NYK", "played": False},
    {"game": 6, "date": "2026-06-16", "home": "NYK", "away": "SAS", "played": False},
    {"game": 7, "date": "2026-06-19", "home": "SAS", "away": "NYK", "played": False},
]

SPREAD_LINES = [-7.5, -5.5, -3.5, -2.5, -1.5, 1.5, 2.5, 3.5, 5.5, 7.5]
SIMULATIONS = 25_000


@dataclass
class GamePrediction:
    game_number: int
    date: str
    home_team: str
    away_team: str
    played: bool
    actual_home_pts: int | None
    actual_away_pts: int | None
    home_win_prob: float
    away_win_prob: float
    predicted_winner: str
    predicted_margin: float
    predicted_home_score: float
    predicted_away_score: float
    spread_probs: dict[str, float]
    market_home_prob: float | None = None
    market_away_prob: float | None = None
    odds_source: str | None = None
    odds_comparison: dict | None = None


def _load_models():
    if not WINNER_MODEL_PATH.exists() or not MARGIN_MODEL_PATH.exists():
        raise FileNotFoundError(
            "Models not found. Run: python3 -m src.train"
        )
    winner_artifact = joblib.load(WINNER_MODEL_PATH)
    margin_model = joblib.load(MARGIN_MODEL_PATH)
    return winner_artifact, margin_model


def _predict_home_win_prob(winner_artifact, X: np.ndarray) -> float:
    if isinstance(winner_artifact, dict):
        hgb_probs = winner_artifact["hgb"].predict_proba(X)[:, 1]
        lr_probs = winner_artifact["lr"].predict_proba(X)[:, 1]
        w = winner_artifact["blend_weight"]
        return float(w * hgb_probs + (1 - w) * lr_probs)
    return float(winner_artifact.predict_proba(X)[0, 1])


def _feature_row_for_game(
    games: pd.DataFrame,
    home: str,
    away: str,
    game_date: pd.Timestamp,
) -> dict:
    home_hist = _team_history_before(games, home, game_date)
    away_hist = _team_history_before(games, away, game_date)
    home_ppg, home_papg = _team_points_for_against(home_hist, home)
    away_ppg, away_papg = _team_points_for_against(away_hist, away)
    home_wr = _team_win_rate(home_hist, home)
    away_wr = _team_win_rate(away_hist, away)
    home_rest = _rest_days(games, home, game_date)
    away_rest = _rest_days(games, away, game_date)
    home_series, away_series = _series_wins_before(games, home, away, game_date)

    home_h2h, away_h2h = _h2h_win_rate(games, home, away, game_date)
    home_recent = _team_recent_stats(home_hist, home)
    away_recent = _team_recent_stats(away_hist, away)

    return {
        "ppg_diff": home_ppg - away_ppg,
        "papg_diff": away_papg - home_papg,
        "win_rate_diff": home_wr - away_wr,
        "rest_diff": home_rest - away_rest,
        "series_wins_diff": home_series - away_series,
        "recent_win_rate_diff": home_recent["win_rate"] - away_recent["win_rate"],
        "recent_margin_diff": home_recent["margin"] - away_recent["margin"],
        "fg_pct_diff": home_recent["fg_pct"] - away_recent["fg_pct"],
        "fg3_pct_diff": home_recent["fg3_pct"] - away_recent["fg3_pct"],
        "reb_diff": home_recent["reb"] - away_recent["reb"],
        "ast_diff": home_recent["ast"] - away_recent["ast"],
        "tov_diff": away_recent["tov"] - home_recent["tov"],
        "h2h_win_rate_diff": home_h2h - away_h2h,
        "home_court": 1,
        "is_finals": 1,
    }


def _spread_cover_probs(home_margin_samples: np.ndarray, lines: list[float]) -> dict[str, float]:
    """Probability home team covers each spread line (negative = home favored)."""
    probs = {}
    for line in lines:
        key = f"home_{line:+.1f}"
        probs[key] = float(np.mean(home_margin_samples > line))
    return probs


def _simulate_margins(predicted_margin: float, rng: np.random.Generator) -> np.ndarray:
    """Sample game margins around model prediction with playoff-like variance."""
    noise = rng.normal(0, 11.5, SIMULATIONS)
    return predicted_margin + noise


def predict_single_game(
    games: pd.DataFrame,
    winner_artifact,
    margin_model,
    schedule_entry: dict,
    actual_scores: dict | None = None,
    game_odds: dict | None = None,
) -> GamePrediction:
    home = schedule_entry["home"]
    away = schedule_entry["away"]
    game_date = pd.Timestamp(schedule_entry["date"])
    features = _feature_row_for_game(games, home, away, game_date)
    X = np.array([[features[c] for c in FEATURE_COLUMNS]])

    home_win_prob = _predict_home_win_prob(winner_artifact, X)
    predicted_margin = float(margin_model.predict(X)[0])
    rng = np.random.default_rng(42 + schedule_entry["game"])
    margin_samples = _simulate_margins(predicted_margin, rng)

    avg_total = features["ppg_diff"] + 220  # rough total from both teams
    predicted_home = (avg_total + predicted_margin) / 2
    predicted_away = (avg_total - predicted_margin) / 2

    actual_home = actual_away = None
    if actual_scores and schedule_entry["game"] in actual_scores:
        actual_home, actual_away = actual_scores[schedule_entry["game"]]

    spread_probs = _spread_cover_probs(margin_samples, SPREAD_LINES)

    market_home = market_away = odds_source = None
    odds_comparison = None
    if game_odds:
        market_home = game_odds.get("home_win_prob")
        market_away = game_odds.get("away_win_prob")
        odds_source = game_odds.get("source")
        if market_home is not None:
            odds_comparison = compare_model_vs_market(
                home_win_prob, market_home, home, away
            )

    return GamePrediction(
        game_number=schedule_entry["game"],
        date=schedule_entry["date"],
        home_team=home,
        away_team=away,
        played=schedule_entry["played"],
        actual_home_pts=actual_home,
        actual_away_pts=actual_away,
        home_win_prob=round(home_win_prob, 4),
        away_win_prob=round(1 - home_win_prob, 4),
        predicted_winner=home if home_win_prob >= 0.5 else away,
        predicted_margin=round(predicted_margin, 1),
        predicted_home_score=round(predicted_home, 1),
        predicted_away_score=round(predicted_away, 1),
        spread_probs={k: round(v, 4) for k, v in spread_probs.items()},
        market_home_prob=market_home,
        market_away_prob=market_away,
        odds_source=odds_source,
        odds_comparison=odds_comparison,
    )


def _simulate_series(
    game_predictions: list[GamePrediction],
    nyk_wins: int = 3,
    sas_wins: int = 1,
    sims: int = SIMULATIONS,
) -> dict:
    """Monte Carlo series outcomes from remaining game win probabilities."""
    rng = np.random.default_rng(123)
    outcomes = {
        "NYK_in_5": 0,
        "NYK_in_6": 0,
        "NYK_in_7": 0,
        "SAS_in_6": 0,
        "SAS_in_7": 0,
    }

    remaining = [g for g in game_predictions if not g.played]
    if not remaining:
        return {k: 0.0 for k in outcomes}

    for _ in range(sims):
        n_w, s_w = nyk_wins, sas_wins
        for game in remaining:
            home, away = game.home_team, game.away_team
            p_home = game.home_win_prob
            home_wins = rng.random() < p_home
            winner = home if home_wins else away
            if winner == "NYK":
                n_w += 1
            else:
                s_w += 1
            if n_w == 4 or s_w == 4:
                break

        total_games = n_w + s_w
        if n_w == 4 and s_w == 1:
            outcomes["NYK_in_5"] += 1
        elif n_w == 4 and s_w == 2:
            outcomes["NYK_in_6"] += 1
        elif n_w == 4 and s_w == 3:
            outcomes["NYK_in_7"] += 1
        elif s_w == 4 and n_w == 3:
            outcomes["SAS_in_7"] += 1
        elif s_w == 4 and n_w == 2:
            outcomes["SAS_in_6"] += 1

    return {k: round(v / sims, 4) for k, v in outcomes.items()}


def get_finals_actual_scores(games: pd.DataFrame) -> dict[int, tuple[int, int]]:
    finals = games[
        (games["season"] == VALIDATION_SEASON)
        & (games["home_team"].isin(FINALS_TEAMS))
        & (games["away_team"].isin(FINALS_TEAMS))
    ].sort_values("game_date")

    scores: dict[int, tuple[int, int]] = {}
    for i, (_, row) in enumerate(finals.iterrows(), start=1):
        scores[i] = (int(row["home_pts"]), int(row["away_pts"]))
    return scores


def generate_predictions() -> dict:
    games, _ = load_or_fetch_data()
    winner_artifact, margin_model = _load_models()
    actual_scores = get_finals_actual_scores(games)

    metrics = {}
    if METRICS_PATH.exists():
        with open(METRICS_PATH) as f:
            metrics = json.load(f)

    schedule_for_odds = [
        {"game": e["game"], "home": e["home"], "away": e["away"]}
        for e in FINALS_SCHEDULE
    ]
    odds_data = get_odds_comparison(schedule_for_odds)
    odds_by_game = {g["game_number"]: g for g in odds_data["game_odds"]}

    game_preds = [
        predict_single_game(
            games,
            winner_artifact,
            margin_model,
            entry,
            actual_scores,
            odds_by_game.get(entry["game"]),
        )
        for entry in FINALS_SCHEDULE
    ]

    nyk_wins = sas_wins = 0
    for gnum, (hp, ap) in actual_scores.items():
        home = FINALS_SCHEDULE[gnum - 1]["home"]
        winner = home if hp > ap else FINALS_SCHEDULE[gnum - 1]["away"]
        if winner == "NYK":
            nyk_wins += 1
        else:
            sas_wins += 1

    series_probs = _simulate_series(game_preds, nyk_wins, sas_wins)
    nyk_series_prob = series_probs["NYK_in_5"] + series_probs["NYK_in_6"] + series_probs["NYK_in_7"]
    sas_series_prob = series_probs["SAS_in_6"] + series_probs["SAS_in_7"]

    series_odds = odds_data["series_odds"]
    series_comparison = {
        "NYK": compare_model_vs_market(
            nyk_series_prob,
            series_odds["NYK_win_prob"],
            "NYK",
            "SAS",
        ),
        "model_NYK_series_prob": round(nyk_series_prob, 4),
        "market_NYK_series_prob": series_odds["NYK_win_prob"],
        "market_SAS_series_prob": series_odds["SAS_win_prob"],
        "odds_source": series_odds["source"],
        "is_demo": series_odds.get("is_demo", True),
    }

    return {
        "series_status": {
            "nyk_wins": nyk_wins,
            "sas_wins": sas_wins,
            "leader": "NYK" if nyk_wins > sas_wins else "SAS",
        },
        "model_metrics": metrics,
        "odds_meta": {
            "mode": odds_data["mode"],
            "api_key_configured": odds_data["api_key_configured"],
            "fetched_at": odds_data["fetched_at"],
            "live_event": odds_data.get("live_event"),
        },
        "series_outcome_probabilities": {
            **series_probs,
            "NYK_wins_series": round(nyk_series_prob, 4),
            "SAS_wins_series": round(sas_series_prob, 4),
        },
        "series_odds_comparison": series_comparison,
        "games": [asdict(g) for g in game_preds],
        "spread_lines": SPREAD_LINES,
    }


if __name__ == "__main__":
    print(json.dumps(generate_predictions(), indent=2))
