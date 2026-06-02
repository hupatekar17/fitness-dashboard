import { LineChart, Line, ResponsiveContainer } from "recharts";

export default function MetricCard({ label, value, sub, series, dataKey = "value", color = "#4ade80" }) {
  const data = (series || []).filter(d => d[dataKey] != null);
  const hasSparkline = data.length > 1;

  return (
    <div className="metric-card">
      <div className="label">{label}</div>
      <div className="value" style={{ color: value === "—" ? "var(--muted)" : "var(--text)" }}>
        {value}
      </div>
      <div className="sub">{sub}</div>
      {hasSparkline && (
        <div className="sparkline">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 4 }}>
              <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}