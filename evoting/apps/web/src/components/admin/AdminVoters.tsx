"use client";

import { useCallback, useEffect, useState } from "react";
import { admin, type VoterOut, type VoterStatus } from "@/lib/api";
import { errorMessage, formatDateTime } from "@/lib/format";
import { Alert, Badge, Button, Card, Spinner } from "@/components/ui";
import { cn } from "@/lib/cn";

const FILTERS: VoterStatus[] = ["pending", "accepted", "rejected"];

const STATUS_TONE: Record<VoterStatus, "success" | "warning" | "danger"> = {
  accepted: "success",
  pending: "warning",
  rejected: "danger",
};

export function AdminVoters() {
  const [filter, setFilter] = useState<VoterStatus>("pending");
  const [voters, setVoters] = useState<VoterOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pendingId, setPendingId] = useState<string | null>(null);

  const load = useCallback((status: VoterStatus) => {
    setLoading(true);
    admin
      .voters(status)
      .then((data) => {
        setVoters(data);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load(filter);
  }, [filter, load]);

  async function setStatus(id: string, status: "accepted" | "rejected") {
    setPendingId(id);
    setError(null);
    try {
      await admin.setVoterStatus(id, status);
      load(filter);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setPendingId(null);
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1">
          {FILTERS.map((status) => (
            <button
              key={status}
              type="button"
              onClick={() => setFilter(status)}
              className={cn(
                "rounded-md px-3 py-1.5 text-sm font-medium capitalize transition-colors",
                filter === status
                  ? "bg-indigo-600 text-white"
                  : "text-slate-600 hover:bg-slate-100",
              )}
            >
              {status}
            </button>
          ))}
        </div>
        <Button variant="outline" size="sm" onClick={() => load(filter)}>
          Refresh
        </Button>
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
      ) : voters.length === 0 ? (
        <p className="mt-4 text-sm text-slate-600">No {filter} voters.</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {voters.map((voter) => (
            <li key={voter.id}>
              <Card className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-slate-900">{voter.full_name}</h3>
                    <Badge tone={STATUS_TONE[voter.status]}>{voter.status}</Badge>
                  </div>
                  <p className="mt-1 text-sm text-slate-500">{voter.email}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    Registered {formatDateTime(voter.created_at)}
                  </p>
                </div>
                {voter.status === "pending" && (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      loading={pendingId === voter.id}
                      onClick={() => setStatus(voter.id, "accepted")}
                    >
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      disabled={pendingId === voter.id}
                      onClick={() => setStatus(voter.id, "rejected")}
                    >
                      Reject
                    </Button>
                  </div>
                )}
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
