"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

type HealthResponse = {
  status: string;
};

type HealthState = {
  status: "idle" | "loading" | "ok" | "error";
  message: string;
  checkedAt?: string;
};

const defaultState: HealthState = {
  status: "idle",
  message: "Awaiting check..."
};

export default function StudioStatusPage() {
  const backendUrl = useMemo(
    () => process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000",
    []
  );
  const [health, setHealth] = useState<HealthState>(defaultState);

  const checkHealth = useCallback(async () => {
    setHealth({ status: "loading", message: "Contacting backend..." });
    try {
      const response = await fetch(`${backendUrl}/health`, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`Backend responded ${response.status}`);
      }
      const data = (await response.json()) as HealthResponse;
      setHealth({
        status: data.status === "ok" ? "ok" : "error",
        message: data.status === "ok" ? "Backend is healthy." : "Backend returned unexpected status.",
        checkedAt: new Date().toLocaleTimeString()
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setHealth({ status: "error", message, checkedAt: new Date().toLocaleTimeString() });
    }
  }, [backendUrl]);

  useEffect(() => {
    void checkHealth();
  }, [checkHealth]);

  const badgeClasses = {
    idle: "bg-slate-200 text-slate-600",
    loading: "bg-slate-900 text-white animate-pulse-soft",
    ok: "bg-emerald-500 text-white",
    error: "bg-rose-500 text-white"
  } as const;

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-16">
      <header className="space-y-6 motion-safe:animate-fade-up">
        <div className="inline-flex items-center gap-3 rounded-full border border-white/70 bg-white/60 px-4 py-2 text-xs uppercase tracking-[0.3em] text-slate-500 backdrop-blur">
          Studio diagnostics
        </div>
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-4">
            <h1 className="font-display text-4xl leading-tight text-slate-900 sm:text-5xl">
              Local backend status for your editing studio.
            </h1>
            <p className="max-w-2xl text-lg text-slate-600">
              Use this page to verify the frontend-backend handshake before starting local generation
              or edit runs.
            </p>
          </div>
          <div className="rounded-3xl border border-white/70 bg-white/70 px-6 py-4 shadow-soft backdrop-blur">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Backend URL</p>
            <p className="mt-2 font-mono text-sm text-slate-800">{backendUrl}</p>
          </div>
        </div>
      </header>

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr] motion-safe:animate-fade-up">
        <div className="rounded-3xl border border-white/70 bg-white/70 p-8 shadow-soft backdrop-blur">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="font-display text-2xl text-slate-900">Backend health</h2>
              <p className="mt-2 text-sm text-slate-500">
                Live signal from FastAPI. Keep this green before starting model runs.
              </p>
            </div>
            <span
              className={`rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] ${
                badgeClasses[health.status]
              }`}
            >
              {health.status}
            </span>
          </div>
          <div className="mt-6 space-y-4">
            <p className="text-lg text-slate-700">{health.message}</p>
            {health.checkedAt ? (
              <p className="text-sm text-slate-500">Last checked: {health.checkedAt}</p>
            ) : null}
            <button
              type="button"
              onClick={checkHealth}
              className="rounded-full border border-slate-900 px-5 py-2 text-sm font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white"
            >
              Refresh status
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-6">
          <div className="rounded-3xl border border-white/70 bg-white/70 p-6 shadow-soft backdrop-blur">
            <h3 className="font-display text-xl text-slate-900">Diagnostics lane</h3>
            <p className="mt-2 text-sm text-slate-500">
              Reserved for future side-by-side compare tooling. Sprint 1 keeps this route focused on
              backend verification rather than primary editing work.
            </p>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <div className="flex items-center justify-between">
                <span>Backend health</span>
                <span className="rounded-full bg-slate-200 px-3 py-1 text-xs uppercase text-slate-600">
                  placeholder
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Route role</span>
                <span className="rounded-full bg-slate-200 px-3 py-1 text-xs uppercase text-slate-600">
                  placeholder
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/70 bg-white/70 p-6 shadow-soft backdrop-blur">
            <h3 className="font-display text-xl text-slate-900">Pipeline checklist</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>1. Confirm backend health check is green.</li>
              <li>2. Start the fast-check backend profile when iterating locally.</li>
              <li>3. Return to `/chat` for generate or edit work.</li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
}
