"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Plus, Trash2 } from "lucide-react";
import {
  admin,
  type ElectionOut,
  type CandidateInput,
} from "@/lib/api";
import { errorMessage, formatDateTime } from "@/lib/format";
import { Alert, Badge, Button, Card, Field, Input, Spinner } from "@/components/ui";
import { AssemblyPicker } from "@/components/AssemblyPicker";

interface CandidateDraft extends CandidateInput {
  key: string;
}

function emptyCandidate(): CandidateDraft {
  return { key: crypto.randomUUID(), name: "", party: "", symbol_url: "" };
}

/** Convert a `datetime-local` value to an ISO string, or null if empty/invalid. */
function toIso(local: string): string | null {
  if (!local) return null;
  const date = new Date(local);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

export function AdminElections({
  onSelectResults,
}: {
  onSelectResults: (electionId: string) => void;
}) {
  const [elections, setElections] = useState<ElectionOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [electionType, setElectionType] = useState("assembly");
  const [assemblyId, setAssemblyId] = useState("");
  const [startAt, setStartAt] = useState("");
  const [endAt, setEndAt] = useState("");
  const [candidates, setCandidates] = useState<CandidateDraft[]>([
    emptyCandidate(),
    emptyCandidate(),
  ]);
  const [formError, setFormError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [createdName, setCreatedName] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    admin
      .elections()
      .then((data) => {
        setElections(data);
        setListError(null);
      })
      .catch((err) => setListError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  function updateCandidate(key: string, field: keyof CandidateInput, val: string) {
    setCandidates((prev) =>
      prev.map((c) => (c.key === key ? { ...c, [field]: val } : c)),
    );
  }

  function resetForm() {
    setName("");
    setElectionType("assembly");
    setAssemblyId("");
    setStartAt("");
    setEndAt("");
    setCandidates([emptyCandidate(), emptyCandidate()]);
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setCreatedName(null);

    const startIso = toIso(startAt);
    const endIso = toIso(endAt);
    const cleanCandidates = candidates
      .map((c) => ({
        name: c.name.trim(),
        party: c.party.trim(),
        symbol_url: c.symbol_url?.trim() || undefined,
      }))
      .filter((c) => c.name.length > 0);

    if (!name.trim()) return setFormError("Enter an election name.");
    if (!assemblyId) return setFormError("Select an assembly constituency.");
    if (!startIso || !endIso) return setFormError("Enter valid start and end times.");
    if (new Date(endIso) <= new Date(startIso)) {
      return setFormError("End time must be after the start time.");
    }
    if (cleanCandidates.length < 2) {
      return setFormError("Add at least two candidates with a name.");
    }

    setCreating(true);
    try {
      const created = await admin.createElection({
        name: name.trim(),
        election_type: electionType,
        assembly_constituency_id: assemblyId,
        start_at: startIso,
        end_at: endIso,
        candidates: cleanCandidates,
      });
      setCreatedName(created.name);
      resetForm();
      load();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setCreating(false);
    }
  }

  async function closeElection(id: string) {
    try {
      await admin.closeElection(id);
      load();
    } catch (err) {
      setListError(errorMessage(err));
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      {/* Create form */}
      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Create election</h2>
        <form onSubmit={handleCreate} className="mt-4 space-y-4" noValidate>
          {createdName && (
            <Alert tone="success">Created election “{createdName}”.</Alert>
          )}
          {formError && <Alert tone="error">{formError}</Alert>}

          <Field label="Name" htmlFor="el-name">
            <Input id="el-name" value={name} onChange={(e) => setName(e.target.value)} />
          </Field>
          <Field label="Election type" htmlFor="el-type">
            <Input
              id="el-type"
              value={electionType}
              onChange={(e) => setElectionType(e.target.value)}
            />
          </Field>

          <AssemblyPicker value={assemblyId} onChange={setAssemblyId} idPrefix="el" />

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Start" htmlFor="el-start">
              <Input
                id="el-start"
                type="datetime-local"
                value={startAt}
                onChange={(e) => setStartAt(e.target.value)}
              />
            </Field>
            <Field label="End" htmlFor="el-end">
              <Input
                id="el-end"
                type="datetime-local"
                value={endAt}
                onChange={(e) => setEndAt(e.target.value)}
              />
            </Field>
          </div>

          <div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">
                Candidates (min 2)
              </span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setCandidates((p) => [...p, emptyCandidate()])}
              >
                <Plus className="h-4 w-4" aria-hidden /> Add
              </Button>
            </div>
            <ul className="mt-3 space-y-3">
              {candidates.map((c, index) => (
                <li
                  key={c.key}
                  className="rounded-lg border border-slate-200 p-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Candidate {index + 1}
                    </span>
                    {candidates.length > 2 && (
                      <button
                        type="button"
                        onClick={() =>
                          setCandidates((p) => p.filter((x) => x.key !== c.key))
                        }
                        className="text-slate-400 hover:text-rose-600"
                        aria-label={`Remove candidate ${index + 1}`}
                      >
                        <Trash2 className="h-4 w-4" aria-hidden />
                      </button>
                    )}
                  </div>
                  <div className="mt-2 grid gap-2 sm:grid-cols-2">
                    <Input
                      placeholder="Name"
                      aria-label={`Candidate ${index + 1} name`}
                      value={c.name}
                      onChange={(e) => updateCandidate(c.key, "name", e.target.value)}
                    />
                    <Input
                      placeholder="Party"
                      aria-label={`Candidate ${index + 1} party`}
                      value={c.party}
                      onChange={(e) => updateCandidate(c.key, "party", e.target.value)}
                    />
                  </div>
                  <Input
                    className="mt-2"
                    placeholder="Symbol URL (optional)"
                    aria-label={`Candidate ${index + 1} symbol URL`}
                    value={c.symbol_url ?? ""}
                    onChange={(e) => updateCandidate(c.key, "symbol_url", e.target.value)}
                  />
                </li>
              ))}
            </ul>
          </div>

          <Button type="submit" loading={creating} className="w-full">
            Create election
          </Button>
        </form>
      </Card>

      {/* List */}
      <div>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Elections</h2>
          <Button variant="outline" size="sm" onClick={load}>
            Refresh
          </Button>
        </div>
        {listError && (
          <div className="mt-4">
            <Alert tone="error">{listError}</Alert>
          </div>
        )}
        {loading ? (
          <div className="flex justify-center py-16">
            <Spinner className="h-6 w-6 text-indigo-600" />
          </div>
        ) : elections.length === 0 ? (
          <p className="mt-4 text-sm text-slate-600">No elections yet.</p>
        ) : (
          <ul className="mt-4 space-y-3">
            {elections.map((election) => (
              <li key={election.id}>
                <Card>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-slate-900">{election.name}</h3>
                        <Badge tone="info">{election.status}</Badge>
                        {election.result_published && (
                          <Badge tone="success">Published</Badge>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-slate-500">
                        {formatDateTime(election.start_at)} —{" "}
                        {formatDateTime(election.end_at)}
                      </p>
                      <p className="mt-1 text-xs text-slate-400">
                        Chain election #{election.chain_election_id} · {election.election_type}
                      </p>
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onSelectResults(election.id)}
                    >
                      View results
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => closeElection(election.id)}
                    >
                      Close
                    </Button>
                  </div>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
