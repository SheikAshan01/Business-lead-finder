'use client';

import { Suspense, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import {
  ArrowUpDown,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
  Filter,
  Globe2,
  Mail,
  MapPin,
  Phone,
  RotateCcw,
  Search,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react';
import { Header } from '@/components/Header';
import { LeadDetailsModal } from '@/components/LeadDetailsModal';
import { Sidebar } from '@/components/Sidebar';
import {
  bulkDeleteBusinesses,
  deleteBusiness,
  fetchBusinesses,
  fetchCategories,
  fetchDistricts,
  getExportUrl,
  toggleSaveBusiness,
  type Business,
  type Category,
  type DistrictLocation,
} from '@/lib/api';

export default function LeadsPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center text-xs text-muted">Loading leads workspace...</div>}>
      <LeadsContent />
    </Suspense>
  );
}

function LeadsContent() {
  const searchParams = useSearchParams();

  // Filter States
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>(undefined);
  const [selectedDistrict, setSelectedDistrict] = useState(searchParams.get('district') || '');
  const [websiteStatus, setWebsiteStatus] = useState<string>(searchParams.get('website_status') || '');
  const [emailStatus, setEmailStatus] = useState<string>('');
  const [phoneStatus, setPhoneStatus] = useState<string>('');
  const [scoreRange, setScoreRange] = useState<string>('');
  const [leadStatus, setLeadStatus] = useState<string>('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortBy, setSortBy] = useState('lead_score');
  const [sortOrder, setSortOrder] = useState('desc');

  // Data States
  const [leads, setLeads] = useState<Business[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [categories, setCategories] = useState<Category[]>([]);
  const [districts, setDistricts] = useState<DistrictLocation[]>([]);
  const [loading, setLoading] = useState(true);

  // Selected Lead for Modal
  const [selectedLead, setSelectedLead] = useState<Business | null>(null);

  // Row Selection
  const [rowSelection, setRowSelection] = useState<Record<string, boolean>>({});

  // Fetch Categories & Districts on mount
  useEffect(() => {
    fetchCategories().then(setCategories).catch(console.error);
    fetchDistricts().then(setDistricts).catch(console.error);
  }, []);

  // Fetch Leads when filters change
  const loadLeads = () => {
    setLoading(true);
    let min_score: number | undefined;
    let max_score: number | undefined;
    if (scoreRange === '0-25') { min_score = 0; max_score = 25; }
    else if (scoreRange === '26-50') { min_score = 26; max_score = 50; }
    else if (scoreRange === '51-75') { min_score = 51; max_score = 75; }
    else if (scoreRange === '76-100') { min_score = 76; max_score = 100; }

    fetchBusinesses({
      page,
      page_size: pageSize,
      search,
      category_id: selectedCategory,
      district: selectedDistrict,
      website_status: websiteStatus || undefined,
      email_status: emailStatus || undefined,
      phone_status: phoneStatus || undefined,
      min_score,
      max_score,
      lead_status: leadStatus || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
    })
      .then((data) => {
        setLeads(data.items);
        setTotal(data.total);
        setTotalPages(data.total_pages);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadLeads();
  }, [page, pageSize, search, selectedCategory, selectedDistrict, websiteStatus, emailStatus, phoneStatus, scoreRange, leadStatus, sortBy, sortOrder]);

  async function handleToggleSave(id: number) {
    try {
      const updated = await toggleSaveBusiness(id);
      setLeads((prev) => prev.map((item) => (item.id === id ? { ...item, is_saved: updated.is_saved } : item)));
    } catch (err) {
      console.error(err);
    }
  }

  const [deleting, setDeleting] = useState(false);

  async function handleDeleteSingle(b: Business) {
    if (!window.confirm(`Are you sure you want to permanently delete "${b.business_name}"?`)) {
      return;
    }
    try {
      setDeleting(true);
      await deleteBusiness(b.id);
      setLeads((prev) => prev.filter((item) => item.id !== b.id));
      setTotal((prev) => Math.max(0, prev - 1));
      if (selectedLead?.id === b.id) {
        setSelectedLead(null);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to delete lead');
    } finally {
      setDeleting(false);
    }
  }

  async function handleBulkDelete() {
    const validSelectedIds = selectedIds.filter((id): id is number => typeof id === 'number');
    const count = validSelectedIds.length;
    if (count === 0) return;
    if (!window.confirm(`Are you sure you want to permanently delete ${count} selected business lead${count > 1 ? 's' : ''}?`)) {
      return;
    }
    try {
      setDeleting(true);
      await bulkDeleteBusinesses(validSelectedIds);
      setRowSelection({});
      loadLeads();
    } catch (err: any) {
      alert(err.message || 'Failed to delete selected leads');
    } finally {
      setDeleting(false);
    }
  }

  function resetFilters() {
    setSearch('');
    setSelectedCategory(undefined);
    setSelectedDistrict('');
    setWebsiteStatus('');
    setEmailStatus('');
    setPhoneStatus('');
    setScoreRange('');
    setLeadStatus('');
    setPage(1);
  }

  // TanStack Table Column Definitions
  const columns = useMemo<ColumnDef<Business>[]>(
    () => [
      {
        id: 'select',
        header: ({ table }) => (
          <input
            type="checkbox"
            checked={table.getIsAllPageRowsSelected()}
            onChange={table.getToggleAllPageRowsSelectedHandler()}
            className="rounded border-line text-blue focus:ring-blue"
          />
        ),
        cell: ({ row }) => (
          <input
            type="checkbox"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
            className="rounded border-line text-blue focus:ring-blue"
          />
        ),
      },
      {
        accessorKey: 'business_name',
        header: 'Business Name',
        cell: ({ row }) => {
          const b = row.original;
          return (
            <div>
              <p
                onClick={() => setSelectedLead(b)}
                className="font-bold text-ink hover:text-blue cursor-pointer transition"
              >
                {b.business_name}
              </p>
              <div className="flex items-center gap-1.5 text-[11px] text-muted">
                <span>{b.category_name || 'Commercial'}</span>
                {b.client_name && <span>• {b.client_name}</span>}
              </div>
            </div>
          );
        },
      },
      {
        accessorKey: 'district',
        header: 'Location',
        cell: ({ row }) => {
          const b = row.original;
          return (
            <span className="flex items-center gap-1 text-slate-700 text-xs">
              <MapPin size={13} className="text-slate-400 shrink-0" />
              <span>{b.district || 'Tamil Nadu'}</span>
            </span>
          );
        },
      },
      {
        id: 'contact',
        header: 'Contact Details',
        cell: ({ row }) => {
          const b = row.original;
          return (
            <div className="space-y-0.5 text-xs">
              {b.phone ? (
                <a href={`tel:${b.phone}`} className="flex items-center gap-1 font-medium text-slate-800 hover:text-blue">
                  <Phone size={12} className="text-blue shrink-0" />
                  <span>+91 {b.phone}</span>
                </a>
              ) : (
                <span className="text-muted italic text-[11px]">No phone</span>
              )}
              {b.email && (
                <a href={`mailto:${b.email}`} className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-blue">
                  <Mail size={11} className="shrink-0" />
                  <span className="truncate max-w-[130px]">{b.email}</span>
                </a>
              )}
            </div>
          );
        },
      },
      {
        accessorKey: 'website_status',
        header: 'Website Presence',
        cell: ({ row }) => {
          const status = row.original.website_status;
          const isNoWeb = status === 'NO_WEBSITE';
          const isFound = status === 'WEBSITE_FOUND';
          return (
            <div>
              <span
                className={`inline-block rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                  isNoWeb
                    ? 'bg-rose-50 text-rose-700'
                    : isFound
                    ? 'bg-emerald-50 text-emerald-700'
                    : 'bg-slate-100 text-slate-700'
                }`}
              >
                {status.replace('_', ' ')}
              </span>
              {row.original.website_url && (
                <a
                  href={row.original.website_url}
                  target="_blank"
                  rel="noreferrer"
                  className="block mt-0.5 text-[10px] text-blue hover:underline truncate max-w-[120px]"
                >
                  {row.original.website_url.replace(/^https?:\/\//, '')}
                </a>
              )}
            </div>
          );
        },
      },
      {
        accessorKey: 'lead_score',
        header: () => (
          <button
            onClick={() => {
              if (sortBy === 'lead_score') {
                setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
              } else {
                setSortBy('lead_score');
                setSortOrder('desc');
              }
            }}
            className="flex items-center gap-1 font-bold text-muted hover:text-ink"
          >
            <span>Score</span>
            <ArrowUpDown size={12} />
          </button>
        ),
        cell: ({ row }) => {
          const score = row.original.lead_score;
          const isHigh = score >= 75;
          return (
            <div className="flex items-center gap-1">
              <span className={`font-bold text-xs ${isHigh ? 'text-blue' : 'text-slate-700'}`}>{score}</span>
              <span className="text-[10px] text-muted">/100</span>
              {isHigh && <Sparkles size={11} className="text-amber-500 fill-amber-500" />}
            </div>
          );
        },
      },
      {
        accessorKey: 'lead_status',
        header: 'Status',
        cell: ({ row }) => {
          const st = row.original.lead_status;
          return (
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-700">
              {st}
            </span>
          );
        },
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => {
          const b = row.original;
          return (
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setSelectedLead(b)}
                title="View Full Profile & Notes"
                className="rounded-lg border border-line bg-white p-1.5 text-slate-700 hover:border-blue hover:text-blue transition shadow-sm"
              >
                <Eye size={14} />
              </button>
              <button
                onClick={() => handleToggleSave(b.id)}
                title={b.is_saved ? 'Remove Bookmark' : 'Save Lead'}
                className={`rounded-lg border p-1.5 transition shadow-sm ${
                  b.is_saved
                    ? 'border-amber-400 bg-amber-50 text-amber-600'
                    : 'border-line bg-white text-slate-400 hover:text-amber-600'
                }`}
              >
                <Bookmark size={14} className={b.is_saved ? 'fill-amber-500' : ''} />
              </button>
              <button
                onClick={() => handleDeleteSingle(b)}
                title="Delete Lead"
                className="rounded-lg border border-line bg-white p-1.5 text-slate-400 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-600 transition shadow-sm"
              >
                <Trash2 size={14} />
              </button>
            </div>
          );
        },
      },
    ],
    [sortBy, sortOrder, deleting]
  );

  const table = useReactTable({
    data: leads,
    columns,
    state: { rowSelection },
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
  });

  // Selected lead IDs for selective export
  const selectedIds = Object.keys(rowSelection)
    .filter((idx) => rowSelection[idx])
    .map((idx) => leads[parseInt(idx)]?.id)
    .filter(Boolean);

  const exportParams: Record<string, string | number | undefined> = {
    website_status: websiteStatus || undefined,
    district: selectedDistrict || undefined,
    category_id: selectedCategory || undefined,
    lead_status: leadStatus || undefined,
    selected_ids: selectedIds.length > 0 ? selectedIds.join(',') : undefined,
  };

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-12">
        <Header title="All Business Leads" subtitle="Verified Tamil Nadu commercial prospects directory with multi-field filtering" />

        {/* Filter Controls Bar */}
        <section className="mb-6 rounded-2xl border border-line bg-white p-5 shadow-sm space-y-4">
          {/* Top Row: Search & Prominent NO WEBSITE Quick Filter */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            {/* Search Input */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3.5 top-3 text-slate-400" size={16} />
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                placeholder="Search by business name, phone, email, address..."
                className="w-full rounded-xl border border-line bg-slate-50/70 py-2.5 pl-10 pr-4 text-xs text-ink placeholder:text-slate-400 outline-none focus:border-blue transition"
              />
            </div>

            {/* Quick Filter: [NO WEBSITE] Prominent Action & Bulk Delete */}
            <div className="flex flex-wrap items-center gap-2">
              {selectedIds.length > 0 && (
                <button
                  onClick={handleBulkDelete}
                  disabled={deleting}
                  className="flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2.5 text-xs font-bold text-white shadow-sm hover:bg-rose-700 transition disabled:opacity-50 ring-2 ring-rose-600/30"
                >
                  <Trash2 size={15} />
                  <span>{deleting ? 'Deleting...' : `Delete Selected (${selectedIds.length})`}</span>
                </button>
              )}

              <button
                onClick={() => {
                  setWebsiteStatus(websiteStatus === 'NO_WEBSITE' ? '' : 'NO_WEBSITE');
                  setPage(1);
                }}
                className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition shadow-sm ${
                  websiteStatus === 'NO_WEBSITE'
                    ? 'bg-rose-600 text-white shadow-rose-600/25 ring-2 ring-rose-600'
                    : 'border border-rose-200 bg-rose-50/80 text-rose-700 hover:bg-rose-100'
                }`}
              >
                <Globe2 size={15} />
                <span>[ NO WEBSITE ] Leads</span>
                {websiteStatus === 'NO_WEBSITE' && <X size={13} className="ml-1" />}
              </button>

              {/* Exports */}
              <a
                href={getExportUrl('csv', exportParams)}
                download
                className="flex items-center gap-1.5 rounded-xl border border-line bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:border-blue hover:text-blue transition shadow-sm"
              >
                <Download size={14} />
                <span>CSV</span>
              </a>
              <a
                href={getExportUrl('excel', exportParams)}
                download
                className="flex items-center gap-1.5 rounded-xl border border-line bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:border-emerald-600 hover:text-emerald-600 transition shadow-sm"
              >
                <Download size={14} />
                <span>Excel</span>
              </a>
            </div>
          </div>

          {/* Secondary Filter Dropdowns Row */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6 pt-2 border-t border-line text-xs">
            {/* Category */}
            <select
              value={selectedCategory || ''}
              onChange={(e) => {
                setSelectedCategory(e.target.value ? Number(e.target.value) : undefined);
                setPage(1);
              }}
              className="rounded-xl border border-line bg-white px-3 py-2 text-slate-700 outline-none focus:border-blue"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>

            {/* District */}
            <select
              value={selectedDistrict}
              onChange={(e) => {
                setSelectedDistrict(e.target.value);
                setPage(1);
              }}
              className="rounded-xl border border-line bg-white px-3 py-2 text-slate-700 outline-none focus:border-blue"
            >
              <option value="">All TN Districts</option>
              {districts.map((d) => (
                <option key={d.district} value={d.district}>
                  {d.district}
                </option>
              ))}
            </select>

            {/* Website Status */}
            <select
              value={websiteStatus}
              onChange={(e) => {
                setWebsiteStatus(e.target.value);
                setPage(1);
              }}
              className="rounded-xl border border-line bg-white px-3 py-2 text-slate-700 outline-none focus:border-blue"
            >
              <option value="">All Websites</option>
              <option value="NO_WEBSITE">No Website</option>
              <option value="WEBSITE_FOUND">Website Found</option>
              <option value="SOCIAL_ONLY">Social Only</option>
              <option value="WEBSITE_BROKEN">Website Broken</option>
              <option value="WEBSITE_UNVERIFIED">Unverified</option>
            </select>

            {/* Email Filter */}
            <select
              value={emailStatus}
              onChange={(e) => {
                setEmailStatus(e.target.value);
                setPage(1);
              }}
              className="rounded-xl border border-line bg-white px-3 py-2 text-slate-700 outline-none focus:border-blue"
            >
              <option value="">Email: Any</option>
              <option value="available">Email Available</option>
              <option value="unavailable">Email Missing</option>
            </select>

            {/* Phone Filter */}
            <select
              value={phoneStatus}
              onChange={(e) => {
                setPhoneStatus(e.target.value);
                setPage(1);
              }}
              className="rounded-xl border border-line bg-white px-3 py-2 text-slate-700 outline-none focus:border-blue"
            >
              <option value="">Phone: Any</option>
              <option value="available">Phone Available</option>
              <option value="unavailable">Phone Missing</option>
            </select>

            {/* Score Range */}
            <select
              value={scoreRange}
              onChange={(e) => {
                setScoreRange(e.target.value);
                setPage(1);
              }}
              className="rounded-xl border border-line bg-white px-3 py-2 text-slate-700 outline-none focus:border-blue"
            >
              <option value="">Score: Any</option>
              <option value="76-100">Score 76 - 100</option>
              <option value="51-75">Score 51 - 75</option>
              <option value="26-50">Score 26 - 50</option>
              <option value="0-25">Score 0 - 25</option>
            </select>
          </div>

          {/* Active Filter Badges */}
          {(search || selectedCategory || selectedDistrict || websiteStatus || emailStatus || phoneStatus || scoreRange || leadStatus) && (
            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="text-[11px] font-semibold text-muted">Active filters:</span>
              {websiteStatus && (
                <span className="inline-flex items-center gap-1 rounded-md bg-blue/10 px-2 py-0.5 text-[11px] font-semibold text-blue">
                  Website: {websiteStatus}
                  <X size={12} className="cursor-pointer" onClick={() => setWebsiteStatus('')} />
                </span>
              )}
              {selectedDistrict && (
                <span className="inline-flex items-center gap-1 rounded-md bg-blue/10 px-2 py-0.5 text-[11px] font-semibold text-blue">
                  District: {selectedDistrict}
                  <X size={12} className="cursor-pointer" onClick={() => setSelectedDistrict('')} />
                </span>
              )}
              <button onClick={resetFilters} className="text-[11px] font-semibold text-rose-600 hover:underline ml-auto">
                Clear all filters
              </button>
            </div>
          )}
        </section>

        {/* Bulk Action Banner */}
        {selectedIds.length > 0 && (
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-rose-200 bg-rose-50/90 p-4 text-xs shadow-sm animate-in fade-in">
            <div className="flex items-center gap-2.5">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-rose-600 text-xs font-bold text-white shadow-sm">
                {selectedIds.length}
              </span>
              <span className="font-semibold text-rose-950">
                {selectedIds.length} business lead{selectedIds.length > 1 ? 's' : ''} selected
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setRowSelection({})}
                className="rounded-xl border border-rose-200 bg-white px-3.5 py-1.5 font-semibold text-rose-700 hover:bg-rose-100 transition"
              >
                Clear Selection
              </button>
              <button
                type="button"
                onClick={handleBulkDelete}
                disabled={deleting}
                className="flex items-center gap-1.5 rounded-xl bg-rose-600 px-4 py-1.5 font-bold text-white shadow-sm hover:bg-rose-700 transition disabled:opacity-50"
              >
                <Trash2 size={14} />
                <span>{deleting ? 'Deleting...' : `Delete Selected (${selectedIds.length})`}</span>
              </button>
            </div>
          </div>
        )}

        {/* TanStack Table Container */}
        <section className="rounded-2xl border border-line bg-white shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-xs text-muted">Loading business leads...</div>
          ) : leads.length === 0 ? (
            <div className="p-16 text-center">
              <p className="text-sm font-semibold text-slate-700">No businesses match the chosen criteria</p>
              <p className="mt-1 text-xs text-muted">Try clearing some filters or start a new discovery job.</p>
              <button
                onClick={resetFilters}
                className="mt-4 rounded-xl border border-line bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Reset Filters
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[850px] text-left text-xs">
                <thead className="border-b border-line bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-muted">
                  {table.getHeaderGroups().map((headerGroup) => (
                    <tr key={headerGroup.id}>
                      {headerGroup.headers.map((header) => (
                        <th key={header.id} className="px-5 py-3.5">
                          {flexRender(header.column.columnDef.header, header.getContext())}
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody className="divide-y divide-line">
                  {table.getRowModel().rows.map((row) => (
                    <tr key={row.id} className="hover:bg-slate-50 transition">
                      {row.getVisibleCells().map((cell) => (
                        <td key={cell.id} className="px-5 py-3.5">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination Footer */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-t border-line px-5 py-3.5 text-xs text-slate-600 bg-slate-50/50">
            <div>
              Showing <span className="font-bold text-ink">{leads.length > 0 ? (page - 1) * pageSize + 1 : 0}</span> to{' '}
              <span className="font-bold text-ink">{Math.min(page * pageSize, total)}</span> of{' '}
              <span className="font-bold text-ink">{total.toLocaleString()}</span> leads
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] text-muted">Rows per page:</span>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(Number(e.target.value));
                    setPage(1);
                  }}
                  className="rounded-lg border border-line bg-white px-2 py-1 text-xs outline-none focus:border-blue"
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>

              <div className="flex items-center gap-1">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                  className="rounded-lg border border-line bg-white p-1.5 text-slate-600 hover:bg-slate-100 disabled:opacity-40 transition"
                >
                  <ChevronLeft size={16} />
                </button>
                <span className="px-2 text-xs font-semibold text-slate-700">
                  {page} / {totalPages || 1}
                </span>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage(page + 1)}
                  className="rounded-lg border border-line bg-white p-1.5 text-slate-600 hover:bg-slate-100 disabled:opacity-40 transition"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Lead Details Modal */}
        <LeadDetailsModal
          business={selectedLead}
          onClose={() => setSelectedLead(null)}
          onDelete={(deletedId) => {
            setLeads((prev) => prev.filter((l) => l.id !== deletedId));
            setTotal((prev) => Math.max(0, prev - 1));
            setSelectedLead(null);
          }}
          onUpdate={(updated) => {
            setSelectedLead(updated);
            setLeads((prev) => prev.map((l) => (l.id === updated.id ? updated : l)));
          }}
        />
      </main>
    </div>
  );
}
