'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Database,
  Globe2,
  Layers,
  Loader2,
  MapPin,
  Play,
  RotateCcw,
  Search,
  Sparkles,
  Zap,
} from 'lucide-react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import {
  API_URL,
  createScrape,
  fetchCategories,
  fetchDistricts,
  fetchJob,
  fetchJobs,
  fetchTaluks,
  type Category,
  type DistrictLocation,
  type ScrapeJob,
} from '@/lib/api';

export default function ScraperPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [districts, setDistricts] = useState<DistrictLocation[]>([]);
  const [taluks, setTaluks] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('Restaurants');
  const [customCategory, setCustomCategory] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('Madurai');
  const [selectedTaluk, setSelectedTaluk] = useState('');
  const [customLocation, setCustomLocation] = useState('');
  const [recentJobs, setRecentJobs] = useState<ScrapeJob[]>([]);

  // Active Job State
  const [activeJob, setActiveJob] = useState<ScrapeJob | null>(null);
  const [isScraping, setIsScraping] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Poller Ref
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const progressSectionRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    fetchCategories().then(setCategories).catch(console.error);
    fetchDistricts().then(setDistricts).catch(console.error);
    fetchJobs().then(setRecentJobs).catch(console.error);

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
      if (eventSourceRef.current) eventSourceRef.current.close();
    };
  }, []);

  useEffect(() => {
    if (selectedDistrict) {
      fetchTaluks(selectedDistrict)
        .then((data) => setTaluks(data.map((t) => t.taluk)))
        .catch(console.error);
    }
  }, [selectedDistrict]);

  function stopTracking() {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsScraping(false);
    fetchJobs().then(setRecentJobs).catch(console.error);
  }

  async function handleStartScrape(e: React.FormEvent) {
    e.preventDefault();
    const finalCategory = customCategory.trim() || selectedCategory;
    const finalLocation =
      customLocation.trim() || (selectedTaluk ? `${selectedTaluk}, ${selectedDistrict}` : selectedDistrict);

    if (!finalCategory || !finalLocation) {
      setErrorMsg('Please select or specify both category and location.');
      return;
    }

    // Reset previous track
    stopTracking();
    setIsScraping(true);
    setErrorMsg('');

    try {
      const job = await createScrape(finalCategory, finalLocation);
      setActiveJob({ ...job, progress: 8, status: 'RUNNING' });

      // Smooth scroll to progress section
      setTimeout(() => {
        progressSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 100);

      // 1. Establish SSE stream for live real-time progress events
      try {
        const eventSource = new EventSource(`${API_URL}/scrape/jobs/${job.id}/stream`);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.error) {
              setErrorMsg(data.error);
              stopTracking();
              return;
            }

            setActiveJob((prev) => ({
              ...(prev || job),
              ...data,
              // Never decrease percentage to ensure smooth upward progress
              progress: Math.max(prev?.progress || 0, data.progress || 0),
            }));

            if (data.status === 'COMPLETED' || data.status === 'FAILED') {
              stopTracking();
            }
          } catch (parseErr) {
            console.error('SSE parse error:', parseErr);
          }
        };

        eventSource.onerror = () => {
          // SSE connection hiccup - keep polling fallback alive
          console.warn('SSE stream disconnected, relying on polling fallback.');
        };
      } catch (sseErr) {
        console.warn('SSE not available, falling back to polling', sseErr);
      }

      // 2. Resilient Polling Fallback (every 350ms) to ensure continuous, reliable updates
      pollIntervalRef.current = setInterval(async () => {
        try {
          const fresh = await fetchJob(job.id);
          setActiveJob((prev) => ({
            ...(prev || job),
            ...fresh,
            progress: Math.max(prev?.progress || 0, fresh.progress || 0),
          }));

          if (fresh.status === 'COMPLETED' || fresh.status === 'FAILED') {
            stopTracking();
          }
        } catch (pollErr) {
          console.error('Polling error:', pollErr);
        }
      }, 350);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to trigger discovery job.');
      setIsScraping(false);
    }
  }

  // Determine stage message from percentage
  function getStageMessage(job: ScrapeJob) {
    if (job.status === 'FAILED') {
      return job.error_message || 'Discovery encountered an error.';
    }
    if (job.status === 'COMPLETED') {
      return `Discovery finished! Found ${job.valid} businesses (${job.no_website} with NO official website).`;
    }
    const prog = job.progress || 0;
    if (prog < 15) return 'Initializing Tamil Nadu discovery engine & Open Data...';
    if (prog < 35) return `Querying OpenStreetMap Nominatim for ${job.category} in ${job.location}...`;
    if (prog < 55) return `Normalizing business names, addresses, and contact phone numbers...`;
    if (prog < 75) return `Probing official websites & identifying digital presence gaps...`;
    if (prog < 98) return `RapidFuzz deduplicating & computing 100-point lead qualification scores...`;
    return 'Finalizing qualified leads and storing to CRM database...';
  }

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header
          title="Business Lead Finder"
          subtitle="Target Tamil Nadu commercial sectors & identify businesses with no official website"
        />

        {/* Main Discovery Configuration Card */}
        <section className="mb-8 rounded-2xl bg-[#0b1220] p-6 text-white shadow-xl shadow-blue-500/10 sm:p-8">
          <div className="max-w-3xl">
            <div className="mb-3 flex items-center gap-2 text-cyan-400">
              <Sparkles size={16} />
              <span className="text-xs font-bold uppercase tracking-wider">Discovery Wizard</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">Start Business Discovery</h2>
            <p className="mt-2 text-xs leading-relaxed text-slate-300 sm:text-sm">
              Discover registered commercial businesses, extract contact details, check official website presence, and
              isolate high-potential leads across Tamil Nadu.
            </p>

            <form onSubmit={handleStartScrape} className="mt-8 space-y-6">
              {errorMsg && (
                <div className="flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
                  <AlertCircle size={15} />
                  <span>{errorMsg}</span>
                </div>
              )}

              <div className="grid gap-6 sm:grid-cols-2">
                {/* 1. Business Category */}
                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <Layers size={14} className="text-cyan-400" />
                    <span>Business Category</span>
                  </label>
                  <select
                    value={selectedCategory}
                    disabled={isScraping}
                    onChange={(e) => {
                      setSelectedCategory(e.target.value);
                      setCustomCategory('');
                    }}
                    className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-xs sm:text-sm text-white outline-none focus:border-cyan-400 disabled:opacity-60 transition"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.name} className="bg-[#0b1220] text-white">
                        {c.name} {c.business_count > 0 ? `(${c.business_count})` : ''}
                      </option>
                    ))}
                  </select>
                  <div className="text-[11px] text-slate-400">or type custom category:</div>
                  <input
                    type="text"
                    value={customCategory}
                    disabled={isScraping}
                    onChange={(e) => setCustomCategory(e.target.value)}
                    placeholder="Custom category (e.g. Organic Millet Store)..."
                    className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-xs text-white placeholder:text-slate-500 outline-none focus:border-cyan-400 disabled:opacity-60 transition"
                  />
                </div>

                {/* 2. Tamil Nadu Location */}
                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <MapPin size={14} className="text-cyan-400" />
                    <span>Tamil Nadu Location</span>
                  </label>
                  <select
                    value={selectedDistrict}
                    disabled={isScraping}
                    onChange={(e) => {
                      setSelectedDistrict(e.target.value);
                      setSelectedTaluk('');
                      setCustomLocation('');
                    }}
                    className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-xs sm:text-sm text-white outline-none focus:border-cyan-400 disabled:opacity-60 transition"
                  >
                    {districts.map((d) => (
                      <option key={d.district} value={d.district} className="bg-[#0b1220] text-white">
                        {d.district} {d.business_count > 0 ? `(${d.business_count})` : ''}
                      </option>
                    ))}
                  </select>

                  {/* Optional Taluk selector */}
                  {taluks.length > 0 && (
                    <select
                      value={selectedTaluk}
                      disabled={isScraping}
                      onChange={(e) => setSelectedTaluk(e.target.value)}
                      className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-xs text-white outline-none focus:border-cyan-400 disabled:opacity-60 transition"
                    >
                      <option value="" className="bg-[#0b1220] text-slate-400">
                        All Taluks in {selectedDistrict}
                      </option>
                      {taluks.map((t) => (
                        <option key={t} value={t} className="bg-[#0b1220] text-white">
                          {t}
                        </option>
                      ))}
                    </select>
                  )}

                  <div className="text-[11px] text-slate-400">or type custom location:</div>
                  <input
                    type="text"
                    value={customLocation}
                    disabled={isScraping}
                    onChange={(e) => setCustomLocation(e.target.value)}
                    placeholder="Custom area (e.g. Anna Nagar, Chennai)..."
                    className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-xs text-white placeholder:text-slate-500 outline-none focus:border-cyan-400 disabled:opacity-60 transition"
                  />
                </div>
              </div>

              {/* Single Prominent SCRAP Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isScraping}
                  className="flex w-full sm:w-auto items-center justify-center gap-2.5 rounded-xl px-10 py-3.5 text-sm font-black tracking-wider text-white shadow-2xl transition active:scale-[0.98] disabled:cursor-wait"
                  style={{
                    background: 'linear-gradient(135deg, #2563eb 0%, #4f46e5 50%, #06b6d4 100%)',
                    boxShadow: '0 10px 25px -4px rgba(37, 99, 235, 0.6), 0 0 15px rgba(6, 182, 212, 0.4)',
                  }}
                >
                  {isScraping ? (
                    <>
                      <Loader2 size={18} className="animate-spin text-white" />
                      <span>Scraping ({activeJob?.progress || 0}%)...</span>
                    </>
                  ) : (
                    <>
                      <Search size={18} className="text-white" strokeWidth={2.5} />
                      <span>SCRAP</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </section>

        {/* Live Scraping Progress Panel (Dual-channel SSE + Resilient Polling) */}
        {activeJob && (
          <div ref={progressSectionRef}>
            <section className="mb-8 rounded-2xl border-2 border-blue-500/40 bg-white p-6 shadow-xl shadow-blue-500/10 animate-rise">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-5">
                <div>
                  <div className="flex items-center gap-2.5">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-blue-600">
                      Job #{activeJob.id}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold ${
                        activeJob.status === 'COMPLETED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : activeJob.status === 'FAILED'
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-blue-50 text-blue-700 ring-1 ring-blue-500/20'
                      }`}
                    >
                      {activeJob.status === 'RUNNING' && (
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-600"></span>
                        </span>
                      )}
                      {activeJob.status === 'COMPLETED' && <CheckCircle2 size={13} className="text-emerald-600" />}
                      <span>{activeJob.status}</span>
                    </span>
                  </div>
                  <p className="text-base font-bold text-slate-900 mt-1">
                    Discovering: <span className="text-blue-600">{activeJob.category}</span> in{' '}
                    <span className="text-slate-800">{activeJob.location}</span>
                  </p>
                </div>

                {activeJob.status === 'COMPLETED' && (
                  <Link
                    href={`/leads?district=${encodeURIComponent(activeJob.location)}`}
                    className="inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-xs font-bold text-white shadow-md hover:brightness-110 transition"
                    style={{
                      background: 'linear-gradient(135deg, #2563eb 0%, #4f46e5 50%, #06b6d4 100%)',
                      boxShadow: '0 4px 14px rgba(37, 99, 235, 0.4)',
                    }}
                  >
                    <span>View Discovered Leads ({activeJob.valid})</span>
                    <ArrowRight size={14} />
                  </Link>
                )}
              </div>

              {/* Progress Bar with Dynamic Stage Message & Percentage Counter */}
              <div className="space-y-3 mb-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-semibold text-slate-700">
                  <div className="flex items-center gap-2 text-slate-800 font-medium">
                    {isScraping && <Loader2 size={16} className="animate-spin text-blue-600 shrink-0" />}
                    <span className="text-slate-900 font-bold">{getStageMessage(activeJob)}</span>
                  </div>
                  <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
                    <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider">PROGRESS:</span>
                    <span
                      className="font-mono text-sm font-black text-white px-2.5 py-0.5 rounded-lg shadow-sm"
                      style={{
                        background: 'linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)',
                      }}
                    >
                      {activeJob.progress}%
                    </span>
                  </div>
                </div>

                {/* Progress Track */}
                <div
                  className="relative h-6 w-full rounded-full p-1 overflow-hidden shadow-inner border"
                  style={{
                    background: '#e2e8f0',
                    borderColor: '#cbd5e1',
                  }}
                >
                  <div
                    className="h-full rounded-full shadow-lg transition-all duration-300 ease-out flex items-center justify-end pr-2.5"
                    style={{
                      width: `${Math.max(activeJob.progress, 5)}%`,
                      background: 'linear-gradient(90deg, #2563eb 0%, #4f46e5 50%, #06b6d4 100%)',
                      boxShadow: '0 0 14px rgba(37, 99, 235, 0.6)',
                    }}
                  >
                    <span className="text-[11px] font-black text-white leading-none drop-shadow">
                      {activeJob.progress}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Live Metric Counters Grid */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-6 text-center">
                <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-3 transition hover:border-slate-300">
                  <p className="text-[11px] text-slate-500 font-semibold">Discovered</p>
                  <p className="text-xl font-extrabold text-slate-900 mt-0.5">{activeJob.discovered}</p>
                </div>
                <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-3 transition hover:border-emerald-300">
                  <p className="text-[11px] text-emerald-700 font-semibold">Valid</p>
                  <p className="text-xl font-extrabold text-emerald-700 mt-0.5">{activeJob.valid}</p>
                </div>
                <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-3 transition hover:border-amber-300">
                  <p className="text-[11px] text-amber-700 font-semibold">Duplicates</p>
                  <p className="text-xl font-extrabold text-amber-700 mt-0.5">{activeJob.duplicates}</p>
                </div>
                <div className="rounded-xl border border-rose-200 bg-rose-50/70 p-3 transition hover:border-rose-300">
                  <p className="text-[11px] text-rose-700 font-semibold">No Website</p>
                  <p className="text-xl font-extrabold text-rose-700 mt-0.5">{activeJob.no_website}</p>
                </div>
                <div className="rounded-xl border border-teal-200 bg-teal-50/60 p-3 transition hover:border-teal-300">
                  <p className="text-[11px] text-teal-700 font-semibold">Website Found</p>
                  <p className="text-xl font-extrabold text-teal-700 mt-0.5">{activeJob.website_found}</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-3 transition hover:border-slate-300">
                  <p className="text-[11px] text-slate-500 font-semibold">Errors</p>
                  <p className="text-xl font-extrabold text-slate-700 mt-0.5">{activeJob.errors}</p>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* Recent Discovery Jobs Log */}
        <section className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="border-b border-slate-100 p-5">
            <h3 className="text-base font-bold text-slate-900">Recent Scrape Jobs</h3>
            <p className="text-xs text-slate-500">History of background lead discovery jobs</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-xs">
              <thead className="border-b border-slate-100 bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-5 py-3">Job ID</th>
                  <th className="px-5 py-3">Target</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Discovered</th>
                  <th className="px-5 py-3">No Website</th>
                  <th className="px-5 py-3">Website Found</th>
                  <th className="px-5 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentJobs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-5 py-8 text-center text-slate-400">
                      No previous discovery jobs found.
                    </td>
                  </tr>
                ) : (
                  recentJobs.map((j) => (
                    <tr key={j.id} className="hover:bg-slate-50/80 transition">
                      <td className="px-5 py-3 font-bold text-slate-800">#{j.id}</td>
                      <td className="px-5 py-3">
                        <span className="font-bold text-slate-900">{j.category}</span>
                        <span className="text-slate-500 block text-[11px]">{j.location}</span>
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                            j.status === 'COMPLETED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : j.status === 'FAILED'
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-blue-50 text-blue-700'
                          }`}
                        >
                          {j.status}
                        </span>
                      </td>
                      <td className="px-5 py-3 font-semibold text-slate-700">{j.discovered}</td>
                      <td className="px-5 py-3 font-bold text-rose-600">{j.no_website}</td>
                      <td className="px-5 py-3 font-semibold text-teal-700">{j.website_found}</td>
                      <td className="px-5 py-3 text-slate-500 text-[11px]">
                        {j.created_at ? new Date(j.created_at).toLocaleTimeString() : 'N/A'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
