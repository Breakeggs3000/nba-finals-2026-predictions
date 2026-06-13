"""Fetch and prepare NBA playoff game data."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TRAIN_SEASONS = ["2021-22", "2022-23", "2023-24", "2024-25"]
VALIDATION_SEASON = "2025-26"
FINALS_TEAMS = {"NYK", "SAS"}


def fetch_playoff_games(seasons: list[str], pause: float = 0.6) -> pd.DataFrame:
    """Download playoff box-score rows from the NBA stats API."""
    frames: list[pd.DataFrame] = []
    for season in seasons:
        gf = leaguegamefinder.LeagueGameFinder(
            season_nullable=season,
            season_type_nullable="Playoffs",
            league_id_nullable="00",
        )
        df = gf.get_data_frames()[0]
        df["SEASON"] = season
        frames.append(df)
        time.sleep(pause)
    return pd.concat(frames, ignore_index=True)


def _parse_matchup(matchup: str) -> tuple[str, str, bool]:
    """Return (team, opponent, is_home) from a MATCHUP string like 'NYK vs. SAS'."""
    if " vs. " in matchup:
        team, opponent = matchup.split(" vs. ")
        return team.strip(), opponent.strip(), True
    if " @ " in matchup:
        team, opponent = matchup.split(" @ ")
        return team.strip(), opponent.strip(), False
    raise ValueError(f"Unknown matchup format: {matchup}")


def build_game_table(raw: pd.DataFrame) -> pd.DataFrame:
    """Collapse two team rows per game into one game-level record."""
    games: list[dict] = []
    for game_id, group in raw.groupby("GAME_ID"):
        if len(group) != 2:
            continue
        home_row = group[group["MATCHUP"].str.contains(" vs. ", regex=False)]
        away_row = group[group["MATCHUP"].str.contains(" @ ", regex=False)]
        if len(home_row) != 1 or len(away_row) != 1:
            continue

        home = home_row.iloc[0]
        away = away_row.iloc[0]
        home_team, _, _ = _parse_matchup(home["MATCHUP"])
        away_team, _, _ = _parse_matchup(away["MATCHUP"])

        games.append(
            {
                "game_id": game_id,
                "season": home["SEASON"],
                "game_date": pd.to_datetime(home["GAME_DATE"]),
                "home_team": home_team,
                "away_team": away_team,
                "home_pts": int(home["PTS"]),
                "away_pts": int(away["PTS"]),
                "home_win": int(home["WL"] == "W"),
                "margin": int(home["PTS"]) - int(away["PTS"]),
                "home_fg_pct": float(home["FG_PCT"]),
                "away_fg_pct": float(away["FG_PCT"]),
                "home_fg3_pct": float(home["FG3_PCT"]),
                "away_fg3_pct": float(away["FG3_PCT"]),
                "home_reb": int(home["REB"]),
                "away_reb": int(away["REB"]),
                "home_ast": int(home["AST"]),
                "away_ast": int(away["AST"]),
                "home_tov": int(home["TOV"]),
                "away_tov": int(away["TOV"]),
            }
        )

    table = pd.DataFrame(games).sort_values(["season", "game_date", "game_id"])
    return table.reset_index(drop=True)


def _team_history_before(
    games: pd.DataFrame, team: str, before_date: pd.Timestamp
) -> pd.DataFrame:
    mask = (
        (games["game_date"] < before_date)
        & ((games["home_team"] == team) | (games["away_team"] == team))
    )
    return games.loc[mask]


def _team_points_for_against(history: pd.DataFrame, team: str) -> tuple[float, float]:
    if history.empty:
        return 110.0, 110.0
    pts_for, pts_against = [], []
    for _, row in history.iterrows():
        if row["home_team"] == team:
            pts_for.append(row["home_pts"])
            pts_against.append(row["away_pts"])
        else:
            pts_for.append(row["away_pts"])
            pts_against.append(row["home_pts"])
    return float(sum(pts_for) / len(pts_for)), float(sum(pts_against) / len(pts_against))


def _team_win_rate(history: pd.DataFrame, team: str) -> float:
    if history.empty:
        return 0.5
    wins = 0
    for _, row in history.iterrows():
        if row["home_team"] == team:
            wins += row["home_win"]
        else:
            wins += 1 - row["home_win"]
    return wins / len(history)


def _team_recent_stats(
    history: pd.DataFrame, team: str, n: int = 5
) -> dict[str, float]:
    """Rolling averages for the last N playoff games."""
    defaults = {
        "win_rate": 0.5,
        "margin": 0.0,
        "fg_pct": 0.45,
        "fg3_pct": 0.35,
        "reb": 42.0,
        "ast": 24.0,
        "tov": 14.0,
    }
    if history.empty:
        return defaults

    recent = history.tail(n)
    wins, margins, fg, fg3, reb, ast, tov = [], [], [], [], [], [], []
    for _, row in recent.iterrows():
        if row["home_team"] == team:
            wins.append(row["home_win"])
            margins.append(row["margin"])
            fg.append(row["home_fg_pct"])
            fg3.append(row["home_fg3_pct"])
            reb.append(row["home_reb"])
            ast.append(row["home_ast"])
            tov.append(row["home_tov"])
        else:
            wins.append(1 - row["home_win"])
            margins.append(-row["margin"])
            fg.append(row["away_fg_pct"])
            fg3.append(row["away_fg3_pct"])
            reb.append(row["away_reb"])
            ast.append(row["away_ast"])
            tov.append(row["away_tov"])

    return {
        "win_rate": sum(wins) / len(wins),
        "margin": sum(margins) / len(margins),
        "fg_pct": sum(fg) / len(fg),
        "fg3_pct": sum(fg3) / len(fg3),
        "reb": sum(reb) / len(reb),
        "ast": sum(ast) / len(ast),
        "tov": sum(tov) / len(tov),
    }


def _h2h_win_rate(
    games: pd.DataFrame, team_a: str, team_b: str, before_date: pd.Timestamp
) -> tuple[float, float]:
    mask = (
        (games["game_date"] < before_date)
        & (
            ((games["home_team"] == team_a) & (games["away_team"] == team_b))
            | ((games["home_team"] == team_b) & (games["away_team"] == team_a))
        )
    )
    h2h = games.loc[mask]
    if h2h.empty:
        return 0.5, 0.5
    wins_a = wins_b = 0
    for _, row in h2h.iterrows():
        winner = row["home_team"] if row["home_win"] else row["away_team"]
        if winner == team_a:
            wins_a += 1
        else:
            wins_b += 1
    total = len(h2h)
    return wins_a / total, wins_b / total


def _series_wins_before(
    games: pd.DataFrame,
    team_a: str,
    team_b: str,
    before_date: pd.Timestamp,
) -> tuple[int, int]:
    mask = (
        (games["game_date"] < before_date)
        & (
            ((games["home_team"] == team_a) & (games["away_team"] == team_b))
            | ((games["home_team"] == team_b) & (games["away_team"] == team_a))
        )
    )
    series = games.loc[mask]
    wins_a = wins_b = 0
    for _, row in series.iterrows():
        winner = row["home_team"] if row["home_win"] else row["away_team"]
        if winner == team_a:
            wins_a += 1
        else:
            wins_b += 1
    return wins_a, wins_b


def _rest_days(history: pd.DataFrame, team: str, game_date: pd.Timestamp) -> float:
    team_games = history[history["game_date"] < game_date]
    if team_games.empty:
        return 3.0
    last = team_games["game_date"].max()
    return float((game_date - last).days)


def build_features(games: pd.DataFrame) -> pd.DataFrame:
    """Engineer pre-game features for each playoff game."""
    rows: list[dict] = []
    for _, game in games.iterrows():
        home, away = game["home_team"], game["away_team"]
        date = game["game_date"]

        home_hist = _team_history_before(games, home, date)
        away_hist = _team_history_before(games, away, date)

        home_ppg, home_papg = _team_points_for_against(home_hist, home)
        away_ppg, away_papg = _team_points_for_against(away_hist, away)

        home_wr = _team_win_rate(home_hist, home)
        away_wr = _team_win_rate(away_hist, away)

        home_rest = _rest_days(games, home, date)
        away_rest = _rest_days(games, away, date)

        home_series, away_series = _series_wins_before(games, home, away, date)
        is_finals = int({home, away} == FINALS_TEAMS)

        home_recent = _team_recent_stats(home_hist, home)
        away_recent = _team_recent_stats(away_hist, away)
        home_h2h, away_h2h = _h2h_win_rate(games, home, away, date)

        rows.append(
            {
                "game_id": game["game_id"],
                "season": game["season"],
                "game_date": date,
                "home_team": home,
                "away_team": away,
                "home_win": game["home_win"],
                "margin": game["margin"],
                "home_ppg": home_ppg,
                "away_ppg": away_ppg,
                "home_papg": home_papg,
                "away_papg": away_papg,
                "ppg_diff": home_ppg - away_ppg,
                "papg_diff": away_papg - home_papg,
                "home_win_rate": home_wr,
                "away_win_rate": away_wr,
                "win_rate_diff": home_wr - away_wr,
                "home_rest_days": home_rest,
                "away_rest_days": away_rest,
                "rest_diff": home_rest - away_rest,
                "home_series_wins": home_series,
                "away_series_wins": away_series,
                "series_wins_diff": home_series - away_series,
                "is_finals": is_finals,
                "home_court": 1,
                "recent_win_rate_diff": home_recent["win_rate"] - away_recent["win_rate"],
                "recent_margin_diff": home_recent["margin"] - away_recent["margin"],
                "fg_pct_diff": home_recent["fg_pct"] - away_recent["fg_pct"],
                "fg3_pct_diff": home_recent["fg3_pct"] - away_recent["fg3_pct"],
                "reb_diff": home_recent["reb"] - away_recent["reb"],
                "ast_diff": home_recent["ast"] - away_recent["ast"],
                "tov_diff": away_recent["tov"] - home_recent["tov"],
                "h2h_win_rate_diff": home_h2h - away_h2h,
            }
        )

    return pd.DataFrame(rows)


FEATURE_COLUMNS = [
    "ppg_diff",
    "papg_diff",
    "win_rate_diff",
    "rest_diff",
    "series_wins_diff",
    "recent_win_rate_diff",
    "recent_margin_diff",
    "fg_pct_diff",
    "fg3_pct_diff",
    "reb_diff",
    "ast_diff",
    "tov_diff",
    "h2h_win_rate_diff",
    "home_court",
    "is_finals",
]


def load_or_fetch_data(force_refresh: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (games, features), fetching from API if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    games_path = DATA_DIR / "playoff_games.csv"
    features_path = DATA_DIR / "playoff_features.csv"

    if not force_refresh and games_path.exists() and features_path.exists():
        games = pd.read_csv(games_path, parse_dates=["game_date"])
        features = pd.read_csv(features_path, parse_dates=["game_date"])
        return games, features

    all_seasons = TRAIN_SEASONS + [VALIDATION_SEASON]
    raw = fetch_playoff_games(all_seasons)
    games = build_game_table(raw)
    features = build_features(games)

    games.to_csv(games_path, index=False)
    features.to_csv(features_path, index=False)
    return games, features
