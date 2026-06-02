function fmtKm(m) { return m ? (m / 1000).toFixed(1) + " km" : "—"; }
function fmtMin(s) {
  if (!s) return "—";
  const min = Math.round(s / 60);
  if (min < 60) return `${min} min`;
  const h = Math.floor(min / 60);
  const r = min % 60;
  return `${h}h ${r}m`;
}
function fmtDate(s) {
  try {
    return new Date(s).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
  } catch { return s; }
}

export default function ActivityList({ activities }) {
  if (!activities) return <div className="loading">loading…</div>;
  const valid = (activities || []).filter(a => !a._error);
  if (!valid.length) return <div className="empty">no recent activities</div>;

  return (
    <div>
      {valid.slice(0, 8).map((a, i) => (
        <div key={i} className="activity-row">
          <div style={{ minWidth: 0, flex: 1 }}>
            <div>
              <span className={`source-badge ${a.source}`}>{a.source}</span>
              <strong>{a.name || a.type || "Activity"}</strong>
            </div>
            <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 4 }}>
              {fmtDate(a.start_time)} · {a.type}
            </div>
          </div>
          <div style={{ textAlign: "right", whiteSpace: "nowrap" }}>
            <div style={{ fontWeight: 600, fontSize: 14, fontVariantNumeric: "tabular-nums" }}>
              {fmtKm(a.distance_meters)}
            </div>
            <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 2 }}>
              {fmtMin(a.duration_seconds)}
              {a.avg_hr ? ` · ${Math.round(a.avg_hr)} bpm` : ""}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}