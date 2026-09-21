'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Download, Globe2, PlusCircle, Search, Sparkles } from 'lucide-react';
import { getExportUrl } from '@/lib/api';

interface HeaderProps {
  title: string;
  subtitle?: string;
  showExport?: boolean;
}

export function Header({ title, subtitle, showExport = true }: HeaderProps) {
  return (
    <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-line pb-5">
      <div>
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-blue mb-1">
          <span>SRA SOFTWARE SOLUTIONS</span>
          <span className="text-slate-300">•</span>
          <span className="text-slate-500">Tamil Nadu Discovery</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-ink sm:text-3xl">{title}</h1>
        {subtitle && <p className="mt-1 text-xs text-muted sm:text-sm">{subtitle}</p>}
      </div>

      <div className="flex flex-wrap items-center gap-2.5">
        <Link
          href="/scraper"
          className="inline-flex items-center gap-2 rounded-xl bg-blue px-4 py-2.5 text-xs font-bold text-white shadow-md shadow-blue/20 hover:bg-blue/90 transition"
        >
          <PlusCircle size={15} />
          <span>New Discovery Job</span>
        </Link>

        {showExport && (
          <div className="flex items-center gap-1.5">
            <a
              href={getExportUrl('csv')}
              download
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:border-blue hover:text-blue transition shadow-sm"
              title="Export all leads to CSV"
            >
              <Download size={14} />
              <span>CSV</span>
            </a>
            <a
              href={getExportUrl('excel')}
              download
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:border-emerald-600 hover:text-emerald-600 transition shadow-sm"
              title="Export all leads to Excel"
            >
              <Download size={14} />
              <span>Excel</span>
            </a>
          </div>
        )}
      </div>
    </header>
  );
}
