  """FastAPI backend for the fitness dashboard."""
from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="Fitness Dashboard")

app.add_middleware(
    CORSMiddleware,
      allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
    ],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}


@app.get("/api/today")
@ttl_cache(seconds=300)
def today():
    return gc.today_snapshot()


@app.get("/api/sleep")
@ttl_cache(seconds=600)
def sleep(days: int = 7):
    return gc.sleep_series(days=days)


@app.get("/api/hrv")
@ttl_cache(seconds=600)
def hrv(days: int = 14):
    return gc.hrv_series(days=days)


@app.get("/api/rhr")
@ttl_cache(seconds=600)
def rhr(days: int = 7):
    return gc.rhr_series(days=days)


@app.get("/api/body-battery")
@ttl_cache(seconds=300)
def body_battery():
    return gc.body_battery_today()


@app.get("/api/training-status")
@ttl_cache(seconds=600)
def training_status():
    return gc.training_status()


@app.get("/api/activities")
@ttl_cache(seconds=300)
def activities(days: int = 7):
    strava_acts = []
    garmin_acts = []
    try:
        strava_acts = sc.recent_activities(days=days) or []
    except Exception as e:
        print(f"[activities] strava error: {e}")
    try:
        garmin_acts = gc.recent_activities(days=days) or []
    except Exception as e:
        print(f"[activities] garmin error: {e}")
    try:
        return _merge(strava_acts, garmin_acts)
    except Exception as e:
        print(f"[activities] merge error: {e}")
        return [a for a in (strava_acts + garmin_acts) if isinstance(a, dict)]


@app.get("/api/weekly-mileage")
@ttl_cache(seconds=600)
def weekly_mileage():
    try:
        return sc.weekly_mileage(weeks=4)
    except Exception as e:
        return [{"_error": str(e)}]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    include_metrics: bool = True


@app.post("/api/chat")
def chat(req: ChatRequest):
    metrics_ctx = None
    if req.include_metrics:
        try:
            metrics_ctx = coach.build_context(gc, sc)
        except Exception as e:
            metrics_ctx = f"(metrics unavailable: {e})"
    return coach.chat([m.dict() for m in req.messages], metrics_ctx)


def _parse_ts(s):
    """Parse an ISO timestamp robustly. Returns aware UTC datetime or None."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from cache import ttl_cache
import garmin_client as gc
import strava_client as sc

import coach


   if not isinstance(s, str):
        return None
    try:
        s2 = s.replace("Z", "+00:00")
        t = datetime.fromisoformat(s2)
        if t.tzinfo is None:
            # Naive → treat as UTC (Garmin's startTimeGMT)
            t = t.replace(tzinfo=timezone.utc)
        return t
    except Exception:
        return None


def _merge(strava, garmin):
    """Deduplicate by start time within 5 minutes; prefer Strava."""
    merged = []
    seen = []
    combined = [a for a in (strava + garmin)
                if isinstance(a, dict) and a.get("start_time")]
    combined.sort(key=lambda x: x.get("start_time") or "", reverse=True)
    for act in combined:
        t = _parse_ts(act["start_time"])
        if t is None:
            merged.append(act)
            continue
        dup = False
        for s in seen:
            try:
                if abs((t - s).total_seconds()) < 300:
                    dup = True
                    break
            except Exception:
                pass
        if dup:
            continue
        seen.append(t)
        merged.append(act)
    return merged
