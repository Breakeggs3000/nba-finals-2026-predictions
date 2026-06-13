#!/usr/bin/env python3
"""CLI for NBA Finals 2026 predictions."""

from __future__ import annotations

import argparse
import json
import sys

from src.predict import generate_predictions
from src.train import train_models


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _print_predictions(data: dict) -> None:
    status = data["series_status"]
    print("\n" + "=" * 60)
    print("  2026 NBA FINALS: KNICKS vs SPURS — ML PREDICTIONS")
    print("=" * 60)
    print(f"\nSeries: NYK {status['nyk_wins']} - {status['sas_wins']} SAS")
    print(f"Leader: {status['leader']}\n")

    metrics = data.get("model_metrics", {})
    if metrics:
        print("Model Performance")
        print("-" * 40)
        if "cv_accuracy_mean" in metrics:
            print(f"  CV accuracy (train):     {_pct(metrics['cv_accuracy_mean'])}")
        if "validation_2026_playoffs_accuracy" in metrics:
            print(
                f"  2026 playoffs accuracy:  "
                f"{_pct(metrics['validation_2026_playoffs_accuracy'])}"
            )
        if "finals_played_games_accuracy" in metrics:
            print(
                f"  Finals G1-4 accuracy:    "
                f"{_pct(metrics['finals_played_games_accuracy'])}"
            )
        print()

    series = data["series_outcome_probabilities"]
    print("Series Outcome Probabilities")
    print("-" * 40)
    print(f"  Knicks win series:       {_pct(series['NYK_wins_series'])}")
    print(f"    └ In 5 games:          {_pct(series['NYK_in_5'])}")
    print(f"    └ In 6 games:          {_pct(series['NYK_in_6'])}")
    print(f"    └ In 7 games:          {_pct(series['NYK_in_7'])}")
    print(f"  Spurs win series:        {_pct(series['SAS_wins_series'])}")
    print(f"    └ In 6 games:          {_pct(series['SAS_in_6'])}")
    print(f"    └ In 7 games:          {_pct(series['SAS_in_7'])}")
    print()

    sc = data.get("series_odds_comparison", {})
    if sc:
        print("Model vs Market (Series)")
        print("-" * 40)
        print(f"  Model NYK series:        {_pct(sc.get('model_NYK_series_prob', 0))}")
        print(f"  Market NYK series:       {_pct(sc.get('market_NYK_series_prob', 0))}")
        if "NYK" in sc:
            edge = sc["NYK"]
            print(
                f"  Edge signal:             {edge['edge_pick']} "
                f"({edge['signal']}, {edge['edge_magnitude'] * 100:.1f}%)"
            )
        print(f"  Odds source:             {sc.get('odds_source', 'N/A')}")
        print()

    odds_meta = data.get("odds_meta", {})
    if odds_meta:
        mode = odds_meta.get("mode", "demo")
        print(f"Odds mode: {mode.upper()}")
        if mode == "demo":
            print("  (Set ODDS_API_KEY env var for live odds)")
        print()

    for game in data["games"]:
        print(f"Game {game['game_number']} — {game['date']}")
        print(f"  {game['away_team']} @ {game['home_team']}")
        if game["played"]:
            print(
                f"  FINAL: {game['away_team']} {game['actual_away_pts']} — "
                f"{game['home_team']} {game['actual_home_pts']}"
            )
        print(
            f"  Predicted: {game['predicted_away_score']:.0f} - "
            f"{game['predicted_home_score']:.0f} "
            f"(margin {game['predicted_margin']:+.1f})"
        )
        print(f"  Win prob: {game['away_team']} {_pct(game['away_win_prob'])} | "
              f"{game['home_team']} {_pct(game['home_win_prob'])}")
        print(f"  Pick: {game['predicted_winner']}")

        if game.get("odds_comparison"):
            oc = game["odds_comparison"]
            print(
                f"  Model vs Market (home): "
                f"{_pct(oc['model_home_prob'])} vs {_pct(oc['market_home_prob'])} "
                f"→ {oc['edge_pick']} ({oc['signal']}, "
                f"{oc['edge_magnitude'] * 100:+.1f}% edge)"
            )

        print("  Spread cover (home team covers):")
        key_lines = ["-3.5", "-2.5", "-1.5", "+1.5", "+2.5", "+3.5"]
        for line in key_lines:
            key = f"home_{float(line):+.1f}"
            if key in game["spread_probs"]:
                print(f"    Home {line}: {_pct(game['spread_probs'][key])}")
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="NBA Finals 2026 Knicks vs Spurs predictions"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Fetch data and train models before predicting",
    )
    parser.add_argument(
        "--refresh-data",
        action="store_true",
        help="Force refresh playoff data from NBA API",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the web dashboard",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6666,
        help="Web server port (default: 6666)",
    )
    args = parser.parse_args(argv)

    if args.serve:
        import os
        os.environ["WEB_PORT"] = str(args.port)
        from web.app import app, WEB_PORT
        print(f"Starting dashboard at http://127.0.0.1:{WEB_PORT}")
        app.run(debug=True, port=WEB_PORT, host="0.0.0.0")
        return 0

    if args.train:
        print("Training models...", file=sys.stderr)
        metrics = train_models(force_refresh_data=args.refresh_data)
        if not args.json:
            print(f"Training complete. CV accuracy: {_pct(metrics['cv_accuracy_mean'])}")

    try:
        data = generate_predictions()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        print("Run: python3 cli.py --train", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        _print_predictions(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
