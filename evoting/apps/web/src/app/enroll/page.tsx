"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { CheckCircle2, Camera } from "lucide-react";
import { CameraCapture, type CameraHandle } from "@/components/CameraCapture";
import { enrollment } from "@/lib/api";
import { useRequireAuth } from "@/lib/use-require-auth";
import { errorMessage } from "@/lib/format";
import { Alert, Button, Card, Spinner } from "@/components/ui";

export default function EnrollPage() {
  const { ready, allowed } = useRequireAuth("voter");
  const cameraRef = useRef<CameraHandle>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enrolledVersion, setEnrolledVersion] = useState<string | null>(null);
  const [alreadyEnrolled, setAlreadyEnrolled] = useState(false);

  useEffect(() => {
    if (!allowed) return;
    enrollment.status().then((s) => setAlreadyEnrolled(s.enrolled)).catch(() => undefined);
  }, [allowed]);

  if (!ready || !allowed) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-6 w-6 text-indigo-600" />
      </div>
    );
  }

  async function handleCapture() {
    setError(null);
    setSubmitting(true);
    try {
      const blob = await cameraRef.current?.captureBlob();
      if (!blob) throw new Error("Camera is not ready yet.");
      const result = await enrollment.face(blob);
      setEnrolledVersion(result.algorithm_version);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  if (enrolledVersion !== null) {
    return (
      <div className="mx-auto max-w-md px-4 py-16">
        <Card>
          <div className="flex flex-col items-center text-center">
            <CheckCircle2 className="h-12 w-12 text-emerald-500" aria-hidden />
            <h1 className="mt-4 text-2xl font-bold text-slate-900">Face enrolled</h1>
            <p className="mt-2 text-sm text-slate-600">
              Your reference photo has been saved (algorithm {enrolledVersion}). You are
              ready to verify your identity when voting.
            </p>
            <Link
              href="/dashboard"
              className="mt-6 inline-flex w-full items-center justify-center rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"
            >
              Back to dashboard
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-12">
      <h1 className="text-3xl font-bold text-slate-900">Face enrollment</h1>
      <p className="mt-2 text-slate-600">
        Look straight at the camera in good lighting and capture a clear photo. This
        becomes your reference for identity verification at vote time.
      </p>

      {alreadyEnrolled && (
        <div className="mt-4">
          <Alert tone="info">
            You already have a reference photo. Capturing again replaces it.
          </Alert>
        </div>
      )}

      <Card className="mt-6">
        <CameraCapture ref={cameraRef} onReadyChange={setCameraReady} />
        {error && (
          <div className="mt-4">
            <Alert tone="error">{error}</Alert>
          </div>
        )}
        <Button
          onClick={handleCapture}
          disabled={!cameraReady}
          loading={submitting}
          className="mt-4 w-full"
        >
          <Camera className="h-4 w-4" aria-hidden /> Capture &amp; enroll
        </Button>
      </Card>
    </div>
  );
}
