'use client';

import Link from 'next/link';
import { Download, Globe2, Menu, PlusCircle, Search, Sparkles } from 'lucide-react';
import { getExportUrl } from '@/lib/api';

interface HeaderProps {
  title: string;
  subtitle?: string;
  showExport?: boolean;
}

export function Header({ title, subtitle, showExport = true }: HeaderProps) {
  const toggleMobileSidebar = () => {
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('toggle-mobile-sidebar'));
    }
  };

  return (
    <header className="mb-6 flex flex-col gap-4 border-b border-line pb-5">
      {/* Top Mobile Bar with Hamburger and Brand */}
      <div className="flex items-center justify-between lg:hidden">
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={toggleMobileSidebar}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-line bg-white text-slate-700 hover:bg-slate-50 shadow-xs transition"
            aria-label="Toggle navigation menu"
          >
            <Menu size={18} />
          </button>
          <div className="flex items-center gap-1.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue text-xs font-bold text-white shadow-xs">
              SRA
            </span>
            <span className="font-bold text-sm text-ink">Lead Finder</span>
          </div>
        </div>

        <Link
          href="/scraper"
          className="inline-flex items-center gap-1.5 rounded-lg bg-blue px-2.5 py-1.5 text-xs font-bold text-white shadow-sm"
        >
          <PlusCircle size={13} />
          <span>Scrap</span>
        </Link>
      </div>

      {/* Main Title & Action Row */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-[10px] sm:text-xs font-bold uppercase tracking-wider text-blue mb-1">
            <span>SRA SOFTWARE SOLUTIONS</span>
            <span className="text-slate-300">•</span>
            <span className="text-slate-500">Tamil Nadu Discovery</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-ink sm:text-2xl md:text-3xl">{title}</h1>
          {subtitle && <p className="mt-0.5 text-xs text-muted sm:text-sm">{subtitle}</p>}
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:gap-2.5">
          <Link
            href="/scraper"
            className="hidden sm:inline-flex items-center gap-2 rounded-xl bg-blue px-4 py-2.5 text-xs font-bold text-white shadow-md shadow-blue/20 hover:bg-blue/90 transition"
          >
            <PlusCircle size={15} />
            <span>New Discovery Job</span>
          </Link>

          {showExport && (
            <div className="flex items-center gap-1.5">
              <a
                href={getExportUrl('csv')}
                download
                className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3 py-1.5 sm:py-2 text-xs font-semibold text-slate-700 hover:border-blue hover:text-blue transition shadow-xs"
                title="Export all leads to CSV"
              >
                <Download size={13} />
                <span>CSV</span>
              </a>
              <a
                href={getExportUrl('excel')}
                download
                className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3 py-1.5 sm:py-2 text-xs font-semibold text-slate-700 hover:border-emerald-600 hover:text-emerald-600 transition shadow-xs"
                title="Export all leads to Excel"
              >
                <Download size={13} />
                <span>Excel</span>
              </a>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
