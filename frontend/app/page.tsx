"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { Execution } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";
import { Card, CardContent } from "@/components/Card";
import { Button, IconButton } from "@/components/Button";
import { SearchBar } from "@/components/SearchBar";
import { FilterDropdown } from "@/components/FilterDropdown";

const API = "";

function elapsed(ex: Execution): string {
  if (!ex.started_at) return "—";
  const start = new Date(ex.started_at).getTime();
  const end = ex.completed_at ? new Date(ex.completed_at).getTime() : Date.now();
  const s = Math.floor((end - start) / 1000);
  if (s < 60) return `${s}s`;
  return `${Math.floor(s / 60)}m ${s % 60}s`;
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3600_000) return `${Math.floor(diff / 60_000)}m ago`;
  return `${Math.floor(diff / 3600_000)}h ago`;
}

function currentPhaseLabel(ex: Execution): string {
  if (!ex.current_phase) return "—";
  const labels: Record<string, string> = {
    research: "Research",
    planning: "Planning",
    execution: "Execution",
    review: "Review",
    testing: "Testing",
    deployment: "Deployment",
  };
  return labels[ex.current_phase] ?? ex.current_phase;
}

function PlusIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  );
}

function ArrowRightIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
      />
    </svg>
  );
}

function EmptyState() {
  return (
    <Card className="border-dashed">
      <CardContent className="py-16 flex flex-col items-center justify-center text-center">
        <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-6">
          <svg
            className="w-8 h-8 text-zinc-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-zinc-300 mb-2">No executions yet</h3>
        <p className="text-sm text-zinc-500 mb-6 max-w-sm">
          Start your first automated development workflow and watch AI agents build, test, and deploy your
          code.
        </p>
        <Button>
          <PlusIcon />
          New Execution
        </Button>
      </CardContent>
    </Card>
  );
}

function ExecutionCard({ execution }: { execution: Execution }) {
  return (
    <Link href={`/executions/${execution.id}`} className="block">
      <Card hover className="group">
        <CardContent className="py-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <StatusBadge status={execution.status} />
                <span className="text-xs text-zinc-600 font-mono">{execution.id}</span>
              </div>
              <p className="text-sm text-zinc-200 truncate mb-1">{execution.feature_request}</p>
              <div className="flex items-center gap-4 text-xs text-zinc-500">
                <span className="font-mono">{currentPhaseLabel(execution)}</span>
                <span>•</span>
                <span>{elapsed(execution)}</span>
                <span>•</span>
                <span>{timeAgo(execution.created_at)}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 text-zinc-500 group-hover:text-zinc-300 transition-colors">
              <span className="text-sm">View</span>
              <ArrowRightIcon />
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function LoadingSkeleton() {
  return (
    <Card>
      <CardContent className="py-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className="h-5 w-20 rounded-full skeleton" />
              <div className="h-4 w-16 rounded skeleton" />
            </div>
            <div className="h-4 w-3/4 rounded skeleton mb-2" />
            <div className="flex items-center gap-4">
              <div className="h-3 w-20 rounded skeleton" />
              <div className="h-3 w-16 rounded skeleton" />
              <div className="h-3 w-24 rounded skeleton" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [feature, setFeature] = useState("");
  const [githubRepo, setGithubRepo] = useState("");
  const [workspaceMode, setWorkspaceMode] = useState("sandbox");
  const [submitting, setSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  async function fetchAll() {
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.set("search", searchQuery);
      if (statusFilter) params.set("status", statusFilter);
      const queryString = params.toString();
      const url = `${API}/api/executions${queryString ? `?${queryString}` : ""}`;
      const r = await fetch(url);
      if (r.ok) setExecutions(await r.json());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setLoading(true);
    fetchAll();
    const t = setInterval(fetchAll, 5000);
    return () => clearInterval(t);
  }, [searchQuery, statusFilter]);

  async function startExecution() {
    if (!feature.trim()) return;
    setSubmitting(true);
    try {
      const r = await fetch(`${API}/api/executions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          feature_request: feature.trim(),
          github_repo: githubRepo.trim() || null,
          workspace_mode: workspaceMode,
        }),
      });
      if (r.ok) {
        const { id } = await r.json();
        setShowForm(false);
        setFeature("");
        setGithubRepo("");
        setWorkspaceMode("sandbox");
        window.location.href = `/executions/${id}`;
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">Executions</h1>
          <p className="text-sm text-zinc-500 mt-1">Automated development pipeline runs</p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <PlusIcon />
          New execution
        </Button>
      </div>

      {/* Search and filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search executions..."
          />
        </div>
        <div className="w-48">
          <FilterDropdown
            label=""
            value={statusFilter}
            onChange={setStatusFilter}
            options={[
              { value: "running", label: "Running" },
              { value: "completed", label: "Completed" },
              { value: "failed", label: "Failed" },
              { value: "cancelled", label: "Cancelled" },
            ]}
            placeholder="All statuses"
          />
        </div>
      </div>

      {/* New execution form */}
      {showForm && (
        <Card className="animate-scale-in">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-zinc-300">New execution</h2>
              <button
                onClick={() => setShowForm(false)}
                className="text-zinc-500 hover:text-zinc-300 text-sm transition-colors"
              >
                Cancel
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-zinc-500 block mb-1.5">Feature request</label>
                <textarea
                  value={feature}
                  onChange={(e) => setFeature(e.target.value)}
                  placeholder="e.g. Add JWT authentication with refresh tokens"
                  rows={3}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 resize-none transition-colors"
                  autoFocus
                />
              </div>
              <div>
                <label className="text-xs text-zinc-500 block mb-1.5">GitHub Repository (optional)</label>
                <input
                  type="text"
                  value={githubRepo}
                  onChange={(e) => setGithubRepo(e.target.value)}
                  placeholder="e.g. owner/repo"
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-colors"
                />
              </div>
              <div>
                <label className="text-xs text-zinc-500 block mb-1.5">Workspace Mode</label>
                <select
                  value={workspaceMode}
                  onChange={(e) => setWorkspaceMode(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2.5 text-sm text-zinc-100 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-colors"
                >
                  <option value="sandbox">Sandbox (local output directory)</option>
                  <option value="git">Git (clone repo, create PR)</option>
                </select>
              </div>
              <div className="flex justify-end gap-3">
                <Button variant="ghost" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
                <Button onClick={startExecution} loading={submitting} disabled={!feature.trim()}>
                  Start workflow
                  <ArrowRightIcon />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Executions list */}
      {loading ? (
        <div className="space-y-3 animate-stagger">
          <LoadingSkeleton />
          <LoadingSkeleton />
          <LoadingSkeleton />
        </div>
      ) : executions.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="space-y-3 animate-stagger">
          {executions.map((ex) => (
            <ExecutionCard key={ex.id} execution={ex} />
          ))}
        </div>
      )}
    </div>
  );
}
