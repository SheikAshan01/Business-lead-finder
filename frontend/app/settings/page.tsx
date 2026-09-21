'use client';

import { Key, Lock, Server, Shield, Sparkles } from 'lucide-react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header title="System Settings" subtitle="Environment configuration, security parameters, and data source connectors" />

        <div className="max-w-4xl space-y-6">
          {/* Connector Config */}
          <section className="rounded-2xl border border-line bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold text-ink">
              <Server size={18} className="text-blue" />
              <span>Data Source Connectors</span>
            </div>
            <p className="text-xs text-muted">
              Configure credentials and rate limits for permitted data sources in your <code className="bg-slate-100 px-1.5 py-0.5 rounded text-blue">.env</code> file.
            </p>

            <div className="space-y-3 pt-2">
              <div className="rounded-xl border border-line bg-slate-50 p-4 text-xs">
                <div className="flex items-center justify-between font-bold text-ink mb-1">
                  <span>OpenStreetMap Overpass API (Tamil Nadu)</span>
                  <span className="text-emerald-600 font-semibold">Active / Permitted</span>
                </div>
                <p className="text-slate-600">Endpoint: <code className="text-slate-800">https://overpass-api.de/api/interpreter</code></p>
                <p className="text-slate-500 text-[11px] mt-1">Extracts commercial establishments with contact tags across Tamil Nadu under ODbL terms.</p>
              </div>

              <div className="rounded-xl border border-line bg-slate-50 p-4 text-xs">
                <div className="flex items-center justify-between font-bold text-ink mb-1">
                  <span>Google Places API (New)</span>
                  <span className="text-slate-500 font-semibold">Configurable via .env</span>
                </div>
                <p className="text-slate-600">Environment variable: <code className="text-blue">GOOGLE_PLACES_API_KEY</code></p>
                <p className="text-slate-500 text-[11px] mt-1">To enable Google Places, add your API key to your backend environment file.</p>
              </div>
            </div>
          </section>

          {/* Security & Token Settings */}
          <section className="rounded-2xl border border-line bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold text-ink">
              <Lock size={18} className="text-blue" />
              <span>Security & Token Policies</span>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 text-xs">
              <div className="rounded-xl border border-line p-3.5 bg-slate-50">
                <span className="text-muted block text-[11px]">JWT Algorithm</span>
                <span className="font-bold text-ink mt-0.5 block">HMAC-SHA256 (HS256)</span>
              </div>
              <div className="rounded-xl border border-line p-3.5 bg-slate-50">
                <span className="text-muted block text-[11px]">Access Token Lifetime</span>
                <span className="font-bold text-ink mt-0.5 block">24 Hours</span>
              </div>
              <div className="rounded-xl border border-line p-3.5 bg-slate-50">
                <span className="text-muted block text-[11px]">Password Hashing</span>
                <span className="font-bold text-ink mt-0.5 block">Bcrypt (Salt Rounds: 12)</span>
              </div>
              <div className="rounded-xl border border-line p-3.5 bg-slate-50">
                <span className="text-muted block text-[11px]">CORS Allowed Origins</span>
                <span className="font-bold text-ink mt-0.5 block">http://localhost:3000</span>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
