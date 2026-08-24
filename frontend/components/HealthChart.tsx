"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Props {
  data: {
    day: number;
    capacity_pct: number;
  }[];
}

export default function HealthChart({ data }: Props) {
  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis
            dataKey="day"
            tick={{ fontSize: 11 }}
          />

          <YAxis
            domain={[80, 101]}
            tick={{ fontSize: 11 }}
          />

          <Tooltip />

          <Line
            type="monotone"
            dataKey="capacity_pct"
            strokeWidth={3}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}