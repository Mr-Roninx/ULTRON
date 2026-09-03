"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Zap,
  CheckCircle2,
  XCircle,
  Clock,
  Activity,
  Sparkles,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  Copy,
  Check,
  CreditCard,
  Radio,
  Flame,
  ShoppingBag,
  RotateCcw,
} from "lucide-react";
import { api } from "../../../lib/auth";

interface PlaygroundConfig {
  tenant_id: string;
  environment: "live" | "test";
  is_live: boolean;
  key_id: string;
  masked_key_id: string;
  safety_ceiling_paise: number;
  capacity_limit: number;
}

interface PipelineStageData {
  stage_number: number;
  stage_name: string;
  status: "PASSED" | "BLOCKED" | "DEFERRED" | "ABSTAINED" | "FAILED" | "SKIPPED" | "READY_FOR_SETTLEMENT" | "RECONCILED";
  timestamp: string;
  data: Record<string, any>;
}

interface SimulationResponse {
  success: boolean;
  opportunity_id: string;
  scenario: string;
  final_verdict: "AUTHORIZED" | "BLOCKED" | "ABSTAIN" | "WAIT";
  execution_status: string;
  link_url?: string;
  stages: PipelineStageData[];
}

export default function RecoveryPlaygroundPage() {
  const [config, setConfig] = useState<PlaygroundConfig | null>(null);
  const [configLoading, setConfigLoading] = useState(true);

  // Playground Checkout Form State
  const [amountPaise, setAmountPaise] = useState<number>(100); // Default ₹1.00 safe micropayment
  const [customAmount, setCustomAmount] = useState<string>("1.00");
  const [customerName, setCustomerName] = useState("Aarav Patel");
  const [customerEmail, setCustomerEmail] = useState("aarav.patel@example.com");
  const [customerPhone, setCustomerPhone] = useState("+919876543210");
  const [isOpeningCheckout, setIsOpeningCheckout] = useState(false);

  // Simulation & Pipeline State
  const [runningScenario, setRunningScenario] = useState<string | null>(null);
  const [activeTrace, setActiveTrace] = useState<SimulationResponse | null>(null);
  const [activeStageNumber, setActiveStageNumber] = useState<number>(0);
  const [expandedStage, setExpandedStage] = useState<number | null>(null);
  const [reconciling, setReconciling] = useState(false);
  const [reconciledResult, setReconciledResult] = useState<any>(null);
  const [copiedLink, setCopiedLink] = useState(false);

  // Fetch Playground Config
  const fetchConfig = useCallback(async () => {
    try {
      const data = await api<PlaygroundConfig>("/v1/playground/config");
      setConfig(data);
    } catch (e) {
      console.error("Failed to load playground config:", e);
    } finally {
      setConfigLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  // Handle Preset Amount Selection
  const handleSelectAmount = (paise: number) => {
    setAmountPaise(paise);
    setCustomAmount((paise / 100).toFixed(2));
  };

  const handleCustomAmountChange = (val: string) => {
    setCustomAmount(val);
    const parsed = parseFloat(val);
    if (!isNaN(parsed) && parsed > 0) {
      setAmountPaise(Math.round(parsed * 100));
    }
  };

  // Dynamically load Razorpay checkout script
  const loadRazorpayScript = (): Promise<boolean> => {
    return new Promise((resolve) => {
      if (typeof window !== "undefined" && (window as any).Razorpay) {
        resolve(true);
        return;
      }
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  // Launch Real Razorpay Checkout Modal
  const handleOpenRazorpayCheckout = async () => {
    setIsOpeningCheckout(true);
    try {
      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        alert("Failed to load Razorpay Checkout SDK. Please check your internet connection.");
        return;
      }

      // 1. Create order on backend
      const orderRes = await api<{
        success: boolean;
        order_id: string;
        amount: number;
        currency: string;
        key_id: string;
      }>("/v1/playground/create-order", {
        method: "POST",
        body: JSON.stringify({
          amount_paise: amountPaise,
          currency: "INR",
          description: `ULTRON Recovery Playground Test (₹${(amountPaise / 100).toFixed(2)})`,
        }),
      });

      const options = {
        key: orderRes.key_id,
        amount: orderRes.amount,
        currency: orderRes.currency,
        name: "ULTRON Cloud / Apex SaaS",
        description: `Recovery Simulation Order #${orderRes.order_id.slice(-6)}`,
        image: "https://cdn.razorpay.com/logos/7K3b6d18wHwKzL_medium.png",
        order_id: orderRes.order_id,
        prefill: {
          name: customerName,
          email: customerEmail,
          contact: customerPhone,
        },
        notes: {
          system: "ULTRON Autonomous Recovery Control Plane",
          playground_test: "true",
        },
        theme: {
          color: "#3b82f6",
        },
        handler: async function (response: any) {
          // Payment Success in Razorpay Modal
          alert(`Payment captured successfully! Razorpay Payment ID: ${response.razorpay_payment_id}`);
        },
        modal: {
          ondismiss: function () {
            // Dismissed modal -> simulate failure or prompt user
          },
        },
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.on("payment.failed", function (response: any) {
        // Automatically trigger soft decline scenario on failure event
        handleTriggerScenario("soft_insufficient_funds", {
          errorCode: response.error?.code || "PAYMENT_FAILED",
          errorDesc: response.error?.description || "Payment failed at gateway",
        });
      });
      rzp.open();
    } catch (err: any) {
      alert(`Razorpay Checkout error: ${err.message}`);
    } finally {
      setIsOpeningCheckout(false);
    }
  };

  // Run a full 7-stage simulation scenario
  const handleTriggerScenario = async (scenarioType: string, overrideParams?: any) => {
    setRunningScenario(scenarioType);
    setActiveTrace(null);
    setReconciledResult(null);
    setActiveStageNumber(1);

    try {
      const res = await api<SimulationResponse>("/v1/playground/simulate-scenario", {
        method: "POST",
        body: JSON.stringify({
          scenario: scenarioType,
          amount_paise: amountPaise,
          customer_name: customerName,
          customer_email: customerEmail,
          customer_contact: customerPhone,
          ...overrideParams,
        }),
      });

      setActiveTrace(res);

      // Animate through all 7 stages with beam effect
      for (let i = 1; i <= 7; i++) {
        setActiveStageNumber(i);
        await new Promise((r) => setTimeout(r, 220));
      }
    } catch (err: any) {
      alert(`Simulation failed: ${err.message}`);
    } finally {
      setRunningScenario(null);
    }
  };

  // Simulate customer paying the generated recovery link
  const handleReconcileSettlement = async () => {
    if (!activeTrace?.opportunity_id) return;
    setReconciling(true);
    try {
      const data = await api<{
        success: boolean;
        opportunity_id: string;
        ledger_entry_id: string;
        amount_recovered_display: string;
      }>("/v1/playground/reconcile-link", {
        method: "POST",
        body: JSON.stringify({
          opportunity_id: activeTrace.opportunity_id,
        }),
      });
      setReconciledResult(data);
    } catch (err: any) {
      alert(`Reconciliation error: ${err.message}`);
    } finally {
      setReconciling(false);
    }
  };

  const copyLinkToClipboard = (url: string) => {
    navigator.clipboard.writeText(url);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2500);
  };

  const getStageStatusBadge = (status: string) => {
    switch (status) {
      case "PASSED":
        return (
          <span className="badge badge-green" style={{ fontSize: 10, padding: "2px 6px" }}>
            <CheckCircle2 size={10} /> PASSED
          </span>
        );
      case "BLOCKED":
        return (
          <span className="badge badge-red" style={{ fontSize: 10, padding: "2px 6px" }}>
            <XCircle size={10} /> VETOED / BLOCKED
          </span>
        );
      case "DEFERRED":
        return (
          <span className="badge badge-amber" style={{ fontSize: 10, padding: "2px 6px" }}>
            <Clock size={10} /> WAIT (DEFERRED)
          </span>
        );
      case "ABSTAINED":
        return (
          <span className="badge badge-gray" style={{ fontSize: 10, padding: "2px 6px" }}>
            ABSTAIN
          </span>
        );
      case "FAILED":
        return (
          <span className="badge badge-red" style={{ fontSize: 10, padding: "2px 6px" }}>
            <XCircle size={10} /> FAILED
          </span>
        );
      case "SKIPPED":
        return (
          <span className="badge badge-gray" style={{ fontSize: 10, padding: "2px 6px" }}>
            SKIPPED
          </span>
        );
      case "READY_FOR_SETTLEMENT":
        return (
          <span className="badge badge-violet" style={{ fontSize: 10, padding: "2px 6px" }}>
            <Radio size={10} /> READY
          </span>
        );
      default:
        return <span className="badge badge-gray" style={{ fontSize: 10 }}>{status}</span>;
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Top Header & Live Environment Mode */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "linear-gradient(135deg, rgba(245,158,11,0.2), rgba(59,130,246,0.2))",
              border: "1px solid rgba(245,158,11,0.3)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <Zap size={16} color="var(--amber)" />
            </div>
            <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Razorpay Recovery Playground & Visualizer</h1>

            {config && (
              <span style={{
                fontSize: 11, padding: "3px 10px", borderRadius: 12, fontWeight: 700,
                background: config.is_live ? "rgba(16,185,129,0.18)" : "rgba(245,158,11,0.18)",
                color: config.is_live ? "var(--emerald)" : "var(--amber)",
                display: "inline-flex", alignItems: "center", gap: 6,
                border: config.is_live ? "1px solid rgba(16,185,129,0.3)" : "1px solid rgba(245,158,11,0.3)"
              }}>
                <span style={{
                  width: 7, height: 7, borderRadius: "50%",
                  background: config.is_live ? "var(--emerald)" : "var(--amber)",
                  boxShadow: config.is_live ? "0 0 10px var(--emerald)" : "0 0 8px var(--amber)"
                }} />
                {config.is_live ? `LIVE RAZORPAY MODE (${config.masked_key_id})` : `TEST MODE (${config.masked_key_id})`}
              </span>
            )}
          </div>
          <p style={{ fontSize: 13, color: "var(--text-muted)", margin: 0 }}>
            Interact with the official Razorpay Checkout modal, trigger failure scenarios, and watch the 7-phase autonomous recovery engine execute live with real-time telemetry.
          </p>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn btn-ghost" onClick={fetchConfig} style={{ gap: 6 }}>
            <RefreshCw size={14} className={configLoading ? "spin" : ""} /> Refresh Keys
          </button>
          <Link href="/dashboard/settings/integrations" className="btn btn-ghost" style={{ gap: 6 }}>
            Manage Keys &rarr;
          </Link>
        </div>
      </div>

      {/* Main Grid: Storefront Simulator (Left) vs 7-Stage Visualizer (Right) */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))", gap: 24, alignItems: "start" }}>

        {/* LEFT COLUMN: MERCHANT CHECKOUT & SCENARIO LAUNCHER */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

          {/* Product & Micropayment Checkout Card */}
          <div className="card" style={{ padding: 24, position: "relative", overflow: "hidden" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <span className="badge badge-blue" style={{ fontSize: 10, marginBottom: 6 }}>SAMPLE MERCHANT STOREFRONT</span>
                <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>Apex Cloud Subscription</h2>
                <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>High-performance SaaS computing tier</p>
              </div>
              <div style={{
                width: 44, height: 44, borderRadius: 12,
                background: "rgba(59,130,246,0.1)",
                display: "flex", alignItems: "center", justifyContent: "center"
              }}>
                <ShoppingBag size={22} color="var(--electric-blue)" />
              </div>
            </div>

            {/* Micropayment Safe Amount Selector */}
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 8, display: "block" }}>
                Select Checkout Amount (INR ₹):
              </label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {[
                  { label: "₹1.00 (Safe Micropayment)", paise: 100 },
                  { label: "₹10.00", paise: 1000 },
                  { label: "₹499.00", paise: 49900 },
                  { label: "₹1,499.00", paise: 149900 },
                ].map((preset) => (
                  <button
                    key={preset.paise}
                    onClick={() => handleSelectAmount(preset.paise)}
                    className="btn"
                    style={{
                      fontSize: 12,
                      padding: "6px 12px",
                      background: amountPaise === preset.paise ? "rgba(59,130,246,0.2)" : "rgba(255,255,255,0.04)",
                      border: amountPaise === preset.paise ? "1px solid var(--electric-blue)" : "1px solid var(--border)",
                      color: amountPaise === preset.paise ? "var(--electric-blue)" : "var(--text-primary)",
                      fontWeight: 600,
                    }}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Custom Amount: ₹</span>
                <input
                  type="number"
                  step="0.01"
                  min="1"
                  value={customAmount}
                  onChange={(e) => handleCustomAmountChange(e.target.value)}
                  style={{
                    background: "var(--bg-base)",
                    border: "1px solid var(--border)",
                    borderRadius: 6,
                    padding: "4px 8px",
                    color: "var(--text-primary)",
                    fontSize: 13,
                    width: 100,
                  }}
                />
              </div>
            </div>

            {/* Customer Information Form */}
            <div style={{ display: "flex", flexDirection: "column", gap: 10, padding: 14, borderRadius: 8, background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)", marginBottom: 18 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>Customer Details for Razorpay Prefill:</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                <input
                  type="text"
                  placeholder="Customer Name"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  style={{ background: "var(--bg-base)", border: "1px solid var(--border)", borderRadius: 6, padding: "6px 8px", fontSize: 12, color: "var(--text-primary)" }}
                />
                <input
                  type="text"
                  placeholder="Phone (+91...)"
                  value={customerPhone}
                  onChange={(e) => setCustomerPhone(e.target.value)}
                  style={{ background: "var(--bg-base)", border: "1px solid var(--border)", borderRadius: 6, padding: "6px 8px", fontSize: 12, color: "var(--text-primary)" }}
                />
              </div>
              <input
                type="email"
                placeholder="Email Address"
                value={customerEmail}
                onChange={(e) => setCustomerEmail(e.target.value)}
                style={{ background: "var(--bg-base)", border: "1px solid var(--border)", borderRadius: 6, padding: "6px 8px", fontSize: 12, color: "var(--text-primary)" }}
              />
            </div>

            {/* Open Official Checkout Modal Button */}
            <button
              className="btn btn-primary"
              onClick={handleOpenRazorpayCheckout}
              disabled={isOpeningCheckout}
              style={{
                width: "100%",
                padding: "12px",
                fontSize: 14,
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                background: "linear-gradient(135deg, #3b82f6, #2563eb)",
                boxShadow: "0 4px 14px rgba(59,130,246,0.3)",
              }}
            >
              {isOpeningCheckout ? <RefreshCw size={16} className="spin" /> : <CreditCard size={16} />}
              {isOpeningCheckout ? "Creating Order…" : `Pay ₹${(amountPaise / 100).toFixed(2)} via Official Razorpay Modal`}
            </button>
          </div>

          {/* 1-Click Simulation Scenario Presets */}
          <div className="card" style={{ padding: 22 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <Flame size={16} color="var(--amber)" />
              <h3 style={{ fontSize: 15, fontWeight: 700, margin: 0 }}>1-Click Payment Failure Simulation Presets</h3>
            </div>
            <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>
              Instantly simulate real-world failure events to test recovery algorithms without manual card declines:
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {/* Preset 1 */}
              <button
                className="btn"
                onClick={() => handleTriggerScenario("soft_insufficient_funds")}
                disabled={Boolean(runningScenario)}
                style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "12px 16px", borderRadius: 8,
                  background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.25)",
                  textAlign: "left", cursor: "pointer",
                }}
              >
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "var(--emerald)", display: "flex", alignItems: "center", gap: 6 }}>
                    🟢 Soft Decline: Insufficient Funds
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                    High intervention lift $\to$ Generates Razorpay payment link automatically
                  </div>
                </div>
                <ChevronRight size={16} color="var(--emerald)" />
              </button>

              {/* Preset 2 */}
              <button
                className="btn"
                onClick={() => handleTriggerScenario("soft_expired_card")}
                disabled={Boolean(runningScenario)}
                style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "12px 16px", borderRadius: 8,
                  background: "rgba(59,130,246,0.06)", border: "1px solid rgba(59,130,246,0.25)",
                  textAlign: "left", cursor: "pointer",
                }}
              >
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "var(--electric-blue)", display: "flex", alignItems: "center", gap: 6 }}>
                    🟢 Soft Decline: Expired Card Renewal
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                    Customer needs alternate payment channel $\to$ High IVEN score
                  </div>
                </div>
                <ChevronRight size={16} color="var(--electric-blue)" />
              </button>

              {/* Preset 3 */}
              <button
                className="btn"
                onClick={() => handleTriggerScenario("hard_stolen_card")}
                disabled={Boolean(runningScenario)}
                style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "12px 16px", borderRadius: 8,
                  background: "rgba(244,63,94,0.06)", border: "1px solid rgba(244,63,94,0.25)",
                  textAlign: "left", cursor: "pointer",
                }}
              >
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "var(--rose)", display: "flex", alignItems: "center", gap: 6 }}>
                    🔴 Hard Decline: Stolen Card / Fraud Block
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                    Action Authority compliance veto triggers $\to$ Execution strictly BLOCKED
                  </div>
                </div>
                <ChevronRight size={16} color="var(--rose)" />
              </button>

              {/* Preset 4 */}
              <button
                className="btn"
                onClick={() => handleTriggerScenario("capacity_saturation")}
                disabled={Boolean(runningScenario)}
                style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "12px 16px", borderRadius: 8,
                  background: "rgba(245,158,11,0.06)", border: "1px solid rgba(245,158,11,0.25)",
                  textAlign: "left", cursor: "pointer",
                }}
              >
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "var(--amber)", display: "flex", alignItems: "center", gap: 6 }}>
                    🟡 Capacity Competition & Shadow Price Bound
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                    Over-capacity batch $\to$ Greedy allocation assigns WAIT decision
                  </div>
                </div>
                <ChevronRight size={16} color="var(--amber)" />
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: 7-STAGE REAL-TIME NODE FLOW & TELEMETRY */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div className="card" style={{ padding: 24, position: "relative", minHeight: 600 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>ULTRON 7-Stage Real-Time Execution Visualizer</h2>
                <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                  Live deterministic state machine trace from ingestion to settlement reconciliation.
                </p>
              </div>
              {runningScenario && (
                <span className="badge badge-blue animate-pulse-glow" style={{ fontSize: 11 }}>
                  <Radio size={12} className="spin" /> Executing Pipeline…
                </span>
              )}
            </div>

            {!activeTrace ? (
              <div style={{ padding: "64px 24px", textAlign: "center", color: "var(--text-muted)" }}>
                <Activity size={36} color="var(--electric-blue)" style={{ marginBottom: 12, opacity: 0.8 }} />
                <p style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
                  Pipeline Standby (Awaiting Checkout Event)
                </p>
                <p style={{ fontSize: 12, maxWidth: 360, margin: "0 auto" }}>
                  Open the official Razorpay Checkout on the left or click any 1-Click Simulation Preset to illuminate the 7-stage engine.
                </p>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>

                {/* 7 Interactive Stage Nodes */}
                {activeTrace.stages.map((stg) => {
                  const isCurrent = activeStageNumber === stg.stage_number;
                  const isExpanded = expandedStage === stg.stage_number;

                  return (
                    <div
                      key={stg.stage_number}
                      style={{
                        borderRadius: 10,
                        border: isCurrent
                          ? "1px solid var(--electric-blue)"
                          : stg.status === "BLOCKED"
                          ? "1px solid rgba(244,63,94,0.3)"
                          : "1px solid var(--border)",
                        background: isCurrent
                          ? "rgba(59,130,246,0.08)"
                          : stg.status === "BLOCKED"
                          ? "rgba(244,63,94,0.04)"
                          : "rgba(255,255,255,0.02)",
                        transition: "all 0.2s ease",
                        overflow: "hidden",
                      }}
                    >
                      {/* Stage Summary Row */}
                      <div
                        onClick={() => setExpandedStage(isExpanded ? null : stg.stage_number)}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "12px 16px",
                          cursor: "pointer",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                          <div style={{
                            width: 26, height: 26, borderRadius: "50%",
                            background: isCurrent ? "var(--electric-blue)" : "rgba(255,255,255,0.08)",
                            color: isCurrent ? "#fff" : "var(--text-muted)",
                            fontSize: 12, fontWeight: 800,
                            display: "flex", alignItems: "center", justifyContent: "center"
                          }}>
                            {stg.stage_number}
                          </div>
                          <div>
                            <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)" }}>
                              {stg.stage_name}
                            </div>
                            <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                              {stg.stage_number === 1 && `Event: ${stg.data.payment_id} (${stg.data.amount_display})`}
                              {stg.stage_number === 2 && `Taxonomy: ${stg.data.decline_type.toUpperCase()} (${stg.data.reason_code})`}
                              {stg.stage_number === 3 && `IVEN: ${stg.data.iven_display} (Lift ΔP: ${stg.data.incremental_prob?.toFixed(2)})`}
                              {stg.stage_number === 4 && `Decision: ${stg.data.decision} (Rank #${stg.data.rank_in_batch}, λ: ${stg.data.shadow_price_display})`}
                              {stg.stage_number === 5 && `Verdict: ${stg.data.verdict} — ${stg.data.summary_reason}`}
                              {stg.stage_number === 6 && (stg.data.link_url ? `Link Created: ${stg.data.payment_link_id}` : stg.data.message || stg.data.error)}
                              {stg.stage_number === 7 && `State: ${stg.data.ledger_state}`}
                            </div>
                          </div>
                        </div>

                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          {getStageStatusBadge(stg.status)}
                          {isExpanded ? <ChevronDown size={14} color="var(--text-muted)" /> : <ChevronRight size={14} color="var(--text-muted)" />}
                        </div>
                      </div>

                      {/* Expanded "Under the Hood" Mathematical Breakdown Drawer */}
                      {isExpanded && (
                        <div style={{
                          padding: "12px 16px",
                          borderTop: "1px solid var(--border)",
                          background: "#080b11",
                        }}>
                          <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", marginBottom: 6, textTransform: "uppercase" }}>
                            🔬 Under the Hood Execution Variables:
                          </div>
                          <pre style={{
                            margin: 0, padding: 10, borderRadius: 6,
                            background: "rgba(0,0,0,0.5)", border: "1px solid var(--border)",
                            fontFamily: "monospace", fontSize: 11, color: "#93c5fd", overflowX: "auto"
                          }}>
                            {JSON.stringify(stg.data, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  );
                })}

                {/* Generated Live Payment Link & Instant Settlement Card */}
                {activeTrace.link_url && (
                  <div
                    className="animate-fade-in"
                    style={{
                      marginTop: 8,
                      padding: 18,
                      borderRadius: 10,
                      background: "linear-gradient(135deg, rgba(59,130,246,0.12), rgba(16,185,129,0.12))",
                      border: "1px solid rgba(59,130,246,0.3)",
                      display: "flex",
                      flexDirection: "column",
                      gap: 12,
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div style={{ fontSize: 13, fontWeight: 700, color: "var(--emerald)", display: "flex", alignItems: "center", gap: 6 }}>
                        <Sparkles size={16} /> Genuine Razorpay Recovery Payment Link Dispatched
                      </div>
                      <span className="badge badge-green" style={{ fontSize: 11 }}>Active Link</span>
                    </div>

                    <div style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "8px 12px",
                      background: "var(--bg-base)",
                      borderRadius: 6,
                      border: "1px solid var(--border)",
                      fontFamily: "monospace",
                      fontSize: 12,
                      color: "var(--electric-blue)",
                    }}>
                      <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {activeTrace.link_url}
                      </span>
                      <div style={{ display: "flex", gap: 6 }}>
                        <button
                          className="btn btn-ghost"
                          onClick={() => copyLinkToClipboard(activeTrace.link_url!)}
                          style={{ fontSize: 11, padding: "3px 8px", gap: 4 }}
                        >
                          {copiedLink ? <Check size={12} color="var(--emerald)" /> : <Copy size={12} />}
                          {copiedLink ? "Copied" : "Copy"}
                        </button>
                        <a
                          href={activeTrace.link_url}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-primary"
                          style={{ fontSize: 11, padding: "3px 8px", gap: 4 }}
                        >
                          Open Link <ExternalLink size={11} />
                        </a>
                      </div>
                    </div>

                    {/* Instant Settlement Simulator Button */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: 4 }}>
                      <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                        Test customer paying the recovery link:
                      </div>
                      <button
                        className="btn btn-primary"
                        onClick={handleReconcileSettlement}
                        disabled={reconciling || Boolean(reconciledResult)}
                        style={{
                          fontSize: 12,
                          padding: "6px 14px",
                          gap: 6,
                          background: Boolean(reconciledResult) ? "var(--emerald)" : undefined,
                        }}
                      >
                        {reconciling ? <RefreshCw size={13} className="spin" /> : <RotateCcw size={13} />}
                        {Boolean(reconciledResult) ? "Settlement Reconciled! 🎉" : "Simulate Customer Payment"}
                      </button>
                    </div>

                    {/* Settlement Confirmation Drawer */}
                    {reconciledResult && (
                      <div
                        className="animate-fade-in"
                        style={{
                          padding: 12,
                          borderRadius: 8,
                          background: "rgba(16,185,129,0.15)",
                          border: "1px solid rgba(16,185,129,0.35)",
                          fontSize: 12,
                          color: "var(--emerald)",
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                        }}
                      >
                        <CheckCircle2 size={16} />
                        <div>
                          <strong>{reconciledResult.message}</strong>
                          <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
                            Ledger Entry: <code style={{ color: "#fff" }}>{reconciledResult.ledger_entry_id}</code> · Amount: <strong>{reconciledResult.amount_recovered_display}</strong>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
