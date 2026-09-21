'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Activity,
  CheckCircle2,
  Database,
  Layers,
  MapPin,
  RotateCcw,
  Shield,
  ShieldCheck,
  ToggleLeft,
  ToggleRight,
  Users,
  XCircle,
} from 'lucide-react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import {
  fetchAdminLogs,
  fetchAdminSources,
  fetchAdminStats,
  fetchAdminUsers,
  toggleAdminSource,
  type Source,
  type User,
} from '@/lib/api';

export default function AdminPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(false);
  const [activeTab, setActiveTab] = useState<'sources' | 'users' | 'logs' | 'system'>('sources');

  const loadData = () => {
    setLoading(true);
    setAuthError(false);
    Promise.all([fetchAdminSources(), fetchAdminUsers(), fetchAdminLogs(), fetchAdminStats()])
      .then(([s, u, l, st]) => {
        setSources(s);
        setUsers(u);
        setLogs(l);
        setStats(st);
      })
      .catch((err) => {
        if (err?.message?.includes('Authentication') || err?.message?.includes('privileges')) {
          setAuthError(true);
        }
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  async function handleToggleSource(id: number) {
    try {
      const updated = await toggleAdminSource(id);
      setSources((prev) => prev.map((s) => (s.id === id ? updated : s)));
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header title="Admin Control Center" subtitle="Manage source adapters, user credentials, audit trails, and system health" />

        {authError && (
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-amber-900 shadow-sm">
            <div>
              <p className="font-bold text-sm">Administrator Authentication Required</p>
              <p className="text-xs text-amber-700 mt-0.5">
                Managing source adapters and viewing audit logs requires an administrator session (Default: <code className="font-bold">admin@sra.com</code> / <code className="font-bold">admin123</code>).
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="rounded-xl bg-amber-600 px-4 py-2 text-xs font-bold text-white shadow hover:bg-amber-700 transition"
              >
                Sign In to Admin
              </Link>
              <button
                onClick={loadData}
                className="rounded-xl border border-amber-300 bg-white px-3 py-2 text-xs font-semibold text-amber-800 hover:bg-amber-100 transition"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="mb-6 flex gap-2 border-b border-line pb-3">
          {[
            { id: 'sources', label: 'Source Adapters', icon: Database },
            { id: 'users', label: 'User Management', icon: Users },
            { id: 'logs', label: 'Audit Trail', icon: Activity },
            { id: 'system', label: 'System Health', icon: ShieldCheck },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold transition ${
                activeTab === id
                  ? 'bg-blue text-white shadow-md shadow-blue/20'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <Icon size={14} />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Tab 1: Source Adapters */}
        {activeTab === 'sources' && (
          <section className="rounded-2xl border border-line bg-white shadow-sm overflow-hidden">
            <div className="border-b border-line p-5">
              <h3 className="text-sm font-bold text-ink">Modular Source Adapters</h3>
              <p className="text-xs text-muted">
                Enable or disable discovery sources independently without touching code.
              </p>
            </div>
            <div className="divide-y divide-line">
              {sources.map((src) => (
                <div key={src.id} className="flex items-center justify-between p-5 hover:bg-slate-50 transition">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-ink text-sm">{src.name}</span>
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600">
                        {src.source_type}
                      </span>
                    </div>
                    <p className="text-xs text-muted mt-1">
                      Rate limit: {src.rate_limit} req/min
                      {src.terms_url && (
                        <a href={src.terms_url} target="_blank" rel="noreferrer" className="ml-2 text-blue hover:underline">
                          (Terms & Compliance URL)
                        </a>
                      )}
                    </p>
                  </div>

                  <button
                    onClick={() => handleToggleSource(src.id)}
                    className={`flex items-center gap-1.5 rounded-xl border px-3.5 py-1.5 text-xs font-bold transition shadow-sm ${
                      src.enabled
                        ? 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                        : 'border-slate-200 bg-slate-100 text-slate-500 hover:bg-slate-200'
                    }`}
                  >
                    {src.enabled ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                    <span>{src.enabled ? 'Enabled' : 'Disabled'}</span>
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Tab 2: Users */}
        {activeTab === 'users' && (
          <section className="rounded-2xl border border-line bg-white shadow-sm overflow-hidden">
            <div className="border-b border-line p-5">
              <h3 className="text-sm font-bold text-ink">Authorized Accounts</h3>
              <p className="text-xs text-muted">Internal SRA team accounts & role permissions</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-line bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-muted">
                  <tr>
                    <th className="px-5 py-3.5">Name</th>
                    <th className="px-5 py-3.5">Email</th>
                    <th className="px-5 py-3.5">Role</th>
                    <th className="px-5 py-3.5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50">
                      <td className="px-5 py-3.5 font-bold text-ink">{u.full_name}</td>
                      <td className="px-5 py-3.5 text-slate-600">{u.email}</td>
                      <td className="px-5 py-3.5">
                        <span className="rounded-md bg-blue/10 px-2 py-0.5 text-[10px] font-bold text-blue">
                          {u.role.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-700">
                          Active
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Tab 3: Logs */}
        {activeTab === 'logs' && (
          <section className="rounded-2xl border border-line bg-white shadow-sm overflow-hidden">
            <div className="border-b border-line p-5">
              <h3 className="text-sm font-bold text-ink">Security & Action Audit Logs</h3>
              <p className="text-xs text-muted">Chronological audit trail of user and scraper events</p>
            </div>
            <div className="divide-y divide-line">
              {logs.length === 0 ? (
                <div className="p-8 text-center text-xs text-muted">No audit events recorded yet.</div>
              ) : (
                logs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-4 hover:bg-slate-50 text-xs">
                    <div>
                      <span className="font-bold text-ink">{log.action}</span>
                      <span className="text-muted ml-2">[{log.entity_type} #{log.entity_id || 'sys'}]</span>
                      {log.details && <p className="text-[11px] text-slate-600 mt-0.5">{log.details}</p>}
                    </div>
                    <span className="text-[11px] text-muted">
                      {new Date(log.created_at).toLocaleString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </section>
        )}

        {/* Tab 4: System Health */}
        {activeTab === 'system' && (
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-2xl border border-line bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold text-muted">System Status</span>
              <p className="mt-2 text-2xl font-bold text-emerald-600 capitalize">{stats.status || 'Operational'}</p>
              <p className="text-[11px] text-muted mt-1">FastAPI Backend & Database healthy</p>
            </div>
            <div className="rounded-2xl border border-line bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold text-muted">Total Businesses Managed</span>
              <p className="mt-2 text-2xl font-bold text-blue">{stats.businesses_count || 0}</p>
              <p className="text-[11px] text-muted mt-1">Normalized & deduplicated</p>
            </div>
            <div className="rounded-2xl border border-line bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold text-muted">Scrape Jobs Executed</span>
              <p className="mt-2 text-2xl font-bold text-ink">{stats.jobs_count || 0}</p>
              <p className="text-[11px] text-muted mt-1">Background tasks</p>
            </div>
            <div className="rounded-2xl border border-line bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold text-muted">Configured Categories</span>
              <p className="mt-2 text-2xl font-bold text-indigo-600">{stats.categories_count || 0}</p>
              <p className="text-[11px] text-muted mt-1">Commercial sectors</p>
            </div>
            <div className="rounded-2xl border border-line bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold text-muted">Configured Locations</span>
              <p className="mt-2 text-2xl font-bold text-purple-600">{stats.locations_count || 0}</p>
              <p className="text-[11px] text-muted mt-1">Districts & taluks</p>
            </div>
            <div className="rounded-2xl border border-line bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold text-muted">Active Adapters</span>
              <p className="mt-2 text-2xl font-bold text-teal-600">{stats.sources_count || 0}</p>
              <p className="text-[11px] text-muted mt-1">Plug-and-play data sources</p>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
