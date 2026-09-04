"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useMotionController, MOTION_ACTS } from "../useMotionController";
import "../pitch.css";

interface SyntheticItem {
  id: string;
  name: string;
  amount: number;
  iven: number;
  dp: number;
  dec: "ACT" | "WAIT" | "ABSTAIN";
  reason: string;
}

const SYNTHETIC_DATA: SyntheticItem[] = [
  { id: "synth_09_corp", name: "Corp Annual Software License", amount: 25000, iven: 6996, dp: 0.28, dec: "ACT", reason: "network_timeout" },
  { id: "synth_14_cloud", name: "Multi-Region GPU Compute", amount: 18000, iven: 3236, dp: 0.18, dec: "ACT", reason: "bank_gateway_timeout" },
  { id: "synth_07_ent", name: "Enterprise Sub Renewal", amount: 15000, iven: 3296, dp: 0.22, dec: "ACT", reason: "bank_gateway_timeout" },
  { id: "synth_08_saas", name: "Mid-tier SaaS Plan Attempt 2", amount: 8500, iven: 2716, dp: 0.32, dec: "ACT", reason: "insufficient_funds" },
  { id: "synth_12_retainer", name: "Legal & Advisory Retainer", amount: 12000, iven: 2396, dp: 0.20, dec: "ACT", reason: "insufficient_funds" },
  { id: "synth_15_training", name: "Enterprise Training Workshop", amount: 6000, iven: 2096, dp: 0.35, dec: "WAIT", reason: "insufficient_funds" },
  { id: "synth_11_hardware", name: "Hardware Lease Deposit", amount: 20000, iven: 1996, dp: 0.10, dec: "WAIT", reason: "payment_auth_failed" },
  { id: "synth_10_ecom", name: "Consumer Order Checkout", amount: 3500, iven: 1046, dp: 0.30, dec: "WAIT", reason: "insufficient_funds" },
  { id: "synth_01_stolen", name: "Stolen or Lost Card", amount: 4500, iven: 0, dp: 0.00, dec: "ABSTAIN", reason: "stolen_card" },
];

export default function MotionVideoPage() {
  const {
    currentTime,
    isPlaying,
    isMuted,
    activeActIndex,
    currentAct,
    setTime,
    togglePlay,
    toggleMute,
    jumpToAct,
    restart,
  } = useMotionController();

  const [scale, setScale] = useState<number>(1);
  const particleCanvasRef = useRef<HTMLCanvasElement | null>(null);

  // Auto-scaler for crisp 1920x1080 display on any resolution
  useEffect(() => {
    function handleResize() {
      const targetW = 1920;
      const targetH = 1080;
      const windowW = window.innerWidth;
      const windowH = window.innerHeight;
      const s = Math.min(windowW / targetW, windowH / targetH);
      setScale(s);
    }
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Background Particles Renderer
  useEffect(() => {
    const canvas = particleCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = 1920;
    canvas.height = 1080;

    const particles: Array<{ x: number; y: number; vx: number; vy: number; radius: number; alpha: number; color: string }> = [];
    for (let i = 0; i < 70; i++) {
      particles.push({
        x: Math.random() * 1920,
        y: Math.random() * 1080,
        vx: (Math.random() - 0.5) * 0.5,
        vy: -0.3 - Math.random() * 0.7,
        radius: Math.random() * 2 + 1,
        alpha: Math.random() * 0.4 + 0.2,
        color: Math.random() > 0.6 ? "#10b981" : (Math.random() > 0.5 ? "#06b6d4" : "#6366f1"),
      });
    }

    let animId: number;
    function render() {
      if (!ctx) return;
      ctx.clearRect(0, 0, 1920, 1080);
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.y < 0) { p.y = 1080; p.x = Math.random() * 1920; }
        if (p.x < 0) p.x = 1920;
        if (p.x > 1920) p.x = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.shadowBlur = 8;
        ctx.shadowColor = p.color;
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      animId = requestAnimationFrame(render);
    }
    render();

    return () => cancelAnimationFrame(animId);
  }, []);

  // Format time
  const min = Math.floor(currentTime / 60);
  const sec = Math.floor(currentTime % 60);
  const timeFormatted = `${min.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")} / 05:00`;
  const progressPct = (currentTime / 300) * 100;

  // Dynamic values per act
  const actProgressSec = currentTime - currentAct.start;
  const dynIvenAmount = [4500, 15000, 25000, 12000, 8500][Math.floor((actProgressSec / 5) % 5)] || 15000;
  const dynIvenVal = (dynIvenAmount * 0.22 - 4.0 - 2.5).toFixed(2);
  const pipelineHighlightedNode = Math.floor((actProgressSec / 50) * 7);

  return (
    <div className="pitch-cinema-body">
      <div style={{ transform: `scale(${scale})`, transformOrigin: "center center" }}>
        <div id="canvas-viewport">
          {/* Particle Background & Cyber Scanlines */}
          <canvas ref={particleCanvasRef} id="particle-canvas" />
          <div className="cyber-grid" />
          <div className="scanline-layer" />

          {/* ====================================================================
               1. PERSISTENT TOP HUD
               ==================================================================== */}
          <header id="top-hud">
            <div className="hud-left">
              <Link href="/pitch" className="brand-badge" style={{ textDecoration: "none" }}>
                <div className="brand-icon">⚡</div>
                <span>ULTRON</span>
              </Link>
              <span className="version-pill">v6.1 NEXT.JS</span>
            </div>

            <nav className="hud-center">
              {MOTION_ACTS.map((act, i) => (
                <div
                  key={act.id}
                  className={`act-tab ${activeActIndex === i ? "active" : ""}`}
                  onClick={() => jumpToAct(i)}
                >
                  <span className="act-num">0{act.id}</span> {act.name}
                </div>
              ))}
            </nav>

            <div className="hud-right">
              <div className="time-display">
                <span>⏱</span>
                <span>{timeFormatted}</span>
              </div>
              <button className="control-btn" onClick={togglePlay} title="Play/Pause [Space]">
                {isPlaying ? "⏸" : "▶"}
              </button>
              <button className="control-btn" onClick={restart} title="Restart [R]">
                ↺
              </button>
              <button className={`control-btn ${isMuted ? "active" : ""}`} onClick={toggleMute} title="Mute [M]">
                {isMuted ? "🔇" : "🔊"}
              </button>
            </div>
          </header>

          {/* 300-Second Interactive Scrubber */}
          <div
            id="timeline-scrubber-bar"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const clickX = e.clientX - rect.left;
              const pct = Math.max(0, Math.min(1, clickX / rect.width));
              setTime(pct * 300);
            }}
          >
            <div id="timeline-progress" style={{ width: `${progressPct}%` }} />
          </div>

          {/* ====================================================================
               2. SCENE STAGE (The 6 Motion Graphic Acts)
               ==================================================================== */}
          <main id="scene-stage">

            {/* ACT 1: The $68B Blindspot & Naive Retries */}
            <section className={`scene ${activeActIndex === 0 ? "active" : ""}`} id="scene-act-1">
              <div className="scene-header">
                <div className="scene-tag">{currentAct.tag}</div>
                <h1 className="scene-title">{currentAct.title}</h1>
                <p className="scene-subtitle">{currentAct.subtitle}</p>
              </div>

              <div className="act1-grid">
                <div className="act1-visual">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--pitch-border-subtle)", paddingBottom: 12 }}>
                    <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 700, color: "var(--pitch-rose)" }}>STREAMING CHECKOUT DECLINES</span>
                    <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-text-muted)" }}>Simulated Razorpay Ingestion</span>
                  </div>

                  <div className="failing-stream-container">
                    <div className="stream-card">
                      <div>
                        <div style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>Bank Gateway Timeout</div>
                        <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-text-muted)" }}>bank_gateway_timeout • 58% self-heals naturally</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 800, color: "#fff" }}>₹15,000</div>
                        <span className="badge-fail">DECLINED</span>
                      </div>
                    </div>
                    <div className="stream-card">
                      <div>
                        <div style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>Insufficient Funds Attempt #2</div>
                        <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-text-muted)" }}>insufficient_funds • High customer fatigue</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 800, color: "#fff" }}>₹8,500</div>
                        <span className="badge-fail">DECLINED</span>
                      </div>
                    </div>
                    <div className="stream-card">
                      <div>
                        <div style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>Stolen Card Reported by Issuer</div>
                        <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-text-muted)" }}>stolen_card • Hard Decline (Fraud Risk)</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 800, color: "#fff" }}>₹4,500</div>
                        <span className="badge-fail">DECLINED</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, color: "var(--pitch-text-muted)", display: "flex", justifyContent: "space-between" }}>
                    <span>Delivery Cost: ₹4.00/link + ₹0.85/WhatsApp</span>
                    <span>Counterfactual Ignored: 100%</span>
                  </div>
                </div>

                <div className="act1-stats-column">
                  <div className="stat-card-leakage">
                    <div className="num">$68.4B</div>
                    <div style={{ fontWeight: 700, fontSize: 18, color: "#fff" }}>Global Annual Failed Payment Waste</div>
                    <p style={{ fontSize: 13, color: "var(--pitch-text-secondary)", marginTop: 6, lineHeight: 1.4 }}>
                      Standard gateways treat every decline identically—ignoring whether an error is transient, permanent fraud, or already self-healing.
                    </p>
                  </div>

                  <div className="counterfactual-box">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>The Counterfactual Fallacy</span>
                      <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, color: "var(--pitch-cyan)", fontWeight: 700 }}>58% Natural Self-Healing</span>
                    </div>
                    <div className="decay-curve-bar">
                      <div className="decay-fill-natural" />
                    </div>
                    <p style={{ fontSize: 12, color: "var(--pitch-text-muted)", lineHeight: 1.4 }}>
                      Traditional dunning takes 100% credit for revenue that was already going to recover on its own without spending a single link fee.
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* ACT 2: The Paradigm Shift & IVEN */}
            <section className={`scene ${activeActIndex === 1 ? "active" : ""}`} id="scene-act-2">
              <div className="scene-header">
                <div className="scene-tag">{currentAct.tag}</div>
                <h1 className="scene-title">{currentAct.title}</h1>
                <p className="scene-subtitle">{currentAct.subtitle}</p>
              </div>

              <div className="act2-grid">
                <div className="formula-stage-box">
                  <div className="math-banner">
                    IVEN = (ΔP × Amount) - Costs
                  </div>

                  <div className="formula-breakdown">
                    <div className="f-item">
                      <div>
                        <div style={{ fontWeight: 700, color: "#fff" }}>Incremental Lift (ΔP)</div>
                        <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>P(intervention) - P(natural)</div>
                      </div>
                      <div style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 800, color: "var(--pitch-cyan)" }}>+22.0% Lift</div>
                    </div>

                    <div className="f-item rose">
                      <div>
                        <div style={{ fontWeight: 700, color: "#fff" }}>Operational Delivery Cost</div>
                        <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Razorpay link creation + WhatsApp API</div>
                      </div>
                      <div style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 800, color: "var(--pitch-rose)" }}>-₹4.00 / link</div>
                    </div>

                    <div className="f-item amber">
                      <div>
                        <div style={{ fontWeight: 700, color: "#fff" }}>Non-Linear Fatigue Penalty</div>
                        <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Exponential penalty across attempt history</div>
                      </div>
                      <div style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 800, color: "var(--pitch-amber)" }}>-₹2.50 to -₹15.00</div>
                    </div>
                  </div>

                  <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 10, padding: 14, fontSize: 12, color: "var(--pitch-text-secondary)", lineHeight: 1.4 }}>
                    <strong style={{ color: "var(--pitch-emerald)" }}>Invariant Rule:</strong> Hard declines (stolen/lost/pickup) are strictly hard-clamped at ΔP = 0.00 and IVEN ≤ 0.
                  </div>
                </div>

                <div className="act2-interactive-calculator">
                  <div style={{ fontWeight: 800, fontSize: 18, color: "#fff" }}>Real-Time Expected Value Engine</div>
                  <p style={{ fontSize: 13, color: "var(--pitch-text-secondary)" }}>
                    Continuously recalculating net recovery value across candidate transactions:
                  </p>

                  <div className="calc-live-result">
                    <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 700, color: "var(--pitch-text-muted)" }}>EXPECTED INCREMENTAL VALUE (IVEN)</span>
                    <div className="res-value" id="calc-dyn-iven">+₹{Number(dynIvenVal).toLocaleString()}</div>
                    <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, color: "var(--pitch-emerald)" }}>Positive Net Economic Yield</span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: 12, fontFamily: "var(--pitch-font-mono)" }}>
                    <div style={{ background: "rgba(255,255,255,0.03)", padding: 12, borderRadius: 8 }}>
                      <span style={{ color: "var(--pitch-text-muted)" }}>Natural Recovery:</span><br />
                      <strong style={{ color: "#fff" }}>48.0% (₹7,200)</strong>
                    </div>
                    <div style={{ background: "rgba(255,255,255,0.03)", padding: 12, borderRadius: 8 }}>
                      <span style={{ color: "var(--pitch-text-muted)" }}>Intervention Prob:</span><br />
                      <strong style={{ color: "var(--pitch-cyan)" }}>70.0% (₹10,500)</strong>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* ACT 3: Inside the 7-Stage Pipeline Machine */}
            <section className={`scene ${activeActIndex === 2 ? "active" : ""}`} id="scene-act-3">
              <div className="scene-header">
                <div className="scene-tag">{currentAct.tag}</div>
                <h1 className="scene-title">{currentAct.title}</h1>
                <p className="scene-subtitle">{currentAct.subtitle}</p>
              </div>

              <div className="pipeline-conveyor">
                {[
                  { step: "01", name: "Ingestion & Interception", desc: "HMAC-SHA256 verified webhooks & 1-line client drop-in (sdk/ultron.js)." },
                  { step: "02", name: "Perception Normalization", desc: "Decline taxonomy classification (hard/soft) and customer attempt tracking." },
                  { step: "03", name: "Economic Reasoning", desc: "Bayesian Beta calibration & IVEN calculation with non-linear fatigue." },
                  { step: "04", name: "Recovery Market", desc: "Greedy knapsack portfolio allocation under capacity cap K=5 & Shadow Price λ." },
                  { step: "05", name: "Action Authority", desc: "Independent 5-gate compliance check with unconditional veto power." },
                  { step: "06", name: "Resilient Execution", desc: "Circuit breaker, dead-letter retries, and omnichannel WhatsApp/Email delivery." },
                  { step: "07", name: "Truth Engine", desc: "Double-entry SHA-256 ledger & authoritative bank settlement reconciliation." },
                ].map((node, i) => (
                  <div key={node.step} className={`pipeline-node ${pipelineHighlightedNode === i ? "highlight" : ""}`}>
                    <div className="node-step">Stage {node.step}</div>
                    <div className="node-name">{node.name}</div>
                    <div className="node-desc">{node.desc}</div>
                    <div className="node-indicator" />
                  </div>
                ))}
              </div>
            </section>

            {/* ACT 4: The Decision Triad & Shadow Price */}
            <section className={`scene ${activeActIndex === 3 ? "active" : ""}`} id="scene-act-4">
              <div className="scene-header">
                <div className="scene-tag">{currentAct.tag}</div>
                <h1 className="scene-title">{currentAct.title}</h1>
                <p className="scene-subtitle">{currentAct.subtitle}</p>
              </div>

              <div className="act4-layout">
                <div className="triad-card-group">
                  <div className="triad-box act">
                    <div className="triad-pill">ACT</div>
                    <div>
                      <div style={{ fontWeight: 800, fontSize: 16, color: "#fff" }}>Allocated for Immediate Execution</div>
                      <div style={{ fontSize: 13, color: "var(--pitch-text-secondary)", marginTop: 2 }}>
                        High positive IVEN ranked within the top K=5 capacity limit.
                      </div>
                    </div>
                  </div>

                  <div className="triad-box wait">
                    <div className="triad-pill">WAIT</div>
                    <div>
                      <div style={{ fontWeight: 800, fontSize: 16, color: "#fff" }}>Deferred to Next Available Sweep</div>
                      <div style={{ fontSize: 13, color: "var(--pitch-text-secondary)", marginTop: 2 }}>
                        Positive IVEN, but below this run's marginal Shadow Price (λ = ₹23.96).
                      </div>
                    </div>
                  </div>

                  <div className="triad-box abstain">
                    <div className="triad-pill">ABSTAIN</div>
                    <div>
                      <div style={{ fontWeight: 800, fontSize: 16, color: "#fff" }}>Rational Inaction (Saved Capital)</div>
                      <div style={{ fontSize: 13, color: "var(--pitch-text-secondary)", marginTop: 2 }}>
                        Negative IVEN, low data confidence, or fraudulent hard decline. Doing nothing saves money.
                      </div>
                    </div>
                  </div>
                </div>

                <div className="knapsack-monitor">
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                      <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 800, color: "var(--pitch-cyan)" }}>GREEDY KNAPSACK ALLOCATION (K=5)</span>
                      <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-emerald)" }}>5 OF 16 ACCEPTED</span>
                    </div>

                    <div className="knapsack-list">
                      {SYNTHETIC_DATA.map((item, idx) => (
                        <div key={item.id} className={`knapsack-row ${idx < 5 ? "allocated" : ""}`}>
                          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <span style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 800, color: idx < 5 ? "var(--pitch-emerald)" : "var(--pitch-text-muted)" }}>
                              #{idx + 1}
                            </span>
                            <span style={{ color: "#fff", fontWeight: 600 }}>{item.name}</span>
                          </div>
                          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                            <span style={{ fontFamily: "var(--pitch-font-mono)", color: "var(--pitch-text-secondary)" }}>₹{item.amount.toLocaleString()}</span>
                            <span style={{ fontFamily: "var(--pitch-font-mono)", fontWeight: 700, color: idx < 5 ? "var(--pitch-emerald)" : (item.dec === "WAIT" ? "var(--pitch-amber)" : "var(--pitch-rose)") }}>
                              IVEN: +₹{item.iven}
                            </span>
                            <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 10, padding: "2px 6px", borderRadius: 4, background: idx < 5 ? "rgba(16,185,129,0.2)" : "rgba(255,255,255,0.06)", color: idx < 5 ? "var(--pitch-emerald)" : "var(--pitch-text-secondary)" }}>
                              {item.dec}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="shadow-price-badge">
                    <div>
                      <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-text-muted)" }}>MARGINAL RUN CUTOFF</span>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>Equilibrium Shadow Price (λ)</div>
                    </div>
                    <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 24, fontWeight: 900, color: "var(--pitch-cyan)" }}>₹23.96</div>
                  </div>
                </div>
              </div>
            </section>

            {/* ACT 5: Action Authority & Compliance Gate */}
            <section className={`scene ${activeActIndex === 4 ? "active" : ""}`} id="scene-act-5">
              <div className="scene-header">
                <div className="scene-tag">{currentAct.tag}</div>
                <h1 className="scene-title">{currentAct.title}</h1>
                <p className="scene-subtitle">{currentAct.subtitle}</p>
              </div>

              <div className="act5-scanner-grid">
                <div className="laser-gate-cluster">
                  <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 700, color: "var(--pitch-text-muted)" }}>THE 5 COMPLIANCE VETO GATES</div>

                  <div className="laser-gate-item pass">
                    <div>
                      <div style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>1. Hard Decline Check</div>
                      <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Zero auto-contact after fraud or stolen card declination</div>
                    </div>
                    <span className="gate-status">PASSED</span>
                  </div>

                  <div className="laser-gate-item pass">
                    <div>
                      <div style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>2. Retry Cap Check</div>
                      <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Hard ceiling at 3 attempts to prevent issuer harassment</div>
                    </div>
                    <span className="gate-status">PASSED</span>
                  </div>

                  <div className="laser-gate-item pass">
                    <div>
                      <div style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>3. Kill Switch Check</div>
                      <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Emergency operator cutoff disengaged</div>
                    </div>
                    <span className="gate-status">PASSED</span>
                  </div>

                  <div className="laser-gate-item pass">
                    <div>
                      <div style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>4. Confidence Recheck</div>
                      <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Requires sufficient observational confidence</div>
                    </div>
                    <span className="gate-status">PASSED</span>
                  </div>

                  <div className="laser-gate-item pass">
                    <div>
                      <div style={{ fontWeight: 700, color: "#fff", fontSize: 14 }}>5. Capacity Recheck</div>
                      <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Must be within active batch allocation cap K=5</div>
                    </div>
                    <span className="gate-status">PASSED</span>
                  </div>
                </div>

                <div className="enterprise-shield-box">
                  <div style={{ fontWeight: 800, fontSize: 18, color: "#fff" }}>Enterprise Mission-Critical Security</div>
                  <p style={{ fontSize: 13, color: "var(--pitch-text-secondary)", lineHeight: 1.4 }}>
                    Built to run silently in production with zero-trust architectural boundaries:
                  </p>

                  <div className="shield-spec-item">
                    <div className="shield-icon">🛡️</div>
                    <div>
                      <div style={{ fontWeight: 700, color: "#fff" }}>Scrypt + AES-256-GCM</div>
                      <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>Envelope encryption for merchant credentials</div>
                    </div>
                  </div>

                  <div className="shield-spec-item">
                    <div className="shield-icon">⚡</div>
                    <div>
                      <div style={{ fontWeight: 700, color: "#fff" }}>1-Line Client Drop-In</div>
                      <div style={{ fontSize: 12, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>&lt;script src=&quot;.../sdk/ultron.js&quot;&gt;</div>
                    </div>
                  </div>

                  <div className="shield-spec-item">
                    <div className="shield-icon">💾</div>
                    <div>
                      <div style={{ fontWeight: 700, color: "#fff" }}>Dual-Engine Persistence</div>
                      <div style={{ fontSize: 12, color: "var(--pitch-text-muted)" }}>SQLite WAL + Supabase PostgreSQL pool</div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* ACT 6: Causal Truth, Cryptographic Ledger & ROI */}
            <section className={`scene ${activeActIndex === 5 ? "active" : ""}`} id="scene-act-6">
              <div className="scene-header">
                <div className="scene-tag">{currentAct.tag}</div>
                <h1 className="scene-title">{currentAct.title}</h1>
                <p className="scene-subtitle">{currentAct.subtitle}</p>
              </div>

              <div className="act6-grid">
                <div className="blockchain-stack">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 12, fontWeight: 800, color: "var(--pitch-cyan)" }}>DOUBLE-ENTRY CRYPTOGRAPHIC LEDGER</span>
                    <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, color: "var(--pitch-text-muted)" }}>SHA-256 HASH CHAIN</span>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    <div className="block-entry">
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                        <span style={{ fontWeight: 700, color: "#fff" }}>LEDGER ENTRY #2</span>
                        <span style={{ fontFamily: "var(--pitch-font-mono)", color: "var(--pitch-emerald)" }}>CONFIRMED SETTLED</span>
                      </div>
                      <div className="block-hash">SHA-256: 3a4b9c1d8e7f2015948271038495aebc8172635490abcedf1234567890abcdef</div>
                      <div style={{ fontSize: 11, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>
                        Debit: bank_settlement • Credit: recovered_revenue • ₹15,000.00
                      </div>
                    </div>

                    <div className="block-entry">
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                        <span style={{ fontWeight: 700, color: "#fff" }}>LEDGER ENTRY #1 (GENESIS)</span>
                        <span style={{ fontFamily: "var(--pitch-font-mono)", color: "var(--pitch-emerald)" }}>CONFIRMED SETTLED</span>
                      </div>
                      <div className="block-hash">SHA-256: 0000000000000000000000000000000000000000000000000000000000000000</div>
                      <div style={{ fontSize: 11, color: "var(--pitch-text-muted)", fontFamily: "var(--pitch-font-mono)" }}>
                        Debit: bank_settlement • Credit: recovered_revenue • ₹25,000.00
                      </div>
                    </div>
                  </div>
                </div>

                <div className="impact-scoreboard">
                  <div className="impact-kpi-card">
                    <div className="kpi-num">+22.4%</div>
                    <div style={{ fontWeight: 800, fontSize: 18, color: "#fff", marginTop: 4 }}>Verified Net Recovered GMV Lift</div>
                    <p style={{ fontSize: 13, color: "var(--pitch-text-secondary)", marginTop: 6, lineHeight: 1.4 }}>
                      Statistically significant lift proven against a 5% holdout control group via paired Student&apos;s t-tests (df=4, p &lt; 0.05).
                    </p>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                    <div style={{ background: "var(--pitch-bg-panel)", border: "1px solid var(--pitch-border-subtle)", borderRadius: 14, padding: 18 }}>
                      <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 28, fontWeight: 900, color: "var(--pitch-cyan)" }}>-64.2%</div>
                      <div style={{ fontWeight: 700, fontSize: 13, color: "#fff", marginTop: 2 }}>Wasted Message Spend</div>
                      <div style={{ fontSize: 11, color: "var(--pitch-text-muted)", marginTop: 2 }}>Saved by rational abstention</div>
                    </div>

                    <div style={{ background: "var(--pitch-bg-panel)", border: "1px solid var(--pitch-border-subtle)", borderRadius: 14, padding: 18 }}>
                      <div style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 28, fontWeight: 900, color: "var(--pitch-emerald)" }}>0.0%</div>
                      <div style={{ fontWeight: 700, fontSize: 13, color: "#fff", marginTop: 2 }}>Fraud Liability Penalties</div>
                      <div style={{ fontSize: 11, color: "var(--pitch-text-muted)", marginTop: 2 }}>Vetoed by Action Authority</div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

          </main>

          {/* ====================================================================
               3. PERSISTENT BOTTOM DOCK
               ==================================================================== */}
          <footer id="bottom-dock">
            <div className="dock-narrator">
              <div className="voice-wave">
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
                <div className="wave-bar" />
              </div>
              <span style={{ fontFamily: "var(--pitch-font-mono)", fontSize: 11, fontWeight: 800, color: "var(--pitch-cyan)" }}>AI NARRATOR</span>
            </div>

            <div className="caption-karaoke-box">
              <p className="caption-karaoke-text" id="caption-text">
                [{currentAct.name}] {currentAct.narrative}
              </p>
            </div>

            <div className="dock-hotkeys">
              <span>Controls:</span>
              <span className="hotkey-pill">Space</span> Play/Pause
              <span className="hotkey-pill">← / →</span> Seek 10s
              <span className="hotkey-pill">1-6</span> Jump Act
              <span className="hotkey-pill">R</span> Restart
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
