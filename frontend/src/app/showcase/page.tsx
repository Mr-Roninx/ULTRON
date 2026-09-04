"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import "../pitch/pitch.css";

interface LabScenario {
  id: string;
  name: string;
  amount: number;
  currency: string;
  reasonCode: string;
  attempt: number;
  declineType: "hard" | "soft";
  pNatural: number;
  pIntervention: number;
  fatigueCost: number;
  linkCost: number;
  expectedDecision: "ACT" | "WAIT" | "ABSTAIN";
  decisionBadge: string;
  decisionColor: string;
  laserResult: "PASSED" | "VETOED";
  laserReason: string;
  summary: string;
}

const FAILURE_SCENARIOS: LabScenario[] = [
  {
    id: "scen_stolen",
    name: "Stolen Card Reported by Issuer",
    amount: 4500,
    currency: "INR",
    reasonCode: "stolen_card",
    attempt: 1,
    declineType: "hard",
    pNatural: 0.02,
    pIntervention: 0.02,
    fatigueCost: 0,
    linkCost: 4.0,
    expectedDecision: "ABSTAIN",
    decisionBadge: "ABSTAIN / BLOCKED",
    decisionColor: "var(--pitch-rose)",
    laserResult: "VETOED",
    laserReason: "Check 1 Failed: Hard decline (fraud/lost card). Contact strictly blocked.",
    summary: "Permanent decline. Retrying burns fees and risks bank fraud penalties. ULTRON rationally abstains, saving capital and reputation.",
  },
  {
    id: "scen_timeout",
    name: "Bank Gateway Timeout (UPI)",
    amount: 15000,
    currency: "INR",
    reasonCode: "bank_gateway_timeout",
    attempt: 1,
    declineType: "soft",
    pNatural: 0.48,
    pIntervention: 0.70,
    fatigueCost: 0,
    linkCost: 4.0,
    expectedDecision: "ACT",
    decisionBadge: "ACT / ALLOCATED",
    decisionColor: "var(--pitch-emerald)",
    laserResult: "PASSED",
    laserReason: "All 5 compliance checks passed. Ranked #2 within capacity cap K=5.",
    summary: "Recoverable soft decline with high incremental yield (+₹3,296 IVEN). Allocated for immediate WhatsApp recovery link dispatch.",
  },
  {
    id: "scen_funds_att3",
    name: "Insufficient Funds Attempt #3",
    amount: 1800,
    currency: "INR",
    reasonCode: "insufficient_funds",
    attempt: 3,
    declineType: "soft",
    pNatural: 0.05,
    pIntervention: 0.20,
    fatigueCost: 7.5,
    linkCost: 4.0,
    expectedDecision: "WAIT",
    decisionBadge: "WAIT / DEFERRED",
    decisionColor: "var(--pitch-amber)",
    laserResult: "VETOED",
    laserReason: "Check 2 Flagged: Attempt count at retry cap. Below Shadow Price λ (₹23.96).",
    summary: "Excessive contact fatigue lowers yield below this run's marginal threshold. Deferred to prevent spam and customer churn.",
  },
  {
    id: "scen_license",
    name: "Annual Corporate Software License",
    amount: 25000,
    currency: "INR",
    reasonCode: "network_timeout",
    attempt: 1,
    declineType: "soft",
    pNatural: 0.12,
    pIntervention: 0.40,
    fatigueCost: 0,
    linkCost: 4.0,
    expectedDecision: "ACT",
    decisionBadge: "ACT / ALLOCATED (RANK #1)",
    decisionColor: "var(--pitch-emerald)",
    laserResult: "PASSED",
    laserReason: "All 5 checks passed. Top-ranked portfolio opportunity (+₹6,996 IVEN).",
    summary: "High-value transaction with 28% incremental lift. Intervening delivers massive net ROI without wasting customer goodwill.",
  },
];

export default function MotionShowcasePage() {
  // Mode Switcher: "legacy" vs "ultron"
  const [controlMode, setControlMode] = useState<"ultron" | "legacy">("ultron");

  // Failure Lab Interactive State
  const [activeScenario, setActiveScenario] = useState<LabScenario>(FAILURE_SCENARIOS[1]);
  const [simulationStage, setSimulationStage] = useState<number>(6); // 0 to 6
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Bento Interactive Controls
  const [interactiveDeltaP, setInteractiveDeltaP] = useState<number>(22);
  const [ledgerBlocks, setLedgerBlocks] = useState<Array<{ id: number; hash: string; opp: string; amt: string }>>([
    { id: 1, hash: "0000000000000000000000000000000000000000000000000000000000000000", opp: "GENESIS_ROOT", amt: "₹25,000.00" },
    { id: 2, hash: "3a4b9c1d8e7f2015948271038495aebc8172635490abcedf1234567890abcdef", opp: "synth_09_corp", amt: "₹25,000.00" },
  ]);

  // Audio tone generator
  const audioCtxRef = useRef<AudioContext | null>(null);
  const playSound = useCallback((freq: number, type: OscillatorType = "sine", duration = 0.15, gainVal = 0.04) => {
    if (typeof window === "undefined") return;
    try {
      if (!audioCtxRef.current) {
        const AudioClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        if (AudioClass) audioCtxRef.current = new AudioClass();
      }
      const ctx = audioCtxRef.current;
      if (!ctx) return;
      if (ctx.state === "suspended") ctx.resume();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch {
      // Audio not permitted
    }
  }, []);

  // Run Failure Lab Simulation Animation
  const runLabSimulation = useCallback((scenario: LabScenario) => {
    setActiveScenario(scenario);
    setIsSimulating(true);
    setSimulationStage(0);
    playSound(440, "sine", 0.1, 0.05);

    let stage = 0;
    const interval = setInterval(() => {
      stage += 1;
      setSimulationStage(stage);
      playSound(480 + stage * 40, "sine", 0.08, 0.03);

      if (stage >= 6) {
        clearInterval(interval);
        setIsSimulating(false);
        if (scenario.expectedDecision === "ACT") {
          playSound(783.99, "triangle", 0.25, 0.06);
        } else if (scenario.expectedDecision === "ABSTAIN") {
          playSound(220, "sawtooth", 0.25, 0.06);
        } else {
          playSound(523.25, "sine", 0.2, 0.05);
        }
      }
    }, 280);
  }, [playSound]);

  // Mine Simulated Ledger Block
  const mineLedgerBlock = useCallback(() => {
    const chars = "0123456789abcdef";
    let hash = "";
    for (let i = 0; i < 64; i++) hash += chars[Math.floor(Math.random() * chars.length)];

    const newBlock = {
      id: ledgerBlocks.length + 1,
      hash,
      opp: `opp_recov_${Date.now().toString().slice(-4)}`,
      amt: `₹${(Math.floor(Math.random() * 200 + 20) * 100).toLocaleString()}.00`,
    };

    setLedgerBlocks(prev => [newBlock, ...prev.slice(0, 4)]);
    playSound(880, "triangle", 0.15, 0.05);
  }, [ledgerBlocks.length, playSound]);

  // Calculated IVEN in Lab
  const deltaP = Math.max(0, activeScenario.pIntervention - activeScenario.pNatural);
  const calculatedIven = (deltaP * activeScenario.amount - activeScenario.linkCost - activeScenario.fatigueCost).toFixed(2);

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--pitch-bg-deep)", color: "var(--pitch-text-primary)", position: "relative", overflowX: "hidden", fontFamily: "var(--pitch-font-sans)" }}>
      {/* Background Cyber Grid & Glow Ambience */}
      <div className="cyber-grid" />
      <div style={{ position: "fixed", top: "-150px", left: "-100px", width: 650, height: 650, borderRadius: "50%", background: "#06b6d4", filter: "blur(160px)", opacity: 0.15, pointerEvents: "none" }} />
      <div style={{ position: "fixed", top: "350px", right: "-150px", width: 650, height: 650, borderRadius: "50%", background: "#10b981", filter: "blur(160px)", opacity: 0.15, pointerEvents: "none" }} />

      {/* ====================================================================
           1. TOP NAVIGATION HEADER
           ==================================================================== */}
      <header style={{ position: "sticky", top: 0, zIndex: 60, background: "rgba(3, 6, 12, 0.88)", backdropFilter: "blur(20px)", borderBottom: "1px solid rgba(255, 255, 255, 0.08)" }}>
        <div style={{ maxWidth: 1320, margin: "0 auto", padding: "16px 28px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ width: 38, height: 38, background: "linear-gradient(135deg, var(--pitch-emerald), var(--pitch-cyan))", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, boxShadow: "0 0 16px var(--pitch-emerald-glow)" }}>
              ⚡
            </div>
            <div>
              <span style={{ fontWeight: 900, fontSize: 20, letterSpacing: 0.5 }}>ULTRON</span>
              <span style={{ display: "block", fontSize: 11, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>PRODUCT SHOWCASE</span>
            </div>
          </div>

          <nav style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <a href="#failure-lab" style={{ color: "var(--pitch-text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 600 }}>
              Failure Lab
            </a>
            <a href="#bento-grid" style={{ color: "var(--pitch-text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 600 }}>
              Architecture
            </a>
            <a href="#comparison" style={{ color: "var(--pitch-text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 600 }}>
              Experience
            </a>
            <Link
              href="/pitch/video"
              style={{
                background: "rgba(16, 185, 129, 0.15)",
                color: "var(--pitch-emerald)",
                border: "1px solid rgba(16, 185, 129, 0.35)",
                padding: "8px 18px",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                gap: 8,
                textDecoration: "none",
                fontSize: 13,
                fontWeight: 800,
                boxShadow: "0 0 14px rgba(16, 185, 129, 0.2)",
              }}
            >
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--pitch-emerald)" }} />
              Watch 5-Min Motion Video (1080p)
            </Link>
          </nav>
        </div>
      </header>

      {/* ====================================================================
           2. HERO WITH INTERACTIVE MODE SWITCHER
           ==================================================================== */}
      <section style={{ maxWidth: 1240, margin: "0 auto", padding: "80px 24px 60px 24px", textAlign: "center", position: "relative", zIndex: 10 }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", background: "rgba(6, 182, 212, 0.1)", border: "1px solid rgba(6, 182, 212, 0.25)", borderRadius: 9999, fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 700, color: "var(--pitch-cyan)", marginBottom: 24 }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--pitch-cyan)" }} />
          AUTONOMOUS ECONOMIC CONTROL PLANE FOR RAZORPAY
        </div>

        <h1 style={{ fontSize: 58, fontWeight: 900, lineHeight: 1.12, letterSpacing: -1.2, maxWidth: 960, margin: "0 auto 24px auto" }}>
          Turn Payment Failures Into<br />
          <span style={{ background: "linear-gradient(135deg, var(--pitch-emerald) 0%, var(--pitch-cyan) 60%, var(--pitch-indigo) 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            Autonomous Economic Yield
          </span>
        </h1>

        <p style={{ fontSize: 19, color: "var(--pitch-text-secondary)", lineHeight: 1.6, maxWidth: 820, margin: "0 auto 40px auto" }}>
          ULTRON sits above retry schedulers. It evaluates every checkout failure as an economic recovery opportunity, competing in a greedy portfolio knapsack under scarce capacity limits and surviving deterministic compliance vetoes.
        </p>

        {/* Live Mode Switcher */}
        <div style={{ display: "inline-flex", alignItems: "center", background: "rgba(15, 23, 42, 0.9)", border: "1px solid var(--pitch-border-subtle)", padding: 6, borderRadius: 14, gap: 8, marginBottom: 50, boxShadow: "0 10px 30px rgba(0, 0, 0, 0.5)" }}>
          <button
            onClick={() => { setControlMode("ultron"); playSound(660, "sine", 0.1, 0.04); }}
            style={{
              padding: "10px 24px",
              borderRadius: 10,
              fontSize: 13,
              fontWeight: 800,
              cursor: "pointer",
              border: "none",
              background: controlMode === "ultron" ? "linear-gradient(135deg, var(--pitch-emerald), #059669)" : "transparent",
              color: controlMode === "ultron" ? "#000" : "var(--pitch-text-secondary)",
              boxShadow: controlMode === "ultron" ? "0 4px 16px rgba(16, 185, 129, 0.4)" : "none",
              transition: "all 0.2s",
            }}
          >
            ⚡ ULTRON Autonomous Mode
          </button>
          <button
            onClick={() => { setControlMode("legacy"); playSound(330, "sawtooth", 0.1, 0.04); }}
            style={{
              padding: "10px 24px",
              borderRadius: 10,
              fontSize: 13,
              fontWeight: 800,
              cursor: "pointer",
              border: "none",
              background: controlMode === "legacy" ? "rgba(244, 63, 94, 0.2)" : "transparent",
              color: controlMode === "legacy" ? "var(--pitch-rose)" : "var(--pitch-text-secondary)",
              transition: "all 0.2s",
            }}
          >
            ⚠️ Legacy Gateway Retries
          </button>
        </div>

        {/* Interactive Mode Comparison Visualizer */}
        <div style={{
          background: controlMode === "ultron" ? "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(11, 19, 38, 0.95) 100%)" : "linear-gradient(135deg, rgba(244, 63, 94, 0.1) 0%, rgba(11, 19, 38, 0.95) 100%)",
          border: `1px solid ${controlMode === "ultron" ? "rgba(16, 185, 129, 0.4)" : "rgba(244, 63, 94, 0.4)"}`,
          borderRadius: 24,
          padding: 36,
          boxShadow: controlMode === "ultron" ? "0 20px 60px rgba(16, 185, 129, 0.15)" : "0 20px 60px rgba(244, 63, 94, 0.15)",
          textAlign: "left",
          transition: "all 0.4s ease",
        }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20 }}>
            <div>
              <span style={{ fontSize: 12, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>DECISION PARADIGM</span>
              <div style={{ fontSize: 20, fontWeight: 900, color: "#fff", marginTop: 4 }}>
                {controlMode === "ultron" ? "Microeconomic Knapsack" : "Naive Sequential Loop"}
              </div>
              <p style={{ fontSize: 12, color: "var(--pitch-text-secondary)", marginTop: 4 }}>
                {controlMode === "ultron" ? "Rationally abstains when intervention yield is negative." : "Retries blindly until bank locks customer card."}
              </p>
            </div>

            <div>
              <span style={{ fontSize: 12, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>NET RECOVERY LIFT</span>
              <div style={{ fontSize: 28, fontWeight: 900, color: controlMode === "ultron" ? "var(--pitch-emerald)" : "var(--pitch-rose)", marginTop: 4, fontFamily: "var(--pitch-font-mono)" }}>
                {controlMode === "ultron" ? "+22.4%" : "0.0% (Illusory)"}
              </div>
              <p style={{ fontSize: 12, color: "var(--pitch-text-secondary)", marginTop: 4 }}>
                {controlMode === "ultron" ? "Statistically proven vs 5% holdout paired t-tests." : "Takes credit for 58% natural self-healing."}
              </p>
            </div>

            <div>
              <span style={{ fontSize: 12, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>WASTED LINK FEES</span>
              <div style={{ fontSize: 28, fontWeight: 900, color: controlMode === "ultron" ? "var(--pitch-cyan)" : "var(--pitch-rose)", marginTop: 4, fontFamily: "var(--pitch-font-mono)" }}>
                {controlMode === "ultron" ? "-64.2%" : "₹4.85 / blast"}
              </div>
              <p style={{ fontSize: 12, color: "var(--pitch-text-secondary)", marginTop: 4 }}>
                {controlMode === "ultron" ? "Saves link fees on self-healing and hard declines." : "Blasts link to permanent stolen/lost cards."}
              </p>
            </div>

            <div>
              <span style={{ fontSize: 12, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>FRAUD COMPLIANCE</span>
              <div style={{ fontSize: 20, fontWeight: 900, color: controlMode === "ultron" ? "var(--pitch-emerald)" : "var(--pitch-rose)", marginTop: 4 }}>
                {controlMode === "ultron" ? "Zero Liability Veto" : "High Risk Exposure"}
              </div>
              <p style={{ fontSize: 12, color: "var(--pitch-text-secondary)", marginTop: 4 }}>
                {controlMode === "ultron" ? "Action Authority stops stolen cards at Gate 1." : "Spams unauthorized users, prompting chargebacks."}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
           3. INTERACTIVE FAILURE LAB (Playable Motion Sandbox)
           ==================================================================== */}
      <section id="failure-lab" style={{ maxWidth: 1240, margin: "60px auto", padding: "0 24px", position: "relative", zIndex: 10 }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 800, color: "var(--pitch-cyan)", letterSpacing: 1.5 }}>
            THE INTERACTIVE FAILURE LAB
          </span>
          <h2 style={{ fontSize: 40, fontWeight: 900, marginTop: 6 }}>Trigger a Failure &amp; Watch ULTRON Decide</h2>
          <p style={{ color: "var(--pitch-text-secondary)", marginTop: 6, fontSize: 16 }}>
            Select a payment failure scenario to watch the transaction animate in real-time through the 7-stage deterministic pipeline.
          </p>
        </div>

        <div style={{ background: "var(--pitch-bg-card)", border: "1px solid var(--pitch-border-subtle)", borderRadius: 24, padding: 36, backdropFilter: "blur(16px)" }}>
          {/* Scenario Selector Tabs */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 32 }}>
            {FAILURE_SCENARIOS.map((scen) => (
              <button
                key={scen.id}
                onClick={() => runLabSimulation(scen)}
                style={{
                  background: activeScenario.id === scen.id ? "rgba(6, 182, 212, 0.15)" : "rgba(255, 255, 255, 0.03)",
                  borderColor: activeScenario.id === scen.id ? "var(--pitch-cyan)" : "rgba(255, 255, 255, 0.08)",
                  borderWidth: 1,
                  borderStyle: "solid",
                  borderRadius: 14,
                  padding: "16px 18px",
                  textAlign: "left",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, fontFamily: "var(--pitch-font-mono)", color: "var(--pitch-text-muted)" }}>
                  <span>{scen.declineType.toUpperCase()} DECLINE</span>
                  <span>ATT #{scen.attempt}</span>
                </div>
                <div style={{ fontWeight: 800, fontSize: 14, color: "#fff", marginTop: 4 }}>
                  {scen.name}
                </div>
                <div style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 900, color: scen.decisionColor, marginTop: 8, fontSize: 16 }}>
                  ₹{scen.amount.toLocaleString()}
                </div>
              </button>
            ))}
          </div>

          {/* Animated 7-Stage Visual Pipeline */}
          <div style={{ marginBottom: 32 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 800, color: "var(--pitch-cyan)" }}>
                STAGE 0{simulationStage + 1} OF 07: DETERMINISTIC RECOVERY ENGINE
              </span>
              <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: isSimulating ? "var(--pitch-amber)" : "var(--pitch-emerald)" }}>
                {isSimulating ? "⚡ PROCESSING PIPELINE..." : "✓ RESOLVED"}
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 10 }}>
              {[
                "1. Ingestion",
                "2. Perception",
                "3. Economics",
                "4. Market",
                "5. Authority",
                "6. Execution",
                "7. Truth",
              ].map((stageName, idx) => (
                <div
                  key={stageName}
                  style={{
                    background: simulationStage >= idx ? (simulationStage === idx ? "rgba(6, 182, 212, 0.25)" : "rgba(16, 185, 129, 0.15)") : "rgba(255, 255, 255, 0.03)",
                    borderColor: simulationStage >= idx ? (simulationStage === idx ? "var(--pitch-cyan)" : "rgba(16, 185, 129, 0.4)") : "rgba(255, 255, 255, 0.06)",
                    borderWidth: 1,
                    borderStyle: "solid",
                    borderRadius: 10,
                    padding: 12,
                    textAlign: "center",
                    fontSize: 12,
                    fontFamily: "var(--pitch-font-mono)",
                    fontWeight: 700,
                    color: simulationStage >= idx ? "#fff" : "var(--pitch-text-muted)",
                    transition: "all 0.3s ease",
                    boxShadow: simulationStage === idx ? "0 0 16px rgba(6, 182, 212, 0.3)" : "none",
                  }}
                >
                  {stageName}
                </div>
              ))}
            </div>
          </div>

          {/* Live Decision Card & Microeconomic Math Breakdown */}
          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 24, background: "rgba(15, 23, 42, 0.9)", border: "1px solid var(--pitch-border-subtle)", borderRadius: 18, padding: 28 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{
                  fontFamily: "var(--pitch-font-mono)",
                  fontSize: 14,
                  fontWeight: 900,
                  padding: "6px 14px",
                  borderRadius: 8,
                  background: activeScenario.expectedDecision === "ACT" ? "rgba(16, 185, 129, 0.2)" : (activeScenario.expectedDecision === "WAIT" ? "rgba(245, 158, 11, 0.2)" : "rgba(244, 63, 94, 0.2)"),
                  color: activeScenario.decisionColor,
                  border: `1px solid ${activeScenario.decisionColor}`,
                }}>
                  {activeScenario.decisionBadge}
                </span>
                <span style={{ fontSize: 13, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>
                  Code: {activeScenario.reasonCode}
                </span>
              </div>

              <h3 style={{ fontSize: 24, fontWeight: 900, color: "#fff", marginTop: 14 }}>
                {activeScenario.name}
              </h3>
              <p style={{ fontSize: 14, color: "var(--pitch-text-secondary)", marginTop: 6, lineHeight: 1.5 }}>
                {activeScenario.summary}
              </p>

              <div style={{ marginTop: 20, padding: 14, background: "rgba(255, 255, 255, 0.03)", borderRadius: 10, borderLeft: `3px solid ${activeScenario.decisionColor}` }}>
                <div style={{ fontSize: 11, fontFamily: "var(--pitch-font-mono)", fontWeight: 800, color: "var(--pitch-text-muted)" }}>
                  ACTION AUTHORITY COMPLIANCE VERDICT
                </div>
                <div style={{ fontSize: 13, color: "#fff", marginTop: 4 }}>
                  {activeScenario.laserReason}
                </div>
              </div>
            </div>

            {/* Formula Breakdown Panel */}
            <div style={{ display: "flex", flexDirection: "column", justifyContent: "space-between", background: "rgba(11, 19, 38, 0.8)", border: "1px solid rgba(255, 255, 255, 0.06)", borderRadius: 14, padding: 20 }}>
              <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, fontWeight: 800, color: "var(--pitch-cyan)" }}>
                MICROECONOMIC SCORING (IVEN)
              </span>

              <div style={{ display: "flex", flexDirection: "column", gap: 8, margin: "12px 0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                  <span style={{ color: "var(--pitch-text-muted)" }}>Gross Transaction Amount:</span>
                  <span style={{ fontFamily: "var(--pitch-font-mono)", color: "#fff" }}>₹{activeScenario.amount.toLocaleString()}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                  <span style={{ color: "var(--pitch-text-muted)" }}>Counterfactual ΔP (Lift):</span>
                  <span style={{ fontFamily: "var(--pitch-font-mono)", color: "var(--pitch-cyan)", fontWeight: 700 }}>+{(deltaP * 100).toFixed(1)}%</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                  <span style={{ color: "var(--pitch-text-muted)" }}>Operational Link Fee:</span>
                  <span style={{ fontFamily: "var(--pitch-font-mono)", color: "var(--pitch-rose)" }}>-₹4.00</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                  <span style={{ color: "var(--pitch-text-muted)" }}>Customer Fatigue Penalty:</span>
                  <span style={{ fontFamily: "var(--pitch-font-mono)", color: "var(--pitch-amber)" }}>-₹{activeScenario.fatigueCost.toFixed(2)}</span>
                </div>
              </div>

              <div style={{ borderTop: "1px solid rgba(255, 255, 255, 0.1)", paddingTop: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: "#fff" }}>Net Expected Incremental Value:</span>
                <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 20, fontWeight: 900, color: Number(calculatedIven) > 0 ? "var(--pitch-emerald)" : "var(--pitch-rose)" }}>
                  {Number(calculatedIven) > 0 ? `+₹${calculatedIven}` : `₹${calculatedIven}`}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
           4. MOTION GRAPHICS BENTO GRID (Linear/Stripe Tier)
           ==================================================================== */}
      <section id="bento-grid" style={{ maxWidth: 1240, margin: "80px auto", padding: "0 24px", position: "relative", zIndex: 10 }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 800, color: "var(--pitch-cyan)", letterSpacing: 1.5 }}>
            DEEP SYSTEM ARCHITECTURE
          </span>
          <h2 style={{ fontSize: 40, fontWeight: 900, marginTop: 6 }}>The Machine Behind the Decisions</h2>
          <p style={{ color: "var(--pitch-text-secondary)", marginTop: 6, fontSize: 16 }}>
            Explore the microeconomic and cryptographic primitives powering autonomous payment recovery.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
          {/* Card 1: Interactive Delta P Slider */}
          <div style={{ background: "var(--pitch-bg-card)", border: "1px solid var(--pitch-border-subtle)", borderRadius: 20, padding: 28, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, fontWeight: 800, color: "var(--pitch-cyan)" }}>COUNTERFACTUAL ΔP</span>
                <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 13, fontWeight: 900, color: "var(--pitch-emerald)" }}>+{interactiveDeltaP}% LIFT</span>
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 800, color: "#fff", marginTop: 8 }}>Incremental vs Natural</h3>
              <p style={{ fontSize: 13, color: "var(--pitch-text-secondary)", marginTop: 6, lineHeight: 1.4 }}>
                A payment that recovers naturally is not incremental. Move the slider to observe how true lift is calculated:
              </p>
            </div>

            <div style={{ margin: "24px 0" }}>
              <input
                type="range"
                min="0"
                max="50"
                value={interactiveDeltaP}
                onChange={(e) => setInteractiveDeltaP(Number(e.target.value))}
                style={{ width: "100%", accentColor: "var(--pitch-emerald)" }}
              />
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, fontFamily: "var(--pitch-font-mono)", color: "var(--pitch-text-muted)", marginTop: 8 }}>
                <span>0% (No Lift)</span>
                <span>ΔP = P(int) - P(nat)</span>
                <span>50% (Max Lift)</span>
              </div>
            </div>

            <div style={{ background: "rgba(255, 255, 255, 0.03)", borderRadius: 10, padding: 12, fontSize: 12, color: "var(--pitch-text-secondary)" }}>
              Estimated GMV Lift on ₹10,000 ticket: <strong style={{ color: "var(--pitch-emerald)", fontFamily: "var(--pitch-font-mono)" }}>+₹{(10000 * (interactiveDeltaP / 100)).toLocaleString()}</strong>
            </div>
          </div>

          {/* Card 2: Greedy Knapsack Capacity & Shadow Price */}
          <div style={{ background: "var(--pitch-bg-card)", border: "1px solid var(--pitch-border-subtle)", borderRadius: 20, padding: 28, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, fontWeight: 800, color: "var(--pitch-amber)" }}>CAPACITY ALLOCATION</span>
                <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-emerald)" }}>K = 5 LINKS/RUN</span>
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 800, color: "#fff", marginTop: 8 }}>Equilibrium Shadow Price</h3>
              <p style={{ fontSize: 13, color: "var(--pitch-text-secondary)", marginTop: 6, lineHeight: 1.4 }}>
                Under limited capacity, the marginal accepted opportunity sets the market cutoff price (λ).
              </p>
            </div>

            <div style={{ background: "radial-gradient(circle at center, rgba(6, 182, 212, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%)", border: "1px solid var(--pitch-cyan)", borderRadius: 14, padding: 20, textAlign: "center", margin: "16px 0" }}>
              <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-text-muted)" }}>CURRENT SHADOW PRICE (λ)</span>
              <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 36, fontWeight: 900, color: "var(--pitch-cyan)", marginTop: 2 }}>
                ₹23.96
              </div>
              <span style={{ fontSize: 11, color: "var(--pitch-emerald)" }}>5 of 16 Opportunities Allocated</span>
            </div>

            <div style={{ fontSize: 12, color: "var(--pitch-text-muted)", lineHeight: 1.4 }}>
              Deferred transactions automatically wait until higher-yield batches settle or capacity expands.
            </div>
          </div>

          {/* Card 3: Double-Entry Cryptographic SHA-256 Ledger */}
          <div style={{ background: "var(--pitch-bg-card)", border: "1px solid var(--pitch-border-subtle)", borderRadius: 20, padding: 28, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, fontWeight: 800, color: "var(--pitch-indigo)" }}>TRUTH ENGINE</span>
                <button
                  onClick={mineLedgerBlock}
                  style={{
                    background: "rgba(99, 102, 241, 0.2)",
                    border: "1px solid var(--pitch-indigo)",
                    color: "#fff",
                    fontSize: 11,
                    fontFamily: "var(--pitch-font-mono)",
                    fontWeight: 700,
                    padding: "4px 10px",
                    borderRadius: 6,
                    cursor: "pointer",
                  }}
                >
                  + Simulate Settlement
                </button>
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 800, color: "#fff", marginTop: 8 }}>SHA-256 Hash Chain</h3>
              <p style={{ fontSize: 13, color: "var(--pitch-text-secondary)", marginTop: 6, lineHeight: 1.4 }}>
                LINK_CREATED != RECOVERED. Confirmed revenue is cryptographically chained:
              </p>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 6, margin: "14px 0" }}>
              {ledgerBlocks.slice(0, 2).map((blk) => (
                <div key={blk.id} style={{ background: "rgba(15, 23, 42, 0.9)", border: "1px solid rgba(255, 255, 255, 0.08)", borderRadius: 8, padding: "8px 12px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, fontFamily: "var(--pitch-font-mono)" }}>
                    <span style={{ color: "#fff", fontWeight: 700 }}>BLOCK #{blk.id}</span>
                    <span style={{ color: "var(--pitch-emerald)" }}>{blk.amt}</span>
                  </div>
                  <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 9, color: "var(--pitch-cyan)", wordBreak: "break-all", marginTop: 2 }}>
                    {blk.hash.slice(0, 32)}...
                  </div>
                </div>
              ))}
            </div>

            <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>
              Every entry is reconciled strictly against verified Razorpay bank settlements.
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
           5. SIDE-BY-SIDE MOBILE UX COMPARISON (Customer Experience)
           ==================================================================== */}
      <section id="comparison" style={{ maxWidth: 1140, margin: "80px auto", padding: "0 24px", position: "relative", zIndex: 10 }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 800, color: "var(--pitch-cyan)", letterSpacing: 1.5 }}>
            CUSTOMER LIFETIME VALUE PRESERVATION
          </span>
          <h2 style={{ fontSize: 40, fontWeight: 900, marginTop: 6 }}>The End of Customer Spam Blasts</h2>
          <p style={{ color: "var(--pitch-text-secondary)", marginTop: 6, fontSize: 16 }}>
            Compare the merchant-customer experience between legacy dunning vs ULTRON autonomous recovery.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
          {/* Without ULTRON */}
          <div style={{ background: "rgba(244, 63, 94, 0.05)", border: "1px solid rgba(244, 63, 94, 0.3)", borderRadius: 24, padding: 32 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--pitch-rose)", fontWeight: 800, fontSize: 14 }}>
              <span>✕</span> TRADITIONAL DUNNING BLASTS
            </div>
            <h3 style={{ fontSize: 22, fontWeight: 800, color: "#fff", marginTop: 8 }}>High Fatigue, High Churn</h3>

            <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 20 }}>
              <div style={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(244, 63, 94, 0.2)", borderRadius: 12, padding: 14, fontSize: 13 }}>
                <span style={{ color: "var(--pitch-rose)", fontWeight: 700 }}>2:04 AM:</span> SMS blast sent for transient bank timeout. Customer annoyed.
              </div>
              <div style={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(244, 63, 94, 0.2)", borderRadius: 12, padding: 14, fontSize: 13 }}>
                <span style={{ color: "var(--pitch-rose)", fontWeight: 700 }}>2:15 AM:</span> Automatic retry fails on permanent stolen card. Merchant pays ₹4.00.
              </div>
              <div style={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(244, 63, 94, 0.2)", borderRadius: 12, padding: 14, fontSize: 13 }}>
                <span style={{ color: "var(--pitch-rose)", fontWeight: 700 }}>6:00 AM:</span> 4th email alert sent. Customer unsubscribes and churns.
              </div>
            </div>
          </div>

          {/* With ULTRON */}
          <div style={{ background: "rgba(16, 185, 129, 0.05)", border: "1px solid rgba(16, 185, 129, 0.3)", borderRadius: 24, padding: 32 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--pitch-emerald)", fontWeight: 800, fontSize: 14 }}>
              <span>✓</span> ULTRON AUTONOMOUS CONTROL
            </div>
            <h3 style={{ fontSize: 22, fontWeight: 800, color: "#fff", marginTop: 8 }}>Contextual, Intelligent, High-Yield</h3>

            <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 20 }}>
              <div style={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(16, 185, 129, 0.2)", borderRadius: 12, padding: 14, fontSize: 13 }}>
                <span style={{ color: "var(--pitch-emerald)", fontWeight: 700 }}>Intelligent Hold:</span> 48-minute observation window allows transient errors to self-heal.
              </div>
              <div style={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(16, 185, 129, 0.2)", borderRadius: 12, padding: 14, fontSize: 13 }}>
                <span style={{ color: "var(--pitch-emerald)", fontWeight: 700 }}>Fraud Veto:</span> Action Authority permanently blocks retries on stolen/lost cards.
              </div>
              <div style={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(16, 185, 129, 0.2)", borderRadius: 12, padding: 14, fontSize: 13 }}>
                <span style={{ color: "var(--pitch-emerald)", fontWeight: 700 }}>Prime Delivery:</span> 1 context-rich WhatsApp recovery link sent at 10:15 AM. 1-tap UPI paid.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
           6. BOTTOM CTA BANNER
           ==================================================================== */}
      <section style={{ maxWidth: 1000, margin: "60px auto 100px auto", padding: "48px", background: "linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.12) 100%)", border: "1px solid var(--pitch-border-glow)", borderRadius: 28, textAlign: "center" }}>
        <h2 style={{ fontSize: 36, fontWeight: 900, color: "#fff" }}>
          Ready to Recover GMV Without Burning Trust?
        </h2>
        <p style={{ color: "var(--pitch-text-secondary)", fontSize: 16, maxWidth: 640, margin: "12px auto 28px auto", lineHeight: 1.5 }}>
          Experience the autonomous economic control plane live. Watch the full 5-minute video pitch or open the merchant recovery dashboard.
        </p>

        <div style={{ display: "flex", justifyContent: "center", gap: 16 }}>
          <Link
            href="/pitch/video"
            style={{
              background: "linear-gradient(135deg, var(--pitch-emerald), #059669)",
              color: "#000",
              fontWeight: 800,
              padding: "14px 28px",
              borderRadius: 10,
              textDecoration: "none",
              fontSize: 14,
              boxShadow: "0 4px 20px rgba(16, 185, 129, 0.4)",
            }}
          >
            ▶ Watch 5-Minute Motion Presentation
          </Link>
          <Link
            href="/dashboard"
            style={{
              background: "rgba(255, 255, 255, 0.05)",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              color: "#fff",
              fontWeight: 700,
              padding: "14px 24px",
              borderRadius: 10,
              textDecoration: "none",
              fontSize: 14,
            }}
          >
            Launch Merchant Dashboard →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ textAlign: "center", padding: "40px 24px", borderTop: "1px solid rgba(255, 255, 255, 0.06)", color: "var(--pitch-text-muted)", fontSize: 13 }}>
        <p>ULTRON • Autonomous Economic Control Plane for Razorpay Recovery • Next.js 16 Motion Showcase</p>
      </footer>
    </div>
  );
}
