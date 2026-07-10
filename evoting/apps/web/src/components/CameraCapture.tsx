"use client";

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import { CameraOff, Video } from "lucide-react";
import { Alert } from "./ui";

/** Imperative API exposed to parent components. */
export interface CameraHandle {
  /** Capture a single still frame as a JPEG Blob (used for multipart upload). */
  captureBlob: (quality?: number) => Promise<Blob>;
  /** Capture a single still as raw base64 (no `data:` prefix). */
  captureBase64: (quality?: number) => string;
  /** Capture N frames as raw base64 strings with a delay between each. */
  captureFrames: (count: number, delayMs?: number, quality?: number) => Promise<string[]>;
  /** Whether the live stream is currently active. */
  isReady: () => boolean;
}

interface CameraCaptureProps {
  /** Called once the stream is live (or has stopped). */
  onReadyChange?: (ready: boolean) => void;
  className?: string;
}

function stripDataPrefix(dataUrl: string): string {
  const comma = dataUrl.indexOf(",");
  return comma === -1 ? dataUrl : dataUrl.slice(comma + 1);
}

const delay = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));

export const CameraCapture = forwardRef<CameraHandle, CameraCaptureProps>(
  function CameraCapture({ onReadyChange, className }, ref) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const [ready, setReady] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const updateReady = useCallback(
      (next: boolean) => {
        setReady(next);
        onReadyChange?.(next);
      },
      [onReadyChange],
    );

    useEffect(() => {
      let cancelled = false;

      async function start() {
        if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
          setError("Camera access is not supported in this browser.");
          return;
        }
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "user" },
            audio: false,
          });
          if (cancelled) {
            stream.getTracks().forEach((track) => track.stop());
            return;
          }
          streamRef.current = stream;
          const video = videoRef.current;
          if (video) {
            video.srcObject = stream;
            await video.play().catch(() => undefined);
          }
          setError(null);
          updateReady(true);
        } catch (err) {
          const name = err instanceof DOMException ? err.name : "";
          if (name === "NotAllowedError" || name === "SecurityError") {
            setError(
              "Camera permission was denied. Enable camera access in your browser settings and reload.",
            );
          } else if (name === "NotFoundError") {
            setError("No camera was found on this device.");
          } else {
            setError("Unable to start the camera. Please check your device and try again.");
          }
          updateReady(false);
        }
      }

      void start();

      return () => {
        cancelled = true;
        streamRef.current?.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      };
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const drawFrame = useCallback((quality: number): string => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas) {
        throw new Error("Camera is not ready yet.");
      }
      const width = video.videoWidth;
      const height = video.videoHeight;
      if (width === 0 || height === 0) {
        throw new Error("Camera is still initialising. Please wait a moment.");
      }
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        throw new Error("Unable to capture from the camera on this device.");
      }
      ctx.drawImage(video, 0, 0, width, height);
      return canvas.toDataURL("image/jpeg", quality);
    }, []);

    useImperativeHandle(
      ref,
      (): CameraHandle => ({
        captureBase64: (quality = 0.9) => stripDataPrefix(drawFrame(quality)),
        captureBlob: (quality = 0.9) =>
          new Promise<Blob>((resolve, reject) => {
            const canvas = canvasRef.current;
            drawFrame(quality);
            if (!canvas) {
              reject(new Error("Camera is not ready yet."));
              return;
            }
            canvas.toBlob(
              (blob) => {
                if (blob) resolve(blob);
                else reject(new Error("Failed to capture image."));
              },
              "image/jpeg",
              quality,
            );
          }),
        captureFrames: async (count, delayMs = 350, quality = 0.85) => {
          const frames: string[] = [];
          for (let i = 0; i < count; i += 1) {
            frames.push(stripDataPrefix(drawFrame(quality)));
            if (i < count - 1) await delay(delayMs);
          }
          return frames;
        },
        isReady: () => ready,
      }),
      [drawFrame, ready],
    );

    return (
      <div className={className}>
        <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-900 aspect-video">
          <video
            ref={videoRef}
            playsInline
            muted
            className="h-full w-full object-cover"
          />
          {!ready && !error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-slate-300">
              <Video className="h-8 w-8 animate-pulse" aria-hidden />
              <p className="text-sm">Starting camera…</p>
            </div>
          )}
          {error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-slate-900/90 p-6 text-center text-slate-200">
              <CameraOff className="h-8 w-8" aria-hidden />
              <p className="text-sm">{error}</p>
            </div>
          )}
        </div>
        <canvas ref={canvasRef} className="hidden" aria-hidden />
        {error && (
          <div className="mt-3">
            <Alert tone="error">{error}</Alert>
          </div>
        )}
      </div>
    );
  },
);
