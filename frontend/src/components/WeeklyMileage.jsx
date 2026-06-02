import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from "recharts";

export default function WeeklyMileage({ data }) {
  if (!data) return <div className="loading">loading…</div>;
  const valid = (data || []).filter(d => !d._error);
  if (!valid.length) return <div className="empty">no mileage data</div>;

  const display = valid.map(d => ({ ...d, label: "wk " + d.week_start.slice(5) }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={display} margin={{ top: 8, right: 8, bottom: 0, left: -10 }}>
        <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={{ fill: "#6a6a7a", fontSize: 11 }} stroke="rgba(255,255,255,0.06)" />
        <YAxis tick={{ fill: "#6a6a7a", fontSize: 11 }} stroke="rgba(255,255,255,0.06)" unit=" km" />
        <Tooltip
          contentStyle={{ background: "rgba(20,20,28,0.95)", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 10, backdropFilter: "blur(20px)" }}
          labelStyle={{ color: "#6a6a7a", fontSize: 12 }}
          itemStyle={{ fontWeight: 600 }}
          cursor={{ fill: "rgba(255,255,255,0.04)" }}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: "#6a6a7a", paddingTop: 8 }} iconType="circle" />
        <Bar dataKey="run_km" name="Run" stackId="a" fill="#4ade80" />
        <Bar dataKey="ride_km" name="Ride" stackId="a" fill="#60a5fa" />
        <Bar dataKey="other_km" name="Other" stackId="a" fill="#a78bfa" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}