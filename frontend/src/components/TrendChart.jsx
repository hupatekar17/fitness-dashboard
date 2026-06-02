import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";

export default function TrendChart({ data, dataKey, color, unit }) {
  if (!data) return <div className="loading">loading…</div>;
  if (!data.length) return <div className="empty">no data</div>;

  const display = data.map(d => ({ ...d, label: d.date ? d.date.slice(5) : "" }));
  const allNull = display.every(d => d[dataKey] == null);
  if (allNull) return <div className="empty">no data points</div>;

  const gradId = `grad-${dataKey}-${color.replace("#", "")}`;

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={display} margin={{ top: 8, right: 8, bottom: 0, left: -10 }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={{ fill: "#6a6a7a", fontSize: 11 }} stroke="rgba(255,255,255,0.06)" />
        <YAxis tick={{ fill: "#6a6a7a", fontSize: 11 }} stroke="rgba(255,255,255,0.06)" unit={unit ? ` ${unit}` : ""} />
        <Tooltip
          contentStyle={{ background: "rgba(20,20,28,0.95)", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 10, backdropFilter: "blur(20px)" }}
          labelStyle={{ color: "#6a6a7a", fontSize: 12 }}
          itemStyle={{ color: "#f0f0f3", fontWeight: 600 }}
          cursor={{ stroke: "rgba(255,255,255,0.1)" }}
        />
        <Area
          type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2.5}
          fill={`url(#${gradId})`}
          dot={{ r: 3, fill: color, strokeWidth: 0 }}
          activeDot={{ r: 5, fill: color, stroke: "rgba(255,255,255,0.3)", strokeWidth: 2 }}
          connectNulls
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}