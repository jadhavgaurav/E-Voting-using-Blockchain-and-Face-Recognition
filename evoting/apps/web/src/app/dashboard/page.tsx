"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ScanFace, ReceiptText, Vote } from "lucide-react";
import {
  auth,
  enrollment,
  voting,
  type VoterOut,
  type VoterStatus,
  type EnrollmentStatus,
  type ElectionOut,
} from "@/lib/api";
import { useRequireAuth } from "@/lib/use-require-auth";
import { errorMessage, formatDateTime } from "@/lib/format";
import { Alert, Badge, Button, Card, Spinner } from "@/components/ui";

const STATUS_TONE: Record<VoterStatus, "success" | "warning" | "danger"> = {
  accepted: "success",
  pending: "warning",
  rejected: "danger",
};

const STATUS_LABEL: Record<VoterStatus, string> = {
  accepted: "Approved",
  pending: "Pending approval",
  rejected: "Rejected",
};

export default function DashboardPage() {
  const { ready, allowed } = useRequireAuth("voter");
  const [voter, setVoter] = useState<VoterOut | null>(null);
  const [enroll, setEnroll] = useState<EnrollmentStatus | null>(null);
  const [elections, setElections] = useState<ElectionOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!allowed) return;
    let active = true;
    setLoading(true);
    Promise.all([auth.me(), enrollment.status(), voting.elections()])
      .then(([me, status, els]) => {
        if (!active) return;
        setVoter(me);
        setEnroll(status);
        setElections(els);
        setError(null);
      })
      .catch((err) => active && setError(errorMessage(err)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [allowed]);

  if (!ready || !allowed) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-6 w-6 text-indigo-600" />
      </div>
    );
  }

  const isAccepted = voter?.status === "accepted";
  const isEnrolled = Boolean(enroll?.enrolled);

  function voteBlockedReason(): string | null {
    if (!isAccepted) return "Your registration must be approved before you can vote.";
    if (!isEnrolled) return "Enroll your face before voting.";
    return null;
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      <h1 className="text-3xl font-bold text-slate-900">Your dashboard</h1>

      {error && (
        <div className="mt-6">
          <Alert tone="error">{error}</Alert>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-24">
          <Spinner className="h-6 w-6 text-indigo-600" />
        </div>
      ) : (
        <>
          {/* Status cards */}
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <Card>
              <p className="text-sm font-medium text-slate-500">Account</p>
              <p className="mt-1 text-lg font-semibold text-slate-900">
                {voter?.full_name}
              </p>
              <p className="text-sm text-slate-500">{voter?.email}</p>
              <div className="mt-3">
                {voter && (
                  <Badge tone={STATUS_TONE[voter.status]}>
                    {STATUS_LABEL[voter.status]}
                  </Badge>
                )}
              </div>
              {voter?.blockchain_address && (
                <p className="mt-3 break-all font-mono text-xs text-slate-500">
                  {voter.blockchain_address}
                </p>
              )}
            </Card>

            <Card>
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-500">Face enrollment</p>
                <ScanFace className="h-5 w-5 text-slate-400" aria-hidden />
              </div>
              <div className="mt-2">
                {isEnrolled ? (
                  <Badge tone="success">Enrolled</Badge>
                ) : (
                  <Badge tone="warning">Not enrolled</Badge>
                )}
              </div>
              <p className="mt-2 text-sm text-slate-600">
                {isEnrolled
                  ? "Your reference photo is on file. You are ready to verify at vote time."
                  : "Capture a reference photo so we can confirm your identity when you vote."}
              </p>
              <Link
                href="/enroll"
                className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-indigo-600 hover:underline"
              >
                {isEnrolled ? "Re-enroll face" : "Enroll your face"}
              </Link>
            </Card>
          </div>

          {/* Quick links */}
          <div className="mt-4 flex flex-wrap gap-3">
            <Link
              href="/receipts"
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              <ReceiptText className="h-4 w-4" aria-hidden /> View receipts
            </Link>
          </div>

          {/* Elections */}
          <section className="mt-10">
            <h2 className="text-xl font-bold text-slate-900">Active elections</h2>
            {elections.length === 0 ? (
              <p className="mt-3 text-sm text-slate-600">
                There are no elections available for you right now.
              </p>
            ) : (
              <ul className="mt-4 space-y-3">
                {elections.map((election) => {
                  const blocked = voteBlockedReason();
                  return (
                    <li key={election.id}>
                      <Card className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-slate-900">
                              {election.name}
                            </h3>
                            <Badge tone="info">{election.status}</Badge>
                          </div>
                          <p className="mt-1 text-sm text-slate-500">
                            {formatDateTime(election.start_at)} —{" "}
                            {formatDateTime(election.end_at)}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          {blocked ? (
                            <>
                              <span className="text-xs text-slate-500">{blocked}</span>
                              <Button disabled title={blocked}>
                                <Vote className="h-4 w-4" aria-hidden /> Vote
                              </Button>
                            </>
                          ) : (
                            <Link
                              href={`/vote/${election.id}`}
                              className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
                            >
                              <Vote className="h-4 w-4" aria-hidden /> Vote
                            </Link>
                          )}
                        </div>
                      </Card>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}
