import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "../lib/auth";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ULTRON — Autonomous Payment Recovery",
  description:
    "ULTRON is an autonomous economic control plane for failed-payment recovery. Score, allocate, and execute recovery opportunities on Razorpay — driven by incremental economics, not guesswork.",
  keywords: ["payment recovery", "razorpay", "failed payments", "SaaS", "fintech"],
  authors: [{ name: "ULTRON" }],
  robots: "noindex, nofollow", // SaaS app — not for search indexing
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
