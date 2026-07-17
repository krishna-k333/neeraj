"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { MessageCircle, Radio, Package, Video, Share2, Heart, ArrowRight } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { WarmingBadge } from "@/components/WarmingBadge";
import { ActivityFeed } from "@/components/ActivityFeed";
import { MiniChart } from "@/components/MiniChart";
import { api } from "@/lib/api";
import { format } from "date-fns";

type DashboardStats = {
  messages_sent: number;
  messages_received: number;
  thankyou_sent: number;
  posts_scheduled_today: number;
  videos_created_today: number;
  total_products_in_catalog: number;
  warming: { days_active: number; daily_limit: number; outbound_allowed: boolean; phase: string };
  whatsapp_status: { state?: string };
  recent_activity: Array<{ id: number; direction: string; phone: string; content: string; msg_type: string; created_at: string }>;
  seven_day_messages: number[];
};

export function DashboardPage() {
  const { data: s, isLoading, isError } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.get("/api/dashboard/stats"),
    refetchInterval: 30_000,
  });
  const today = format(new Date(), "EEEE, MMM d, yyyy");

  if (isLoading) {
    return <div className="max-w-[1200px] mx-auto text-sm text-slate-400 py-10 text-center">Loading today&apos;s dashboard…</div>;
  }

  if (isError || !s) {
    return <div className="max-w-[1200px] mx-auto rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-600">Couldn&apos;t load live dashboard data. Check that the dashboard API is running.</div>;
  }

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
        <Link href="/video" className="relative rounded-[20px] bg-gradient-to-br from-teal-500 via-teal-600 to-emerald-700 p-5 text-white overflow-hidden card-hover">
          <div className="absolute -right-8 -top-10 w-36 h-36 rounded-full bg-white/10" />
          <div className="absolute right-10 -bottom-14 w-32 h-32 rounded-full bg-white/10" />
          <p className="text-[13px] font-semibold text-teal-50 relative">Grow your reach with</p>
          <p className="text-[22px] font-extrabold leading-tight relative mt-0.5">AI Product Videos ✨</p>
          <span className="relative mt-3.5 inline-flex items-center gap-1.5 bg-white text-teal-700 text-xs font-bold px-3.5 py-2 rounded-full hover:bg-teal-50 transition">
            Generate now <ArrowRight size={13} />
          </span>
        </Link>
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
          <ActivityFeed messages={s.recent_activity} />
        </div>
        <div className="space-y-5">
          <WarmingBadge status={s.warming} />
          <MiniChart
            title="Messages · 7 days"
            data={s.seven_day_messages}
            color="#0d9488"
            total={s.messages_received + s.messages_sent}
            label="total conversations"
          />
        </div>
      </div>
    </div>
  );
}
