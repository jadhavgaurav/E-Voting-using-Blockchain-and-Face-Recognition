"use client";

import { useState } from "react";
import { useRequireAuth } from "@/lib/use-require-auth";
import { Spinner } from "@/components/ui";
import { cn } from "@/lib/cn";
import { AdminElections } from "@/components/admin/AdminElections";
import { AdminVoters } from "@/components/admin/AdminVoters";
import { AdminResults } from "@/components/admin/AdminResults";

type Tab = "elections" | "voters" | "results";

const TABS: { id: Tab; label: string }[] = [
  { id: "elections", label: "Elections" },
  { id: "voters", label: "Voters" },
  { id: "results", label: "Results" },
];

export default function AdminPage() {
  const { ready, allowed } = useRequireAuth("admin");
  const [tab, setTab] = useState<Tab>("elections");
  const [resultsElectionId, setResultsElectionId] = useState<string | null>(null);

  if (!ready || !allowed) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-6 w-6 text-indigo-600" />
      </div>
    );
  }

  function showResults(id: string) {
    setResultsElectionId(id);
    setTab("results");
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="text-3xl font-bold text-slate-900">Admin console</h1>
      <p className="mt-2 text-slate-600">
        Manage elections, approve voters and monitor live results.
      </p>

      <div
        className="mt-8 flex gap-1 border-b border-slate-200"
        role="tablist"
        aria-label="Admin sections"
      >
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              "-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors",
              tab === t.id
                ? "border-indigo-600 text-indigo-700"
                : "border-transparent text-slate-500 hover:text-slate-800",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="mt-8">
        {tab === "elections" && <AdminElections onSelectResults={showResults} />}
        {tab === "voters" && <AdminVoters />}
        {tab === "results" && <AdminResults initialElectionId={resultsElectionId} />}
      </div>
    </div>
  );
}
