"use client";
import { Search, Bell, Plus } from "lucide-react";
import { usePathname } from "next/navigation";

const PAGE_TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/whatsapp": "WhatsApp Chatbot",
  "/broadcast": "Broadcast Sender",
  "/catalog": "Product Catalog",
  "/social": "Social Media",
  "/video": "Video AI",
  "/settings": "Settings",
};

export function TopBar() {
  const path = usePathname();
  const title = PAGE_TITLES[path] ?? "Dashboard";

  return (
    <header className="h-16 lg:h-[68px] bg-white/70 backdrop-blur-md border-b border-[#eef1f6] flex items-center px-4 lg:px-7 gap-2 lg:gap-3 flex-shrink-0 pl-16 lg:pl-7">
      {/* Search */}
      <div className="hidden sm:flex items-center gap-2.5 bg-[#f5f7fa] border border-transparent focus-within:border-teal-300 focus-within:bg-white rounded-full px-4 py-2.5 w-full max-w-sm transition">
        <Search size={15} className="text-slate-400 flex-shrink-0" />
        <input
          placeholder={`Search ${title.toLowerCase()}…`}
          className="bg-transparent text-[13px] outline-none text-slate-600 placeholder-slate-400 w-full"
        />
      </div>

      {/* Mobile page title */}
      <p className="sm:hidden flex-1 text-sm font-bold text-slate-800 truncate">{title}</p>

      <div className="flex-1 hidden sm:block" />

      <button className="hidden md:flex items-center gap-1.5 btn-accent px-3.5 py-2 text-xs">
        <Plus size={14} /> New Broadcast
      </button>

      <button className="w-9 h-9 lg:w-10 lg:h-10 rounded-full bg-white border border-[#eef1f6] flex items-center justify-center relative text-slate-500 hover:text-slate-800 hover:border-slate-200 transition">
        <Bell size={16} />
        <span className="absolute top-2 right-2.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white" />
      </button>

      <div className="w-9 h-9 lg:w-10 lg:h-10 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-[13px] font-bold text-white cursor-pointer ring-2 ring-white shadow-md">
        N
      </div>
    </header>
  );
}
