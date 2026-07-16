import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";

interface Props {
  title: string;
  value: string | number;
  sub?: string;
  icon: LucideIcon;
  trend?: { value: string; up: boolean };
  color?: string;
}

export function StatCard({ title, value, sub, icon: Icon, trend, color = "#0d9488" }: Props) {
  return (
    <div className="card card-hover p-5">
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ background: `linear-gradient(135deg, ${color}22, ${color}0d)` }}
        >
          <Icon size={18} style={{ color }} strokeWidth={2} />
        </div>
        {trend && (
          <span
            className={`chip flex items-center gap-1 ${
              trend.up ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-500"
            }`}
          >
            {trend.up ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
            {trend.value}
          </span>
        )}
      </div>
      <p className="text-[26px] font-bold text-slate-800 leading-none tracking-tight">{value}</p>
      <p className="text-xs text-slate-400 mt-2 font-medium">{title}{sub ? ` · ${sub}` : ""}</p>
    </div>
  );
}
