# Personal Fitness Dashboard

A local web dashboard that pulls live data from your Strava + Garmin accounts and ships with an embedded Claude-powered AI coach. Runs entirely on your Windows PC.

## Architecture

```
Browser (localhost:5173)
        |
React + Vite frontend
        |  /api/* proxied
FastAPI backend (localhost:8000)
        |
+-- Garmin Connect  (python-garminconnect, reuses ~/.garminconnect/ tokens)
+-- Strava REST API (refreshes tokens from %USERPROFILE%\.strava-mcp.env)
+-- Anthropic Claude API (chat coach)
```

## One-time setup

### 1. Install Node.js
If you don't have it: download LTS from <https://nodejs.org>.

### 2. Backend (Python)
```powershell
cd fitness-dashboard\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
```
Paste your Anthropic API key into `.env` and save. Get a key at <https://console.anthropic.com/settings/keys>.

### 3. Frontend (Node)
```powershell
cd ..\frontend
npm install
```

### 4. Verify your existing tokens
- Garmin: tokens live at `%USERPROFILE%\.garminconnect\`. If expired, refresh with `uvx --python 3.12 --from git+https://github.com/Taxuspt/garmin_mcp garmin-mcp-auth --force-reauth`.
- Strava: tokens live at `%USERPROFILE%\.strava-mcp.env`. The dashboard auto-refreshes them.

## Running

Double-click `start-dashboard.bat`. Two terminal windows open (backend + frontend), and your browser opens to <http://localhost:5173>.

To stop: close both terminal windows.

## What you'll see

- **Top row** — Resting HR · Body Battery · Sleep Score · HRV (today)
- **Readiness panel** — Garmin readiness score with green/yellow/red verdict
- **Weekly mileage** — stacked bars, 4 weeks (run / ride / other)
- **Trend charts** — HRV (14d), RHR (7d), Sleep hours (7d)
- **Recent activities** — Strava + Garmin merged, last 7 days
- **Coach chat** — Claude has your current metrics. Ask anything: "should I train hard today?", "plan my next 4 weeks", "am I overreaching?"

## Project layout

```
fitness-dashboard/
+-- README.md
+-- start-dashboard.bat
+-- backend/
|   +-- requirements.txt
|   +-- .env            (created during setup, not committed)
|   +-- .env.example
|   +-- main.py         FastAPI routes
|   +-- garmin_client.py
|   +-- strava_client.py
|   +-- coach.py        Claude integration
|   +-- cache.py
+-- frontend/
    +-- package.json
    +-- vite.config.js
    +-- index.html
    +-- src/
        +-- main.jsx
        +-- App.jsx
        +-- api.js
        +-- styles.css
        +-- components/
            +-- MetricCard.jsx
            +-- ReadinessPanel.jsx
            +-- TrendChart.jsx
            +-- ActivityList.jsx
            +-- WeeklyMileage.jsx
            +-- CoachChat.jsx
```

## Customizing

- **Accent colors** — edit `:root` variables in `frontend/src/styles.css`
- **Add a new metric panel** — add a route in `backend/main.py`, a helper in `garmin_client.py` or `strava_client.py`, then a component in `frontend/src/components/`
- **Change coach personality** — edit `SYSTEM` in `backend/coach.py`
- **Adjust cache TTL** — pass `seconds=...` to the `@ttl_cache` decorators in `main.py`

## Hosting publicly later

When you want a public URL:
1. `cd frontend && npm run build` → static files in `frontend/dist/`
2. Mount `dist/` as static files in FastAPI, or put nginx in front
3. Deploy to Railway, Render, Fly.io, or similar
4. Move `ANTHROPIC_API_KEY` and Strava credentials to the host's env vars
5. Add HTTP basic auth or a single-user OAuth flow so only you can access

## Troubleshooting

- **Backend won't start** — look at the backend terminal window for the actual error. Common: missing `.env`, missing API key, Garmin tokens expired.
- **Empty charts** — the Garmin payload shape varies; check the backend terminal for parsing warnings. Also possible: you didn't wear the watch that night.
- **"AI coach is not configured"** — your `ANTHROPIC_API_KEY` is missing or still `sk-ant-...`. Edit `backend/.env`, then restart the backend.
- **CORS errors** — backend must be on port 8000 (Vite proxies `/api` there). Don't change the port without updating `vite.config.js` too.
- **Strava 401** — refresh tokens auto-renew. If broken, rerun `uv run python -m strava_mcp.scripts.setup_auth` in your strava-mcp clone.
- **Garmin 401 / login errors** — tokens are about 6 months old. Re-auth: `uvx --python 3.12 --from git+https://github.com/Taxuspt/garmin_mcp garmin-mcp-auth --force-reauth`.

## What this is and isn't

This dashboard is the *view layer* on top of the same data your `strava-garmin-coach` Cowork plugin uses. The plugin lets Claude inside Cowork chat answer questions over MCP tool calls. This dashboard is a permanent visual workspace with its own chat. Use both — they don't conflict.
