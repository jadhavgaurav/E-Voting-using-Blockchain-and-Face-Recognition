"use client";

import { use, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { CheckCircle2, ExternalLink, ScanFace, ShieldCheck } from "lucide-react";
import {
  voting,
  verification,
  ApiError,
  type CandidateOut,
  type LivenessChallenge,
  type ReceiptOut,
  type VerificationStart,
} from "@/lib/api";
import { CameraCapture, type CameraHandle } from "@/components/CameraCapture";
import { useRequireAuth } from "@/lib/use-require-auth";
import { errorMessage } from "@/lib/format";
import { explorerTxUrl } from "@/lib/config";
import { Alert, Badge, Button, Card, Spinner } from "@/components/ui";
import { cn } from "@/lib/cn";

const CHALLENGE_LABEL: Record<LivenessChallenge, string> = {
  blink: "Please blink slowly",
  turn_left: "Please turn your head to the left",
  turn_right: "Please turn your head to the right",
  smile: "Please smile",
};

type Phase = "candidates" | "verify" | "verified" | "done";

export default function VotePage({
  params,
}: {
  params: Promise<{ electionId: string }>;
}) {
  const { electionId } = use(params);
  const { ready, allowed } = useRequireAuth("voter");

  const cameraRef = useRef<CameraHandle>(null);
  const [cameraReady, setCameraReady] = useState(false);

  const [candidates, setCandidates] = useState<CandidateOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [phase, setPhase] = useState<Phase>("candidates");
  const [challenge, setChallenge] = useState<VerificationStart | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [castError, setCastError] = useState<string | null>(null);
  const [casting, setCasting] = useState(false);
  const [receipt, setReceipt] = useState<ReceiptOut | null>(null);

  useEffect(() => {
    if (!allowed) return;
    let active = true;
    setLoading(true);
    voting
      .candidates(electionId)
      .then((data) => active && setCandidates(data))
      .catch((err) => active && setLoadError(errorMessage(err)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [allowed, electionId]);

  if (!ready || !allowed) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-6 w-6 text-indigo-600" />
      </div>
    );
  }

  async function startVerification() {
    setVerifyError(null);
    setVerifying(true);
    try {
      const start = await verification.start(electionId);
      setChallenge(start);
      setPhase("verify");
    } catch (err) {
      if (err instanceof ApiError && err.code === "NOT_APPROVED") {
        setVerifyError(
          "Your registration has not been approved yet, so you cannot vote in this election.",
        );
      } else if (err instanceof ApiError && err.code === "ALREADY_VOTED") {
        setVerifyError("You have already voted in this election.");
      } else {
        setVerifyError(errorMessage(err));
      }
    } finally {
      setVerifying(false);
    }
  }

  async function runLivenessCheck() {
    if (!challenge) return;
    setVerifyError(null);
    setVerifying(true);
    try {
      const camera = cameraRef.current;
      if (!camera) throw new Error("Camera is not ready yet.");
      const frames = await camera.captureFrames(3, 350);
      const probe = camera.captureBase64();
      const result = await verification.face({
        request_id: challenge.request_id,
        election_id: electionId,
        challenge: challenge.challenge,
        frames_b64: frames,
        probe_image_b64: probe,
      });
      if (result.passed) {
        setPhase("verified");
      } else {
        setVerifyError(
          result.reason ||
            "Verification failed. Make sure your face is clearly visible and try the challenge again.",
        );
      }
    } catch (err) {
      if (err instanceof ApiError && err.code === "VERIFICATION_FAILED") {
        setVerifyError(err.detail);
      } else {
        setVerifyError(errorMessage(err));
      }
    } finally {
      setVerifying(false);
    }
  }

  async function castVote() {
    if (!selectedId || !challenge) return;
    setCastError(null);
    setCasting(true);
    try {
      const result = await voting.cast({
        election_id: electionId,
        candidate_id: selectedId,
        verification_request_id: challenge.request_id,
      });
      setReceipt(result);
      setPhase("done");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409 && err.code === "ALREADY_VOTED") {
        setCastError("You have already voted in this election. Each voter gets one ballot.");
      } else if (
        err instanceof ApiError &&
        err.status === 403 &&
        err.code === "NOT_APPROVED"
      ) {
        setCastError("Your registration is not approved, so this ballot was rejected.");
      } else {
        setCastError(errorMessage(err));
      }
    } finally {
      setCasting(false);
    }
  }

  /* ----------------------------- Receipt view ---------------------------- */
  if (phase === "done" && receipt) {
    return (
      <div className="mx-auto max-w-lg px-4 py-16">
        <Card>
          <div className="flex flex-col items-center text-center">
            <CheckCircle2 className="h-12 w-12 text-emerald-500" aria-hidden />
            <h1 className="mt-4 text-2xl font-bold text-slate-900">Vote recorded</h1>
            <p className="mt-2 text-sm text-slate-600">
              Your ballot has been written to the blockchain. Keep this receipt.
            </p>
          </div>
          <dl className="mt-6 space-y-3 rounded-xl bg-slate-50 p-4 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Transaction</dt>
              <dd className="break-all text-right font-mono text-slate-800">
                {receipt.tx_hash}
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Block</dt>
              <dd className="font-mono text-slate-800">#{receipt.block_number}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Candidate index</dt>
              <dd className="font-mono text-slate-800">{receipt.candidate_index}</dd>
            </div>
          </dl>
          <div className="mt-6 flex flex-col gap-3">
            <a
              href={explorerTxUrl(receipt.tx_hash)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"
            >
              View on block explorer <ExternalLink className="h-4 w-4" aria-hidden />
            </a>
            <Link
              href="/receipts"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              All receipts
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  const verified = phase === "verified";

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <Link href="/dashboard" className="text-sm text-indigo-600 hover:underline">
        ← Back to dashboard
      </Link>
      <h1 className="mt-3 text-3xl font-bold text-slate-900">Cast your vote</h1>

      {loadError && (
        <div className="mt-6">
          <Alert tone="error">{loadError}</Alert>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-24">
          <Spinner className="h-6 w-6 text-indigo-600" />
        </div>
      ) : (
        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          {/* Step 1 & 3: candidates */}
          <section>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold text-slate-900">Candidates</h2>
              {verified && <Badge tone="success">Identity verified</Badge>}
            </div>
            {!verified && (
              <p className="mt-1 text-sm text-slate-500">
                Verify your identity to unlock candidate selection.
              </p>
            )}
            <ul className="mt-4 space-y-3">
              {candidates.map((candidate) => {
                const selected = selectedId === candidate.id;
                return (
                  <li key={candidate.id}>
                    <button
                      type="button"
                      disabled={!verified || casting}
                      onClick={() => setSelectedId(candidate.id)}
                      className={cn(
                        "flex w-full items-center gap-3 rounded-xl border p-4 text-left transition-colors",
                        selected
                          ? "border-indigo-600 bg-indigo-50 ring-2 ring-indigo-500/30"
                          : "border-slate-200 bg-white hover:border-slate-300",
                        (!verified || casting) && "cursor-not-allowed opacity-60",
                      )}
                    >
                      <span className="grid h-12 w-12 shrink-0 place-items-center overflow-hidden rounded-full bg-slate-100 text-sm font-semibold text-slate-500">
                        {candidate.symbol_url ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={candidate.symbol_url}
                            alt=""
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          candidate.name.slice(0, 1).toUpperCase()
                        )}
                      </span>
                      <span className="flex-1">
                        <span className="block font-medium text-slate-900">
                          {candidate.name}
                        </span>
                        <span className="block text-sm text-slate-500">
                          {candidate.party}
                        </span>
                      </span>
                      {selected && (
                        <CheckCircle2 className="h-5 w-5 text-indigo-600" aria-hidden />
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>

            {verified && (
              <div className="mt-4">
                {castError && (
                  <div className="mb-3">
                    <Alert tone="error">{castError}</Alert>
                  </div>
                )}
                <Button
                  onClick={castVote}
                  disabled={!selectedId}
                  loading={casting}
                  className="w-full"
                >
                  Cast vote
                </Button>
              </div>
            )}
          </section>

          {/* Step 2: verification */}
          <section>
            <h2 className="text-lg font-semibold text-slate-900">Identity verification</h2>
            <Card className="mt-4">
              {phase === "candidates" && (
                <div className="flex flex-col items-center py-6 text-center">
                  <ShieldCheck className="h-10 w-10 text-indigo-500" aria-hidden />
                  <p className="mt-3 text-sm text-slate-600">
                    We will run a quick liveness challenge before you can vote.
                  </p>
                  {verifyError && (
                    <div className="mt-4 w-full">
                      <Alert tone="error">{verifyError}</Alert>
                    </div>
                  )}
                  <Button
                    onClick={startVerification}
                    loading={verifying}
                    className="mt-4"
                  >
                    <ScanFace className="h-4 w-4" aria-hidden /> Verify identity
                  </Button>
                </div>
              )}

              {phase === "verify" && challenge && (
                <div>
                  <Alert tone="info" title={CHALLENGE_LABEL[challenge.challenge]}>
                    Keep your face centred, then run the check.
                  </Alert>
                  <div className="mt-4">
                    <CameraCapture ref={cameraRef} onReadyChange={setCameraReady} />
                  </div>
                  {verifyError && (
                    <div className="mt-4">
                      <Alert tone="error">{verifyError}</Alert>
                    </div>
                  )}
                  <Button
                    onClick={runLivenessCheck}
                    disabled={!cameraReady}
                    loading={verifying}
                    className="mt-4 w-full"
                  >
                    Run liveness check
                  </Button>
                </div>
              )}

              {verified && (
                <div className="flex flex-col items-center py-6 text-center">
                  <CheckCircle2 className="h-10 w-10 text-emerald-500" aria-hidden />
                  <p className="mt-3 text-sm text-slate-600">
                    Identity verified. Select a candidate and cast your vote.
                  </p>
                </div>
              )}
            </Card>
          </section>
        </div>
      )}
    </div>
  );
}
