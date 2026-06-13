"""Flask web app for NBA Finals 2026 predictions."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, render_template

from src.odds import get_odds_comparison
from src.predict import FINALS_SCHEDULE, generate_predictions
from src.train import train_models

WEB_PORT = int(os.environ.get("WEB_PORT", "6666"))

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    try:
        data = generate_predictions()
    except FileNotFoundError:
        train_models(force_refresh_data=False)
        data = generate_predictions()
    return render_template("index.html", data=data)


@app.route("/api/predictions")
def api_predictions():
    try:
        data = generate_predictions()
    except FileNotFoundError:
        train_models(force_refresh_data=False)
        data = generate_predictions()
    return jsonify(data)


@app.route("/api/odds")
def api_odds():
    schedule = [
        {"game": e["game"], "home": e["home"], "away": e["away"]}
        for e in FINALS_SCHEDULE
    ]
    return jsonify(get_odds_comparison(schedule))


@app.route("/api/retrain", methods=["POST"])
def api_retrain():
    metrics = train_models(force_refresh_data=True)
    data = generate_predictions()
    return jsonify({"metrics": metrics, "predictions": data})


if __name__ == "__main__":
    app.run(debug=True, port=WEB_PORT, host="0.0.0.0")
