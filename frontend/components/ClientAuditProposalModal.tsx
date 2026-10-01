'use client';

import { useState } from 'react';
import {
  Check,
  CheckCircle2,
  Copy,
  Download,
  ExternalLink,
  FileText,
  Globe2,
  MapPin,
  Phone,
  Printer,
  Share2,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  X,
} from 'lucide-react';
import { type Business } from '@/lib/api';

interface ClientAuditProposalModalProps {
  business: Business | null;
  onClose: () => void;
}

export function ClientAuditProposalModal({ business, onClose }: ClientAuditProposalModalProps) {
  if (!business) return null;

  const [copied, setCopied] = useState(false);

  const cleanPhone = (business.phone || business.alternate_phone || '').replace(/\D/g, '');
  const isNoWebsite = business.website_status === 'NO_WEBSITE';

  // Digital Health Score Calculation (out of 100)
  const auditScore = isNoWebsite ? 28 : business.website_status === 'SOCIAL_ONLY' ? 45 : 75;

  const handlePrint = () => {
    window.print();
  };

  const handleShareWhatsApp = () => {
    if (!cleanPhone) {
      alert('Valid phone number not found');
      return;
    }
    const text = `வணக்கம்! ${business.business_name} நிறுவனத்திற்கான "Digital Presence & Website Audit Report" தயார் செய்யப்பட்டுள்ளது.
    
📊 Digital Readiness Score: ${auditScore}/100
⚠️ Status: No Official Website Found
🚀 Projected Impact: 40% Increase in customer inquiries with a Mobile-Friendly Website.

Report Preview & Website Packages:
- SRA Software Solutions (Tamil Nadu)
Phone: +91 94420 00000`;

    window.open(`https://wa.me/${cleanPhone.length === 10 ? '91' + cleanPhone : cleanPhone}?text=${encodeURIComponent(text)}`, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-fade-in print:p-0 print:bg-white">
      <div className="relative flex max-h-[94vh] w-full max-w-3xl flex-col rounded-2xl bg-white shadow-2xl overflow-hidden border border-line print:max-h-none print:shadow-none print:border-none print:w-full">
        {/* Modal Toolbar (Hidden on Print) */}
        <div className="flex items-center justify-between border-b border-line bg-[#0b1220] p-4 text-white print:hidden">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue text-white shadow-md">
              <FileText size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold sm:text-base">Website Audit & Commercial Proposal</h2>
              <p className="text-[11px] text-slate-400">Print or export as PDF to present directly to client</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 rounded-xl bg-blue px-3.5 py-1.5 text-xs font-bold text-white hover:bg-blue/90 transition shadow-sm"
            >
              <Printer size={14} />
              <span>Print / Save PDF</span>
            </button>
            <button
              onClick={handleShareWhatsApp}
              disabled={!cleanPhone}
              className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-emerald-700 transition shadow-sm disabled:opacity-50"
            >
              <Share2 size={13} />
              <span>Send Summary</span>
            </button>
            <button
              onClick={onClose}
              className="rounded-xl bg-white/10 p-1.5 text-slate-300 hover:bg-white/20 hover:text-white transition"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Printable Proposal Document Body */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6 text-slate-800 font-sans print:overflow-visible print:p-6">
          {/* Header Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b-2 border-slate-900 pb-5 gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-blue mb-1">
                <span>SRA SOFTWARE SOLUTIONS</span>
                <span className="text-slate-300">•</span>
                <span>DIGITAL TRANSFORMATION REPORT</span>
              </div>
              <h1 className="text-2xl font-black tracking-tight text-slate-900 sm:text-3xl">
                Digital Presence Audit & Growth Proposal
              </h1>
              <p className="text-xs text-slate-500 mt-1">
                Prepared for Business Leadership & Decision Makers • {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
              </p>
            </div>

            <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-xl border border-line shrink-0">
              <div className="text-right">
                <span className="text-[10px] font-bold uppercase text-slate-500 block">Digital Readiness</span>
                <span className={`text-2xl font-black ${auditScore < 50 ? 'text-rose-600' : 'text-emerald-600'}`}>
                  {auditScore}/100
                </span>
              </div>
              <div className={`h-10 w-2 rounded-full ${auditScore < 50 ? 'bg-rose-500' : 'bg-emerald-500'}`} />
            </div>
          </div>

          {/* Client & Target Overview */}
          <div className="grid gap-4 sm:grid-cols-2 rounded-xl border border-line bg-slate-50/70 p-4">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                Target Business Entity
              </span>
              <p className="text-base font-bold text-slate-900">{business.business_name}</p>
              <p className="text-xs text-slate-600 mt-0.5">Category: {business.category_name || 'Commercial Entity'}</p>
              {business.client_name && <p className="text-xs text-slate-600">Contact: {business.client_name}</p>}
            </div>

            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                Commercial Location
              </span>
              <p className="text-xs text-slate-800 flex items-start gap-1 font-medium">
                <MapPin size={14} className="text-rose-500 shrink-0 mt-0.5" />
                <span>{business.address || 'Address on file'}, {business.district || 'Tamil Nadu'}</span>
              </p>
              {business.phone && (
                <p className="text-xs text-slate-800 flex items-center gap-1 font-medium mt-1">
                  <Phone size={14} className="text-blue shrink-0" />
                  <span>+91 {business.phone}</span>
                </p>
              )}
            </div>
          </div>

          {/* Audit Finding & Problem Statement */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <TrendingUp size={16} className="text-blue" />
              <span>1. Current Digital Audit Findings</span>
            </h3>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-rose-200 bg-rose-50/60 p-3.5">
                <span className="text-xs font-bold text-rose-800 block">Web Presence Status</span>
                <p className="text-sm font-bold text-rose-700 mt-1">
                  {isNoWebsite ? '❌ No Official Website' : business.website_status.replace('_', ' ')}
                </p>
                <p className="text-[11px] text-rose-600 mt-1 leading-snug">
                  Zero indexed landing page for Google search traffic in {business.district || 'Tamil Nadu'}.
                </p>
              </div>

              <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-3.5">
                <span className="text-xs font-bold text-amber-800 block">Customer Capture Rate</span>
                <p className="text-sm font-bold text-amber-700 mt-1">⚠️ Low (~20-30%)</p>
                <p className="text-[11px] text-amber-600 mt-1 leading-snug">
                  Competitors with Google Business sites capture the majority of online buyer inquiries.
                </p>
              </div>

              <div className="rounded-xl border border-blue/20 bg-blue/5 p-3.5">
                <span className="text-xs font-bold text-blue block">Revenue Opportunity</span>
                <p className="text-sm font-bold text-blue mt-1">📈 +35% to +60%</p>
                <p className="text-[11px] text-slate-600 mt-1 leading-snug">
                  Estimated growth with professional website, catalog & 1-click WhatsApp order integration.
                </p>
              </div>
            </div>
          </div>

          {/* Recommended Modernization Architecture */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <Sparkles size={16} className="text-blue" />
              <span>2. Proposed Digital Solutions & Deliverables</span>
            </h3>

            <div className="space-y-2 text-xs">
              <div className="flex items-start gap-2.5 rounded-lg border border-line bg-white p-3 shadow-xs">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-slate-900">Custom Domain (.in / .com) & Ultra-Fast Cloud Hosting</span>
                  <p className="text-slate-600 mt-0.5">
                    Official domain registered directly in your business name with 99.9% uptime and SSL security.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 rounded-lg border border-line bg-white p-3 shadow-xs">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-slate-900">Mobile-First Responsive Website & Product Catalog</span>
                  <p className="text-slate-600 mt-0.5">
                    Showcases all your products, pricing, photos, customer testimonials, and working hours cleanly on any smartphone.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 rounded-lg border border-line bg-white p-3 shadow-xs">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-slate-900">Instant WhatsApp Direct Ordering & Click-to-Call</span>
                  <p className="text-slate-600 mt-0.5">
                    Customers can browse and click a single button to chat, order, or inquire directly with your staff.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 rounded-lg border border-line bg-white p-3 shadow-xs">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-slate-900">Google Local Business & Maps Search SEO</span>
                  <p className="text-slate-600 mt-0.5">
                    Optimized to rank on page 1 of Google when nearby customers search for {business.category_name || 'services'} in {business.district || 'Tamil Nadu'}.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Pricing & Guarantee Footer */}
          <div className="rounded-xl border border-line bg-gradient-to-r from-slate-900 to-[#0e2338] p-5 text-white">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-cyan block mb-1">
                  Ready to Transform Your Business?
                </span>
                <p className="text-base font-bold">Fast 48-Hour Turnaround Guarantee</p>
                <p className="text-xs text-slate-300 mt-0.5">Complete setup, domain, hosting, and lifetime support included.</p>
              </div>

              <div className="text-right sm:border-l sm:border-white/20 sm:pl-6 shrink-0">
                <span className="text-[10px] text-slate-400 block">SRA Solution Team</span>
                <span className="text-sm font-bold text-white block">Tamil Nadu Support Desk</span>
                <span className="text-xs text-cyan font-mono">+91 94420 00000</span>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Action Bar (Hidden on Print) */}
        <div className="flex items-center justify-between border-t border-line bg-slate-50 px-6 py-4 print:hidden">
          <p className="text-xs text-slate-500">
            Tip: Press <strong>Print / Save PDF</strong> to save this document as a PDF to share with the owner.
          </p>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-line bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition shadow-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
