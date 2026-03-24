"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { Execution } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";

const API = "";  // proxied via next.config.ts rewrites

function elapsed(ex: Execution): string {
  if (!ex.started_at) return "—";
  const start = new Date(ex.started_at).getTime();
  const end   = ex.completed_at ? new Date(ex.completed_at).getTime() : Date.now();
  const s     = Math.floor((end - start) / 1000);
  if (s < 60) return `${s}s`;
  return `${Math.floor(s / 60)}m ${s % 60}s`;
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  if (diff < 60_000)   return "just now";
  if (diff < 3600_000) return `${Math.floor(diff / 60_000)}m ago`;
  return `${Math.floor(diff / 3600_000)}h ago`;
}

function currentPhaseLabel(ex: Execution): string {
  if (!ex.current_phase) return "—";
  const labels: Record<string, string> = {
    research: "Research", planning: "Planning", execution: "Execution",
    review: "Review", testing: "Testing", deployment: "Deployment",
  };
  return labels[ex.current_phase] ?? ex.current_phase;
}

export default function Dashboard() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading]       = useState(true);
  const [showForm, setShowForm]     = useState(false);
  const [feature, setFeature]       = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function fetchAll() {
    try {
      const r = await fetch(`${API}/api/executions`);
      if (r.ok) setExecutions(await r.json());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAll();
    const t = setInterval(fetchAll, 3000);
    return () => clearInterval(t);
  }, []);

  async function startExecution() {
    if (!feature.trim()) return;
    setSubmitting(true);
    try {
      const r = await fetch(`${API}/api/executions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ feature_request: feature.trim() }),
      });
      if (r.ok) {
        const { id } = await r.json();
        setShowForm(false);
        setFeature("");
        window.location.href = `/executions/${id}`;
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-zinc-100">Executions</h1>
          <p className="text-sm text-zinc-500 mt-0.5">
            Automated development pipeline runs
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-zinc-100 text-zinc-900 rounded hover:bg-white transition-colors"
        >
          <span>+</span> New execution
        </button>
      </div>

      {/* New execution form */}
      {showForm && (
        <div className="border border-zinc-700 rounded bg-zinc-900 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-zinc-300">New execution</h2>
            <button
              onClick={() => setShowForm(false)}
              className="text-zinc-500 hover:text-zinc-300 text-xs"
            >
              ✕ cancel
            </button>
          </div>
          <div className="space-y-2">
            <label className="text-xs text-zinc-500 block">Feature request</label>
            <textarea
              value={feature}
              onChange={e => setFeature(e.target.value)}
              placeholder="e.g. Add JWT authentication with refresh tokens"
              rows={3}
              className="w-full bg-zinc-950 border border-zinc-700 rounded px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 resize-none font-mono"
              autoFocus
            />
          </div>
          <button
            onClick={startExecution}
            disabled={submitting || !feature.trim()}
            className="px-4 py-2 text-sm font-medium bg-zinc-100 text-zinc-900 rounded hover:bg-white transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {submitting ? "Starting…" : "Start workflow →"}
          </button>
        </div>
      )}

      {/* Executions table */}
      {loading ? (
        <div className="text-sm text-zinc-600 font-mono">Loading…</div>
      ) : executions.length === 0 ? (
        <div className="border border-dashed border-zinc-800 rounded p-12 text-center">
          <p className="text-zinc-600 text-sm">No executions yet.</p>
          <p className="text-zinc-700 text-xs mt-1">
            Click &ldquo;New execution&rdquo; to start the workflow.
          </p>
        </div>
      ) : (
        <div className="border border-zinc-800 rounded overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/50">
                <th className="text-left px-4 py-3 text-xs font-medium text-zinc-500 w-20">ID</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-zinc-500">Feature</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-zinc-500 w-28">Status</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-zinc-500 w-28">Phase</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-zinc-500 w-20">Time</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-zinc-500 w-24">Started</th>
                <th className="w-12" />
              </tr>
            </thead>
            <tbody>
              {executions.map((ex, i) => (
                <tr
                  key={ex.id}
                  className={`border-b border-zinc-800/50 last:border-0 hover:bg-zinc-900/40 transition-colors ${
                    i % 2 === 0 ? "" : "bg-zinc-900/20"
                  }`}
                >
                  <td className="px-4 py-3">
                    <span className="font-mono text-xs text-zinc-500">{ex.id}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-zinc-200 truncate block max-w-sm">
                      {ex.feature_request}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={ex.status} />
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-zinc-500 font-mono">
                      {currentPhaseLabel(ex)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-mono text-zinc-500">
                      {elapsed(ex)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-zinc-600">
                      {timeAgo(ex.created_at)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/executions/${ex.id}`}
                      className="text-xs text-zinc-500 hover:text-zinc-200 transition-colors"
                    >
                      view →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
