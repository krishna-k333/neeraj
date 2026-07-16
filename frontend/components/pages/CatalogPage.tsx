"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { Upload, Search, Tag, IndianRupee, Video, Image as ImageIcon, Trash2 } from "lucide-react";
import { api } from "../../lib/api";

type Product = { id:number; name:string; category:string; color:string; price:number; cloudinary_url:string; media_type:string; tags:string };
const CATS = ["All", "saree", "suit", "lehenga", "dupatta"];

export function CatalogPage() {
  const [search, setSearch] = useState(""); const [cat, setCat] = useState("All");
  const [products, setProducts] = useState<Product[]>([]); const [busy, setBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const load = async () => setProducts(await api.get("/api/catalog/"));
  useEffect(() => { load().catch(console.error); }, []);
  const upload = async (file: File) => {
    const form = new FormData(); form.append("name", file.name.replace(/\.[^/.]+$/, "")); form.append("category", "saree"); form.append("file", file);
    setBusy(true); try { const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; const r = await fetch(`${base}/api/catalog/`, { method:"POST", body:form }); if (!r.ok) throw new Error("Upload failed"); await load(); } finally { setBusy(false); }
  };
  const remove = async (id:number) => { await api.delete(`/api/catalog/${id}`); setProducts(p => p.filter(x => x.id !== id)); };
  const filtered = useMemo(() => products.filter(p => (cat === "All" || p.category === cat) && (!search || `${p.name} ${p.tags} ${p.color}`.toLowerCase().includes(search.toLowerCase()))), [products, cat, search]);
  return <div className="space-y-5 lg:space-y-6 max-w-[1200px] mx-auto">
    <div className="flex items-start sm:items-center justify-between gap-3 flex-col sm:flex-row"><div><h2 className="text-xl lg:text-[22px] font-bold text-slate-800 tracking-tight">Product Catalog</h2><p className="text-[13px] text-slate-400 mt-0.5">{products.length} items · powers WhatsApp replies & video generation</p></div><button onClick={() => fileRef.current?.click()} disabled={busy} className="flex items-center gap-2 btn-accent px-4 py-2.5 w-full sm:w-auto justify-center"><Upload size={15}/> {busy ? "Uploading..." : "Add Product"}</button><input ref={fileRef} type="file" accept="image/*,video/*" className="hidden" onChange={e => e.target.files?.[0] && upload(e.target.files[0])}/></div>
    <div className="flex items-center gap-3 flex-wrap"><div className="flex items-center gap-2.5 bg-white border border-[#eef1f6] rounded-full px-4 py-2.5 w-full sm:w-64"><Search size={14} className="text-slate-400"/><input placeholder="Search name, color, tag..." value={search} onChange={e => setSearch(e.target.value)} className="bg-transparent text-[13px] outline-none text-slate-600 w-full"/></div><div className="flex gap-1.5 overflow-x-auto w-full sm:w-auto">{CATS.map(c => <button key={c} onClick={() => setCat(c)} className={`flex-shrink-0 px-3.5 py-2 rounded-full text-xs font-semibold ${cat === c ? "bg-teal-600 text-white" : "bg-white text-slate-500 border border-[#eef1f6]"}`}>{c[0].toUpperCase()+c.slice(1)}</button>)}</div></div>
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"><div onClick={() => fileRef.current?.click()} className="rounded-[20px] border-2 border-dashed border-slate-200 bg-white/50 flex flex-col items-center justify-center p-4 gap-2.5 cursor-pointer min-h-[240px]"><Upload size={18} className="text-teal-600"/><p className="text-xs text-slate-400 font-medium text-center">Upload image<br/>or video</p></div>{filtered.map(p => <div key={p.id} className="card card-hover overflow-hidden group"><div className="relative"><img src={p.cloudinary_url} alt={p.name} className="w-full h-40 object-cover"/><div className="absolute inset-0 flex items-end justify-end p-2 gap-1.5"><button className="w-8 h-8 rounded-full bg-white/95 flex items-center justify-center">{p.media_type === "video" ? <Video size={13}/> : <ImageIcon size={13}/>}</button><button onClick={() => remove(p.id)} className="w-8 h-8 rounded-full bg-white/95 flex items-center justify-center"><Trash2 size={13} className="text-rose-400"/></button></div><span className="absolute top-2.5 left-2.5 chip bg-white/90 text-slate-600 capitalize shadow-sm">{p.category}</span></div><div className="p-3.5"><p className="text-[13px] font-bold text-slate-700 truncate">{p.name}</p><div className="flex items-center justify-between mt-1.5"><span className="text-[11px] text-slate-400 font-medium">{p.color}</span><span className="text-[13px] font-extrabold text-teal-600 flex items-center"><IndianRupee size={11}/>{p.price.toLocaleString()}</span></div><div className="flex flex-wrap gap-1 mt-2">{p.tags.split(",").filter(Boolean).slice(0,2).map(t => <span key={t} className="text-[10px] font-medium px-2 py-0.5 bg-slate-50 text-slate-400 rounded-full flex items-center gap-1"><Tag size={8}/>{t}</span>)}</div></div></div>)}</div>
  </div>;
}
