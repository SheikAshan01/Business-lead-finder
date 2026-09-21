'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  ArrowUpRight,
  Bookmark,
  CheckCircle2,
  Globe2,
  Mail,
  MapPin,
  Phone,
  PlusCircle,
  Search,
  Sparkles,
  TrendingUp,
  Users,
} from 'lucide-react';
import { Header } from '@/components/Header';
import { LeadDetailsModal } from '@/components/LeadDetailsModal';
import { Sidebar } from '@/components/Sidebar';
import {
  fetchBusinesses,
  fetchCharts,
  fetchStats,
  type Business,
  type DashboardCharts,
  type Stats,
} from '@/lib/api';

const defaultStats: Stats = {
  total: 0,
  no_website: 0,
  website_found: 0,
  saved: 0,
  converted: 0,
  phone: 0,
  email: 0,
  high_score: 0,
};

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>(defaultStats);
  const [charts, setCharts] = useState<DashboardCharts>({
    by_category: [],
    by_district: [],
    no_website_by_district: [],
    status_distribution: [],
  });
  const [recentLeads, setRecentLeads] = useState<Business[]>([]);
  const [selectedLead, setSelectedLead] = useState<Business | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchStats(), fetchCharts(), fetchBusinesses({ page_size: 8, sort_by: 'lead_score', sort_order: 'desc' })])
      .then(([s, c, b]) => {
        setStats(s);
        setCharts(c);
        setRecentLeads(b.items);
      })
      .catch((err) => {
        console.error('Failed to load dashboard data:', err);
      })
      .finally(() => setLoading(false));
  }, []);

  const statCards = [
    { label: 'Total Businesses', value: stats.total, sub: 'Across Tamil Nadu', icon: Users, color: 'text-blue', bg: 'bg-blue/10' },
    { label: 'No Official Website', value: stats.no_website, sub: 'Prime Web Dev Prospects', icon: Globe2, color: 'text-rose-600', bg: 'bg-rose-50' },
    { label: 'Website Verified', value: stats.website_found, sub: 'Online Active', icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { label: 'High-Score Leads', value: stats.high_score, sub: 'Score >= 75/100', icon: Sparkles, color: 'text-amber-500', bg: 'bg-amber-50' },
    { label: 'Phone Available', value: stats.phone, sub: 'Outreach Ready', icon: Phone, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { label: 'Email Available', value: stats.email, sub: 'Direct Mail Contact', icon: Mail, color: 'text-cyan', bg: 'bg-cyan/10' },
    { label: 'Saved Leads', value: stats.saved, sub: 'Bookmarked for Outreach', icon: Bookmark, color: 'text-purple-600', bg: 'bg-purple-50' },
    { label: 'Converted Leads', value: stats.converted, sub: 'Won Digital Clients', icon: TrendingUp, color: 'text-teal-600', bg: 'bg-teal-50' },
  ];

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header title="Dashboard Overview" subtitle="High-level commercial telemetry & qualified Tamil Nadu lead insights" />

        {/* Discovery Callout Hero Banner */}
        <section className="mb-8 rounded-2xl bg-gradient-to-r from-[#0b1220] via-[#101b2f] to-[#0b1220] p-6 text-white shadow-xl shadow-blue/10 sm:p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-xl">
              <div className="mb-2 flex items-center gap-2 text-cyan">
                <Sparkles size={16} />
                <span className="text-xs font-bold uppercase tracking-wider">Discovery Engine</span>
              </div>
              <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">Find Businesses. Verify Websites. Connect.</h2>
              <p className="mt-2 text-xs leading-relaxed text-slate-300 sm:text-sm">
                Target any of Tamil Nadu&apos;s 38 districts and 45+ business categories. Our pipeline identifies businesses without an official website so SRA can help them establish their online presence.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/scraper"
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue to-cyan px-5 py-3 text-xs font-bold text-white shadow-lg shadow-blue/20 hover:opacity-95 transition"
              >
                <Search size={15} />
                <span>Launch Discovery Scraper</span>
              </Link>
              <Link
                href="/leads?website_status=NO_WEBSITE"
                className="flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-5 py-3 text-xs font-bold text-white hover:bg-white/20 transition"
              >
                <Globe2 size={15} className="text-cyan" />
                <span>Quick Filter: No Website ({stats.no_website})</span>
              </Link>
            </div>
          </div>
        </section>

        {/* 8 Metric KPI Cards Grid */}
        <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {statCards.map(({ label, value, sub, icon: Icon, color, bg }) => (
            <div key={label} className="rounded-2xl border border-line bg-white p-5 shadow-sm transition hover:shadow-md">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-semibold text-muted">{label}</p>
                  <p className="mt-1.5 text-2xl font-bold text-ink">{loading ? '...' : value.toLocaleString()}</p>
                </div>
                <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${bg}`}>
                  <Icon size={18} className={color} />
                </div>
              </div>
              <div className="mt-3 flex items-center gap-1 text-[11px] text-slate-500">
                <ArrowUpRight size={13} className="text-emerald-500" />
                <span>{sub}</span>
              </div>
            </div>
          ))}
        </section>

        {/* Charts & Analytics Row */}
        <section className="mb-8 grid gap-6 lg:grid-cols-2">
          {/* Chart 1: Businesses by Category */}
          <div className="rounded-2xl border border-line bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-ink">Discovered Leads by Category</h3>
                <p className="text-xs text-muted">Top sectors identified across Tamil Nadu</p>
              </div>
              <Link href="/categories" className="text-xs font-semibold text-blue hover:underline">
                View all &rarr;
              </Link>
            </div>
            <div className="space-y-3">
              {charts.by_category.length > 0 ? (
                charts.by_category.map((item) => {
                  const maxVal = Math.max(...charts.by_category.map((c) => c.count), 1);
                  const pct = Math.round((item.count / maxVal) * 100);
                  return (
                    <div key={item.label} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium text-slate-700">
                        <span>{item.label}</span>
                        <span className="font-bold text-ink">{item.count}</span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                        <div className="h-full rounded-full bg-blue transition-all duration-500" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-xs text-muted italic py-6 text-center">Run a discovery job to generate category analytics.</p>
              )}
            </div>
          </div>

          {/* Chart 2: Missing Websites by District (Opportunity Focus) */}
          <div className="rounded-2xl border border-line bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-ink">No Website Opportunities by District</h3>
                <p className="text-xs text-muted">Highest concentration of businesses needing web dev</p>
              </div>
              <Link href="/leads?website_status=NO_WEBSITE" className="text-xs font-semibold text-rose-600 hover:underline">
                Target Leads &rarr;
              </Link>
            </div>
            <div className="space-y-3">
              {charts.no_website_by_district.length > 0 ? (
                charts.no_website_by_district.map((item) => {
                  const maxVal = Math.max(...charts.no_website_by_district.map((c) => c.count), 1);
                  const pct = Math.round((item.count / maxVal) * 100);
                  return (
                    <div key={item.label} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium text-slate-700">
                        <span className="flex items-center gap-1.5">
                          <MapPin size={13} className="text-rose-500" />
                          {item.label}
                        </span>
                        <span className="font-bold text-rose-600">{item.count} leads</span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                        <div className="h-full rounded-full bg-gradient-to-r from-rose-500 to-amber-500 transition-all duration-500" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-xs text-muted italic py-6 text-center">No missing website analytics recorded yet.</p>
              )}
            </div>
          </div>
        </section>

        {/* Priority Discovered Leads Table Preview */}
        <section className="rounded-2xl border border-line bg-white shadow-sm overflow-hidden">
          <div className="flex flex-col gap-3 border-b border-line p-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-base font-bold text-ink">Highest Qualified Leads</h2>
              <p className="text-xs text-muted">Ranked by opportunity score & missing website presence</p>
            </div>
            <Link
              href="/leads"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-blue hover:underline"
            >
              <span>Explore all leads</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          {loading ? (
            <div className="p-8 text-center text-xs text-muted">Loading leads...</div>
          ) : recentLeads.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-sm font-semibold text-slate-700">No leads discovered yet</p>
              <p className="mt-1 text-xs text-muted">Launch your first discovery job to populate live Tamil Nadu business leads.</p>
              <Link
                href="/scraper"
                className="mt-4 inline-flex items-center gap-2 rounded-xl bg-blue px-4 py-2 text-xs font-bold text-white shadow"
              >
                <PlusCircle size={14} />
                <span>Start Scraping</span>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[700px] text-left text-xs">
                <thead className="border-b border-line bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-muted">
                  <tr>
                    <th className="px-5 py-3">Business Name</th>
                    <th className="px-5 py-3">District</th>
                    <th className="px-5 py-3">Contact</th>
                    <th className="px-5 py-3">Website Status</th>
                    <th className="px-5 py-3">Score</th>
                    <th className="px-5 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {recentLeads.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-50 transition">
                      <td className="px-5 py-3.5">
                        <p className="font-bold text-ink">{b.business_name}</p>
                        <span className="text-[11px] text-muted">{b.category_name || 'Commercial'}</span>
                      </td>
                      <td className="px-5 py-3.5 text-slate-700">
                        <span className="flex items-center gap-1">
                          <MapPin size={13} className="text-slate-400" />
                          {b.district || 'Tamil Nadu'}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-slate-700">
                        <div className="flex flex-col gap-0.5">
                          {b.phone ? (
                            <span className="flex items-center gap-1 font-medium">
                              <Phone size={12} className="text-blue" />
                              +91 {b.phone}
                            </span>
                          ) : (
                            <span className="text-muted italic">No phone</span>
                          )}
                          {b.email && (
                            <span className="flex items-center gap-1 text-[11px] text-slate-500">
                              <Mail size={11} />
                              {b.email}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                            b.website_status === 'NO_WEBSITE'
                              ? 'bg-rose-50 text-rose-700'
                              : b.website_status === 'WEBSITE_FOUND'
                              ? 'bg-emerald-50 text-emerald-700'
                              : 'bg-slate-100 text-slate-700'
                          }`}
                        >
                          {b.website_status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="font-bold text-blue">{b.lead_score}</span>
                        <span className="text-muted">/100</span>
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <button
                          onClick={() => setSelectedLead(b)}
                          className="rounded-lg border border-line bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 hover:border-blue hover:text-blue transition shadow-sm"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Lead Details Modal */}
        <LeadDetailsModal
          business={selectedLead}
          onClose={() => setSelectedLead(null)}
          onUpdate={(updated) => {
            setSelectedLead(updated);
            setRecentLeads((prev) => prev.map((l) => (l.id === updated.id ? updated : l)));
          }}
        />
      </main>
    </div>
  );
}
