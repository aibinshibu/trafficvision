"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../lib/auth-context";
import ErrorMessage from "../components/ErrorMessage";
import { canAccess, DEFAULT_HOME } from "../lib/rbac";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Only follow ?next= if it is an internal route the signed-in role may open
  const destinationFor = (role: Parameters<typeof canAccess>[0]) => {
    const next = typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("next") : null;
    if (next && next.startsWith("/") && !next.startsWith("//") && canAccess(role, next)) return next;
    return DEFAULT_HOME;
  };

  const { role: currentRole } = useAuth();
  useEffect(() => {
    if (!isLoading && isAuthenticated) router.replace(destinationFor(currentRole));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoading, isAuthenticated, currentRole]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // QA Validation: AUTH-004 (Empty fields)
    if (!email.trim() || !password.trim()) {
      setError("Please fill in both email and password fields.");
      return;
    }

    // QA Validation: AUTH-003 (Invalid email)
    if (!email.includes("@") || !email.includes(".")) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Invalid credentials. Please verify your email and password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] flex items-center justify-center p-4 selection:bg-cyan-500/30 selection:text-cyan-200">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl backdrop-blur-xl">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-cyan-600 to-indigo-600 text-2xl shadow-lg shadow-cyan-500/20 mb-3">
            🚦
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white">
            TrafficVision <span className="text-cyan-400">AI</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">Smart Traffic Command Center & Prediction</p>
        </div>

        {error && (
          <div className="mb-5">
            <ErrorMessage message={error} onDismiss={() => setError(null)} />
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com" autoComplete="email"
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Password
              </label>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-[11px] text-slate-400 hover:text-slate-200"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password" autoComplete="current-password"
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:brightness-110 py-3 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin text-base">🔄</span>
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Sign In to Console</span>
            )}
          </button>
        </form>

        {/* Register Link */}
        <div className="mt-6 text-center text-xs text-slate-400">
          Need a commuter account?{" "}
          <Link href="/register" className="font-semibold text-cyan-400 hover:underline">
            Register here
          </Link>
        </div>
      </div>
    </div>
  );
}
