"use client";
import React, { useState } from "react";
import { Camera, PlayCircle, ThumbsUp, MapPin, Calendar, Clock, ImagePlus, Zap, Check, type LucideIcon } from "lucide-react";

const PLATFORMS = [
  { id: "instagram", label: "Instagram", icon: Camera, color: "#e1306c", gradient: "from-pink-500 to-rose-600" },
  { id: "youtube",   label: "YouTube",   icon: PlayCircle, color: "#ff0000", gradient: "from-red-500 to-red-700" },
  { id: "facebook",  label: "Facebook",  icon: ThumbsUp, color: "#1877f2", gradient: "from-blue-500 to-blue-700" },
  { id: "google_my_business", label: "Google Business", icon: MapPin, color: "#34a853", gradient: "from-green-500 to-emerald-700" },
];

const POSTS = [
  { id: 1, caption: "✨ नई Banarasi Silk Saree Collection! 🥻 Shop now at Neeraj Enterprises", scheduled_at: "Jul 4, 10:00 AM", platforms: ["instagram", "youtube", "facebook"], status: "scheduled" },
  { id: 2, caption: "Grand Summer Sale — Up to 40% off on all suits! 🎉", scheduled_at: "Jul 4, 2:00 PM", platforms: ["instagram", "facebook", "google_my_business"], status: "scheduled" },
  { id: 3, caption: "Behind the scenes at our shop 📸 #Saree #Fashion", scheduled_at: "Jul 3, 11:00 AM", platforms: ["instagram"], status: "published" },
];

const PLATFORM_META: Record<string, { color: string; Icon: LucideIcon; label: string }> = {
  instagram: { color: "#e1306c", Icon: Camera,     label: "Instagram" },
  youtube:   { color: "#ff0000", Icon: PlayCircle, label: "YouTube" },
  facebook:  { color: "#1877f2", Icon: ThumbsUp,   label: "Facebook" },
  google_my_business: { color: "#34a853", Icon: MapPin, label: "Google Business" },
};

export function SocialPage() {
  const [selected, setSelected] = useState<string[]>(["instagram", "youtube", "facebook", "google_my_business"]);
  const [caption, setCaption] = useState("");

  const toggle = (id: string) => {
    setSelected(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);
  };

  return (
    <div className="space-y-5 lg:space-y-6 max-w-[1200px] mx-auto">
      <div>
        <h2 className="text-xl lg:text-[22px] font-bold text-slate-800 tracking-tight">Social Media</h2>
        <p className="text-[13px] text-slate-400 mt-0.5">Post once → publishes to Instagram, YouTube, Facebook & Google Business simultaneously</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Compose ONCE */}
        <div className="card p-5 lg:p-6 space-y-5">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-100 to-emerald-100 flex items-center justify-center">
              <Zap size={16} className="text-teal-600" />
            </div>
            <div>
              <h3 className="text-[15px] font-bold text-slate-800">Post Once, Everywhere</h3>
              <p className="text-[11px] text-slate-400 font-medium">One caption, one media, all platforms</p>
            </div>
          </div>

          {/* Media */}
          <div className="border-2 border-dashed border-slate-200 rounded-2xl p-6 text-center cursor-pointer hover:border-teal-400 hover:bg-teal-50/30 transition group">
            <div className="w-11 h-11 rounded-full bg-teal-50 flex items-center justify-center mx-auto mb-2.5 group-hover:scale-110 transition">
              <ImagePlus size={18} className="text-teal-600" />
            </div>
            <p className="text-xs text-slate-400 font-medium">Drop media or pick from catalog</p>
          </div>

          {/* Caption */}
          <div>
            <label className="text-xs font-bold text-slate-500 mb-2 block">Caption</label>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              rows={4}
              placeholder="Write once — publishes to all selected platforms…"
              className="w-full border border-[#eef1f6] bg-slate-50/50 rounded-2xl px-4 py-3 text-[13px] outline-none focus:border-teal-300 focus:bg-white transition resize-none"
            />
            <p className="text-[10px] text-slate-400 mt-1 font-medium">{caption.length} chars · IG max 2,200 · YT max 5,000 · FB max 63,206 · Google Business max 1,500</p>
          </div>

          {/* Platform checkboxes */}
          <div>
            <label className="text-xs font-bold text-slate-500 mb-2 block">Publish to</label>
            <div className="space-y-2">
              {PLATFORMS.map(p => {
                const active = selected.includes(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => toggle(p.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-2xl border transition ${
                      active
                        ? "border-teal-300 bg-teal-50/50"
                        : "border-[#eef1f6] hover:border-slate-300 bg-white"
                    }`}
                  >
                    <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${p.gradient} flex items-center justify-center text-white flex-shrink-0`}>
                      <p.icon size={16} />
                    </div>
                    <span className="text-[13px] font-semibold text-slate-700 flex-1 text-left">{p.label}</span>
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center transition ${
                      active ? "bg-teal-500" : "bg-slate-100 border border-slate-200"
                    }`}>
                      {active && <Check size={12} className="text-white" strokeWidth={3} />}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Time */}
          <div>
            <label className="text-xs font-bold text-slate-500 mb-2 flex items-center gap-1.5"><Clock size={12} /> Schedule Time</label>
            <input type="datetime-local" className="w-full border border-[#eef1f6] bg-slate-50/50 rounded-2xl px-4 py-2.5 text-[13px] outline-none focus:border-teal-300 focus:bg-white transition" />
          </div>

          <button
            disabled={!selected.length || !caption}
            className="w-full py-3 btn-accent flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none"
          >
            <Calendar size={14} /> Publish to {selected.length} {selected.length === 1 ? "platform" : "platforms"}
          </button>
        </div>

        {/* Posts list */}
        <div className="lg:col-span-2 space-y-3">
          <h3 className="text-[15px] font-bold text-slate-800 px-1">Upcoming & Published</h3>
          {POSTS.map(post => (
            <div key={post.id} className="card card-hover p-4 lg:p-5">
              {/* Platform stack */}
              <div className="flex items-start gap-3 lg:gap-4">
                <div className="flex -space-x-2 flex-shrink-0">
                  {post.platforms.map((pid, i) => {
                    const meta = PLATFORM_META[pid];
                    return (
                      <div
                        key={pid}
                        className="w-10 h-10 rounded-2xl flex items-center justify-center ring-2 ring-white"
                        style={{ background: `linear-gradient(135deg, ${meta.color}, ${meta.color}dd)`, zIndex: 10 - i }}
                      >
                        <meta.Icon size={16} className="text-white" />
                      </div>
                    );
                  })}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-semibold text-slate-700 line-clamp-2 leading-relaxed">{post.caption}</p>
                  <div className="flex flex-wrap items-center gap-2 mt-2">
                    <span className="text-[10px] text-slate-400 flex items-center gap-1 font-medium"><Clock size={10} /> {post.scheduled_at}</span>
                    <span className="text-[10px] text-slate-300">·</span>
                    <span className="text-[10px] text-slate-500 font-semibold">
                      {post.platforms.map(p => PLATFORM_META[p].label).join(" + ")}
                    </span>
                  </div>
                </div>
                <span className={`chip flex-shrink-0 ${post.status === "published" ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"}`}>
                  {post.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
