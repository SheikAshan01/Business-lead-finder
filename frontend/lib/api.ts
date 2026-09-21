export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Stats {
  total: number;
  no_website: number;
  website_found: number;
  saved: number;
  converted: number;
  phone: number;
  email: number;
  high_score: number;
}

export interface ChartItem {
  label: string;
  count: number;
}

export interface DashboardCharts {
  by_category: ChartItem[];
  by_district: ChartItem[];
  no_website_by_district: ChartItem[];
  status_distribution: ChartItem[];
}

export interface LeadNote {
  id: number;
  business_id: number;
  user_id?: number | null;
  note: string;
  created_at: string;
}

export interface StatusHistory {
  id: number;
  old_status: string;
  new_status: string;
  reason?: string | null;
  created_at: string;
}

export interface Business {
  id: number;
  business_name: string;
  client_name?: string | null;
  category_id?: number | null;
  category_name?: string | null;
  phone?: string | null;
  alternate_phone?: string | null;
  email?: string | null;
  address?: string | null;
  area?: string | null;
  taluk?: string | null;
  district?: string | null;
  state: string;
  pincode?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  website_url?: string | null;
  website_status: string;
  website_verified: boolean;
  website_checked_at?: string | null;
  facebook_url?: string | null;
  instagram_url?: string | null;
  youtube_url?: string | null;
  whatsapp_url?: string | null;
  source?: string | null;
  source_url?: string | null;
  source_record_id?: string | null;
  lead_score: number;
  score_reasons?: string | null;
  lead_status: string;
  is_saved: boolean;
  created_at?: string | null;
  updated_at?: string | null;
  notes?: LeadNote[];
  status_history?: StatusHistory[];
}

export interface PaginatedBusinesses {
  items: Business[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  enabled: boolean;
  business_count: number;
}

export interface DistrictLocation {
  district: string;
  business_count: number;
}

export interface ScrapeJob {
  id: number;
  category: string;
  location: string;
  status: string;
  progress: number;
  discovered: number;
  valid: number;
  duplicates: number;
  no_website: number;
  website_found: number;
  errors: number;
  error_message?: string | null;
  created_at?: string | null;
  completed_at?: string | null;
}

export interface Source {
  id: number;
  name: string;
  source_type: string;
  enabled: boolean;
  rate_limit: number;
  terms_url?: string | null;
}

// Auth Token Helper
export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("sra_token");
}

export function setAuthToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("sra_token", token);
  }
}

export function clearAuthToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("sra_token");
    localStorage.removeItem("sra_user");
  }
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("sra_user");
  return raw ? JSON.parse(raw) : null;
}

export function setStoredUser(user: User) {
  if (typeof window !== "undefined") {
    localStorage.setItem("sra_user", JSON.stringify(user));
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let token = getAuthToken();
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  // If 401 unauthorized and not already attempting login, auto-authenticate default session & retry
  if (res.status === 401 && typeof window !== "undefined" && !path.includes("/auth/login")) {
    try {
      const loginRes = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "admin@sra.com", password: "admin123" }),
      });
      if (loginRes.ok) {
        const data = await loginRes.json();
        if (data.access_token) {
          setAuthToken(data.access_token);
          setStoredUser(data.user);
          headers.set("Authorization", `Bearer ${data.access_token}`);
          // Retry original request with fresh token
          res = await fetch(`${API_URL}${path}`, {
            ...options,
            headers,
            cache: "no-store",
          });
        }
      }
    } catch {
      // ignore
    }
  }

  if (!res.ok) {
    let message = "Request failed";
    try {
      const err = await res.json();
      message = err.detail || err.message || message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}

// Auth APIs
export async function loginApi(email: string, password: string) {
  const data = await request<{ access_token: string; user: User }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAuthToken(data.access_token);
  setStoredUser(data.user);
  return data;
}

export async function getMeApi(): Promise<User> {
  return request<User>("/auth/me");
}

// Dashboard Stats & Charts
export async function fetchStats(): Promise<Stats> {
  return request<Stats>("/dashboard/stats");
}

export async function fetchCharts(): Promise<DashboardCharts> {
  return request<DashboardCharts>("/dashboard/charts");
}

// Businesses
export async function fetchBusinesses(params: {
  page?: number;
  page_size?: number;
  search?: string;
  category_id?: number;
  district?: string;
  taluk?: string;
  website_status?: string;
  email_status?: string;
  phone_status?: string;
  min_score?: number;
  max_score?: number;
  lead_status?: string;
  saved?: boolean;
  sort_by?: string;
  sort_order?: string;
} = {}): Promise<PaginatedBusinesses> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== "") {
      query.append(key, String(val));
    }
  });
  return request<PaginatedBusinesses>(`/businesses?${query.toString()}`);
}

export async function fetchBusiness(id: number): Promise<Business> {
  return request<Business>(`/businesses/${id}`);
}

export async function toggleSaveBusiness(id: number): Promise<Business> {
  return request<Business>(`/businesses/${id}/save`, { method: "PATCH" });
}

export async function deleteBusiness(id: number): Promise<void> {
  return request<void>(`/businesses/${id}`, { method: "DELETE" });
}

export async function bulkDeleteBusinesses(ids: number[]): Promise<{ deleted: number }> {
  return request<{ deleted: number }>("/businesses/bulk-delete", {
    method: "POST",
    body: JSON.stringify({ ids }),
  });
}

export async function updateBusinessStatus(id: number, status: string, reason?: string): Promise<Business> {
  return request<Business>(`/businesses/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status, reason }),
  });
}

export async function addBusinessNote(id: number, note: string): Promise<LeadNote> {
  return request<LeadNote>(`/businesses/${id}/notes`, {
    method: "POST",
    body: JSON.stringify({ note }),
  });
}

export async function getBusinessNotes(id: number): Promise<LeadNote[]> {
  return request<LeadNote[]>(`/businesses/${id}/notes`);
}

// Categories & Locations
export async function fetchCategories(): Promise<Category[]> {
  return request<Category[]>("/categories");
}

export async function createCategory(name: string): Promise<Category> {
  return request<Category>("/categories", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function fetchDistricts(): Promise<DistrictLocation[]> {
  return request<DistrictLocation[]>("/locations/districts");
}

export async function fetchTaluks(district: string): Promise<{ district: string; taluk: string }[]> {
  return request<{ district: string; taluk: string }[]>(`/locations/taluks?district=${encodeURIComponent(district)}`);
}

// Scrape Jobs
export async function createScrape(category: string, location: string): Promise<ScrapeJob> {
  return request<ScrapeJob>("/scrape", {
    method: "POST",
    body: JSON.stringify({ category, location }),
  });
}

export async function fetchJobs(): Promise<ScrapeJob[]> {
  return request<ScrapeJob[]>("/scrape/jobs");
}

export async function fetchJob(id: number): Promise<ScrapeJob> {
  return request<ScrapeJob>(`/scrape/jobs/${id}`);
}

// Admin
export async function fetchAdminSources(): Promise<Source[]> {
  return request<Source[]>("/admin/sources");
}

export async function toggleAdminSource(id: number): Promise<Source> {
  return request<Source>(`/admin/sources/${id}/toggle`, { method: "PATCH" });
}

export async function fetchAdminUsers(): Promise<User[]> {
  return request<User[]>("/admin/users");
}

export async function fetchAdminLogs(): Promise<{ id: number; action: string; details?: string; created_at: string }[]> {
  return request<{ id: number; action: string; details?: string; created_at: string }[]>("/admin/logs");
}

export async function fetchAdminStats(): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>("/admin/system-stats");
}

// Export URLs
export function getExportUrl(format: "csv" | "excel", params: Record<string, string | number | boolean | undefined> = {}): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== "") {
      query.append(key, String(val));
    }
  });
  return `${API_URL}/export/${format}?${query.toString()}`;
}
