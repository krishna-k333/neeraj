"use client";
import { useEffect, useState } from "react";
import { MessageCircle, Wifi, WifiOff, ArrowDownLeft, ArrowUpRight, Sparkles } from "lucide-react";
import { api } from "@/lib/api";

type Conversation = { phone: string; last: string; direction: string; time: string | null };
type ChatMessage = { id: number; direction: string; content: string; status: string; msg_type: string; time: string | null };

const AVATAR_GRADIENTS = [
  "from-rose-400 to-pink-600",
  "from-teal-400 to-emerald-600",
  "from-violet-400 to-purple-600",
];

function formatTime(iso: string | null) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function WhatsAppPage() {
  const [status, setStatus] = useState<{ state?: string } | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedPhone, setSelectedPhone] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/whatsapp/status").then(setStatus).catch(() => setStatus({ state: "close" }));

    api.get("/api/whatsapp/conversations")
      .then((data: Conversation[]) => {
        setConversations(data);
        if (data.length > 0) setSelectedPhone(data[0].phone);
      })
      .finally(() => setLoading(false));

    const interval = setInterval(() => {
      api.get("/api/whatsapp/conversations").then(setConversations).catch(() => {});
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!selectedPhone) return;
    const load = () => {
      api.get(`/api/whatsapp/messages?phone=${encodeURIComponent(selectedPhone)}`)
        .then(setMessages)
        .catch(() => setMessages([]));
    };
    load();
    const interval = setInterval(load, 8000);
    return () => clearInterval(interval);
  }, [selectedPhone]);

  const connected = status?.state === "open";

  return (
    <div className="space-y-5 lg:space-y-6 max-w-[1200px] mx-auto">
      <div className="flex items-start sm:items-center justify-between gap-3 flex-col sm:flex-row">
        <div>
          <h2 className="text-xl lg:text-[22px] font-bold text-slate-800 tracking-tight">WhatsApp Chatbot</h2>
          <p className="text-[13px] text-slate-400 mt-0.5">AI answers customers in Hindi & English — automatically</p>
        </div>
        <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold ${connected ? "bg-emerald-50 text-emerald-600 border border-emerald-200/70" : "bg-rose-50 text-rose-500 border border-rose-200/70"}`}>
          {connected ? <Wifi size={13} /> : <WifiOff size={13} />}
          {connected ? "Connected" : "Disconnected"}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 h-[calc(100vh-220px)] min-h-[500px]">
        {/* Conversation list */}
        <div className="card overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-[#f3f5f9]">
            <p className="text-[15px] font-bold text-slate-800">Conversations</p>
            <p className="text-xs text-slate-400 mt-0.5">{conversations.length} active chats</p>
          </div>
          <div className="flex-1 overflow-y-auto">
            {loading && (
              <p className="text-xs text-slate-400 px-5 py-6 text-center">Loading chats…</p>
            )}
            {!loading && conversations.length === 0 && (
              <p className="text-xs text-slate-400 px-5 py-6 text-center">No conversations yet</p>
            )}
            {conversations.map((c, i) => (
              <div
                key={c.phone}
                onClick={() => setSelectedPhone(c.phone)}
                className={`px-5 py-4 cursor-pointer hover:bg-slate-50/60 transition border-b border-[#f3f5f9] ${c.phone === selectedPhone ? "bg-teal-50/50 border-l-[3px] border-l-teal-500" : ""}`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2.5">
                    <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${AVATAR_GRADIENTS[i % 3]} flex items-center justify-center text-white text-[11px] font-bold shadow-sm`}>{c.phone.slice(-2)}</div>
                    <span className="text-[13px] font-bold text-slate-700">{c.phone}</span>
                  </div>
                  <span className="text-[10px] text-slate-300 font-semibold">{formatTime(c.time)}</span>
                </div>
                <p className="text-xs text-slate-400 truncate flex items-center gap-1.5 pl-[46px]">
                  {c.direction === "outbound" ? <ArrowUpRight size={10} className="text-emerald-400 flex-shrink-0" /> : <ArrowDownLeft size={10} className="text-teal-500 flex-shrink-0" />}
                  {c.last}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Chat window */}
        <div className="lg:col-span-2 card flex flex-col overflow-hidden">
          {/* Chat header */}
          <div className="px-6 py-4 border-b border-[#f3f5f9] flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-rose-400 to-pink-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
              {selectedPhone ? selectedPhone.slice(-2) : <MessageCircle size={16} />}
            </div>
            <div>
              <p className="text-[14px] font-bold text-slate-800">{selectedPhone || "Select a conversation"}</p>
              <p className="text-[11px] text-slate-400 font-semibold">Read-only view — live from Evolution API</p>
            </div>
            <div className="ml-auto flex items-center gap-1.5 text-[11px] bg-gradient-to-r from-violet-50 to-purple-50 text-violet-600 px-3 py-1.5 rounded-full border border-violet-100 font-bold">
              <Sparkles size={11} /> AI Active
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-5 space-y-3.5 bg-[#f8fafb]">
            {!selectedPhone && (
              <p className="text-xs text-slate-400 text-center mt-10">Pick a conversation to view its history</p>
            )}
            {selectedPhone && messages.length === 0 && (
              <p className="text-xs text-slate-400 text-center mt-10">No messages yet</p>
            )}
            {messages.map((m) => (
              <div key={m.id} className={`flex ${m.direction === "inbound" ? "justify-start" : "justify-end"}`}>
                <div className={`max-w-[75%] px-4 py-3 text-[13px] leading-relaxed ${
                  m.direction === "inbound"
                    ? "bg-white text-slate-700 rounded-2xl rounded-tl-md shadow-sm border border-[#eef1f6]"
                    : "bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-2xl rounded-tr-md shadow-md shadow-teal-200/50"
                }`}>
                  <p>{m.content}</p>
                  <p className={`text-[10px] mt-1.5 font-medium ${m.direction === "inbound" ? "text-slate-300" : "text-teal-100"} text-right`}>{formatTime(m.time)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
