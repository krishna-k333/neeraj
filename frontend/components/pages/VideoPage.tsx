"use client";
import { useState } from "react";
import { Video, Sparkles, Clock, CheckCircle, Loader, Zap, Calendar, type LucideIcon } from "lucide-react";
import { api } from "@/lib/api";

const PRODUCTS = [
  { id: 1, name: "Banarasi Silk Saree", thumb: "https://placehold.co/80x80/f43f5e/fff?text=S" },
  { id: 2, name: "Kanjivaram Saree", thumb: "https://placehold.co/80x80/10b981/fff?text=K" },
  { id: 3, name: "Anarkali Suit", thumb: "https://placehold.co/80x80/3b82f6/fff?text=A" },
];

const JOBS = [
  { id: 1, name: "Banarasi Silk Saree", status: "done", cloudinary_url: "https://placehold.co/320x180/0d9488/fff?text=Video+Ready", created_at: "10 mins ago" },
  { id: 2, name: "Anarkali Suit", status: "processing", cloudinary_url: null, created_at: "25 mins ago" },
];

const STATUS_META: Record<string, { color: string; label: string; Icon: LucideIcon }> = {
  done:       { color: "#0d9488", label: "Ready",      Icon: CheckCircle },
  processing: { color: "#f59e0b", label: "Generating", Icon: Loader },
  pending:    { color: "#94a3b8", label: "Queued",     Icon: Clock },
  failed:     { color: "#ef4444", label: "Failed",     Icon: Clock },
};

const VIDEO_STYLES = [
  { id: "showcase", title: "Product-only showcase", duration: "5–7 sec", description: "Cinematic macro-pan across the fabric. No model." },
  { id: "model_walk", title: "Virtual model fashion walk", duration: "7 sec", description: "An Indian model wears the saree in a premium boutique." },
  { id: "dynamic_cut", title: "Combined dynamic cut", duration: "10 sec", description: "Product close-up transitions into a model showroom shot." },
] as const;

// Mock quota — replace with fetch to /api/video/quota
const QUOTA = {
  used: 8,
  limit: 40,
  cycle_start: "Jul 9",
  cycle_end: "Aug 8",
  days_until_reset: 6,
};

function QuotaCard() {
  const remaining = QUOTA.limit - QUOTA.used;
  const pct = (QUOTA.used / QUOTA.limit) * 100;
  const low = remaining <= 5;

  return (
    <div className="card p-5 lg:p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-100 to-purple-100 flex items-center justify-center">
            <Zap size={16} className="text-violet-600" />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-800">Monthly Quota</p>
            <p className="text-[11px] text-slate-400 font-medium">Billing cycle from the 9th</p>
          </div>
        </div>
        <span className={`chip ${low ? "bg-rose-50 text-rose-600" : "bg-violet-50 text-violet-600"}`}>
          {remaining} left
        </span>
      </div>

      <div className="flex items-baseline gap-1.5">
        <p className="text-[28px] font-extrabold text-slate-800 leading-none tracking-tight">{QUOTA.used}</p>
        <p className="text-sm font-semibold text-slate-400">/ {QUOTA.limit}</p>
      </div>
      <p className="text-xs text-slate-400 font-medium mt-1">videos used this cycle</p>

      {/* Progress bar */}
      <div className="mt-4 w-full bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          className={`h-2 rounded-full transition-all bg-gradient-to-r ${low ? "from-rose-400 to-rose-500" : "from-violet-400 to-purple-600"}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="mt-4 flex items-center gap-2 text-[11px] text-slate-500 font-medium bg-slate-50 rounded-xl px-3 py-2">
        <Calendar size={11} className="text-slate-400" />
        Cycle: <span className="font-semibold text-slate-700">{QUOTA.cycle_start} → {QUOTA.cycle_end}</span>
        <span className="text-slate-300">·</span>
        <span className="text-slate-500">resets in {QUOTA.days_until_reset}d</span>
      </div>
    </div>
  );
}

export function VideoPage() {
  const remaining = QUOTA.limit - QUOTA.used;
  const canGenerate = remaining > 0;

  const [productId, setProductId] = useState<number | null>(null);
  const [productReference, setProductReference] = useState("");
  const [videoStyle, setVideoStyle] = useState<(typeof VIDEO_STYLES)[number]["id"] | null>(null);
  const [voiceoverScript, setVoiceoverScript] = useState("");
  const [languageVibe, setLanguageVibe] = useState("High-energy Hinglish");
  const [submitting, setSubmitting] = useState(false);

  async function handleGenerate() {
    if (!productId || !videoStyle || !voiceoverScript.trim()) return;
    setSubmitting(true);
    try {
      await api.post("/api/video/generate", {
        product_id: productId,
        product_reference: productReference,
        video_style: videoStyle,
        audio_script: voiceoverScript.trim(),
        language_vibe: languageVibe,
      });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-5 lg:space-y-6 max-w-[1200px] mx-auto">
      <div>
        <h2 className="text-xl lg:text-[22px] font-bold text-slate-800 tracking-tight">Video AI Generator</h2>
        <p className="text-[13px] text-slate-400 mt-0.5">AI-generated · 9:16 Reels format · 40 videos/month</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left column: quota + generator */}
        <div className="space-y-5">
          <QuotaCard />

          <div className="card p-5 lg:p-6 space-y-5">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-violet-50 flex items-center justify-center">
                <Sparkles size={16} className="text-violet-500" />
              </div>
              <h3 className="text-[15px] font-bold text-slate-800">Generate Video</h3>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-500 mb-2.5 block">Select Product from Catalog</label>
              <div className="space-y-2">
                {PRODUCTS.map(p => (
                  <label key={p.id} className="flex items-center gap-3 p-3 rounded-2xl border border-[#eef1f6] cursor-pointer hover:border-violet-300 hover:bg-violet-50/40 transition has-[:checked]:border-violet-400 has-[:checked]:bg-violet-50/60">
                    <input
                      type="radio"
                      name="product"
                      className="accent-violet-500"
                      checked={productId === p.id}
                      onChange={() => setProductId(p.id)}
                    />
                    <img src={p.thumb} alt={p.name} className="w-9 h-9 rounded-xl object-cover" />
                    <span className="text-[13px] font-semibold text-slate-600">{p.name}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-500 mb-2 block">Product Details <span className="font-medium text-slate-400">(optional override)</span></label>
              <input
                type="text"
                value={productReference}
                onChange={(e) => setProductReference(e.target.value)}
                placeholder="e.g. Red Banarasi silk saree with gold zari border"
                className="w-full border border-[#eef1f6] bg-slate-50/50 rounded-2xl px-4 py-3 text-[13px] outline-none focus:border-violet-300 focus:bg-white transition"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-500 mb-2.5 block">Choose Video Style</label>
              <div className="space-y-2">
                {VIDEO_STYLES.map(style => <button type="button" key={style.id} onClick={() => setVideoStyle(style.id)} className={`w-full rounded-2xl border p-3 text-left transition ${videoStyle === style.id ? "border-violet-400 bg-violet-50" : "border-[#eef1f6] hover:border-violet-300"}`}><div className="flex items-center justify-between gap-3"><span className="text-[13px] font-bold text-slate-700">{style.title}</span><span className="text-[11px] font-semibold text-violet-600">{style.duration}</span></div><p className="mt-1 text-[11px] text-slate-500">{style.description}</p></button>)}
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-500 mb-2 block">Language / Vibe</label>
              <input
                type="text"
                value={languageVibe}
                onChange={(e) => setLanguageVibe(e.target.value)}
                placeholder="e.g. High-energy Hinglish"
                className="w-full border border-[#eef1f6] bg-slate-50/50 rounded-2xl px-4 py-3 text-[13px] outline-none focus:border-violet-300 focus:bg-white transition"
              />
            </div>

            {videoStyle && <div>
              <label className="text-xs font-bold text-slate-500 mb-2 block">Your Voiceover Script <span className="text-rose-500">(required)</span></label>
              <p className="mb-2 text-[11px] text-slate-400">Write the exact words a human should say. We will use your script as-is and won’t generate one.</p>
              <textarea value={voiceoverScript} onChange={(e) => setVoiceoverScript(e.target.value)} rows={4} placeholder="Type your voiceover script here..." className="w-full resize-y border border-[#eef1f6] bg-slate-50/50 rounded-2xl px-4 py-3 text-[13px] outline-none focus:border-violet-300 focus:bg-white transition" />
            </div>}

            <button
              disabled={!canGenerate || !productId || !videoStyle || !voiceoverScript.trim() || submitting}
              onClick={handleGenerate}
              className="w-full py-3.5 rounded-xl text-sm font-bold text-white bg-gradient-to-r from-violet-500 to-purple-600 hover:opacity-90 transition flex items-center justify-center gap-2 shadow-lg shadow-violet-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none"
            >
              <Video size={15} />
              {!canGenerate
                ? `Cap reached — resets in ${QUOTA.days_until_reset}d`
                : submitting
                ? "Generating…"
                : "Generate Video"}
            </button>
            <p className="text-[11px] text-slate-400 text-center font-medium">AI expands these fields into a cinematic prompt · ~3–5 min per video</p>
          </div>
        </div>

        {/* Jobs */}
        <div className="lg:col-span-2 space-y-3">
          <h3 className="text-[15px] font-bold text-slate-800 px-1">Video Jobs</h3>
          {JOBS.map(job => {
            const meta = STATUS_META[job.status];
            return (
              <div key={job.id} className="card card-hover p-4 lg:p-5 flex items-center gap-3 lg:gap-5">
                {job.cloudinary_url ? (
                  <img src={job.cloudinary_url} alt={job.name} className="w-20 h-12 lg:w-28 lg:h-16 rounded-2xl object-cover flex-shrink-0 shadow-sm" />
                ) : (
                  <div className="w-20 h-12 lg:w-28 lg:h-16 rounded-2xl bg-slate-50 border border-[#eef1f6] flex items-center justify-center flex-shrink-0">
                    <Loader size={18} className="text-slate-300 animate-spin" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] lg:text-[14px] font-bold text-slate-700 truncate">{job.name}</p>
                  <p className="text-xs text-slate-400 mt-1 font-medium">{job.created_at}</p>
                </div>
                <div className="flex items-center gap-1.5 chip flex-shrink-0" style={{ backgroundColor: `${meta.color}12`, color: meta.color }}>
                  <meta.Icon size={11} className={job.status === "processing" ? "animate-spin" : ""} />
                  <span className="hidden sm:inline">{meta.label}</span>
                </div>
                {job.status === "done" && (
                  <button className="btn-accent px-3 lg:px-4 py-2 text-xs hidden sm:block">Share</button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
