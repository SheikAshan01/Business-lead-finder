'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Layers, PlusCircle, Search } from 'lucide-react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { createCategory, fetchCategories, type Category } from '@/lib/api';

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [newCatName, setNewCatName] = useState('');
  const [search, setSearch] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadCategories = () => {
    fetchCategories()
      .then(setCategories)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCategories();
  }, []);

  async function handleAddCategory(e: React.FormEvent) {
    e.preventDefault();
    if (!newCatName.trim()) return;
    setSubmitting(true);
    try {
      await createCategory(newCatName.trim());
      setNewCatName('');
      loadCategories();
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  }

  const filtered = categories.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header title="Business Categories" subtitle="Configured commercial categories & discovered leads distribution" />

        {/* Add Category Form & Search Card */}
        <section className="mb-6 grid gap-4 sm:grid-cols-2">
          {/* Add Category */}
          <div className="rounded-2xl border border-line bg-white p-5 shadow-sm">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
              <PlusCircle size={14} className="text-blue" />
              <span>Add Custom Category</span>
            </h3>
            <form onSubmit={handleAddCategory} className="flex gap-2">
              <input
                type="text"
                value={newCatName}
                onChange={(e) => setNewCatName(e.target.value)}
                placeholder="e.g. Electric Vehicle Showrooms..."
                className="flex-1 rounded-xl border border-line bg-slate-50/70 px-3.5 py-2 text-xs outline-none focus:border-blue"
              />
              <button
                type="submit"
                disabled={submitting || !newCatName.trim()}
                className="rounded-xl bg-blue px-4 py-2 text-xs font-bold text-white shadow hover:bg-blue/90 disabled:opacity-50 transition"
              >
                {submitting ? 'Adding...' : 'Add'}
              </button>
            </form>
          </div>

          {/* Search */}
          <div className="rounded-2xl border border-line bg-white p-5 shadow-sm flex flex-col justify-center">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
              <Search size={14} className="text-blue" />
              <span>Filter Categories</span>
            </h3>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search category name..."
              className="w-full rounded-xl border border-line bg-slate-50/70 px-3.5 py-2 text-xs outline-none focus:border-blue"
            />
          </div>
        </section>

        {/* Categories Grid */}
        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((cat) => (
            <div
              key={cat.id}
              className="flex items-center justify-between rounded-2xl border border-line bg-white p-4 shadow-sm hover:border-blue/40 transition"
            >
              <div className="min-w-0 pr-3">
                <p className="font-bold text-ink truncate text-xs sm:text-sm">{cat.name}</p>
                <span className="text-[11px] text-muted">
                  {cat.business_count} leads recorded
                </span>
              </div>
              <Link
                href={`/leads?category_id=${cat.id}`}
                className="rounded-lg border border-line bg-slate-50 p-2 text-slate-600 hover:border-blue hover:text-blue transition shrink-0"
                title={`View ${cat.name} leads`}
              >
                <ArrowRight size={14} />
              </Link>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}
