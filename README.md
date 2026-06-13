# NBA Finals 2026 — Knicks vs Spurs Predictor

Machine learning model for predicting the **2026 NBA Finals** between the New York Knicks and San Antonio Spurs. Trained on historical playoff data (2021–2025), validated on the 2026 playoffs, with game-by-game win probabilities, spread cover rates, series outcome scenarios, and **model vs market odds comparison**.

## Stack

| Layer | Technology | Port |
|-------|-----------|------|
| Frontend | Next.js 16 (TypeScript + Tailwind CSS + Recharts) | **3000** |
| Backend | FastAPI + Uvicorn | **8000** |
| ML pipeline | Python — scikit-learn, pandas, joblib | — |

## Quick Start

### 1. Install Python dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 2. Train the models (first run)

```bash
python3 cli.py --train
```

### 3. Start the FastAPI backend

```bash
uvicorn web.api:app --reload --port 8000
```

### 4. Start the Next.js frontend

```bash
cd frontend && npm run dev
```

Open **http://localhost:3000**

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/predictions` | GET | Full prediction JSON with odds comparison |
| `/api/odds` | GET | Market odds only |
| `/api/retrain` | POST | Retrain with fresh NBA API data |
| `/health` | GET | Health check |

Interactive API docs: http://localhost:8000/docs

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ODDS_API_KEY` | The Odds API key for live betting odds (optional) |
| `NEXT_PUBLIC_API_URL` | Override backend URL (default: `http://localhost:8000`) |

---

## Model

- **Winner model**: Calibrated HistGradientBoostingClassifier blended with logistic regression (65/35 blend)
- **Margin model**: HistGradientBoostingRegressor for point differential and spread simulation
- **Features**: 15 engineered playoff stats — rolling PPG, win rate, rest, series context, recent form (FG%, rebounds, assists, turnovers), head-to-head, home court
- **CV accuracy**: ~62.6% (5-fold stratified CV on 2021–2025 playoffs)
- **Stored artifacts**: `models/winner_model.joblib`, `models/margin_model.joblib`, `models/training_metrics.json`

## Features

| Feature | Description |
|---------|-------------|
| `ppg_diff` | Home vs away rolling points per game |
| `papg_diff` | Points-allowed differential |
| `win_rate_diff` | Playoff win rate differential |
| `rest_diff` | Rest days differential |
| `series_wins_diff` | Series wins before this game |
| `recent_win_rate_diff` | Last 5 games win rate differential |
| `recent_margin_diff` | Last 5 games margin differential |
| `fg_pct_diff` / `fg3_pct_diff` | Shooting efficiency differential |
| `reb_diff` / `ast_diff` / `tov_diff` | Rebounding, assists, turnover differentials |
| `h2h_win_rate_diff` | Head-to-head playoff win rate |
| `home_court` | Home court indicator |
| `is_finals` | Finals flag |

## Live Odds Comparison

- **Demo mode** (default): Simulated Finals betting lines for the NYK 3-1 lead scenario
- **Live mode**: Set `ODDS_API_KEY` for real odds from [The Odds API](https://the-odds-api.com/)

```bash
export ODDS_API_KEY=your_key_here
uvicorn web.api:app --reload --port 8000
```

---

## Legacy (Flask server — port 6666)

The original Flask server is still available but runs on port 6666 (a browser-blocked port — not recommended for normal use).

```bash
# Legacy: start Flask server
python3 web/app.py
# or
python3 cli.py --serve
# Open http://127.0.0.1:6666  (requires non-Chromium browser or curl)
```

The Flask server is preserved for backwards compatibility. Use the FastAPI + Next.js stack for the full dashboard experience.

## Current Series (as of build)

Knicks lead Spurs **3–1**. Game 5: June 13, 2026 @ San Antonio.
