"use client";
import { useState } from "react";
import { Radio, AlertTriangle, CheckCircle, Clock, ShieldCheck, Send } from "lucide-react";

const WARMING = {
  days_active: 1,
  daily_limit: 0,
  outbound_allowed: false,
  phase: "listen-only",
};

const SCHEDULE = [
  { days: "Days 1–3", limit: "0 · listen only", status: "active" },
  { days: "Days 4–7", limit: "150 / day", status: "upcoming" },
  { days: "Days 8–14", limit: "400 / day", status: "upcoming" },
  { days: "Days 15–21", limit: "1,000 / day", status: "upcoming" },
  { days: "Day 22+", limit: "2,000 / day", status: "upcoming" },
];

export function BroadcastPage() {
  const [phones, setPhones] = useState("");
  const [message, setMessage] = useState("");

  const phoneList = phones.split("\n").filter(Boolean);

  return (
    <div className="space-y-5 lg:space-y-6 max-w-[1200px] mx-auto">
      <div>
        <h2 className="text-xl lg:text-[22px] font-bold text-slate-800 tracking-tight">Broadcast Sender</h2>
        <p className="text-[13px] text-slate-400 mt-0.5">Anti-block engine · 2.5–5s random delay between every message</p>
      </div>

      {/* Warming Alert */}
      {!WARMING.outbound_allowed ? (
        <div className="flex items-start gap-3.5 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/70 rounded-[20px] p-5">
          <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
            <AlertTriangle size={18} className="text-amber-600" />
          </div>
          <div>
            <p className="text-sm font-bold text-amber-800">Outbound locked — Day {WARMING.days_active} of 3</p>
            <p className="text-[13px] text-amber-600 mt-1 leading-relaxed">Your number is in listen-only mode. Outbound unlocks on Day 4 — this warming protects your number from getting banned by WhatsApp.</p>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-3.5 bg-emerald-50 border border-emerald-200/70 rounded-[20px] p-5">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
            <CheckCircle size={18} className="text-emerald-600" />
          </div>
          <p className="text-sm text-emerald-700 font-bold">Outbound active · {WARMING.daily_limit.toLocaleString()} msgs/day limit</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Compose */}
        <div className="lg:col-span-2 card p-6 space-y-5">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-teal-50 flex items-center justify-center">
              <Radio size={16} className="text-teal-600" />
            </div>
            <h3 className="text-[15px] font-bold text-slate-800">Compose Broadcast</h3>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-500 mb-2 block">Phone Numbers <span className="font-medium text-slate-400">(one per line, 10-digit)</span></label>
            <textarea
              value={phones}
              onChange={e => setPhones(e.target.value)}
              rows={6}
              placeholder={"9812345678\n9198765432\n..."}
              className="w-full border border-[#eef1f6] bg-slate-50/50 rounded-2xl px-4 py-3 text-[13px] text-slate-700 outline-none focus:border-teal-300 focus:bg-white transition resize-none font-mono"
            />
            <p className="text-xs text-slate-400 mt-1.5 font-medium">{phoneList.length} numbers entered</p>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-500 mb-2 block">Message <span className="font-medium text-slate-400">(Hindi / English)</span></label>
            <textarea
              value={message}
              onChange={e => setMessage(e.target.value)}
              rows={5}
              placeholder="नमस्ते! हमारे नए Collection की जानकारी के लिए…"
              className="w-full border border-[#eef1f6] bg-slate-50/50 rounded-2xl px-4 py-3 text-[13px] text-slate-700 outline-none focus:border-teal-300 focus:bg-white transition resize-none"
            />
            <p className="text-xs text-slate-400 mt-1.5 font-medium">{message.length} characters</p>
          </div>

          <button
            disabled={!WARMING.outbound_allowed || !phoneList.length || !message}
            className="w-full py-3.5 btn-accent disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none flex items-center justify-center gap-2"
          >
            <Send size={15} />
            Send to {phoneList.length} contacts
          </button>
        </div>

        {/* Warming Schedule */}
        <div className="space-y-5">
          <div className="card p-6">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-9 h-9 rounded-xl bg-amber-50 flex items-center justify-center">
                <Clock size={16} className="text-amber-500" />
              </div>
              <h3 className="text-[15px] font-bold text-slate-800">Warming Schedule</h3>
            </div>
            <div className="space-y-2.5">
              {SCHEDULE.map((s, i) => (
                <div key={i} className={`flex items-center justify-between py-3 px-4 rounded-2xl transition ${s.status === "active" ? "bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/70" : "bg-slate-50/70"}`}>
                  <div>
                    <p className={`text-[13px] font-bold ${s.status === "active" ? "text-amber-700" : "text-slate-600"}`}>{s.days}</p>
                    <p className={`text-xs mt-0.5 font-medium ${s.status === "active" ? "text-amber-500" : "text-slate-400"}`}>{s.limit}</p>
                  </div>
                  {s.status === "active" && <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse ring-4 ring-amber-100" />}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[20px] bg-gradient-to-br from-teal-500 to-emerald-700 p-5 text-white relative overflow-hidden">
            <div className="absolute -right-6 -top-8 w-24 h-24 rounded-full bg-white/10" />
            <ShieldCheck size={20} className="mb-2.5 text-teal-100" />
            <p className="text-[13px] font-bold leading-snug">Anti-block protection active</p>
            <p className="text-xs text-teal-100 mt-1.5 leading-relaxed">Random 2.5–5s delay between each message keeps your number safe.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
