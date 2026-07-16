import { Flame } from "lucide-react";

interface WarmingStatus {
  days_active: number;
  daily_limit: number;
  outbound_allowed: boolean;
  phase: string;
}

const STEPS = [
  { label: "D1–3", limit: 0 },
  { label: "D4–7", limit: 150 },
  { label: "W2", limit: 400 },
  { label: "W3", limit: 1000 },
  { label: "W4+", limit: 2000 },
];

export function WarmingBadge({ status }: { status: WarmingStatus }) {
  const color = !status.outbound_allowed ? "#f59e0b" : status.daily_limit >= 1000 ? "#0d9488" : "#3b82f6";
  const activeStep = STEPS.findIndex(s => s.limit === status.daily_limit);

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: `${color}18` }}>
            <Flame size={15} style={{ color }} />
          </div>
          <p className="text-[13px] font-bold text-slate-700">Number Warming</p>
        </div>
        <span className="chip" style={{ backgroundColor: `${color}15`, color }}>
          Day {status.days_active}
        </span>
      </div>

      <p className="text-[26px] font-bold text-slate-800 leading-none tracking-tight">
        {status.daily_limit.toLocaleString()}
        <span className="text-sm font-medium text-slate-400"> msgs/day</span>
      </p>
      <p className="text-xs font-medium mt-1.5 capitalize" style={{ color }}>{status.phase}</p>

      {/* Step progress */}
      <div className="flex items-center gap-1 mt-4">
        {STEPS.map((s, i) => (
          <div key={s.label} className="flex-1">
            <div
              className="h-1.5 rounded-full transition-all"
              style={{ backgroundColor: i <= activeStep ? color : "#eef1f6" }}
            />
            <p className={`text-[9px] mt-1 text-center font-semibold ${i === activeStep ? "" : "text-slate-300"}`}
               style={i === activeStep ? { color } : {}}>
              {s.label}
            </p>
          </div>
        ))}
      </div>
      <p className="text-[10px] text-slate-400 mt-2">Hard cap 2,000/day · 2.5–5s delay between msgs</p>
    </div>
  );
}
