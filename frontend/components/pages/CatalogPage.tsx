"use client";
import { useState } from "react";
import { Upload, Search, Tag, IndianRupee, Video, Image as ImageIcon, Trash2 } from "lucide-react";

const MOCK_PRODUCTS = [
  { id: 1, name: "Banarasi Silk Saree", category: "saree", color: "Red", price: 2500, cloudinary_url: "https://placehold.co/300x400/f43f5e/fff?text=Banarasi", media_type: "image", tags: "silk,bridal,festive" },
  { id: 2, name: "Kanjivaram Saree", category: "saree", color: "Green", price: 3800, cloudinary_url: "https://placehold.co/300x400/10b981/fff?text=Kanjivaram", media_type: "image", tags: "silk,wedding,south" },
  { id: 3, name: "Anarkali Suit Set", category: "suit", color: "Blue", price: 1800, cloudinary_url: "https://placehold.co/300x400/3b82f6/fff?text=Anarkali", media_type: "image", tags: "party,designer" },
  { id: 4, name: "Georgette Saree", category: "saree", color: "Pink", price: 1200, cloudinary_url: "https://placehold.co/300x400/ec4899/fff?text=Georgette", media_type: "image", tags: "casual,daily" },
  { id: 5, name: "Palazzo Suit", category: "suit", color: "Yellow", price: 1500, cloudinary_url: "https://placehold.co/300x400/f59e0b/fff?text=Palazzo", media_type: "image", tags: "casual,cotton" },
  { id: 6, name: "Bridal Lehenga", category: "lehenga", color: "Maroon", price: 8500, cloudinary_url: "https://placehold.co/300x400/b91c1c/fff?text=Lehenga", media_type: "image", tags: "bridal,heavy,wedding" },
];

const CATS = ["All", "saree", "suit", "lehenga", "dupatta"];

export function CatalogPage() {
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState("All");

  const filtered = MOCK_PRODUCTS.filter(p => {
    const matchCat = cat === "All" || p.category === cat;
    const matchSearch = !search || p.name.toLowerCase().includes(search.toLowerCase()) || p.tags.includes(search.toLowerCase()) || p.color.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div className="space-y-5 lg:space-y-6 max-w-[1200px] mx-auto">
      {/* Header */}
      <div className="flex items-start sm:items-center justify-between gap-3 flex-col sm:flex-row">
        <div>
          <h2 className="text-xl lg:text-[22px] font-bold text-slate-800 tracking-tight">Product Catalog</h2>
          <p className="text-[13px] text-slate-400 mt-0.5">{MOCK_PRODUCTS.length} items · powers WhatsApp replies & video generation</p>
        </div>
        <button className="flex items-center gap-2 btn-accent px-4 py-2.5 w-full sm:w-auto justify-center">
          <Upload size={15} /> Add Product
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2.5 bg-white border border-[#eef1f6] rounded-full px-4 py-2.5 w-full sm:w-64 focus-within:border-teal-300 transition">
          <Search size={14} className="text-slate-400" />
          <input placeholder="Search name, color, tag…" value={search} onChange={e => setSearch(e.target.value)} className="bg-transparent text-[13px] outline-none text-slate-600 placeholder-slate-400 w-full" />
        </div>
        <div className="flex gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {CATS.map(c => (
            <button key={c} onClick={() => setCat(c)} className={`flex-shrink-0 px-3.5 py-2 rounded-full text-xs font-semibold transition ${cat === c ? "bg-teal-600 text-white shadow-md shadow-teal-200" : "bg-white text-slate-500 border border-[#eef1f6] hover:border-teal-300 hover:text-teal-600"}`}>
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {/* Upload card */}
        <div className="rounded-[20px] border-2 border-dashed border-slate-200 bg-white/50 flex flex-col items-center justify-center p-4 gap-2.5 cursor-pointer hover:border-teal-400 hover:bg-teal-50/40 transition min-h-[240px] group">
          <div className="w-11 h-11 rounded-full bg-teal-50 flex items-center justify-center group-hover:scale-110 transition">
            <Upload size={18} className="text-teal-600" />
          </div>
          <p className="text-xs text-slate-400 font-medium text-center">Upload image<br/>or video</p>
        </div>

        {filtered.map(p => (
          <div key={p.id} className="card card-hover overflow-hidden group">
            <div className="relative">
              <img src={p.cloudinary_url} alt={p.name} className="w-full h-40 object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition flex items-end justify-end p-2 gap-1.5">
                <button className="w-8 h-8 rounded-full bg-white/95 flex items-center justify-center shadow-md hover:scale-105 transition">
                  {p.media_type === "video" ? <Video size={13} className="text-slate-600" /> : <ImageIcon size={13} className="text-slate-600" />}
                </button>
                <button className="w-8 h-8 rounded-full bg-white/95 flex items-center justify-center shadow-md hover:scale-105 transition">
                  <Trash2 size={13} className="text-rose-400" />
                </button>
              </div>
              <span className="absolute top-2.5 left-2.5 chip bg-white/90 text-slate-600 backdrop-blur-sm capitalize shadow-sm">{p.category}</span>
            </div>
            <div className="p-3.5">
              <p className="text-[13px] font-bold text-slate-700 truncate">{p.name}</p>
              <div className="flex items-center justify-between mt-1.5">
                <span className="text-[11px] text-slate-400 font-medium">{p.color}</span>
                <span className="text-[13px] font-extrabold text-teal-600 flex items-center"><IndianRupee size={11} strokeWidth={2.5} />{p.price.toLocaleString()}</span>
              </div>
              <div className="flex flex-wrap gap-1 mt-2">
                {p.tags.split(",").slice(0, 2).map(t => (
                  <span key={t} className="text-[10px] font-medium px-2 py-0.5 bg-slate-50 text-slate-400 rounded-full flex items-center gap-1"><Tag size={8}/>{t}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
