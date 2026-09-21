'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Clock, Database, PlusCircle, RotateCcw } from 'lucide-react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { fetchJobs, type ScrapeJob } from '@/lib/api';

export default function JobsPage() {
  const [jobs, setJobs] = useState<ScrapeJob[]>([]);
  const [loading, setLoading] = useState(true);

  const loadJobs = () => {
    setLoading(true);
    fetchJobs()
      .then(setJobs)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadJobs();
  }, []);

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header title="Scrape Jobs History" subtitle="Background discovery tasks, telemetry, and conversion metrics" />

        <div className="mb-6 flex items-center justify-between">
          <p className="text-xs text-muted">
            Total Jobs Logged: <strong className="text-ink font-bold">{jobs.length}</strong>
          </p>
          <div className="flex gap-2">
            <button
              onClick={loadJobs}
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition shadow-sm"
            >
              <RotateCcw size={14} />
              <span>Refresh</span>
            </button>
            <Link
              href="/scraper"
              className="inline-flex items-center gap-1.5 rounded-xl bg-blue px-3.5 py-2 text-xs font-bold text-white shadow hover:bg-blue/90 transition"
            >
              <PlusCircle size={14} />
              <span>New Job</span>
            </Link>
          </div>
        </div>

        <section className="rounded-2xl border border-line bg-white shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-xs text-muted">Loading jobs...</div>
          ) : jobs.length === 0 ? (
            <div className="p-16 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue/10 text-blue mb-3">
                <Database size={24} />
              </div>
              <p className="text-sm font-semibold text-slate-700">No discovery jobs recorded yet</p>
              <p className="mt-1 text-xs text-muted">Start a background job using the discovery scraper.</p>
              <Link
                href="/scraper"
                className="mt-4 inline-flex items-center gap-2 rounded-xl bg-blue px-4 py-2 text-xs font-bold text-white shadow"
              >
                Launch Scraper
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[850px] text-left text-xs">
                <thead className="border-b border-line bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-muted">
                  <tr>
                    <th className="px-5 py-3.5">ID</th>
                    <th className="px-5 py-3.5">Target Scope</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5">Progress</th>
                    <th className="px-5 py-3.5">Discovered</th>
                    <th className="px-5 py-3.5">Valid</th>
                    <th className="px-5 py-3.5">No Website</th>
                    <th className="px-5 py-3.5">Website Found</th>
                    <th className="px-5 py-3.5">Errors</th>
                    <th className="px-5 py-3.5 text-right">Results</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {jobs.map((j) => (
                    <tr key={j.id} className="hover:bg-slate-50 transition">
                      <td className="px-5 py-3.5 font-bold text-slate-800">#{j.id}</td>
                      <td className="px-5 py-3.5">
                        <p className="font-bold text-ink">{j.category}</p>
                        <p className="text-[11px] text-muted">{j.location}</p>
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                            j.status === 'COMPLETED'
                              ? 'bg-emerald-100 text-emerald-700'
                              : j.status === 'FAILED'
                              ? 'bg-rose-100 text-rose-700'
                              : 'bg-blue/10 text-blue animate-pulse'
                          }`}
                        >
                          {j.status}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 font-semibold text-slate-700">
                        {j.progress}%
                      </td>
                      <td className="px-5 py-3.5 font-medium text-slate-700">{j.discovered}</td>
                      <td className="px-5 py-3.5 font-semibold text-emerald-600">{j.valid}</td>
                      <td className="px-5 py-3.5 font-bold text-rose-600">{j.no_website}</td>
                      <td className="px-5 py-3.5 font-semibold text-teal-700">{j.website_found}</td>
                      <td className="px-5 py-3.5 font-medium text-slate-500">{j.errors}</td>
                      <td className="px-5 py-3.5 text-right">
                        <Link
                          href={`/leads?district=${encodeURIComponent(j.location)}`}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-blue hover:underline"
                        >
                          <span>View Leads</span>
                          <ArrowRight size={12} />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
