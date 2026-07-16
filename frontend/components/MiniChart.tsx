"use client";
import { AreaChart, Area, ResponsiveContainer, Tooltip } from "recharts";

interface Props {
  title: string;
  data: number[];
  color: string;
  total: number;
  label: string;
}

export function MiniChart({ title, data, color, total, label }: Props) {
  const chartData = data.map((v, i) => ({ i, v }));
  const gradId = `grad-${color.replace("#", "")}`;

  return (
    <div className="card p-5">
      <p className="text-[13px] font-bold text-slate-700 mb-3">{title}</p>
      <p className="text-[26px] font-bold text-slate-800 leading-none tracking-tight">{total.toLocaleString()}</p>
      <p className="text-xs text-slate-400 mt-1.5 mb-3 font-medium">{label}</p>
      <div className="h-[72px] -mx-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.22} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Tooltip
              cursor={{ stroke: color, strokeWidth: 1, strokeDasharray: "3 3" }}
              contentStyle={{ fontSize: 11, padding: "4px 10px", borderRadius: 10, border: "1px solid #eef1f6", boxShadow: "0 4px 12px rgba(0,0,0,0.08)" }}
              formatter={(value) => [Number(value ?? 0), "msgs"]}
              labelFormatter={() => ""}
            />
            <Area
              type="monotone"
              dataKey="v"
              stroke={color}
              strokeWidth={2.5}
              fill={`url(#${gradId})`}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 2, stroke: "#fff" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
