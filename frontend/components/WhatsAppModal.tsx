'use client';

import { useState } from 'react';
import {
  Check,
  Copy,
  ExternalLink,
  Mail,
  MessageCircle,
  Phone,
  Send,
  Sparkles,
  X,
} from 'lucide-react';
import { addBusinessNote, API_URL, type Business } from '@/lib/api';

interface WhatsAppModalProps {
  business: Business | null;
  onClose: () => void;
  onNoteAdded?: (businessId: number, note: any) => void;
}

const TEMPLATES = [
  {
    id: 'tamil_website',
    name: 'Website Pitch (Tamil)',
    badge: 'Tamil',
    template: `வணக்கம் {client_name}! {district}-ல் உள்ள உங்கள் "{business_name}" நிறுவனத்திற்கு அதிகாரப்பூர்வ Website இல்லாததை கவனித்தோம்.

இப்போது 80% வாடிக்கையாளர்கள் கடைகளுக்கு வரும் முன் கூகுளில் தேடுகிறார்கள். உங்கள் வணிகத்திற்கு நவீன Mobile-Friendly Website அமைத்து, புதிய வாடிக்கையாளர்களை பெற நாங்கள் உதவுகிறோம்!

✅ Google Maps & Search Ranking
✅ WhatsApp Direct Order Button
✅ தயாரிப்புகள் & சேவைகள் Display

உங்களுக்கு இலவச Demo பார்க்க விருப்பமா?
- SRA Software Solutions (Tamil Nadu)`,
  },
  {
    id: 'english_website',
    name: 'Website Pitch (English)',
    badge: 'English',
    template: `Hello {client_name}!

We noticed your business "{business_name}" in {district} does not currently have an official website.

Over 75% of local customers in {district} search online before visiting or purchasing. We build high-speed, modern websites that bring you genuine daily leads and Google visibility.

Would you like a free sample website design for {business_name}?

Best regards,
SRA Software Solutions`,
  },
  {
    id: 'ecommerce_catalog',
    name: 'Online Catalog & Orders (Tamil)',
    badge: 'Catalog',
    template: `வணக்கம்! "{business_name}" வாடிக்கையாளர்கள் உங்கள் {category} பொருட்களை ஆன்லைனிலேயே பார்த்து, WhatsApp-ல் நேரடியாக ஆர்டர் செய்யும் வகையில் Digital Catalog & E-Commerce Website அமைத்து தருகிறோம்!

குறைந்த செலவில் உங்கள் கடைக்கு ஆன்லைன் ஆர்டர்களை அதிகப்படுத்த விரும்பினால் பதிலளிக்கவும்!
- SRA Software Solutions`,
  },
  {
    id: 'local_seo',
    name: 'Google Local Ranking',
    badge: 'SEO',
    template: `வணக்கம் {client_name}! "{business_name}" கூகுளில் தேடும்போது முதல் பக்கத்தில் வரவும், {district}-ல் உள்ள அதிக வாடிக்கையாளர்கள் உங்களை எளிதில் தொடர்பு கொள்ளவும் Google SEO & Business Website ஆஃபர் செய்கிறோம்! விவரங்களுக்கு பேசலாமா?`,
  },
];

export function WhatsAppModal({ business, onClose, onNoteAdded }: WhatsAppModalProps) {
  if (!business) return null;

  const rawPhone = (business.phone || business.alternate_phone || '').replace(/\D/g, '');
  const cleanPhone = rawPhone.length === 10 ? `91${rawPhone}` : rawPhone;

  const replacePlaceholders = (text: string) => {
    return text
      .replace(/{business_name}/g, business.business_name || 'உங்கள் வணிகம்')
      .replace(/{district}/g, business.district || 'Tamil Nadu')
      .replace(/{category}/g, business.category_name || 'Business')
      .replace(/{client_name}/g, business.client_name || 'அன்புடையீர்');
  };

  const [selectedTemplateId, setSelectedTemplateId] = useState(TEMPLATES[0].id);
  const [message, setMessage] = useState(replacePlaceholders(TEMPLATES[0].template));
  const [copied, setCopied] = useState(false);
  const [generatingAi, setGeneratingAi] = useState(false);
  const [aiTone, setAiTone] = useState<'tamil' | 'english' | 'urgency'>('tamil');

  const [activeChannel, setActiveChannel] = useState<'whatsapp' | 'email'>('whatsapp');
  const [emailSubject, setEmailSubject] = useState(`Website & Digital Growth proposal for ${business.business_name}`);

  const handleSelectTemplate = (tpl: typeof TEMPLATES[0]) => {
    setSelectedTemplateId(tpl.id);
    setMessage(replacePlaceholders(tpl.template));
  };

  const handleGenerateAiPitch = async () => {
    setGeneratingAi(true);
    try {
      // Call backend outreach API
      const res = await fetch(`${API_URL}/outreach/generate-pitch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_id: business.id,
          pitch_type: activeChannel === 'email' ? 'cold_email' : 'website_pitch',
          language: aiTone,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setMessage(data.message);
        if (data.subject) setEmailSubject(data.subject);
      } else {
        throw new Error('API unavailable');
      }
    } catch {
      // Offline fallback
      let aiText = '';
      const bName = business.business_name;
      const dist = business.district || 'Tamil Nadu';
      const cat = business.category_name || 'Business';

      if (aiTone === 'tamil') {
        aiText = `வணக்கம்! ${dist}-ல் உள்ள உங்கள் "${bName}" வாடிக்கையாளர்கள் பலரும் இப்போது ஆன்லைனில் தேடுகிறார்கள். உங்கள் போட்டி கடைகளுக்கு வெப்சைட் உள்ள நிலையில், உங்களுக்கான தனி வெப்சைட் மற்றும் WhatsApp Ordering அமைத்தால் விற்பனை 40% வரை அதிகரிக்கும்! இலவசமாக ஒரு மாதிரி வெப்சைட் பார்க்க விருப்பமா? - SRA Software Solutions`;
      } else if (aiTone === 'english') {
        aiText = `Hello! We analyzed local online demand for ${cat} in ${dist}. Businesses with an active website receive 3x more customer inquiries. For "${bName}", we can deploy a high-speed, professional website with Google Maps integration within 48 hours. Let us know if you'd like a free mockup preview! - SRA Software Solutions`;
      } else {
        aiText = `முக்கிய அறிவிப்பு: ${dist}-ல் ${cat} தேடும் நூற்றுக்கணக்கான வாடிக்கையாளர்கள் "${bName}"-க்கு வெப்சைட் இல்லாததால் மற்ற கடைகளுக்கு செல்கிறார்கள்! இந்த மாத சிறப்பு சலுகையாக அதிவேக Business Website அமைத்து தருகிறோம். உடனடி விவரங்களுக்கு பதிலளிக்கவும்!`;
      }
      setMessage(aiText);
    } finally {
      setGeneratingAi(false);
    }
  };

  const handleCopy = () => {
    const fullText = activeChannel === 'email' ? `Subject: ${emailSubject}\n\n${message}` : message;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSendWhatsApp = async (useAppProtocol = false) => {
    if (!cleanPhone) {
      alert('Valid phone number not found for this lead.');
      return;
    }

    // Auto-record CRM note
    try {
      const noteText = `[WhatsApp Outreach] Sent pitch to +${cleanPhone}: "${message.slice(0, 80)}..."`;
      const note = await addBusinessNote(business.id, noteText);
      onNoteAdded?.(business.id, note);
    } catch (e) {
      console.error('Failed to log note:', e);
    }

    const encoded = encodeURIComponent(message);
    const url = useAppProtocol
      ? `whatsapp://send?phone=${cleanPhone}&text=${encoded}`
      : `https://wa.me/${cleanPhone}?text=${encoded}`;
    window.open(url, '_blank');
  };

  const handleSendEmail = () => {
    const recipient = business.email || '';
    const subjectEnc = encodeURIComponent(emailSubject);
    const bodyEnc = encodeURIComponent(message);
    window.open(`mailto:${recipient}?subject=${subjectEnc}&body=${bodyEnc}`, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-fade-in">
      <div className="relative flex max-h-[92vh] w-full max-w-2xl flex-col rounded-2xl bg-white shadow-2xl overflow-hidden border border-line">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-line bg-gradient-to-r from-[#0d1a2d] to-[#0a3622] p-5 text-white">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500 text-white shadow-lg shadow-emerald-500/20">
              <MessageCircle size={22} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold">1-Click WhatsApp Outreach</h2>
                <span className="rounded bg-emerald-400/20 px-2 py-0.5 text-[10px] font-bold text-emerald-300">
                  Direct Connect
                </span>
              </div>
              <p className="text-xs text-slate-300">
                To: <span className="font-semibold text-white">{business.business_name}</span> (+91 {business.phone || 'No phone'})
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-xl bg-white/10 p-2 text-slate-300 hover:bg-white/20 hover:text-white transition"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {/* Channel Tabs: WhatsApp vs Email */}
          <div className="flex rounded-xl bg-slate-100 p-1">
            <button
              type="button"
              onClick={() => setActiveChannel('whatsapp')}
              className={`flex flex-1 items-center justify-center gap-2 rounded-lg py-2 text-xs font-bold transition ${
                activeChannel === 'whatsapp'
                  ? 'bg-emerald-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <MessageCircle size={15} />
              <span>WhatsApp Direct Message</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveChannel('email')}
              className={`flex flex-1 items-center justify-center gap-2 rounded-lg py-2 text-xs font-bold transition ${
                activeChannel === 'email'
                  ? 'bg-blue text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Mail size={15} />
              <span>Cold Email Proposal</span>
            </button>
          </div>

          {/* Template Selector */}
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-2">
              Select Message Pitch Template
            </span>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {TEMPLATES.map((t) => (
                <button
                  key={t.id}
                  onClick={() => handleSelectTemplate(t)}
                  className={`flex flex-col items-start rounded-xl border p-2.5 text-left text-xs transition ${
                    selectedTemplateId === t.id
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold shadow-sm'
                      : 'border-line bg-slate-50 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <span className="rounded bg-white/80 px-1.5 py-0.5 text-[9px] font-bold text-slate-600 mb-1 border border-line">
                    {t.badge}
                  </span>
                  <span className="line-clamp-2">{t.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* AI Pitch Generator Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-blue/20 bg-blue/5 p-3">
            <div className="flex items-center gap-2">
              <Sparkles size={16} className="text-blue" />
              <span className="text-xs font-bold text-blue">Smart AI Pitch Generator</span>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={aiTone}
                onChange={(e: any) => setAiTone(e.target.value)}
                className="rounded-lg border border-line bg-white px-2 py-1 text-xs font-medium text-slate-700 outline-none"
              >
                <option value="tamil">Friendly Tamil</option>
                <option value="english">Professional English</option>
                <option value="urgency">High Urgency</option>
              </select>
              <button
                type="button"
                onClick={handleGenerateAiPitch}
                disabled={generatingAi}
                className="inline-flex items-center gap-1.5 rounded-lg bg-blue px-3 py-1.5 text-xs font-bold text-white hover:bg-blue/90 transition shadow-sm disabled:opacity-60"
              >
                <Sparkles size={13} />
                <span>{generatingAi ? 'Generating...' : 'Generate Pitch'}</span>
              </button>
            </div>
          </div>

          {/* Email Subject Line (when email active) */}
          {activeChannel === 'email' && (
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-1">
                Email Subject Line
              </label>
              <input
                type="text"
                value={emailSubject}
                onChange={(e) => setEmailSubject(e.target.value)}
                className="w-full rounded-xl border border-line px-3 py-2 text-xs font-semibold text-slate-800 outline-none focus:border-blue shadow-inner"
              />
            </div>
          )}

          {/* Editable Message Box */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500">
                {activeChannel === 'email' ? 'Email Body Text' : 'WhatsApp Message Preview'}
              </label>
              <span className="text-[11px] text-muted">Variables: {'{business_name}'}, {'{district}'}</span>
            </div>
            <textarea
              rows={7}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full rounded-xl border border-line p-3 text-xs leading-relaxed text-slate-800 outline-none focus:border-emerald-500 font-sans shadow-inner"
              placeholder="Type your outreach message..."
            />
          </div>

          {/* Contact Alert if missing */}
          {activeChannel === 'whatsapp' && !cleanPhone && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
              ⚠️ This lead does not have a recorded phone number. You can still copy the message and send via email or social profiles.
            </div>
          )}
          {activeChannel === 'email' && !business.email && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
              ℹ️ Direct email address not found for this lead. You can copy the subject and body to contact them via contact form or social inbox.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-line bg-slate-50 px-5 py-3.5">
          <button
            type="button"
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition shadow-sm"
          >
            {copied ? <Check size={14} className="text-emerald-600" /> : <Copy size={14} />}
            <span>{copied ? 'Copied to Clipboard!' : 'Copy Text'}</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-line bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition"
            >
              Cancel
            </button>

            {activeChannel === 'whatsapp' ? (
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  disabled={!cleanPhone}
                  onClick={() => handleSendWhatsApp(false)}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2.5 text-xs font-bold text-white hover:bg-emerald-700 transition shadow-md shadow-emerald-600/20 disabled:opacity-50"
                  title="Open in WhatsApp Web"
                >
                  <Send size={13} />
                  <span>WhatsApp Web</span>
                  <ExternalLink size={11} />
                </button>
                <button
                  type="button"
                  disabled={!cleanPhone}
                  onClick={() => handleSendWhatsApp(true)}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-700 px-3.5 py-2.5 text-xs font-bold text-white hover:bg-emerald-800 transition shadow-sm disabled:opacity-50"
                  title="Open in Windows Desktop WhatsApp App"
                >
                  <span>App</span>
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={handleSendEmail}
                className="inline-flex items-center gap-2 rounded-xl bg-blue px-5 py-2.5 text-xs font-bold text-white hover:bg-blue/90 transition shadow-md shadow-blue/20"
              >
                <Mail size={14} />
                <span>Open in Email Client</span>
                <ExternalLink size={12} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
