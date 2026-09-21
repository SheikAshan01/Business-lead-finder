'use client';

import { useState } from 'react';
import {
  Bookmark,
  Building2,
  Calendar,
  CheckCircle2,
  ExternalLink,
  Globe2,
  Mail,
  MapPin,
  MessageSquare,
  Phone,
  Send,
  Share2,
  ShieldCheck,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react';
import {
  addBusinessNote,
  deleteBusiness,
  toggleSaveBusiness,
  updateBusinessStatus,
  type Business,
} from '@/lib/api';

interface LeadDetailsModalProps {
  business: Business | null;
  onClose: () => void;
  onUpdate: (updated: Business) => void;
  onDelete?: (id: number) => void;
}

const STATUS_OPTIONS = [
  { value: 'NEW', label: 'New' },
  { value: 'CONTACTED', label: 'Contacted' },
  { value: 'INTERESTED', label: 'Interested' },
  { value: 'FOLLOW_UP', label: 'Follow Up' },
  { value: 'CONVERTED', label: 'Converted' },
  { value: 'NOT_INTERESTED', label: 'Not Interested' },
];

export function LeadDetailsModal({ business, onClose, onUpdate, onDelete }: LeadDetailsModalProps) {
  if (!business) return null;
  return <LeadDetailsContent business={business} onClose={onClose} onUpdate={onUpdate} onDelete={onDelete} />;
}

function LeadDetailsContent({
  business,
  onClose,
  onUpdate,
  onDelete,
}: {
  business: Business;
  onClose: () => void;
  onUpdate: (updated: Business) => void;
  onDelete?: (id: number) => void;
}) {
  const [newNote, setNewNote] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);
  const [status, setStatus] = useState(business.lead_status);
  const [isSaved, setIsSaved] = useState(business.is_saved);

  // Parse score reasons
  let reasons: string[] = [];
  try {
    if (business.score_reasons) {
      reasons = JSON.parse(business.score_reasons);
    }
  } catch {
    reasons = [];
  }

  async function handleStatusChange(newStatus: string) {
    setStatus(newStatus);
    try {
      const updated = await updateBusinessStatus(business.id, newStatus, `Updated from details modal`);
      onUpdate(updated);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleToggleSave() {
    setIsSaved(!isSaved);
    try {
      const updated = await toggleSaveBusiness(business.id);
      onUpdate(updated);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleAddNote(e: React.FormEvent) {
    e.preventDefault();
    if (!newNote.trim()) return;
    setSubmittingNote(true);
    try {
      const note = await addBusinessNote(business.id, newNote.trim());
      const updated = {
        ...business,
        notes: [note, ...(business.notes || [])],
      };
      onUpdate(updated);
      setNewNote('');
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingNote(false);
    }
  }

  const websiteBadgeColor =
    business.website_status === 'NO_WEBSITE'
      ? 'bg-rose-50 text-rose-700 border-rose-200'
      : business.website_status === 'WEBSITE_FOUND'
      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
      : business.website_status === 'SOCIAL_ONLY'
      ? 'bg-amber-50 text-amber-700 border-amber-200'
      : 'bg-slate-100 text-slate-600 border-slate-200';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-fade-in">
      <div className="relative flex max-h-[90vh] w-full max-w-3xl flex-col rounded-2xl bg-white shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-start justify-between border-b border-line bg-[#0b1220] p-6 text-white">
          <div className="min-w-0 flex-1 pr-4">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="rounded-full bg-white/10 px-2.5 py-0.5 text-xs font-semibold text-cyan">
                {business.category_name || 'General Business'}
              </span>
              <span className="rounded-full bg-white/10 px-2.5 py-0.5 text-xs font-medium text-slate-300">
                {business.district || 'Tamil Nadu'}
              </span>
              <span className="text-xs text-slate-400">ID #{business.id}</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight sm:text-2xl">{business.business_name}</h2>
            {business.client_name && (
              <p className="mt-1 text-xs text-slate-300">Contact Person: {business.client_name}</p>
            )}
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleToggleSave}
              className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-bold transition ${
                isSaved
                  ? 'border-amber-400 bg-amber-400/20 text-amber-300'
                  : 'border-white/20 bg-white/10 text-white hover:bg-white/20'
              }`}
            >
              <Bookmark size={14} className={isSaved ? 'fill-amber-300' : ''} />
              <span>{isSaved ? 'Saved' : 'Save'}</span>
            </button>
            <button
              onClick={onClose}
              className="rounded-xl bg-white/10 p-2 text-slate-300 hover:bg-white/20 hover:text-white transition"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Top Stat Row: Lead Score & Website Status */}
          <div className="grid gap-4 sm:grid-cols-2">
            {/* Opportunity Score Card */}
            <div className="rounded-xl border border-blue/20 bg-blue/5 p-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-blue flex items-center gap-1.5">
                  <Sparkles size={14} /> Qualification Score
                </span>
                <span className="text-2xl font-bold text-blue">{business.lead_score}/100</span>
              </div>
              <div className="mt-2.5 space-y-1">
                {reasons.length > 0 ? (
                  reasons.map((r, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-xs text-slate-700">
                      <CheckCircle2 size={13} className="text-emerald-600 shrink-0" />
                      <span>{r}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-muted">Baseline evaluation pending</p>
                )}
              </div>
            </div>

            {/* Website Status Card */}
            <div className="rounded-xl border border-line p-4 bg-slate-50/60">
              <span className="text-xs font-bold uppercase tracking-wider text-muted flex items-center gap-1.5">
                <Globe2 size={14} /> Web Presence Status
              </span>
              <div className="mt-2 flex items-center gap-2">
                <span className={`inline-flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs font-bold ${websiteBadgeColor}`}>
                  {business.website_status.replace('_', ' ')}
                </span>
              </div>
              {business.website_url ? (
                <a
                  href={business.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2.5 inline-flex items-center gap-1 text-xs font-semibold text-blue hover:underline break-all"
                >
                  <span>{business.website_url}</span>
                  <ExternalLink size={12} className="shrink-0" />
                </a>
              ) : (
                <p className="mt-2 text-xs text-slate-500 italic">
                  No official business website detected. High-priority prospect for digital setup.
                </p>
              )}
            </div>
          </div>

          {/* Contact & Location Info */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-line p-4 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Contact Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-slate-700">
                  <Phone size={15} className="text-blue shrink-0" />
                  {business.phone ? (
                    <a href={`tel:${business.phone}`} className="hover:text-blue font-medium">
                      +91 {business.phone}
                    </a>
                  ) : (
                    <span className="text-muted italic">Phone not listed</span>
                  )}
                </div>
                {business.alternate_phone && (
                  <div className="flex items-center gap-2 text-slate-700 text-xs pl-6">
                    <span>Alt: +91 {business.alternate_phone}</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-slate-700">
                  <Mail size={15} className="text-blue shrink-0" />
                  {business.email ? (
                    <a href={`mailto:${business.email}`} className="hover:text-blue font-medium">
                      {business.email}
                    </a>
                  ) : (
                    <span className="text-muted italic">Email not listed</span>
                  )}
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-line p-4 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Location</h3>
              <div className="flex items-start gap-2 text-sm text-slate-700">
                <MapPin size={16} className="text-rose-500 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium">{business.address || 'Address unlisted'}</p>
                  <p className="text-xs text-muted mt-0.5">
                    {[business.area, business.taluk, business.district, business.pincode]
                      .filter(Boolean)
                      .join(', ') || 'Tamil Nadu'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Social Profiles & Provenance */}
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-line bg-slate-50 p-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-1">Source Provenance</span>
              <span className="text-xs font-medium text-slate-700">
                {business.source || 'Open Data'}
                {business.source_url && (
                  <a href={business.source_url} target="_blank" rel="noreferrer" className="ml-2 text-blue hover:underline">
                    (View Source Record)
                  </a>
                )}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {business.facebook_url && (
                <a href={business.facebook_url} target="_blank" rel="noreferrer" className="rounded-lg border border-line bg-white p-2 text-slate-600 hover:text-blue">
                  <Share2 size={14} />
                </a>
              )}
              {business.whatsapp_url && (
                <a href={business.whatsapp_url} target="_blank" rel="noreferrer" className="rounded-lg border border-line bg-white p-2 text-emerald-600 hover:bg-emerald-50">
                  <Phone size={14} />
                </a>
              )}
            </div>
          </div>

          {/* CRM Status Section */}
          <div className="rounded-xl border border-line p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Lead CRM Status</h3>
              <select
                value={status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="rounded-xl border border-line bg-white px-3 py-1.5 text-xs font-bold text-ink outline-none focus:border-blue shadow-sm"
              >
                {STATUS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* CRM Notes Thread */}
          <div className="rounded-xl border border-line p-4 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <MessageSquare size={14} /> Lead Notes & Follow-up Log
            </h3>

            {/* Note Input */}
            <form onSubmit={handleAddNote} className="flex gap-2">
              <input
                type="text"
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Add outreach note (e.g. Called owner, scheduled demo for Friday)..."
                className="flex-1 rounded-xl border border-line bg-white px-3.5 py-2.5 text-xs outline-none focus:border-blue"
              />
              <button
                type="submit"
                disabled={submittingNote || !newNote.trim()}
                className="inline-flex items-center gap-1.5 rounded-xl bg-blue px-4 py-2.5 text-xs font-bold text-white hover:bg-blue/90 disabled:opacity-50 transition shadow-sm"
              >
                <Send size={13} />
                <span>{submittingNote ? 'Saving...' : 'Post'}</span>
              </button>
            </form>

            {/* Notes List */}
            <div className="space-y-2.5">
              {business.notes && business.notes.length > 0 ? (
                business.notes.map((n) => (
                  <div key={n.id} className="rounded-xl border border-line bg-slate-50/70 p-3 text-xs">
                    <p className="text-slate-800 leading-relaxed">{n.note}</p>
                    <span className="mt-1.5 block text-[10px] text-muted">
                      {new Date(n.created_at).toLocaleString()}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted italic">No notes recorded yet.</p>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between border-t border-line bg-slate-50 px-6 py-4">
          <button
            type="button"
            onClick={async () => {
              if (window.confirm(`Are you sure you want to delete "${business.business_name}"?`)) {
                try {
                  await deleteBusiness(business.id);
                  onDelete?.(business.id);
                  onClose();
                } catch (e: any) {
                  alert(e.message || 'Failed to delete lead');
                }
              }
            }}
            className="inline-flex items-center gap-1.5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-2 text-xs font-bold text-rose-700 hover:bg-rose-100 transition shadow-sm"
          >
            <Trash2 size={14} />
            <span>Delete Lead</span>
          </button>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-line bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
