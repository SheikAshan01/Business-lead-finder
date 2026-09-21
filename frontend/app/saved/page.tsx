'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Bookmark, Download, ExternalLink, Globe2, Mail, MapPin, Phone, Sparkles } from 'lucide-react';
import { Header } from '@/components/Header';
import { LeadDetailsModal } from '@/components/LeadDetailsModal';
import { Sidebar } from '@/components/Sidebar';
import { fetchBusinesses, getExportUrl, toggleSaveBusiness, type Business } from '@/lib/api';

export default function SavedLeadsPage() {
  const [leads, setLeads] = useState<Business[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Business | null>(null);

  const loadSaved = () => {
    setLoading(false);
    fetchBusinesses({ saved: true, page_size: 100 })
      .then((data) => setLeads(data.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadSaved();
  }, []);

  async function handleUnsave(id: number) {
    try {
      await toggleSaveBusiness(id);
      setLeads((prev) => prev.filter((l) => l.id !== id));
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header title="Saved Leads" subtitle="High-priority bookmarked business leads for digital outreach" />

        <div className="mb-6 flex items-center justify-between">
          <p className="text-xs text-muted">
            Total Saved Leads: <strong className="text-ink font-bold">{leads.length}</strong>
          </p>
          <div className="flex gap-2">
            <a
              href={getExportUrl('csv', { saved: true })}
              download
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:border-blue hover:text-blue transition shadow-sm"
            >
              <Download size={14} />
              <span>Export Saved (CSV)</span>
            </a>
            <a
              href={getExportUrl('excel', { saved: true })}
              download
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:border-emerald-600 hover:text-emerald-600 transition shadow-sm"
            >
              <Download size={14} />
              <span>Export Saved (Excel)</span>
            </a>
          </div>
        </div>

        <section className="rounded-2xl border border-line bg-white shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-xs text-muted">Loading saved leads...</div>
          ) : leads.length === 0 ? (
            <div className="p-16 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-50 text-amber-500 mb-3">
                <Bookmark size={24} />
              </div>
              <p className="text-sm font-semibold text-slate-700">No saved leads yet</p>
              <p className="mt-1 text-xs text-muted">Bookmark important leads from the leads directory or dashboard.</p>
              <Link
                href="/leads"
                className="mt-4 inline-flex items-center gap-2 rounded-xl bg-blue px-4 py-2 text-xs font-bold text-white shadow"
              >
                Browse All Leads
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[800px] text-left text-xs">
                <thead className="border-b border-line bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-muted">
                  <tr>
                    <th className="px-5 py-3.5">Business Name</th>
                    <th className="px-5 py-3.5">District</th>
                    <th className="px-5 py-3.5">Contact</th>
                    <th className="px-5 py-3.5">Website Status</th>
                    <th className="px-5 py-3.5">Score</th>
                    <th className="px-5 py-3.5">Lead Status</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {leads.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-50 transition">
                      <td className="px-5 py-3.5">
                        <p
                          onClick={() => setSelectedLead(b)}
                          className="font-bold text-ink hover:text-blue cursor-pointer"
                        >
                          {b.business_name}
                        </p>
                        <span className="text-[11px] text-muted">{b.category_name || 'Commercial'}</span>
                      </td>
                      <td className="px-5 py-3.5 text-slate-700">
                        <span className="flex items-center gap-1">
                          <MapPin size={13} className="text-slate-400" />
                          {b.district || 'Tamil Nadu'}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="space-y-0.5 text-xs">
                          {b.phone && (
                            <span className="flex items-center gap-1 font-medium text-slate-800">
                              <Phone size={12} className="text-blue" />
                              +91 {b.phone}
                            </span>
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
                      <td className="px-5 py-3.5">
                        <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-700">
                          {b.lead_status}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-right space-x-2">
                        <button
                          onClick={() => setSelectedLead(b)}
                          className="rounded-lg border border-line bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 hover:border-blue hover:text-blue transition shadow-sm"
                        >
                          Details & Notes
                        </button>
                        <button
                          onClick={() => handleUnsave(b.id)}
                          className="rounded-lg border border-line bg-white px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 transition shadow-sm"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <LeadDetailsModal
          business={selectedLead}
          onClose={() => setSelectedLead(null)}
          onDelete={(id) => {
            setLeads((prev) => prev.filter((l) => l.id !== id));
            setSelectedLead(null);
          }}
          onUpdate={(updated) => {
            setSelectedLead(updated);
            setLeads((prev) => prev.map((l) => (l.id === updated.id ? updated : l)));
          }}
        />
      </main>
    </div>
  );
}
