"use client";
import { MessageCircle, Radio, Package, Video, Share2, Heart, ArrowRight } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { WarmingBadge } from "@/components/WarmingBadge";
import { ActivityFeed } from "@/components/ActivityFeed";
import { MiniChart } from "@/components/MiniChart";
import { format } from "date-fns";

// Mock data — replace with useQuery(() => api.get("/api/dashboard/stats")) when backend is live
const MOCK_STATS = {
  messages_sent: 87,
  messages_received: 134,
  thankyou_sent: 12,
  posts_scheduled_today: 3,
  videos_created_today: 1,
  total_products_in_catalog: 48,
  warming: {
    days_active: 1,
    daily_limit: 0,
    outbound_allowed: false,
    phase: "listen-only",
  },
  whatsapp_status: { state: "open" },
};

const MOCK_ACTIVITY = [
  { id: 1, direction: "inbound", phone: "9198XXXX1234", content: "क्या आपके पास लाल रंग की साड़ी है?", msg_type: "text", created_at: new Date().toISOString() },
  { id: 2, direction: "outbound", phone: "9198XXXX1234", content: "जी हाँ! हमारे पास बहुत सुंदर लाल साड़ियाँ हैं। कौन सी रेंज चाहिए?", msg_type: "reply", created_at: new Date().toISOString() },
  { id: 3, direction: "outbound", phone: "9199XXXX5678", content: "🙏 Neeraj Enterprises से खरीदारी के लिए धन्यवाद!", msg_type: "thankyou", created_at: new Date().toISOString() },
  { id: 4, direction: "inbound", phone: "9197XXXX9012", content: "Suit ka price kya hai?", msg_type: "text", created_at: new Date().toISOString() },
];

const MSG_CHART = [40, 55, 80, 62, 90, 87, 134];

export function DashboardPage() {
  const s = MOCK_STATS;
  const today = format(new Date(), "EEEE, MMM d, yyyy");

  return (
    <div className="space-y-5 lg:space-y-6 max-w-[1200px] mx-auto">
      {/* Greeting row + hero banner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 flex flex-col justify-center">
          <p className="text-[13px] text-slate-400 font-medium">{today}</p>
          <h2 className="text-xl lg:text-[26px] font-bold text-slate-800 tracking-tight mt-1">
            Good morning, Neeraj! 🙏
          </h2>
          <p className="text-sm text-slate-500 mt-1.5">
            WhatsApp is{" "}
            <span className={`inline-flex items-center gap-1.5 font-semibold ${s.whatsapp_status.state === "open" ? "text-emerald-600" : "text-rose-500"}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${s.whatsapp_status.state === "open" ? "bg-emerald-500" : "bg-rose-500"}`} />
              {s.whatsapp_status.state === "open" ? "connected" : "disconnected"}
            </span>
            {" "}· AI is answering customers automatically
          </p>
        </div>

        {/* Gradient hero card — like the reference banner */}
        <div className="relative rounded-[20px] bg-gradient-to-br from-teal-500 via-teal-600 to-emerald-700 p-5 text-white overflow-hidden card-hover cursor-pointer">
          <div className="absolute -right-8 -top-10 w-36 h-36 rounded-full bg-white/10" />
          <div className="absolute right-10 -bottom-14 w-32 h-32 rounded-full bg-white/10" />
          <p className="text-[13px] font-semibold text-teal-50 relative">Grow your reach with</p>
          <p className="text-[22px] font-extrabold leading-tight relative mt-0.5">AI Product Videos ✨</p>
          <button className="relative mt-3.5 inline-flex items-center gap-1.5 bg-white text-teal-700 text-xs font-bold px-3.5 py-2 rounded-full hover:bg-teal-50 transition">
            Generate now <ArrowRight size={13} />
          </button>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3 lg:gap-4">
        <StatCard title="Msgs Received" value={s.messages_received} icon={MessageCircle} color="#3b82f6" trend={{ value: "+14%", up: true }} />
        <StatCard title="Msgs Sent" value={s.messages_sent} icon={Radio} color="#8b5cf6" sub="outbound" />
        <StatCard title="Thank-Yous" value={s.thankyou_sent} icon={Heart} color="#f43f5e" trend={{ value: "+3", up: true }} />
        <StatCard title="Catalog Items" value={s.total_products_in_catalog} icon={Package} color="#f59e0b" />
        <StatCard title="Posts Today" value={s.posts_scheduled_today} icon={Share2} color="#0d9488" />
        <StatCard title="Videos Made" value={s.videos_created_today} icon={Video} color="#06b6d4" />
      </div>

      {/* Main content row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <ActivityFeed messages={MOCK_ACTIVITY} />
        </div>
        <div className="space-y-5">
          <WarmingBadge status={s.warming} />
          <MiniChart
            title="Messages · 7 days"
            data={MSG_CHART}
            color="#0d9488"
            total={s.messages_received + s.messages_sent}
            label="total conversations"
          />
        </div>
      </div>
    </div>
  );
}
