function colorFor(score) {
  if (score == null) return { c: "yellow", hex: "#fbbf24" };
  if (score >= 75) return { c: "green", hex: "#4ade80" };
  if (score >= 40) return { c: "yellow", hex: "#fbbf24" };
  return { c: "red", hex: "#f87171" };
}

function verdict(c, score) {
  if (score == null) return "Wear your watch tonight";
  if (c === "green") return "Green — hard session is on the table";
  if (c === "yellow") return "Yellow — keep it easy today";
  return "Red — recovery day";
}

export default function ReadinessPanel({ today }) {
  const score = today?.readiness?.score;
  const { c, hex } = colorFor(score);
  const pct = score != null ? Math.max(0, Math.min(100, score)) : 0;
  const R = 70;
  const C = 2 * Math.PI * R;
  const offset = C - (pct / 100) * C;

  return (
    <div className="readiness-panel">
      <div className="gauge">
        <svg viewBox="0 0 160 160">
          <circle className="gauge-bg" cx="80" cy="80" r={R} />
          <circle
            className="gauge-arc"
            cx="80" cy="80" r={R}
            stroke={hex}
            strokeDasharray={C}
            strokeDashoffset={offset}
            style={{ filter: `drop-shadow(0 0 10px ${hex}66)` }}
          />
        </svg>
        <div className="gauge-number">
          <div className="big" style={{ color: hex }}>{score ?? "—"}</div>
          <div className="small">/ 100</div>
        </div>
      </div>
      <div className="readiness-info">
        <div className="readiness-verdict" style={{ color: hex }}>
          <span className={`dot ${c}`} />
          {verdict(c, score)}
        </div>
        <div className="readiness-meta">
          <div>Sleep:<strong>{today?.sleep?.hours ?? "—"}h</strong></div>
          <div>HRV:<strong>{today?.hrv?.last_night ?? "—"}ms</strong></div>
          <div>Body Battery:<strong>{today?.body_battery?.current ?? "—"}</strong></div>
          <div>RHR:<strong>{today?.rhr ?? "—"}bpm</strong></div>
        </div>
      </div>
    </div>
  );
}