"""Groq-powered AI coach (free, no credit card required)."""
from __future__ import annotations

import os
from datetime import datetime

from groq import Groq

MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM = """You are Harshavardhan's personal endurance coach inside his fitness dashboard.

Coaching philosophy — apply consistently:
- 80/20 polarized training. Easy days easy (Z1-Z2), hard days hard (Z4-Z5). Avoid Z3 gray zone unless asked.
- Recovery beats heroism. If recovery signals are mixed, default conservative.
- Hard days are earned by easy days — never two hard sessions back-to-back without justification.
- Be decisive, not wishy-washy. Give specific sessions: type, duration, target HR range in bpm.
- Reference the user's actual numbers when they're in the metrics block below.

Tone: warm, concise, sport-coach voice. No medical disclaimers or corporate caveats.
Don't suggest seeing a doctor unless the user mentions symptoms that genuinely need one.

When recommending workouts, always give: type, duration, target HR zone, one-line "why".
When asked to plan multiple weeks, structure as a clear schedule with rest days and a long session each week.
"""


def build_context(gc, sc) -> str:
    today = gc.today_snapshot()
    try:
        sa = sc.recent_activities(days=3)
    except Exception:
        sa = []
    try:
        ga = gc.recent_activities(days=3)
    except Exception:
        ga = []

    lines = [f"Current metrics ({datetime.now().strftime('%Y-%m-%d %H:%M')}):"]
    r = today.get("readiness", {}).get("score")
    if r is not None:
        lines.append(f"- Morning readiness: {r}/100")
    s = today.get("sleep") or {}
    if s.get("hours") is not None:
        lines.append(f"- Sleep: {s['hours']}h, score {s.get('score', 'n/a')}")
    h = today.get("hrv") or {}
    if h.get("last_night") is not None:
        lines.append(f"- HRV last night: {h['last_night']}ms (baseline ~{h.get('baseline', 'n/a')}ms)")
    bb = today.get("body_battery") or {}
    if bb.get("current") is not None:
        lines.append(f"- Body Battery: {bb['current']}/100")
    if today.get("rhr") is not None:
        lines.append(f"- Resting HR: {today['rhr']} bpm")

    activities = sa + ga
    if activities:
        lines.append("")
        lines.append("Last 3 days of activities:")
        for a in activities[:6]:
            dist = (a.get("distance_meters") or 0) / 1000
            dur_min = (a.get("duration_seconds") or 0) / 60
            when = (a.get("start_time") or "?")[:10]
            lines.append(
                f"- {when} {a.get('type', '?')}: {dist:.1f}km, {dur_min:.0f}min, "
                f"avg HR {a.get('avg_hr', 'n/a')}"
            )

    return "\n".join(lines)


def chat(messages: list[dict], metrics_context: str | None) -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "role": "assistant",
            "content": (
                "AI coach is not configured. Add a real GROQ_API_KEY to backend/.env "
                "and restart the backend. Get a free key at https://console.groq.com/keys"
            ),
        }

    client = Groq(api_key=api_key)

    system = SYSTEM
    if metrics_context:
        system = SYSTEM + "\n\n" + metrics_context

    formatted = [{"role": "system", "content": system}]
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if not content:
            continue
        if role in ("user", "assistant"):
            formatted.append({"role": role, "content": content})

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=formatted,
        max_tokens=1024,
        temperature=0.7,
    )

    return {"role": "assistant", "content": resp.choices[0].message.content}