"""Garmin Connect client. Reuses tokens at ~/.garminconnect/."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from garminconnect import Garmin

_client: Garmin | None = None


def client() -> Garmin:
    global _client
    if _client is not None:
        return _client
    g = Garmin()
    tokendir = str(Path.home() / ".garminconnect")
    try:
        g.login(tokenstore=tokendir)
    except TypeError:
        g.login()
    _client = g
    return g


def _safe(fn, *args, **kwargs) -> Any:
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        return {"_error": str(e)}


def _d(d: date) -> str:
    return d.isoformat()


def _extract_sleep_score(payload):
    if not isinstance(payload, dict): return None
    dto = payload.get("dailySleepDTO") or {}
    scores = dto.get("sleepScores") or {}
    overall = scores.get("overall") or {}
    if isinstance(overall, dict) and overall.get("value") is not None:
        return overall["value"]
    osc = dto.get("overallSleepScore")
    if isinstance(osc, dict): return osc.get("value")
    return None


def _extract_sleep_hours(payload):
    if not isinstance(payload, dict): return None
    dto = payload.get("dailySleepDTO") or {}
    secs = dto.get("sleepTimeSeconds") or dto.get("sleepDurationInSeconds")
    return round(secs / 3600, 2) if isinstance(secs, (int, float)) else None


def _extract_hrv_last(payload):
    if not isinstance(payload, dict): return None
    summary = payload.get("hrvSummary") or {}
    return summary.get("lastNightAvg") or summary.get("weeklyAvg")


def _extract_hrv_baseline(payload):
    if not isinstance(payload, dict): return None
    summary = payload.get("hrvSummary") or {}
    bl = summary.get("baseline") or {}
    if not isinstance(bl, dict): return None
    lo = bl.get("lowUpper")
    hi = bl.get("balancedHigh") or bl.get("balancedUpper")
    if lo is not None and hi is not None:
        return round((lo + hi) / 2)
    return lo or hi


def _extract_bb(payload):
    out = {"current": None, "drained": None, "charged": None}
    if isinstance(payload, list) and payload: payload = payload[0]
    if not isinstance(payload, dict): return out
    arr = payload.get("bodyBatteryValuesArray")
    if isinstance(arr, list) and arr:
        last = arr[-1]
        if isinstance(last, (list, tuple)) and len(last) >= 2:
            out["current"] = last[1]
    out["drained"] = payload.get("drained")
    out["charged"] = payload.get("charged")
    return out


def _extract_rhr(payload):
    if isinstance(payload, list) and payload: payload = payload[0]
    if not isinstance(payload, dict): return None
    daily = (payload.get("allMetrics") or {}).get("metricsMap", {}).get(
        "WELLNESS_RESTING_HEART_RATE", []
    )
    if daily and isinstance(daily, list) and isinstance(daily[0], dict):
        v = daily[0].get("value")
        if v is not None: return v
    return payload.get("restingHeartRate") or payload.get("value")


def _compute_readiness(snap):
    """Deterministic 0-100 readiness from available signals.
    Each signal contributes 0-25 points based on the 80/20 polarized thresholds."""
    points = 0
    total = 0
    flags = []

    hours = (snap.get("sleep") or {}).get("hours")
    if hours is not None:
        if hours >= 7:   points += 25; flags.append(("sleep_hours", "green"))
        elif hours >= 6: points += 15; flags.append(("sleep_hours", "yellow"))
        else:            points += 5;  flags.append(("sleep_hours", "red"))
        total += 25

    sscore = (snap.get("sleep") or {}).get("score")
    if sscore is not None:
        if sscore >= 80:   points += 25; flags.append(("sleep_score", "green"))
        elif sscore >= 60: points += 15; flags.append(("sleep_score", "yellow"))
        else:              points += 5;  flags.append(("sleep_score", "red"))
        total += 25

    bb = (snap.get("body_battery") or {}).get("current")
    if bb is not None:
        if bb >= 60:   points += 25; flags.append(("body_battery", "green"))
        elif bb >= 30: points += 15; flags.append(("body_battery", "yellow"))
        else:          points += 5;  flags.append(("body_battery", "red"))
        total += 25

    hrv = (snap.get("hrv") or {}).get("last_night")
    baseline = (snap.get("hrv") or {}).get("baseline")
    if hrv is not None:
        if baseline:
            diff = (hrv - baseline) / baseline
            if diff >= -0.05:   points += 25; flags.append(("hrv", "green"))
            elif diff >= -0.10: points += 15; flags.append(("hrv", "yellow"))
            else:               points += 5;  flags.append(("hrv", "red"))
        else:
            points += 15
            flags.append(("hrv", "yellow"))
        total += 25

    if total == 0:
        return None, flags
    return round(100 * points / total), flags


def today_snapshot() -> dict:
    g = client()
    t = date.today()
    readiness = _safe(g.get_training_readiness, _d(t))
    sleep = _safe(g.get_sleep_data, _d(t))
    hrv = _safe(g.get_hrv_data, _d(t))
    bb = _safe(g.get_body_battery, _d(t))
    rhr_fn = getattr(g, "get_rhr_day", None) or getattr(g, "get_user_summary", None)
    rhr = _safe(rhr_fn, _d(t)) if rhr_fn else None

    rscore = None
    if isinstance(readiness, list) and readiness:
        first = readiness[0]
        if isinstance(first, dict):
            rscore = first.get("score") or first.get("readinessScore")
    elif isinstance(readiness, dict):
        rscore = readiness.get("score") or readiness.get("readinessScore")

    result = {
        "date": t.isoformat(),
        "readiness": {"score": rscore, "computed": False},
        "sleep": {
            "score": _extract_sleep_score(sleep),
            "hours": _extract_sleep_hours(sleep),
        },
        "hrv": {
            "last_night": _extract_hrv_last(hrv),
            "baseline": _extract_hrv_baseline(hrv),
        },
        "body_battery": _extract_bb(bb),
        "rhr": _extract_rhr(rhr),
    }

    # Fallback: compute readiness ourselves when Garmin doesn't provide one (FR255 etc.)
    if result["readiness"]["score"] is None:
        score, flags = _compute_readiness(result)
        result["readiness"] = {"score": score, "computed": True, "flags": flags}

    return result


def sleep_series(days: int = 7):
    g = client()
    out = []
    for i in range(days - 1, -1, -1):
        d = date.today() - timedelta(days=i)
        payload = _safe(g.get_sleep_data, _d(d))
        out.append({
            "date": d.isoformat(),
            "score": _extract_sleep_score(payload),
            "hours": _extract_sleep_hours(payload),
        })
    return out


def hrv_series(days: int = 14):
    g = client()
    out = []
    for i in range(days - 1, -1, -1):
        d = date.today() - timedelta(days=i)
        payload = _safe(g.get_hrv_data, _d(d))
        out.append({"date": d.isoformat(), "value": _extract_hrv_last(payload)})
    return out


def rhr_series(days: int = 7):
    g = client()
    fn = getattr(g, "get_rhr_day", None) or getattr(g, "get_user_summary", None)
    out = []
    for i in range(days - 1, -1, -1):
        d = date.today() - timedelta(days=i)
        payload = _safe(fn, _d(d)) if fn else None
        out.append({"date": d.isoformat(), "value": _extract_rhr(payload)})
    return out


def body_battery_today():
    g = client()
    bb = _safe(g.get_body_battery, _d(date.today()))
    return _extract_bb(bb)


def training_status():
    g = client()
    return {"raw": _safe(g.get_training_status, _d(date.today()))}


def training_load_trend():
    g = client()
    return {"raw": _safe(g.get_training_status, _d(date.today()))}


def recent_activities(days: int = 7):
    g = client()
    end = date.today()
    start = end - timedelta(days=days)
    acts = _safe(g.get_activities_by_date, _d(start), _d(end))
    if not isinstance(acts, list):
        return []
    out = []
    for a in acts:
        if not isinstance(a, dict): continue
        out.append({
            "source": "garmin",
            "id": a.get("activityId"),
            "name": a.get("activityName"),
            "type": (a.get("activityType") or {}).get("typeKey") if isinstance(a.get("activityType"), dict) else None,
            "start_time": a.get("startTimeGMT") or a.get("startTimeLocal"),
            "duration_seconds": a.get("duration"),
            "distance_meters": a.get("distance"),
            "avg_hr": a.get("averageHR"),
            "max_hr": a.get("maxHR"),
            "calories": a.get("calories"),
        })
    return out