"use client";

import { useState } from "react";
import Link from "next/link";
import "./pitch.css";

const PIPELINE_STEPS = [
  {
    step: "01",
    title: "Stage 1: Ingestion & Client Interception",
    desc: "Captures raw checkout failure events via HMAC-SHA256 verified webhooks or the drop-in client SDK (<script src=\".../sdk/ultron.js\">). Every raw event is deduplicated and normalized into a canonical RecoveryOpportunity record without executing blindly.",
  },
  {
    step: "02",
    title: "Stage 2: Perception Normalization",
    desc: "Maps provider decline codes into an immutable deterministic taxonomy: hard (stolen/lost/pickup), soft (insufficient funds, expired card, timeouts), or unknown. Queries customer historical attempt counts and trust profiles.",
  },
  {
    step: "03",
    title: "Stage 3: Economic Reasoning & Bayesian Calibration",
    desc: "Calculates Expected Incremental Value Net (IVEN = ΔP × Amount - Costs). Probabilities are calibrated via Beta-Binomial Bayesian posteriors and non-linear customer contact fatigue curves. Hard declines are strictly clamped at ΔP = 0.",
  },
  {
    step: "04",
    title: "Stage 4: Recovery Market Portfolio Allocator",
    desc: "Solves the greedy knapsack under capacity constraint K=5 links/run. Filters out negative IVEN and low-confidence items into ABSTAIN. Allocates top K items into ACT, defers excess to WAIT, and calculates the equilibrium Shadow Price λ.",
  },
  {
    step: "05",
    title: "Stage 5: Action Authority Compliance Gate",
    desc: "Deterministic compliance gate with independent veto power. Evaluates 5 rules: Hard decline check, 3-attempt retry cap, emergency kill switch, confidence recheck, and capacity recheck. Economic value never bypasses compliance.",
  },
  {
    step: "06",
    title: "Stage 6: Resilient Execution Engine",
    desc: "Strictly asserts Action Authority status is AUTHORIZED. Creates Razorpay payment links idempotently using circuit breakers, jittered retries, and omnichannel dispatch across WhatsApp and Email.",
  },
  {
    step: "07",
    title: "Stage 7: Truth Engine & Cryptographic Ledger",
    desc: "Core invariant: LINK_CREATED != RECOVERED. Confirms settlement only upon authoritative bank status = paid. Appends every rupee to an immutable SHA-256 chained double-entry ledger verified against a 5% holdout control group.",
  },
];

export default function PitchLandingPage() {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [gmvLakhs, setGmvLakhs] = useState<number>(50);
  const [failureRate, setFailureRate] = useState<number>(18);

  // Dynamic calculations
  const failedGmv = gmvLakhs * (failureRate / 100);
  const netRecovered = failedGmv * 0.224; // +22.4% verified lift
  const avgTxSize = 2500;
  const failedTxCount = (failedGmv * 100000) / avgTxSize;
  const savedLinkFees = Math.round(failedTxCount * 0.58 * 4.85);

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--pitch-bg-deep)", color: "var(--pitch-text-primary)", position: "relative", overflowX: "hidden" }}>
      {/* Background Ambience */}
      <div className="cyber-grid" />
      <div style={{ position: "fixed", top: "-200px", left: "-100px", width: 600, height: 600, borderRadius: "50%", background: "#06b6d4", filter: "blur(140px)", opacity: 0.15, pointerEvents: "none" }} />
      <div style={{ position: "fixed", top: "300px", right: "-200px", width: 600, height: 600, borderRadius: "50%", background: "#10b981", filter: "blur(140px)", opacity: 0.15, pointerEvents: "none" }} />

      {/* Top Header */}
      <header style={{ position: "sticky", top: 0, zIndex: 50, background: "rgba(3, 6, 12, 0.85)", backdropFilter: "blur(16px)", borderBottom: "1px solid rgba(255, 255, 255, 0.08)" }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", padding: "16px 24px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ width: 36, height: 36, background: "linear-gradient(135deg, var(--pitch-emerald), var(--pitch-cyan))", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>
              ⚡
            </div>
            <div>
              <span style={{ fontWeight: 900, fontSize: 20, letterSpacing: 0.5 }}>ULTRON</span>
              <span style={{ display: "block", fontSize: 11, color: "var(--pitch-text-muted)" }}>Autonomous Economic Control Plane</span>
            </div>
          </div>

          <nav style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <Link href="/showcase" style={{ color: "var(--pitch-cyan)", textDecoration: "none", fontSize: 14, fontWeight: 700 }}>
              ⚡ Product Showcase
            </Link>
            <a href="#pipeline" style={{ color: "var(--pitch-text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 600 }}>
              7-Stage Pipeline
            </a>
            <a href="#calculator" style={{ color: "var(--pitch-text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 600 }}>
              ROI Calculator
            </a>
            <Link
              href="/pitch/video"
              style={{
                background: "rgba(16, 185, 129, 0.15)",
                color: "var(--pitch-emerald)",
                border: "1px solid rgba(16, 185, 129, 0.35)",
                padding: "8px 16px",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                gap: 8,
                textDecoration: "none",
                fontSize: 14,
                fontWeight: 700,
              }}
            >
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--pitch-emerald)" }} />
              5-Min Motion Video (1080p) ↗
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{ position: "relative", zIndex: 10, padding: "80px 24px", textAlign: "center", maxWidth: 1000, margin: "0 auto" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.25)", borderRadius: 9999, fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 700, color: "var(--pitch-emerald)", marginBottom: 24 }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--pitch-emerald)" }} />
          RECOVERY CONTROL PLANE • NEXT.JS 16
        </div>

        <h1 style={{ fontSize: 52, fontWeight: 900, lineHeight: 1.15, marginBottom: 20, letterSpacing: -1 }}>
          Stop Asking &quot;Can We Retry?&quot;<br />
          <span style={{ background: "linear-gradient(135deg, var(--pitch-emerald) 0%, var(--pitch-cyan) 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            Start Asking &quot;Is It Worth Acting?&quot;
          </span>
        </h1>

        <p style={{ fontSize: 18, color: "var(--pitch-text-secondary)", lineHeight: 1.6, maxWidth: 780, margin: "0 auto 36px auto" }}>
          ULTRON sits a layer above payment gateway retries. It treats failed checkout transactions as a scarce-resource portfolio optimization problem, only intervening when true counterfactual lift exceeds operational delivery cost and customer fatigue.
        </p>

        <div style={{ display: "flex", justifyContent: "center", gap: 16, marginBottom: 50 }}>
          <Link
            href="/pitch/video"
            style={{
              background: "linear-gradient(135deg, var(--pitch-emerald), #059669)",
              color: "#000",
              fontWeight: 800,
              padding: "14px 28px",
              borderRadius: 10,
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              gap: 8,
              boxShadow: "0 4px 20px rgba(16, 185, 129, 0.4)",
            }}
          >
            <span>▶</span> Launch 5-Minute Motion Presentation (1080p)
          </Link>
          <a
            href="#calculator"
            style={{
              background: "rgba(255, 255, 255, 0.05)",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              color: "#fff",
              fontWeight: 700,
              padding: "14px 24px",
              borderRadius: 10,
              textDecoration: "none",
            }}
          >
            Calculate Net Recovery Lift →
          </a>
        </div>

        {/* Quick Metrics Strip */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, padding: 24, background: "var(--pitch-bg-card)", border: "1px solid rgba(255, 255, 255, 0.08)", borderRadius: 16, backdropFilter: "blur(12px)" }}>
          <div>
            <span style={{ display: "block", fontFamily: "var(--pitch-font-mono)", fontSize: 28, fontWeight: 900, color: "var(--pitch-cyan)" }}>+22.4%</span>
            <span style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Proven GMV Lift</span>
          </div>
          <div>
            <span style={{ display: "block", fontFamily: "var(--pitch-font-mono)", fontSize: 28, fontWeight: 900, color: "var(--pitch-cyan)" }}>-64%</span>
            <span style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Wasted Link Spend</span>
          </div>
          <div>
            <span style={{ display: "block", fontFamily: "var(--pitch-font-mono)", fontSize: 28, fontWeight: 900, color: "var(--pitch-cyan)" }}>K = 5</span>
            <span style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Knapsack Cap</span>
          </div>
          <div>
            <span style={{ display: "block", fontFamily: "var(--pitch-font-mono)", fontSize: 28, fontWeight: 900, color: "var(--pitch-cyan)" }}>0.0%</span>
            <span style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Fraud Liability</span>
          </div>
        </div>
      </section>

      {/* 7-Stage Pipeline Explorer */}
      <section id="pipeline" style={{ maxWidth: 1200, margin: "60px auto", padding: "0 24px", position: "relative", zIndex: 10 }}>
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, fontWeight: 800, color: "var(--pitch-cyan)", letterSpacing: 1.5 }}>
            DETERMINISTIC ARCHITECTURE
          </span>
          <h2 style={{ fontSize: 36, fontWeight: 900, marginTop: 6 }}>The 7-Stage Execution Machine</h2>
          <p style={{ color: "var(--pitch-text-secondary)", marginTop: 6, fontSize: 15 }}>
            Zero LLMs on the financial execution path. Cryptographic double-entry ledger truth.
          </p>
        </div>

        <div style={{ display: "flex", gap: 8, justifyContent: "center", marginBottom: 24, flexWrap: "wrap" }}>
          {PIPELINE_STEPS.map((s, idx) => (
            <button
              key={s.step}
              onClick={() => setActiveStep(idx)}
              style={{
                background: activeStep === idx ? "rgba(6, 182, 212, 0.15)" : "rgba(255, 255, 255, 0.04)",
                borderColor: activeStep === idx ? "var(--pitch-cyan)" : "rgba(255, 255, 255, 0.08)",
                color: activeStep === idx ? "var(--pitch-cyan)" : "var(--pitch-text-secondary)",
                fontFamily: "var(--pitch-font-mono)",
                fontSize: 13,
                fontWeight: activeStep === idx ? 700 : 500,
                padding: "10px 16px",
                borderRadius: 8,
                borderWidth: 1,
                borderStyle: "solid",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              {s.title.split(":")[0]}
            </button>
          ))}
        </div>

        <div style={{ background: "var(--pitch-bg-card)", border: "1px solid rgba(255, 255, 255, 0.1)", borderRadius: 16, padding: 32, backdropFilter: "blur(12px)" }}>
          <h3 style={{ fontSize: 24, color: "#fff", marginBottom: 8 }}>{PIPELINE_STEPS[activeStep].title}</h3>
          <p style={{ color: "var(--pitch-text-secondary)", lineHeight: 1.6, maxWidth: 800 }}>
            {PIPELINE_STEPS[activeStep].desc}
          </p>
        </div>
      </section>

      {/* Interactive ROI Calculator */}
      <section id="calculator" style={{ maxWidth: 1200, margin: "60px auto", padding: "0 24px", position: "relative", zIndex: 10 }}>
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, fontWeight: 800, color: "var(--pitch-cyan)", letterSpacing: 1.5 }}>
            BUSINESS CASE
          </span>
          <h2 style={{ fontSize: 36, fontWeight: 900, marginTop: 6 }}>Interactive Net Value (IVEN) Calculator</h2>
          <p style={{ color: "var(--pitch-text-secondary)", marginTop: 6, fontSize: 15 }}>
            Simulate your monthly recovery gains based on GMV, decline rates, and rational anti-blast abstention.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 32, background: "var(--pitch-bg-card)", border: "1px solid rgba(255, 255, 255, 0.1)", borderRadius: 20, padding: 36, backdropFilter: "blur(12px)" }}>
          <div>
            <label style={{ display: "block", marginBottom: 8 }}>
              <span>Monthly Checkout Volume: </span>
              <strong style={{ color: "var(--pitch-emerald)", fontFamily: "var(--pitch-font-mono)" }}>₹{gmvLakhs} Lakhs</strong>
              <input
                type="range"
                min="10"
                max="500"
                step="10"
                value={gmvLakhs}
                onChange={(e) => setGmvLakhs(Number(e.target.value))}
                style={{ width: "100%", marginTop: 8, accentColor: "var(--pitch-emerald)" }}
              />
            </label>

            <label style={{ display: "block", marginTop: 24 }}>
              <span>Estimated Checkout Failure Rate: </span>
              <strong style={{ color: "var(--pitch-cyan)", fontFamily: "var(--pitch-font-mono)" }}>{failureRate}%</strong>
              <input
                type="range"
                min="5"
                max="35"
                step="1"
                value={failureRate}
                onChange={(e) => setFailureRate(Number(e.target.value))}
                style={{ width: "100%", marginTop: 8, accentColor: "var(--pitch-cyan)" }}
              />
            </label>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div style={{ background: "rgba(255, 255, 255, 0.03)", border: "1px solid rgba(255, 255, 255, 0.06)", borderRadius: 12, padding: "16px 20px" }}>
              <span style={{ display: "block", fontSize: 12, color: "var(--pitch-text-muted)" }}>Failed GMV at Risk</span>
              <span style={{ display: "block", fontFamily: "var(--pitch-font-mono)", fontSize: 24, fontWeight: 900, marginTop: 4, color: "var(--pitch-rose)" }}>
                ₹{failedGmv.toFixed(2)} Lakhs
              </span>
            </div>

            <div style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.3)", borderRadius: 12, padding: "16px 20px" }}>
              <span style={{ display: "block", fontSize: 12, color: "var(--pitch-text-muted)" }}>Net Recovered Revenue (+22.4% Lift)</span>
              <span style={{ display: "block", fontFamily: "var(--pitch-font-mono)", fontSize: 26, fontWeight: 900, marginTop: 4, color: "var(--pitch-emerald)" }}>
                ₹{netRecovered.toFixed(2)} Lakhs
              </span>
            </div>

            <div style={{ background: "rgba(255, 255, 255, 0.03)", border: "1px solid rgba(255, 255, 255, 0.06)", borderRadius: 12, padding: "16px 20px" }}>
              <span style={{ display: "block", fontSize: 12, color: "var(--pitch-text-muted)" }}>Saved Link &amp; WhatsApp Fees</span>
              <span style={{ display: "block", fontFamily: "var(--pitch-font-mono)", fontSize: 22, fontWeight: 900, marginTop: 4, color: "var(--pitch-cyan)" }}>
                ₹{savedLinkFees.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ textAlign: "center", padding: "40px 24px", borderTop: "1px solid rgba(255, 255, 255, 0.06)", color: "var(--pitch-text-muted)", fontSize: 13 }}>
        <p>ULTRON • Autonomous Economic Control Plane for Razorpay Recovery • Next.js 16 App Router</p>
      </footer>
    </div>
  );
}
