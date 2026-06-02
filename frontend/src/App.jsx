import React, { useEffect, useState } from "react";
import { get } from "./api.js";
import MetricCard from "./components/MetricCard.jsx";
import ReadinessPanel from "./components/ReadinessPanel.jsx";
import TrendChart from "./components/TrendChart.jsx";
import ActivityList from "./components/ActivityList.jsx";
import WeeklyMileage from "./components/WeeklyMileage.jsx";
import CoachChat from "./components/CoachChat.jsx";

function SunIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
}

export default function App() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("theme") || "dark";
    } catch {
      return "dark";
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch {}
  }, [theme]);

  const [today, setToday] = useState(null);
  const [sleep, setSleep] = useState(null);
  const [hrv, setHrv] = useState(null);
  const [rhr, setRhr] = useState(null);
  const [activities, setActivities] = useState(null);
  const [mileage, setMileage] = useState(null);

  useEffect(() => {
    get("/api/today").then(setToday).catch(e => console.error("today", e));
    get("/api/sleep?days=7").then(setSleep).catch(e => console.error("sleep", e));
    get("/api/hrv?days=14").then(setHrv).catch(e => console.error("hrv", e));
    get("/api/rhr?days=7").then(setRhr).catch(e => console.error("rhr", e));
    get("/api/activities?days=7").then(setActivities).catch(e => console.error("acts", e));
    get("/api/weekly-mileage").then(setMileage).catch(e => console.error("mileage", e));
  }, []);

  const t = today || {};
  const sleepLabel = t.sleep?.hours != null ? `${t.sleep.hours}h sleep` : "—";
  const hrvLabel = t.hrv?.baseline != null ? `baseline ${t.hrv.baseline}ms` : "ms";
  const dateLabel = new Date().toLocaleDateString(undefined, {
    weekday: "long", month: "long", day: "numeric",
  });

  return (
    <div className="app">
      <header>
        <div className="header-text">
          <h1>Harshavardhan · Training Dashboard</h1>
          <div className="subtitle">{dateLabel} · Strava + Garmin · Last 7 days</div>
        </div>
        <button
          className="theme-toggle"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          {theme === "dark" ? <SunIcon /> : <MoonIcon />}
        </button>
      </header>

      <div className="metric-row">
        <MetricCard label="Resting HR" value={t.rhr ?? "—"} sub="bpm" series={rhr} color="#fbbf24" />
        <MetricCard label="Body Battery" value={t.body_battery?.current ?? "—"} sub="/ 100" color="#4ade80" />
        <MetricCard label="Sleep Score" value={t.sleep?.score ?? "—"} sub={sleepLabel} series={sleep} dataKey="score" color="#a78bfa" />
        <MetricCard label="HRV" value={t.hrv?.last_night ?? "—"} sub={hrvLabel} series={hrv} color="#60a5fa" />
      </div>

      <div className="grid">
        <div className="card">
          <h3>Today's Readiness</h3>
          <ReadinessPanel today={t} />
        </div>
        <div className="card">
          <h3>Weekly Mileage</h3>
          <WeeklyMileage data={mileage} />
        </div>
      </div>

      <div className="grid">
        <div className="card">
          <h3>HRV · 14 days</h3>
          <TrendChart data={hrv} dataKey="value" color="#60a5fa" unit="ms" />
        </div>
        <div className="card">
          <h3>Resting HR · 7 days</h3>
          <TrendChart data={rhr} dataKey="value" color="#fbbf24" unit="bpm" />
        </div>
      </div>

      <div className="grid">
        <div className="card">
          <h3>Sleep Hours · 7 days</h3>
          <TrendChart data={sleep} dataKey="hours" color="#a78bfa" unit="h" />
        </div>
        <div className="card">
          <h3>Recent Activities</h3>
          <ActivityList activities={activities} />
        </div>
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <h3>Ask Your Coach</h3>
        <CoachChat />
      </div>
    </div>
  );
}