'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  BarChart3,
  Bookmark,
  BriefcaseBusiness,
  Database,
  Globe2,
  Layers,
  LogOut,
  MapPin,
  Search,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { clearAuthToken, getStoredUser, type User } from '@/lib/api';

const navItems = [
  { label: 'Dashboard', href: '/', icon: BarChart3 },
  { label: 'Business Finder', href: '/scraper', icon: Search, badge: 'Scraper' },
  { label: 'All Leads', href: '/leads', icon: BriefcaseBusiness },
  { label: 'Saved Leads', href: '/saved', icon: Bookmark },
  { label: 'Scrape Jobs', href: '/jobs', icon: Database },
  { label: 'Categories', href: '/categories', icon: Layers },
  { label: 'TN Locations', href: '/locations', icon: MapPin },
  { label: 'Admin Panel', href: '/admin', icon: ShieldCheck },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  function handleLogout() {
    clearAuthToken();
    router.push('/login');
  }

  return (
    <aside className="hidden w-64 shrink-0 flex-col bg-[#0b1220] px-5 py-6 text-white lg:flex border-r border-white/5">
      {/* Brand Header */}
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-tr from-blue to-cyan text-sm font-bold text-white shadow-lg shadow-blue/20">
          SRA
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold tracking-tight text-white">Lead Finder</span>
            <span className="rounded bg-cyan/20 px-1 py-0.2 text-[10px] font-semibold text-cyan">v1.0</span>
          </div>
          <p className="text-[11px] font-medium text-slate-400">Find. Verify. Connect.</p>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 space-y-1.5 overflow-y-auto">
        <div className="mb-2 px-3 text-[11px] font-bold uppercase tracking-wider text-slate-500">Navigation</div>
        {navItems.map(({ label, href, icon: Icon, badge }) => {
          const isActive = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <Link
              key={label}
              href={href}
              className={`group flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-medium transition ${
                isActive
                  ? 'bg-blue text-white shadow-md shadow-blue/20'
                  : 'text-slate-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon size={18} className={isActive ? 'text-white' : 'text-slate-400 group-hover:text-cyan'} />
                <span>{label}</span>
              </div>
              {badge && (
                <span className="rounded-full bg-cyan/20 px-2 py-0.5 text-[10px] font-bold text-cyan">
                  {badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Quick Action: No Website Focus */}
      <div className="my-4 rounded-xl border border-cyan/20 bg-cyan/5 p-3.5">
        <div className="flex items-center gap-2 text-xs font-bold text-cyan">
          <Globe2 size={15} />
          <span>Core Mission</span>
        </div>
        <p className="mt-1 text-xs text-slate-300 leading-relaxed">
          Target businesses across Tamil Nadu with missing web presence.
        </p>
        <Link
          href="/leads?website_status=NO_WEBSITE"
          className="mt-2.5 inline-flex items-center gap-1 text-xs font-semibold text-cyan hover:underline"
        >
          View No-Website Leads &rarr;
        </Link>
      </div>

      {/* User Footer */}
      <div className="border-t border-white/10 pt-4">
        <div className="flex items-center justify-between rounded-xl bg-white/5 p-2.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue text-xs font-bold text-white">
              {user ? user.full_name.slice(0, 2).toUpperCase() : 'SR'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-white">{user ? user.full_name : 'SRA User'}</p>
              <p className="truncate text-[10px] text-slate-400">{user ? user.email : 'admin@sra.com'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Log out"
            className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-rose-400 transition"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
