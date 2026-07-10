"use client";

import { useEffect, useState } from "react";
import { ExternalLink, ReceiptText } from "lucide-react";
import { voting, type ReceiptOut } from "@/lib/api";
import { useRequireAuth } from "@/lib/use-require-auth";
import { errorMessage, formatDateTime, shortHash } from "@/lib/format";
import { explorerTxUrl } from "@/lib/config";
import { Alert, Card, Spinner } from "@/components/ui";

export default function ReceiptsPage() {
  const { ready, allowed } = useRequireAuth("voter");
  const [receipts, setReceipts] = useState<ReceiptOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!allowed) return;
    let active = true;
    setLoading(true);
    voting
      .receipts()
      .then((data) => active && setReceipts(data))
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

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-3xl font-bold text-slate-900">Your receipts</h1>
      <p className="mt-2 text-slate-600">
        Each vote you cast is recorded on-chain. Use the explorer link to verify the
        transaction yourself.
      </p>

      {error && (
        <div className="mt-6">
          <Alert tone="error">{error}</Alert>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-24">
          <Spinner className="h-6 w-6 text-indigo-600" />
        </div>
      ) : receipts.length === 0 ? (
        <Card className="mt-6 flex flex-col items-center py-12 text-center">
          <ReceiptText className="h-10 w-10 text-slate-300" aria-hidden />
          <p className="mt-3 text-sm text-slate-600">
            You have not cast any votes yet.
          </p>
        </Card>
      ) : (
        <ul className="mt-6 space-y-3">
          {receipts.map((receipt) => (
            <li key={receipt.tx_hash}>
              <Card>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-slate-500">
                      Cast on {formatDateTime(receipt.created_at)}
                    </p>
                    <p className="mt-1 font-mono text-sm text-slate-800">
                      {shortHash(receipt.tx_hash)}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      Block #{receipt.block_number} · Candidate index{" "}
                      {receipt.candidate_index}
                    </p>
                  </div>
                  <a
                    href={explorerTxUrl(receipt.tx_hash)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                  >
                    View on explorer <ExternalLink className="h-4 w-4" aria-hidden />
                  </a>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
