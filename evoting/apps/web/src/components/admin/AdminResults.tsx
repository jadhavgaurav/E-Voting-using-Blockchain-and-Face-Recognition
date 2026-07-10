"use client";

import { useCallback, useEffect, useState } from "react";
import { admin, type ElectionOut, type ElectionResults } from "@/lib/api";
import { errorMessage } from "@/lib/format";
import { Alert, Badge, Button, Card, Select, Spinner } from "@/components/ui";

export function AdminResults({ initialElectionId }: { initialElectionId: string | null }) {
  const [elections, setElections] = useState<ElectionOut[]>([]);
  const [selectedId, setSelectedId] = useState<string>(initialElectionId ?? "");
  const [data, setData] = useState<ElectionResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    admin.elections().then(setElections).catch((err) => setError(errorMessage(err)));
  }, []);

  useEffect(() => {
    if (initialElectionId) setSelectedId(initialElectionId);
  }, [initialElectionId]);

  const load = useCallback((id: string) => {
    if (!id) {
      setData(null);
      return;
    }
    setLoading(true);
    admin
      .electionResults(id)
      .then((res) => {
        setData(res);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load(selectedId);
  }, [selectedId, load]);

  async function closeElection() {
    if (!selectedId) return;
    setError(null);
    try {
      await admin.closeElection(selectedId);
      load(selectedId);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  const maxVotes = data ? Math.max(1, ...data.results.map((r) => r.votes)) : 1;

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-700">Election</span>
          <Select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="min-w-64"
          >
            <option value="">Select an election…</option>
            {elections.map((el) => (
              <option key={el.id} value={el.id}>
                {el.name}
              </option>
            ))}
          </Select>
        </label>
        {selectedId && (
          <Button variant="danger" size="sm" onClick={closeElection}>
            Close election
          </Button>
        )}
      </div>

      {error && (
        <div className="mt-4">
          <Alert tone="error">{error}</Alert>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-16">
          <Spinner className="h-6 w-6 text-indigo-600" />
        </div>
      ) : data ? (
        <Card className="mt-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">{data.name}</h3>
              <p className="text-sm text-slate-500">
                {data.total_votes} vote{data.total_votes === 1 ? "" : "s"} · source:{" "}
                {data.source}
              </p>
            </div>
            <Badge tone="info">{data.status}</Badge>
          </div>

          <ul className="mt-6 space-y-4">
            {data.results.map((row) => {
              const pct = data.total_votes
                ? Math.round((row.votes / data.total_votes) * 100)
                : 0;
              return (
                <li key={row.candidate_id}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-slate-800">
                      {row.name}{" "}
                      <span className="text-slate-400">({row.party})</span>
                    </span>
                    <span className="tabular-nums text-slate-600">
                      {row.votes} · {pct}%
                    </span>
                  </div>
                  <div className="mt-1 h-3 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-indigo-600 transition-all"
                      style={{ width: `${(row.votes / maxVotes) * 100}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        </Card>
      ) : (
        <p className="mt-6 text-sm text-slate-600">
          Select an election to view its live tally.
        </p>
      )}
    </div>
  );
}
