import Link from "next/link";
import {
  UserPlus,
  ScanFace,
  ShieldCheck,
  Vote,
  ReceiptText,
  ArrowRight,
} from "lucide-react";

const steps = [
  {
    icon: UserPlus,
    title: "Register",
    body: "Create an account with your identity details and pick your assembly constituency.",
  },
  {
    icon: ScanFace,
    title: "Enroll your face",
    body: "Capture a reference photo used later to confirm it is really you.",
  },
  {
    icon: ShieldCheck,
    title: "Verify (liveness)",
    body: "Complete a quick liveness challenge — blink, smile or turn — before each vote.",
  },
  {
    icon: Vote,
    title: "Vote on-chain",
    body: "Your ballot is recorded as a transaction on the Ethereum testnet.",
  },
  {
    icon: ReceiptText,
    title: "Get a receipt",
    body: "Keep a transaction hash you can verify yourself on the block explorer.",
  },
];

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-6xl px-4">
      {/* Hero */}
      <section className="grid gap-10 py-16 md:grid-cols-2 md:items-center md:py-24">
        <div>
          <span className="inline-flex items-center rounded-full bg-indigo-100 px-3 py-1 text-xs font-medium text-indigo-700">
            Blockchain + Face Recognition
          </span>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Voting you can verify, identity you can trust.
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            A secure e-voting platform that pairs biometric identity checks with an
            on-chain ballot record. Cast your vote, then confirm it yourself on a public
            block explorer.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"
            >
              Register to vote <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-800 hover:bg-slate-50"
            >
              Log in
            </Link>
            <Link
              href="/admin/login"
              className="inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100"
            >
              Admin
            </Link>
          </div>
          <p className="mt-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Runs on the Ethereum testnet (Sepolia); this is a demonstration system, not a
            live government election.
          </p>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-gradient-to-br from-indigo-600 to-indigo-800 p-8 text-white shadow-lg">
          <ShieldCheck className="h-10 w-10" aria-hidden />
          <h2 className="mt-4 text-xl font-semibold">Why it is different</h2>
          <ul className="mt-4 space-y-3 text-sm text-indigo-100">
            <li className="flex gap-2">
              <span aria-hidden>•</span> One person, one verified vote — enforced by the
              smart contract.
            </li>
            <li className="flex gap-2">
              <span aria-hidden>•</span> Liveness checks resist spoofing with photos or
              replays.
            </li>
            <li className="flex gap-2">
              <span aria-hidden>•</span> Every ballot leaves a public, tamper-evident
              trail.
            </li>
            <li className="flex gap-2">
              <span aria-hidden>•</span> Results are computed from on-chain tallies.
            </li>
          </ul>
        </div>
      </section>

      {/* How it works */}
      <section className="pb-20">
        <h2 className="text-2xl font-bold text-slate-900">How it works</h2>
        <p className="mt-2 text-slate-600">Five steps from sign-up to a verifiable receipt.</p>
        <ol className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {steps.map((step, index) => (
            <li
              key={step.title}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-center gap-2">
                <span className="grid h-9 w-9 place-items-center rounded-lg bg-indigo-50 text-indigo-600">
                  <step.icon className="h-5 w-5" aria-hidden />
                </span>
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Step {index + 1}
                </span>
              </div>
              <h3 className="mt-3 font-semibold text-slate-900">{step.title}</h3>
              <p className="mt-1 text-sm text-slate-600">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
