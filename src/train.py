"""Train and persist the playoff prediction model."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, mean_absolute_error
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.data_loader import (
    FEATURE_COLUMNS,
    TRAIN_SEASONS,
    VALIDATION_SEASON,
    build_features,
    load_or_fetch_data,
)

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
WINNER_MODEL_PATH = MODEL_DIR / "winner_model.joblib"
MARGIN_MODEL_PATH = MODEL_DIR / "margin_model.joblib"
METRICS_PATH = MODEL_DIR / "training_metrics.json"


def _split_train_validation(features):
    train = features[features["season"].isin(TRAIN_SEASONS)].copy()
    val = features[features["season"] == VALIDATION_SEASON].copy()
    finals_mask = (val["home_team"].isin({"NYK", "SAS"})) & (
        val["away_team"].isin({"NYK", "SAS"})
    )
    val_non_finals = val[~finals_mask].copy()
    return train, val_non_finals, val[finals_mask].copy()


def _build_winner_pipeline() -> Pipeline:
  """Ensemble-style winner model: calibrated HGB + logistic blend."""
  hgb = HistGradientBoostingClassifier(
      max_depth=4,
      max_iter=200,
      learning_rate=0.06,
      min_samples_leaf=8,
      l2_regularization=1.0,
      random_state=42,
  )
  return Pipeline(
      [
          ("scaler", StandardScaler()),
          ("clf", CalibratedClassifierCV(hgb, cv=3, method="isotonic")),
      ]
  )


def _build_margin_model() -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        max_depth=4,
        max_iter=250,
        learning_rate=0.05,
        min_samples_leaf=6,
        l2_regularization=0.5,
        random_state=42,
    )


def _blend_with_logistic(
    hgb_pipeline: Pipeline,
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> Pipeline:
    """Blend HGB probabilities with a logistic baseline for stability."""
    lr = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=3000, C=0.5, class_weight="balanced")),
        ]
    )
    lr.fit(X_train, y_train)
    hgb_probs = hgb_pipeline.predict_proba(X_train)[:, 1]
    lr_probs = lr.predict_proba(X_train)[:, 1]
    blend_weight = 0.65  # favor HGB
    blended = blend_weight * hgb_probs + (1 - blend_weight) * lr_probs
    train_acc = float(accuracy_score(y_train, (blended >= 0.5).astype(int)))
    return hgb_pipeline, lr, blend_weight, train_acc


def train_models(force_refresh_data: bool = False) -> dict:
    """Train winner + margin models and save artifacts."""
    games, cached_features = load_or_fetch_data(force_refresh=force_refresh_data)
    # Rebuild features when columns change or data was refreshed
    if force_refresh_data or set(FEATURE_COLUMNS) - set(cached_features.columns):
        features = build_features(games)
        features.to_csv(
            Path(__file__).resolve().parent.parent / "data" / "playoff_features.csv",
            index=False,
        )
    else:
        features = cached_features

    train, val_non_finals, finals_played = _split_train_validation(features)

    X_train = train[FEATURE_COLUMNS].values
    y_train_win = train["home_win"].values
    y_train_margin = train["margin"].values

    winner_model = _build_winner_pipeline()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(
        winner_model, X_train, y_train_win, cv=cv, scoring="accuracy"
    )

    winner_model.fit(X_train, y_train_win)
    lr_model, blend_weight, blended_train_acc = _blend_with_logistic(
        winner_model, X_train, y_train_win
    )[1:]

    margin_model = _build_margin_model()
    margin_model.fit(X_train, y_train_margin)

    val_metrics: dict = {}
    if not val_non_finals.empty:
        X_val = val_non_finals[FEATURE_COLUMNS].values
        y_val = val_non_finals["home_win"].values
        hgb_probs = winner_model.predict_proba(X_val)[:, 1]
        lr_probs = lr_model.predict_proba(X_val)[:, 1]
        val_probs = blend_weight * hgb_probs + (1 - blend_weight) * lr_probs
        val_preds = (val_probs >= 0.5).astype(int)
        val_metrics["validation_2026_playoffs_accuracy"] = float(
            accuracy_score(y_val, val_preds)
        )
        val_metrics["validation_2026_playoffs_brier"] = float(
            brier_score_loss(y_val, val_probs)
        )
        val_margin_pred = margin_model.predict(X_val)
        val_metrics["validation_2026_playoffs_margin_mae"] = float(
            mean_absolute_error(val_non_finals["margin"].values, val_margin_pred)
        )

    finals_metrics: dict = {}
    if not finals_played.empty:
        X_f = finals_played[FEATURE_COLUMNS].values
        y_f = finals_played["home_win"].values
        hgb_probs = winner_model.predict_proba(X_f)[:, 1]
        lr_probs = lr_model.predict_proba(X_f)[:, 1]
        f_probs = blend_weight * hgb_probs + (1 - blend_weight) * lr_probs
        f_preds = (f_probs >= 0.5).astype(int)
        finals_metrics["finals_played_games_accuracy"] = float(
            accuracy_score(y_f, f_preds)
        )
        finals_metrics["finals_played_games"] = int(len(finals_played))

    metrics = {
        "train_games": int(len(train)),
        "validation_games_2026_playoffs": int(len(val_non_finals)),
        "cv_accuracy_mean": float(cv_scores.mean()),
        "cv_accuracy_std": float(cv_scores.std()),
        "train_accuracy": blended_train_acc,
        "blend_weight_hgb": blend_weight,
        "model_type": "Calibrated HistGradientBoosting + Logistic blend",
        "feature_columns": FEATURE_COLUMNS,
        **val_metrics,
        **finals_metrics,
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"hgb": winner_model, "lr": lr_model, "blend_weight": blend_weight},
        WINNER_MODEL_PATH,
    )
    joblib.dump(margin_model, MARGIN_MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    try:
        m = train_models(force_refresh_data=True)
    except Exception:
        m = train_models(force_refresh_data=False)
    print(json.dumps(m, indent=2))
