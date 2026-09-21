'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Lock, Mail, Shield, Sparkles } from 'lucide-react';
import { loginApi } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('admin@sra.com');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await loginApi(email, password);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#070c14] px-4 py-12 text-white">
      <div className="w-full max-w-md space-y-8 animate-rise">
        {/* Brand Banner */}
        <div className="text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue to-cyan shadow-xl shadow-blue/25">
            <span className="text-xl font-bold tracking-wider text-white">SRA</span>
          </div>
          <p className="mt-4 text-xs font-bold uppercase tracking-[0.25em] text-cyan">SRA Software Solutions</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-white">Business Lead Finder</h1>
          <p className="mt-2 text-xs text-slate-400">Find. Verify. Connect. Discover Tamil Nadu commercial opportunities.</p>
        </div>

        {/* Login Card */}
        <div className="rounded-2xl border border-white/10 bg-[#0f172a] p-8 shadow-2xl">
          <form onSubmit={handleLogin} className="space-y-5">
            {error && (
              <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400" htmlFor="email">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3.5 text-slate-500" size={16} />
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 py-3 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan transition"
                  placeholder="admin@sra.com"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400" htmlFor="password">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3.5 text-slate-500" size={16} />
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 py-3 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan transition"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="group flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue to-cyan py-3 text-sm font-bold text-white shadow-lg shadow-blue/25 hover:opacity-95 disabled:opacity-50 transition"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
              <ArrowRight size={16} className="group-hover:translate-x-0.5 transition" />
            </button>
          </form>

          {/* Quick Demo Credentials */}
          <div className="mt-6 rounded-xl border border-white/5 bg-white/5 p-3.5 text-xs text-slate-400 space-y-1.5">
            <div className="flex items-center gap-1.5 font-semibold text-slate-300">
              <Shield size={13} className="text-cyan" />
              <span>Default Credentials</span>
            </div>
            <div className="flex justify-between text-[11px]">
              <span>Admin: <strong className="text-white">admin@sra.com</strong></span>
              <span>Pass: <strong className="text-white">admin123</strong></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
