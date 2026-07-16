"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import {
  LayoutDashboard, MessageCircle, Radio, Video,
  Share2, Package, Settings, Sparkles, Menu, X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  dot?: boolean;
};

const NAV_MAIN: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "WhatsApp", href: "/whatsapp", icon: MessageCircle, dot: true },
  { label: "Broadcast", href: "/broadcast", icon: Radio },
  { label: "Catalog", href: "/catalog", icon: Package },
];

const NAV_CREATE: NavItem[] = [
  { label: "Social Posts", href: "/social", icon: Share2 },
  { label: "Video AI", href: "/video", icon: Video },
];

function NavGroup({ title, items, path, onClick }: { title: string; items: NavItem[]; path: string; onClick?: () => void }) {
  return (
    <div>
      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.14em] px-3 mb-1.5">{title}</p>
      <div className="space-y-0.5">
        {items.map(({ label, href, icon: Icon, dot }) => {
          const active = path === href;
          return (
            <Link
              key={href}
              href={href}
              onClick={onClick}
              className={`relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] transition-all ${
                active
                  ? "bg-teal-50 text-teal-700 font-semibold"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-800 font-medium"
              }`}
            >
              {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-full bg-teal-500" />}
              <Icon size={17} strokeWidth={active ? 2.2 : 1.8} className={active ? "text-teal-600" : "text-slate-400"} />
              <span className="flex-1">{label}</span>
              {dot && <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function SidebarContent({ path, onNavigate }: { path: string; onNavigate?: () => void }) {
  return (
    <>
      <div className="px-5 pt-6 pb-5">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-400 to-emerald-600 flex items-center justify-center text-white text-[13px] font-extrabold shadow-md shadow-teal-200">
            NE
          </div>
          <div>
            <p className="text-[15px] font-bold text-slate-800 leading-tight tracking-tight">neeraj</p>
            <p className="text-[10px] text-slate-400 leading-tight font-medium">Enterprises OS</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3.5 space-y-6 overflow-y-auto pb-4">
        <NavGroup title="Overview" items={NAV_MAIN} path={path} onClick={onNavigate} />
        <NavGroup title="Create" items={NAV_CREATE} path={path} onClick={onNavigate} />
      </nav>

      <div className="mx-3.5 mb-3 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-700 p-4 text-white relative overflow-hidden">
        <div className="absolute -right-4 -top-6 w-20 h-20 rounded-full bg-white/10" />
        <div className="absolute -right-1 -bottom-8 w-16 h-16 rounded-full bg-white/10" />
        <Sparkles size={16} className="mb-2 text-teal-100" />
        <p className="text-xs font-bold leading-snug">AI is replying to your customers</p>
        <p className="text-[10px] text-teal-100 mt-1">Hindi + English · 24/7</p>
      </div>

      <div className="px-3.5 pb-5 pt-3 border-t border-[#eef1f6] space-y-0.5">
        <Link href="/settings" onClick={onNavigate} className="flex items-center gap-3 px-3 py-2 rounded-xl text-[13px] text-slate-500 hover:bg-slate-50 hover:text-slate-800 font-medium transition-all">
          <Settings size={16} className="text-slate-400" /> Settings
        </Link>
        <div className="flex items-center gap-3 px-3 py-2 rounded-xl text-[13px] text-slate-500 font-medium">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-[11px] font-bold text-white shadow-sm">
            N
          </div>
          <div className="min-w-0 leading-tight">
            <p className="text-xs font-semibold text-slate-700 truncate">Neeraj Shop</p>
            <p className="text-[10px] text-slate-400 truncate">Owner</p>
          </div>
        </div>
      </div>
    </>
  );
}

export function Sidebar() {
  const path = usePathname();
  const [open, setOpen] = useState(false);

  // Close drawer on route change
  useEffect(() => { setOpen(false); }, [path]);

  return (
    <>
      {/* Mobile top hamburger — floats over content when sidebar is hidden */}
      <button
        onClick={() => setOpen(true)}
        className="lg:hidden fixed top-3.5 left-3.5 z-30 w-10 h-10 rounded-xl bg-white border border-[#eef1f6] shadow-md flex items-center justify-center text-slate-600"
        aria-label="Open menu"
      >
        <Menu size={18} />
      </button>

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-[236px] flex-shrink-0 bg-white border-r border-[#eef1f6] flex-col h-full">
        <SidebarContent path={path} />
      </aside>

      {/* Mobile drawer overlay */}
      {open && (
        <div
          className="lg:hidden fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-40"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Mobile drawer */}
      <aside
        className={`lg:hidden fixed top-0 left-0 h-full w-[260px] bg-white border-r border-[#eef1f6] flex flex-col z-50 transform transition-transform duration-300 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <button
          onClick={() => setOpen(false)}
          className="absolute top-4 right-4 w-8 h-8 rounded-lg hover:bg-slate-100 flex items-center justify-center text-slate-500"
          aria-label="Close menu"
        >
          <X size={16} />
        </button>
        <SidebarContent path={path} onNavigate={() => setOpen(false)} />
      </aside>
    </>
  );
}
