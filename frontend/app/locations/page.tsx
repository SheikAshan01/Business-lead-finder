'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Globe2, MapPin, Search } from 'lucide-react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { fetchDistricts, type DistrictLocation } from '@/lib/api';

export default function LocationsPage() {
  const [districts, setDistricts] = useState<DistrictLocation[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDistricts()
      .then(setDistricts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filtered = districts.filter((d) =>
    d.district.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header title="Tamil Nadu Locations" subtitle="Hierarchical 38 districts coverage with discovered business density" />

        {/* Filter Input */}
        <div className="mb-6 max-w-md">
          <div className="relative">
            <Search className="absolute left-3.5 top-3 text-slate-400" size={16} />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search Tamil Nadu district (e.g. Madurai, Coimbatore)..."
              className="w-full rounded-xl border border-line bg-white py-2.5 pl-10 pr-4 text-xs text-ink placeholder:text-slate-400 outline-none focus:border-blue shadow-sm transition"
            />
          </div>
        </div>

        {/* Districts Grid */}
        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((d) => (
            <div
              key={d.district}
              className="flex items-center justify-between rounded-2xl border border-line bg-white p-4 shadow-sm hover:border-blue/40 transition"
            >
              <div className="flex items-center gap-3 min-w-0 pr-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue/10 text-blue shrink-0">
                  <MapPin size={16} />
                </div>
                <div className="min-w-0">
                  <p className="font-bold text-ink truncate text-xs sm:text-sm">{d.district}</p>
                  <span className="text-[11px] text-muted">
                    {d.business_count} leads recorded
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <Link
                  href={`/leads?district=${encodeURIComponent(d.district)}`}
                  className="rounded-lg border border-line bg-slate-50 p-2 text-slate-600 hover:border-blue hover:text-blue transition"
                  title={`View leads in ${d.district}`}
                >
                  <ArrowRight size={14} />
                </Link>
              </div>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}
