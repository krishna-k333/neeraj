import React from "react";
import { format } from "date-fns";
import { ArrowDownLeft, ArrowUpRight, Heart, Radio } from "lucide-react";

interface Message {
  id: number;
  direction: string;
  phone: string;
  content: string;
  msg_type: string;
  created_at: string;
}

const TYPE_META: Record<string, { icon: React.ReactNode; label: string; color: string }> = {
  reply:     { icon: <ArrowUpRight size={13} />,  label: "AI Reply",  color: "#0d9488" },
  text:      { icon: <ArrowDownLeft size={13} />, label: "Inbound",   color: "#3b82f6" },
  thankyou:  { icon: <Heart size={13} />,          label: "Thank You", color: "#f43f5e" },
  broadcast: { icon: <Radio size={13} />,          label: "Broadcast", color: "#8b5cf6" },
};

export function ActivityFeed({ messages }: { messages: Message[] }) {
  return (
    <div className="card overflow-hidden">
      <div className="px-6 py-4 flex items-center justify-between">
        <div>
          <h3 className="text-[15px] font-bold text-slate-800 tracking-tight">Recent Messages</h3>
          <p className="text-xs text-slate-400 mt-0.5">Live customer conversations</p>
        </div>
        <button className="text-xs font-semibold text-teal-600 hover:text-teal-700 transition">View all →</button>
      </div>
      <div>
        {messages.map((m, idx) => {
          const meta = TYPE_META[m.msg_type] ?? TYPE_META["text"];
          const time = format(new Date(m.created_at), "HH:mm");
          return (
            <div key={m.id} className={`px-6 py-4 flex items-start gap-3.5 hover:bg-slate-50/60 transition ${idx !== messages.length - 1 ? "border-b border-[#f3f5f9]" : ""}`}>
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: `${meta.color}14`, color: meta.color }}
              >
                {meta.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[13px] font-bold text-slate-700">{m.phone}</span>
                  <span className="chip" style={{ backgroundColor: `${meta.color}12`, color: meta.color }}>
                    {meta.label}
                  </span>
                </div>
                <p className="text-[13px] text-slate-500 truncate leading-relaxed">{m.content}</p>
              </div>
              <span className="text-[11px] text-slate-300 font-semibold flex-shrink-0 mt-0.5">{time}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
