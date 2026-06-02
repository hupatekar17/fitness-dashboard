"""Strava client. Reads tokens from .strava-mcp.env, auto-refreshes."""
from __future__ import annotations

import os
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

API = "https://www.strava.com/api/v3"


def _env_path() -> Path:
    p = os.environ.get("STRAVA_ENV_PATH") or str(Path.home() / ".strava-mcp.env")
    return Path(p)


def _load_env() -> dict[str, str]:
    p = _env_path()
    if not p.exists():
        return {}
    out: dict[str, str] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _save_env(env: dict[str, str]) -> None:
    p = _env_path()
    lines = [f"{k}={v}" for k, v in env.items()]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _access_token() -> str:
    env = _load_env()
    if not env:
        raise RuntimeError(
            f"Strava env file not found at {_env_path()}. "
            "Run strava-mcp setup_auth first."
        )

    expires_at = int(env.get("STRAVA_TOKEN_EXPIRES_AT", "0") or "0")
    now = int(time.time())

    if expires_at > now + 60 and env.get("STRAVA_ACCESS_TOKEN"):
        return env["STRAVA_ACCESS_TOKEN"]

    r = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": env["STRAVA_CLIENT_ID"],
            "client_secret": env["STRAVA_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "refresh_token": env["STRAVA_REFRESH_TOKEN"],
        },
        timeout=15,
    )
    r.raise_for_status()
    tok = r.json()
    env["STRAVA_ACCESS_TOKEN"] = tok["access_token"]
    env["STRAVA_REFRESH_TOKEN"] = tok["refresh_token"]
    env["STRAVA_TOKEN_EXPIRES_AT"] = str(tok["expires_at"])
    _save_env(env)
    return tok["access_token"]


def _get(path: str, params: dict | None = None) -> Any:
    r = requests.get(
        API + path,
        headers={"Authorization": f"Bearer {_access_token()}"},
        params=params or {},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def recent_activities(days: int = 7) -> list[dict]:
    after = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    acts = _get("/athlete/activities", {"after": after, "per_page": 50})
    out = []
    for a in acts or []:
        out.append({
            "source": "strava",
            "id": a.get("id"),
            "name": a.get("name"),
            "type": a.get("sport_type") or a.get("type"),
            "start_time": a.get("start_date"),
            "duration_seconds": a.get("moving_time"),
            "distance_meters": a.get("distance"),
            "avg_hr": a.get("average_heartrate"),
            "max_hr": a.get("max_heartrate"),
            "elevation_gain": a.get("total_elevation_gain"),
            "kudos": a.get("kudos_count"),
        })
    return out


def weekly_mileage(weeks: int = 4) -> list[dict]:
    """Last N weeks of running + cycling distance, in km. Weeks start Monday."""
    after = int((datetime.now(timezone.utc) - timedelta(weeks=weeks + 1)).timestamp())
    acts = _get("/athlete/activities", {"after": after, "per_page": 100})

    buckets: dict[str, dict[str, float]] = defaultdict(
        lambda: {"run_km": 0.0, "ride_km": 0.0, "other_km": 0.0}
    )

    for a in acts or []:
        try:
            dt = datetime.fromisoformat(a["start_date"].replace("Z", "+00:00"))
        except Exception:
            continue
        monday = dt.date() - timedelta(days=dt.weekday())
        wk = monday.isoformat()
        km = (a.get("distance") or 0) / 1000
        t = (a.get("sport_type") or a.get("type") or "").lower()
        if "run" in t or "hike" in t or "walk" in t:
            buckets[wk]["run_km"] += km
        elif "ride" in t or "cycl" in t or "bike" in t:
            buckets[wk]["ride_km"] += km
        else:
            buckets[wk]["other_km"] += km

    out = []
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    for i in range(weeks - 1, -1, -1):
        monday = this_monday - timedelta(days=7 * i)
        wk = monday.isoformat()
        b = buckets.get(wk, {"run_km": 0.0, "ride_km": 0.0, "other_km": 0.0})
        out.append({
            "week_start": wk,
            "run_km": round(b["run_km"], 1),
            "ride_km": round(b["ride_km"], 1),
            "other_km": round(b["other_km"], 1),
        })
    return out


def athlete_profile() -> dict:
    return _get("/athlete")
