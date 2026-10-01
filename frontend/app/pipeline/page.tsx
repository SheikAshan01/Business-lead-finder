'use client';

import { Suspense, useEffect, useMemo, useState } from 'react';
import {
  ArrowRight,
  ArrowUpDown,
  Bookmark,
  Building2,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  Eye,
  FileText,
  Filter,
  Globe2,
  Kanban,
  MessageCircle,
  Phone,
  PlusCircle,
  RefreshCw,
  Search,
  Sparkles,
  TrendingUp,
  X,
} from 'lucide-react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { LeadDetailsModal } from '@/components/LeadDetailsModal';
import { WhatsAppModal } from '@/components/WhatsAppModal';
import { ClientAuditProposalModal } from '@/components/ClientAuditProposalModal';
import {
  fetchBusinesses,
  fetchCategories,
  fetchDistricts,
  updateBusinessStatus,
  type Business,
  type Category,
  type DistrictLocation,
} from '@/lib/api';

const PIPELINE_STAGES = [
  {
    id: 'NEW',
    title: 'New Leads',
    subtitle: 'Freshly Scraped',
    color: 'border-blue-500/30 bg-blue-50/50 text-blue-900',
    badge: 'bg-blue-100 text-blue-700',
    iconColor: 'text-blue-600',
  },
  {
    id: 'CONTACTED',
    title: 'Contacted',
    subtitle: 'WhatsApp / Call Sent',
    color: 'border-indigo-500/30 bg-indigo-50/50 text-indigo-900',
    badge: 'bg-indigo-100 text-indigo-700',
    iconColor: 'text-indigo-600',
  },
  {
    id: 'QUALIFIED',
    title: 'Interested',
    subtitle: 'Follow Up / In Discussion',
    color: 'border-amber-500/30 bg-amber-50/50 text-amber-900',
    badge: 'bg-amber-100 text-amber-700',
    iconColor: 'text-amber-600',
  },
  {
    id: 'CONVERTED',
    title: 'Converted 🎉',
    subtitle: 'Website Client Won',
    color: 'border-emerald-500/30 bg-emerald-50/50 text-emerald-900',
    badge: 'bg-emerald-100 text-emerald-700',
    iconColor: 'text-emerald-600',
  },
  {
    id: 'NOT_INTERESTED',
    title: 'Dropped',
    subtitle: 'Not Interested',
    color: 'border-rose-500/30 bg-rose-50/50 text-rose-900',
    badge: 'bg-rose-100 text-rose-700',
    iconColor: 'text-rose-600',
  },
];

export default function PipelinePage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center text-xs text-muted">Loading CRM Pipeline...</div>}>
      <PipelineContent />
    </Suspense>
  );
}

function PipelineContent() {
  const [leads, setLeads] = useState<Business[]>([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState<Category[]>([]);
  const [districts, setDistricts] = useState<DistrictLocation[]>([]);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>(undefined);
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [search, setSearch] = useState('');

  // Modals
  const [selectedLead, setSelectedLead] = useState<Business | null>(null);
  const [whatsAppLead, setWhatsAppLead] = useState<Business | null>(null);
  const [proposalLead, setProposalLead] = useState<Business | null>(null);

  const loadPipelineLeads = async () => {
    setLoading(true);
    try {
      const data = await fetchBusinesses({
        page: 1,
        page_size: 150, // Fetch top pipeline leads
        category_id: selectedCategory,
        district: selectedDistrict || undefined,
        search: search.trim() || undefined,
      });
      setLeads(data.items);
    } catch (e) {
      console.error('Failed to load pipeline leads:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories().then(setCategories).catch(console.error);
    fetchDistricts().then(setDistricts).catch(console.error);
  }, []);

  useEffect(() => {
    loadPipelineLeads();
  }, [selectedCategory, selectedDistrict]);

  const handleStageMove = async (business: Business, targetStage: string) => {
    // Optimistic UI update
    setLeads((prev) =>
      prev.map((b) => (b.id === business.id ? { ...b, lead_status: targetStage as any } : b))
    );

    try {
      await updateBusinessStatus(business.id, targetStage, `Moved via CRM Pipeline board`);
    } catch (e) {
      console.error('Failed to move stage:', e);
      loadPipelineLeads(); // rollback on error
    }
  };

  // Group leads by stage
  const groupedLeads = useMemo(() => {
    const map: Record<string, Business[]> = {
      NEW: [],
      CONTACTED: [],
      QUALIFIED: [],
      CONVERTED: [],
      NOT_INTERESTED: [],
    };

    leads.forEach((l) => {
      let st = l.lead_status || 'NEW';
      // Map legacy statuses if any
      if (st === 'INTERESTED' || st === 'FOLLOW_UP') st = 'QUALIFIED';
      if (st === 'DROPPED') st = 'NOT_INTERESTED';

      if (!map[st]) {
        map[st] = [];
      }
      map[st].push(l);
    });

    return map;
  }, [leads]);

  // Overall pipeline metrics
  const totalLeads = leads.length;
  const convertedCount = groupedLeads['CONVERTED']?.length || 0;
  const contactedCount = groupedLeads['CONTACTED']?.length || 0;
  const qualifiedCount = groupedLeads['QUALIFIED']?.length || 0;

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />

      <main className="flex-1 overflow-x-hidden p-6 lg:p-8">
        <Header
          title="CRM Sales Pipeline"
          subtitle="Manage leads across your sales stages from initial discovery to converted website clients"
        />

        {/* Top Metrics Cards */}
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-2xl border border-line bg-white p-4 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted block">In Pipeline</span>
            <span className="text-2xl font-black text-ink mt-1 block">{totalLeads}</span>
            <span className="text-[11px] text-slate-500">Active leads loaded</span>
          </div>

          <div className="rounded-2xl border border-indigo-200 bg-indigo-50/50 p-4 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-700 block">Contacted</span>
            <span className="text-2xl font-black text-indigo-800 mt-1 block">{contactedCount}</span>
            <span className="text-[11px] text-indigo-600">WhatsApp / Call sent</span>
          </div>

          <div className="rounded-2xl border border-amber-200 bg-amber-50/50 p-4 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700 block">High Intent</span>
            <span className="text-2xl font-black text-amber-800 mt-1 block">{qualifiedCount}</span>
            <span className="text-[11px] text-amber-600">Interested in Website</span>
          </div>

          <div className="rounded-2xl border border-emerald-200 bg-emerald-50/50 p-4 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 block">Clients Won 🎉</span>
            <span className="text-2xl font-black text-emerald-800 mt-1 block">{convertedCount}</span>
            <span className="text-[11px] text-emerald-600">Website deals closed</span>
          </div>
        </div>

        {/* Filters & Search Toolbar */}
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line bg-white p-3.5 shadow-xs">
          <div className="flex flex-wrap items-center gap-2.5 flex-1 min-w-[280px]">
            {/* Search Input */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                loadPipelineLeads();
              }}
              className="relative flex-1 min-w-[200px]"
            >
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
              <input
                type="text"
                placeholder="Search business name in pipeline..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-xl border border-line bg-slate-50/70 py-2 pl-9 pr-3 text-xs outline-none focus:border-blue focus:bg-white"
              />
            </form>

            {/* Category Filter */}
            <select
              value={selectedCategory || ''}
              onChange={(e) => setSelectedCategory(e.target.value ? Number(e.target.value) : undefined)}
              className="rounded-xl border border-line bg-white px-3 py-2 text-xs font-medium text-slate-700 outline-none focus:border-blue"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>

            {/* District Filter */}
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="rounded-xl border border-line bg-white px-3 py-2 text-xs font-medium text-slate-700 outline-none focus:border-blue"
            >
              <option value="">All Districts</option>
              {districts.map((d) => (
                <option key={d.district} value={d.district}>
                  {d.district}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={loadPipelineLeads}
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition shadow-xs"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Refresh Board</span>
          </button>
        </div>

        {/* Kanban Board Horizontal Scroll Container */}
        <div className="flex gap-4 overflow-x-auto pb-6 items-start">
          {PIPELINE_STAGES.map((stage) => {
            const stageLeads = groupedLeads[stage.id] || [];

            return (
              <div
                key={stage.id}
                className="flex w-72 sm:w-80 flex-col shrink-0 rounded-2xl border border-line bg-slate-100/70 p-3 shadow-xs"
              >
                {/* Column Header */}
                <div className="mb-3 flex items-center justify-between border-b border-line pb-2.5 px-1">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-ink">{stage.title}</span>
                      <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${stage.badge}`}>
                        {stageLeads.length}
                      </span>
                    </div>
                    <p className="text-[10px] text-muted">{stage.subtitle}</p>
                  </div>
                </div>

                {/* Column Cards Container */}
                <div className="flex flex-col gap-2.5 min-h-[350px]">
                  {stageLeads.length === 0 ? (
                    <div className="flex h-36 flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 p-4 text-center">
                      <p className="text-xs text-slate-400 font-medium">No leads in this stage</p>
                    </div>
                  ) : (
                    stageLeads.map((b) => {
                      const isNoWeb = b.website_status === 'NO_WEBSITE';
                      const cleanPhone = (b.phone || b.alternate_phone || '').replace(/\D/g, '');

                      return (
                        <div
                          key={b.id}
                          className="group relative flex flex-col rounded-xl border border-line bg-white p-3.5 shadow-xs hover:border-blue/50 hover:shadow-md transition"
                        >
                          {/* Card Top: Badges & Score */}
                          <div className="flex items-center justify-between gap-1 mb-2">
                            <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-700 truncate max-w-[130px]">
                              {b.category_name || 'Business'}
                            </span>

                            <div className="flex items-center gap-1.5">
                              <span
                                className={`rounded px-1.5 py-0.5 text-[9px] font-bold ${
                                  isNoWeb
                                    ? 'bg-rose-50 text-rose-700 border border-rose-200'
                                    : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                }`}
                              >
                                {isNoWeb ? 'NO WEBSITE' : 'HAS WEB'}
                              </span>
                              <span className="flex items-center gap-0.5 text-[10px] font-bold text-blue">
                                <Sparkles size={10} className="text-amber-500 fill-amber-500" />
                                {b.lead_score}
                              </span>
                            </div>
                          </div>

                          {/* Card Title & Contact */}
                          <h4
                            onClick={() => setSelectedLead(b)}
                            className="font-bold text-xs text-slate-900 hover:text-blue cursor-pointer transition line-clamp-2 leading-snug"
                          >
                            {b.business_name}
                          </h4>

                          <p className="mt-1 text-[11px] text-muted truncate">
                            📍 {b.district || 'Tamil Nadu'} {b.area ? `• ${b.area}` : ''}
                          </p>

                          {/* Quick Action Buttons on Card */}
                          <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-2.5">
                            <div className="flex items-center gap-1.5">
                              {/* WhatsApp Trigger */}
                              <button
                                type="button"
                                onClick={() => setWhatsAppLead(b)}
                                title="1-Click WhatsApp Outreach"
                                className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition shadow-2xs border border-emerald-200"
                              >
                                <MessageCircle size={13} />
                              </button>

                              {/* Call Trigger */}
                              {cleanPhone ? (
                                <a
                                  href={`tel:${cleanPhone}`}
                                  title={`Call +91 ${cleanPhone}`}
                                  className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue/10 text-blue hover:bg-blue hover:text-white transition shadow-2xs border border-blue/20"
                                >
                                  <Phone size={12} />
                                </a>
                              ) : null}

                              {/* Audit Proposal Trigger */}
                              <button
                                type="button"
                                onClick={() => setProposalLead(b)}
                                title="Website Audit & Proposal PDF"
                                className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-50 text-slate-600 hover:bg-slate-200 hover:text-slate-900 transition shadow-2xs border border-line"
                              >
                                <FileText size={12} />
                              </button>

                              {/* View Details */}
                              <button
                                type="button"
                                onClick={() => setSelectedLead(b)}
                                title="View Lead Details & Notes"
                                className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-50 text-slate-500 hover:bg-slate-200 hover:text-slate-900 transition shadow-2xs border border-line"
                              >
                                <Eye size={12} />
                              </button>
                            </div>

                            {/* Move Stage Selector */}
                            <select
                              value={stage.id}
                              onChange={(e) => handleStageMove(b, e.target.value)}
                              className="rounded-lg border border-line bg-slate-50 px-2 py-1 text-[10px] font-bold text-slate-700 outline-none hover:bg-white"
                            >
                              <option value="NEW">New</option>
                              <option value="CONTACTED">Contacted</option>
                              <option value="QUALIFIED">Interested</option>
                              <option value="CONVERTED">Won 🎉</option>
                              <option value="NOT_INTERESTED">Drop</option>
                            </select>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Modals */}
        {selectedLead && (
          <LeadDetailsModal
            business={selectedLead}
            onClose={() => setSelectedLead(null)}
            onUpdate={(updated) => {
              setLeads((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
              setSelectedLead(updated);
            }}
            onDelete={(id) => {
              setLeads((prev) => prev.filter((item) => item.id !== id));
              setSelectedLead(null);
            }}
          />
        )}

        {whatsAppLead && (
          <WhatsAppModal
            business={whatsAppLead}
            onClose={() => setWhatsAppLead(null)}
            onNoteAdded={(id, note) => {
              setLeads((prev) =>
                prev.map((item) =>
                  item.id === id ? { ...item, notes: [note, ...(item.notes || [])] } : item
                )
              );
            }}
          />
        )}

        {proposalLead && (
          <ClientAuditProposalModal
            business={proposalLead}
            onClose={() => setProposalLead(null)}
          />
        )}
      </main>
    </div>
  );
}
