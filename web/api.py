"""FastAPI backend for NBA Finals 2026 predictions."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import traceback as _tb

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.odds import get_odds_comparison
from src.predict import FINALS_SCHEDULE, generate_predictions
from src.train import train_models

app = FastAPI(title="NBA Finals 2026 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_predictions() -> dict:
    try:
        return generate_predictions()
    except FileNotFoundError:
        train_models(force_refresh_data=False)
        return generate_predictions()


@app.get("/api/predictions")
async def api_predictions():
    try:
        return _get_predictions()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_tb.format_exc()) from exc


@app.get("/api/odds")
async def api_odds():
    try:
        schedule = [
            {"game": e["game"], "home": e["home"], "away": e["away"]}
            for e in FINALS_SCHEDULE
        ]
        return get_odds_comparison(schedule)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/retrain")
async def api_retrain():
    try:
        metrics = train_models(force_refresh_data=True)
        data = generate_predictions()
        return {"metrics": metrics, "predictions": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health")
async def health():
    import sklearn, numpy
    from pathlib import Path
    models_dir = Path(__file__).resolve().parent.parent / "models"
    return {
        "status": "ok",
        "sklearn": sklearn.__version__,
        "numpy": numpy.__version__,
        "winner_model_exists": (models_dir / "winner_model.joblib").exists(),
        "margin_model_exists": (models_dir / "margin_model.joblib").exists(),
        "git_commit": "3cee8e8",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.api:app", host="0.0.0.0", port=8000, reload=True)
