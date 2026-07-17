"use client";
import { useEffect, useMemo, useState } from "react";
import { Check, Image as ImageIcon, IndianRupee, Pencil, Search, Tag, Trash2, Upload, Video, X } from "lucide-react";
import { api } from "../../lib/api";

type Product = { id: number; name: string; category: string; color: string; price: number; cloudinary_url: string; media_type: string; tags: string };
const CATS = ["All", "saree", "suit", "lehenga", "dupatta"];

export function CatalogPage() {
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState("All");
  const [products, setProducts] = useState<Product[]>([]);
  const [busy, setBusy] = useState(false);
  const [editingPriceId, setEditingPriceId] = useState<number | null>(null);
  const [priceDraft, setPriceDraft] = useState("");
  const [savingPrice, setSavingPrice] = useState(false);
  const [priceError, setPriceError] = useState<string | null>(null);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newPrice, setNewPrice] = useState("");
  const [newFile, setNewFile] = useState<File | null>(null);
  const [addError, setAddError] = useState<string | null>(null);

  const load = async () => setProducts(await api.get("/api/catalog/"));
  useEffect(() => { load().catch(console.error); }, []);

  const openAddProduct = () => {
    setNewName("");
    setNewPrice("");
    setNewFile(null);
    setAddError(null);
    setIsAddOpen(true);
  };

  const upload = async () => {
    const price = Number(newPrice);
    if (!newFile) {
      setAddError("Choose an image or video");
      return;
    }
    if (!newName.trim()) {
      setAddError("Enter a product name");
      return;
    }
    if (!newPrice.trim() || !Number.isFinite(price) || price < 0) {
      setAddError("Enter a valid price");
      return;
    }
    const form = new FormData();
    form.append("name", newName.trim());
    form.append("category", "saree");
    form.append("price", String(price));
    form.append("file", newFile);
    setBusy(true);
    setAddError(null);
    try {
      const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const r = await fetch(`${base}/api/catalog/`, { method: "POST", body: form });
      if (!r.ok) throw new Error("Upload failed");
      await load();
      setIsAddOpen(false);
    } catch {
      setAddError("Couldn’t add product. Try again.");
    } finally { setBusy(false); }
  };

  const remove = async (id: number) => {
    await api.delete(`/api/catalog/${id}`);
    setProducts(p => p.filter(x => x.id !== id));
  };

  const beginPriceEdit = (product: Product) => {
    setEditingPriceId(product.id);
    setPriceDraft(String(product.price));
    setPriceError(null);
  };

  const cancelPriceEdit = () => {
    setEditingPriceId(null);
    setPriceDraft("");
    setPriceError(null);
  };

  const savePrice = async (id: number) => {
    const price = Number(priceDraft);
    if (!priceDraft.trim() || !Number.isFinite(price) || price < 0) {
      setPriceError("Enter a valid price");
      return;
    }
    setSavingPrice(true);
    setPriceError(null);
    try {
      const updated = await api.patch(`/api/catalog/${id}/price`, { price }) as Product;
      setProducts(items => items.map(item => item.id === id ? { ...item, price: updated.price } : item));
      cancelPriceEdit();
    } catch {
      setPriceError("Couldn’t save price. Try again.");
    } finally { setSavingPrice(false); }
  };

  const filtered = useMemo(() => products.filter(p =>
    (cat === "All" || p.category === cat) &&
    (!search || `${p.name} ${p.tags} ${p.color}`.toLowerCase().includes(search.toLowerCase()))
  ), [products, cat, search]);

  return <div className="space-y-5 lg:space-y-6 max-w-[1200px] mx-auto">
    <div className="flex items-start sm:items-center justify-between gap-3 flex-col sm:flex-row">
      <div><h2 className="text-xl lg:text-[22px] font-bold text-slate-800 tracking-tight">Product Catalog</h2><p className="text-[13px] text-slate-400 mt-0.5">{products.length} items · powers WhatsApp replies & video generation</p></div>
      <button onClick={openAddProduct} disabled={busy} className="flex items-center gap-2 btn-accent px-4 py-2.5 w-full sm:w-auto justify-center"><Upload size={15} /> Add Product</button>
    </div>

    <div className="flex items-center gap-3 flex-wrap">
      <div className="flex items-center gap-2.5 bg-white border border-[#eef1f6] rounded-full px-4 py-2.5 w-full sm:w-64"><Search size={14} className="text-slate-400" /><input placeholder="Search name, color, tag..." value={search} onChange={e => setSearch(e.target.value)} className="bg-transparent text-[13px] outline-none text-slate-600 w-full" /></div>
      <div className="flex gap-1.5 overflow-x-auto w-full sm:w-auto">{CATS.map(c => <button key={c} onClick={() => setCat(c)} className={`flex-shrink-0 px-3.5 py-2 rounded-full text-xs font-semibold ${cat === c ? "bg-teal-600 text-white" : "bg-white text-slate-500 border border-[#eef1f6]"}`}>{c[0].toUpperCase() + c.slice(1)}</button>)}</div>
    </div>

    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      <button onClick={openAddProduct} className="rounded-[20px] border-2 border-dashed border-slate-200 bg-white/50 flex flex-col items-center justify-center p-4 gap-2.5 min-h-[240px]"><Upload size={18} className="text-teal-600" /><span className="text-xs text-slate-400 font-medium text-center">Add image or video<br />with price</span></button>
      {filtered.map(p => <div key={p.id} className="card card-hover overflow-hidden group">
        <div className="relative"><img src={p.cloudinary_url} alt={p.name} className="w-full h-40 object-cover" /><div className="absolute inset-0 flex items-end justify-end p-2 gap-1.5"><span className="w-8 h-8 rounded-full bg-white/95 flex items-center justify-center">{p.media_type === "video" ? <Video size={13} /> : <ImageIcon size={13} />}</span><button aria-label={`Delete ${p.name}`} onClick={() => remove(p.id)} className="w-8 h-8 rounded-full bg-white/95 flex items-center justify-center"><Trash2 size={13} className="text-rose-400" /></button></div><span className="absolute top-2.5 left-2.5 chip bg-white/90 text-slate-600 capitalize shadow-sm">{p.category}</span></div>
        <div className="p-3.5"><p className="text-[13px] font-bold text-slate-700 truncate">{p.name}</p><div className="flex items-center justify-between mt-1.5"><span className="text-[11px] text-slate-400 font-medium">{p.color}</span>{editingPriceId === p.id ? <div className="flex items-center gap-1"><label className="sr-only" htmlFor={`price-${p.id}`}>Price for {p.name}</label><div className="flex items-center border border-teal-300 bg-white rounded-lg px-1.5 py-1"><IndianRupee size={11} className="text-teal-600" /><input id={`price-${p.id}`} autoFocus inputMode="decimal" value={priceDraft} onChange={e => setPriceDraft(e.target.value)} onKeyDown={e => { if (e.key === "Enter") savePrice(p.id); if (e.key === "Escape") cancelPriceEdit(); }} className="w-14 text-[12px] font-bold text-slate-700 outline-none" /></div><button aria-label="Save price" disabled={savingPrice} onClick={() => savePrice(p.id)} className="p-1 text-teal-600 disabled:opacity-40"><Check size={15} /></button><button aria-label="Cancel price edit" disabled={savingPrice} onClick={cancelPriceEdit} className="p-1 text-slate-400"><X size={15} /></button></div> : <button aria-label={`Edit price for ${p.name}`} onClick={() => beginPriceEdit(p)} className="text-[13px] font-extrabold text-teal-600 flex items-center gap-1 hover:text-teal-700"><IndianRupee size={11} />{p.price.toLocaleString()}<Pencil size={11} /></button>}</div>{editingPriceId === p.id && priceError && <p className="text-[10px] text-rose-500 mt-1">{priceError}</p>}<div className="flex flex-wrap gap-1 mt-2">{p.tags.split(",").filter(Boolean).slice(0, 2).map(t => <span key={t} className="text-[10px] font-medium px-2 py-0.5 bg-slate-50 text-slate-400 rounded-full flex items-center gap-1"><Tag size={8} />{t}</span>)}</div></div>
      </div>)}
    </div>
    {isAddOpen && <div className="fixed inset-0 z-50 bg-slate-900/40 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="add-product-title">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <div className="flex items-center justify-between gap-3"><div><h3 id="add-product-title" className="text-lg font-bold text-slate-800">Add product</h3><p className="mt-1 text-sm text-slate-500">Set the price before adding it to the catalog.</p></div><button aria-label="Close add product" onClick={() => setIsAddOpen(false)} className="p-1 text-slate-400 hover:text-slate-700"><X size={20} /></button></div>
        <div className="mt-5 space-y-4"><label className="block text-sm font-semibold text-slate-700">Product name<input value={newName} onChange={e => setNewName(e.target.value)} className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2.5 outline-none focus:border-teal-500" placeholder="e.g. Rose silk saree" /></label><label className="block text-sm font-semibold text-slate-700">Price (₹)<input value={newPrice} onChange={e => setNewPrice(e.target.value)} inputMode="decimal" className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2.5 outline-none focus:border-teal-500" placeholder="e.g. 2499" /></label><label className="block text-sm font-semibold text-slate-700">Image or video<input type="file" accept="image/*,video/*" onChange={e => setNewFile(e.target.files?.[0] || null)} className="mt-1.5 block w-full text-sm text-slate-500" /></label>{addError && <p className="text-sm text-rose-600">{addError}</p>}</div>
        <div className="mt-6 flex justify-end gap-3"><button onClick={() => setIsAddOpen(false)} disabled={busy} className="px-4 py-2 text-sm font-semibold text-slate-500">Cancel</button><button onClick={upload} disabled={busy} className="btn-accent px-4 py-2 text-sm disabled:opacity-50">{busy ? "Adding..." : "Add product"}</button></div>
      </div>
    </div>}
  </div>;
}
