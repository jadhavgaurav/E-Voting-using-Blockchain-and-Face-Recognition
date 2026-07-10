import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "E-Voting — Blockchain & Face Recognition",
  description:
    "Secure, verifiable e-voting on the Ethereum testnet with biometric identity checks. Demonstration system.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <AuthProvider>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <footer className="border-t border-slate-200 bg-white">
              <div className="mx-auto max-w-6xl px-4 py-6 text-center text-xs text-slate-500">
                Demonstration system · Runs on the Ethereum Sepolia testnet · No real
                ballots are cast.
              </div>
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
