"""Fetch and normalize betting odds for NBA Finals comparison."""

from __future__ import annotations

import os
from datetime import datetime

import requests

ODDS_API_KEY = os.environ.get("ODDS_API_KEY", "")
ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

# Demo odds sourced from typical late-series Finals markets (June 2026 scenario).
# Knicks lead 3-1; market favors NYK to close in Game 5.
DEMO_ODDS_SOURCE = "Demo market (simulated Finals lines, June 2026 scenario)"


def _american_to_implied_prob(american: int) -> float:
    if american > 0:
        return 100 / (american + 100)
    return abs(american) / (abs(american) + 100)


def _normalize_probs(probs: dict[str, float]) -> dict[str, float]:
    total = sum(probs.values())
    if total <= 0:
        return probs
    return {k: round(v / total, 4) for k, v in probs.items()}


def _demo_game_odds(game_number: int, home: str, away: str) -> dict:
    """Realistic demo moneyline odds per game context."""
    scenarios = {
        1: {"home_ml": -115, "away_ml": +105, "spread": -1.5, "spread_home": -110},
        2: {"home_ml": -120, "away_ml": +110, "spread": -2.0, "spread_home": -108},
        3: {"home_ml": +130, "away_ml": -150, "spread": +3.5, "spread_home": -110},
        4: {"home_ml": +125, "away_ml": -145, "spread": +3.0, "spread_home": -108},
        5: {"home_ml": +165, "away_ml": -195, "spread": +4.5, "spread_home": -110},
        6: {"home_ml": -140, "away_ml": +120, "spread": -2.5, "spread_home": -110},
        7: {"home_ml": +150, "away_ml": -175, "spread": +3.5, "spread_home": -108},
    }
    s = scenarios.get(game_number, scenarios[5])
    home_prob = _american_to_implied_prob(s["home_ml"])
    away_prob = _american_to_implied_prob(s["away_ml"])
    normalized = _normalize_probs({home: home_prob, away: away_prob})
    return {
        "game_number": game_number,
        "home_team": home,
        "away_team": away,
        "home_moneyline": s["home_ml"],
        "away_moneyline": s["away_ml"],
        "spread_line": s["spread"],
        "spread_home_price": s["spread_home"],
        "home_win_prob": normalized[home],
        "away_win_prob": normalized[away],
        "source": DEMO_ODDS_SOURCE,
        "is_demo": True,
    }


def _demo_series_odds() -> dict:
    nyk_ml = -450
    sas_ml = +350
    nyk_prob = _american_to_implied_prob(nyk_ml)
    sas_prob = _american_to_implied_prob(sas_ml)
    normalized = _normalize_probs({"NYK": nyk_prob, "SAS": sas_prob})
    return {
        "NYK_moneyline": nyk_ml,
        "SAS_moneyline": sas_ml,
        "NYK_win_prob": normalized["NYK"],
        "SAS_win_prob": normalized["SAS"],
        "NYK_in_5_prob": 0.42,
        "NYK_in_6_prob": 0.22,
        "NYK_in_7_prob": 0.08,
        "SAS_in_6_prob": 0.06,
        "SAS_in_7_prob": 0.04,
        "source": DEMO_ODDS_SOURCE,
        "is_demo": True,
    }


def _fetch_live_odds() -> dict | None:
    if not ODDS_API_KEY:
        return None
    try:
        resp = requests.get(
            ODDS_API_URL,
            params={
                "apiKey": ODDS_API_KEY,
                "regions": "us",
                "markets": "h2h,spreads",
                "oddsFormat": "american",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        events = resp.json()
        finals_events = [
            e for e in events
            if "Knicks" in e.get("home_team", "") + e.get("away_team", "")
            or "Spurs" in e.get("home_team", "") + e.get("away_team", "")
        ]
        if not finals_events:
            return None

        event = finals_events[0]
        bookmakers = event.get("bookmakers", [])
        if not bookmakers:
            return None

        book = bookmakers[0]
        home_team = _map_team_name(event.get("home_team", ""))
        away_team = _map_team_name(event.get("away_team", ""))

        h2h_market = next(
            (m for m in book.get("markets", []) if m["key"] == "h2h"), None
        )
        spread_market = next(
            (m for m in book.get("markets", []) if m["key"] == "spreads"), None
        )

        home_ml, away_ml = None, None
        spread_line, spread_price = None, None
        if h2h_market:
            for outcome in h2h_market["outcomes"]:
                team = _map_team_name(outcome["name"])
                if team == home_team:
                    home_ml = int(outcome["price"])
                elif team == away_team:
                    away_ml = int(outcome["price"])

        if spread_market:
            for outcome in spread_market["outcomes"]:
                if _map_team_name(outcome["name"]) == home_team:
                    spread_line = float(outcome.get("point", 0))
                    spread_price = int(outcome["price"])

        if home_ml is None or away_ml is None:
            return None

        home_prob = _american_to_implied_prob(home_ml)
        away_prob = _american_to_implied_prob(away_ml)
        normalized = _normalize_probs({home_team: home_prob, away_team: away_prob})

        return {
            "live_event": {
                "home_team": home_team,
                "away_team": away_team,
                "commence_time": event.get("commence_time"),
                "bookmaker": book.get("title", "Unknown"),
                "home_moneyline": home_ml,
                "away_moneyline": away_ml,
                "spread_line": spread_line,
                "spread_home_price": spread_price,
                "home_win_prob": normalized[home_team],
                "away_win_prob": normalized[away_team],
                "source": f"The Odds API ({book.get('title', 'book')})",
                "is_demo": False,
            },
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }
    except (requests.RequestException, KeyError, ValueError):
        return None


def _map_team_name(name: str) -> str:
    mapping = {
        "New York Knicks": "NYK",
        "San Antonio Spurs": "SAS",
        "Knicks": "NYK",
        "Spurs": "SAS",
    }
    return mapping.get(name, name)


def get_odds_comparison(schedule: list[dict]) -> dict:
    """Return market odds for each finals game plus series-level lines."""
    live = _fetch_live_odds()
    game_odds = [
        _demo_game_odds(g["game"], g["home"], g["away"]) for g in schedule
    ]
    series_odds = _demo_series_odds()

    result = {
        "mode": "demo",
        "api_key_configured": bool(ODDS_API_KEY),
        "series_odds": series_odds,
        "game_odds": game_odds,
        "live_event": None,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }

    if live:
        result["mode"] = "live"
        result["live_event"] = live.get("live_event")
        result["fetched_at"] = live.get("fetched_at", result["fetched_at"])
        # Overlay live odds on matching upcoming game if teams match
        le = live["live_event"]
        for go in game_odds:
            if (
                not go.get("played", True)
                and go["home_team"] == le["home_team"]
                and go["away_team"] == le["away_team"]
            ):
                go.update({
                    "home_moneyline": le["home_moneyline"],
                    "away_moneyline": le["away_moneyline"],
                    "spread_line": le.get("spread_line", go["spread_line"]),
                    "spread_home_price": le.get(
                        "spread_home_price", go["spread_home_price"]
                    ),
                    "home_win_prob": le["home_win_prob"],
                    "away_win_prob": le["away_win_prob"],
                    "source": le["source"],
                    "is_demo": False,
                })

    return result


def compare_model_vs_market(
    model_home_prob: float,
    market_home_prob: float,
    home_team: str,
    away_team: str,
) -> dict:
    """Edge analysis: positive edge = model sees more value on home."""
    model_away = 1 - model_home_prob
    market_away = 1 - market_home_prob
    home_edge = round(model_home_prob - market_home_prob, 4)
    away_edge = round(model_away - market_away, 4)
    pick = home_team if home_edge > away_edge else away_team
    max_edge = max(abs(home_edge), abs(away_edge))
    signal = "neutral"
    if max_edge >= 0.05:
        signal = "value" if max_edge >= 0.08 else "lean"
    return {
        "home_team": home_team,
        "away_team": away_team,
        "model_home_prob": round(model_home_prob, 4),
        "market_home_prob": round(market_home_prob, 4),
        "home_edge": home_edge,
        "away_edge": away_edge,
        "edge_pick": pick,
        "edge_magnitude": round(max_edge, 4),
        "signal": signal,
    }
