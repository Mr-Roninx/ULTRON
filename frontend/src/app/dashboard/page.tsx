"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  TrendingUp, AlertTriangle, Zap, Power, CheckCircle2, XCircle,
  Play, Send, Smartphone, Activity, Clock, Sparkles,
  BarChart2, ShieldCheck, Layers, ExternalLink
} from "lucide-react";
import { useAuth, api } from "../../lib/auth";

interface Summary {
  total_opportunities: number;
  total_at_risk_display: string;
  total_recovered_display: string;
  total_recovered_paise: number;
  real_recovered_count: number;
  synthetic_recovered_count: number;
  shadow_price_display: string;
  shadow_price_paise: number;
  capacity_limit: number;
  capacity_used: number;
  capacity_available: number;
  kill_switch_active: boolean;
  status_counts: Record<string, number>;
  total_execution_records: number;
  anti_blast?: {
    total_prevented: number;
    messaging_saved_paise: number;
    provider_saved_paise: number;
    goodwill_saved_paise: number;
    total_capital_saved_paise: number;
    total_capital_saved_display: string;
  };
  total_capital_saved_display?: string;
  total_interventions_prevented?: number;
}

interface OpportunityItem {
  id: string;
  amount_paise: number;
  currency: string;
  reason_code: string;
  decline_type: "hard" | "soft" | "unknown";
  attempt_count: number;
  customer_id: string;
  created_at: string;
  status: string;
  source: string;
  score?: {
    natural_recovery_prob: number;
    intervention_recovery_prob: number;
    incremental_prob: number;
    operational_cost_paise: number;
    fatigue_cost_paise: number;
    expected_incremental_value_paise: number;
    confidence: "low" | "medium" | "high";
    source?: "STATIC" | "CALIBRATED";
    credible_interval_95?: [number, number];
  };
  decision?: {
    decision: "ACT" | "WAIT" | "ABSTAIN";
    rank_in_batch: number;
    shadow_price_paise_at_decision: number;
    reason: string;
  };
  authority?: {
    verdict: "AUTHORIZED" | "BLOCKED" | "WAIT" | "ABSTAIN";
    summary_reason: string;
  };
  execution?: {
    razorpay_payment_link_id?: string;
    link_url?: string;
    status?: string;
  };
}

export default function UnifiedRecoveryHubPage() {
  const { tenant } = useAuth();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [opportunities, setOpportunities] = useState<OpportunityItem[]>([]);
  const [filterTab, setFilterTab] = useState<string>("ALL");
  const [sourceFilter, setSourceFilter] = useState<"ALL" | "REAL" | "SYNTHETIC">("ALL");
  const [selectedOpp, setSelectedOpp] = useState<OpportunityItem | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [runningSweep, setRunningSweep] = useState(false);
  const [togglingKillSwitch, setTogglingKillSwitch] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // WhatsApp Preview Modal State
  const [whatsappModalOpp, setWhatsappModalOpp] = useState<OpportunityItem | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const fetchData = useCallback(async () => {
    try {
      const [sumData, oppsData] = await Promise.all([
        api<Summary>("/dashboard/summary", { method: "GET" }).catch(() => null),
        api<{ opportunities: OpportunityItem[] }>("/v1/opportunities?limit=30", { method: "GET" }).catch(() => null),
      ]);

      if (sumData) setSummary(sumData);
      if (oppsData && oppsData.opportunities) setOpportunities(oppsData.opportunities);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // 1-Click Payment Failure Simulator
  const handleSimulateFailure = async () => {
    setSimulating(true);
    try {
      const sampleAmounts = [150000, 250000, 480000, 750000, 320000];
      const sampleReasons = [
        "payment_failed_issuer_down",
        "insufficient_funds_retryable",
        "bank_technical_error",
        "card_authentication_failed_soft",
      ];
      const randomAmount = sampleAmounts[Math.floor(Math.random() * sampleAmounts.length)];
      const randomReason = sampleReasons[Math.floor(Math.random() * sampleReasons.length)];
      const customerPhone = `+9198${Math.floor(10000000 + Math.random() * 90000000)}`;

      await api("/internal/simulate-webhook", {
        method: "POST",
        body: JSON.stringify({
          event: "payment.failed",
          payload: {
            payment: {
              entity: {
                id: `pay_sim_${Date.now()}`,
                amount: randomAmount,
                currency: "INR",
                status: "failed",
                method: "upi",
                error_code: "BAD_REQUEST_ERROR",
                error_description: "Payment declined by customer bank or network timeout",
                error_reason: randomReason,
                contact: customerPhone,
                email: `shopper_${Date.now().toString().slice(-4)}@example.com`,
              },
            },
          },
        }),
      });

      showToast(`Simulated failed payment of ₹${(randomAmount / 100).toLocaleString("en-IN")}`);
      await fetchData();
    } catch (err: any) {
      showToast(`Simulation failed: ${err.message}`);
    } finally {
      setSimulating(false);
    }
  };

  // 1-Click Run Autonomous Sweep
  const handleRunSweep = async () => {
    setRunningSweep(true);
    try {
      await api("/agents/daemon/sweep", { method: "POST" });
      showToast("Autonomous recovery sweep executed across pipeline");
      await fetchData();
    } catch (err: any) {
      showToast(`Sweep error: ${err.message}`);
    } finally {
      setRunningSweep(false);
    }
  };

  // Toggle Emergency Kill Switch
  const handleToggleKillSwitch = async () => {
    if (!summary) return;
    setTogglingKillSwitch(true);
    try {
      const nextState = !summary.kill_switch_active;
      await api("/authority/kill-switch", {
        method: "POST",
        body: JSON.stringify({ enabled: nextState }),
      });
      showToast(nextState ? "Emergency Kill Switch ENGAGED" : "Kill Switch Disengaged");
      await fetchData();
    } catch (err: any) {
      showToast(`Kill switch update failed: ${err.message}`);
    } finally {
      setTogglingKillSwitch(false);
    }
  };

  const filteredOpps = opportunities.filter((o) => {
    // 1. Source filter
    if (sourceFilter === "REAL" && o.source !== "real") return false;
    if (sourceFilter === "SYNTHETIC" && o.source !== "synthetic") return false;

    // 2. Status filter
    if (filterTab === "ALL") return true;
    if (filterTab === "ACTION_NEEDED") return o.status === "pending" || o.status === "scored" || o.status === "allocated";
    if (filterTab === "RECOVERED") return o.status === "recovered";
    if (filterTab === "WAITING") return o.status === "deferred" || o.status === "abstained";
    if (filterTab === "BLOCKED") return o.status === "blocked";
    return true;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "recovered":
        return <span className="badge badge-green"><CheckCircle2 size={11} /> RECOVERED</span>;
      case "executing":
        return <span className="badge badge-blue"><Zap size={11} /> LINK ISSUED</span>;
      case "allocated":
        return <span className="badge badge-blue"><Activity size={11} /> ALLOCATED</span>;
      case "scored":
        return <span className="badge badge-blue"><TrendingUp size={11} /> SCORED</span>;
      case "blocked":
        return <span className="badge badge-red"><XCircle size={11} /> BLOCKED</span>;
      case "deferred":
      case "abstained":
        return <span className="badge badge-amber"><Clock size={11} /> CAPACITY BOUND</span>;
      default:
        return <span className="badge badge-gray">{status.toUpperCase()}</span>;
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: 1440, margin: "0 auto", width: "100%" }}>
      {/* Toast alert */}
      {toastMessage && (
        <div style={{
          position: "fixed", bottom: 24, right: 24, zIndex: 100,
          background: "#202124", color: "#ffffff",
          padding: "12px 20px", borderRadius: 8,
          boxShadow: "var(--shadow-dropdown)", fontSize: 13, fontWeight: 500,
          display: "flex", alignItems: "center", gap: 8,
        }}>
          <CheckCircle2 size={16} color="var(--google-green)" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header Bar */}
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        marginBottom: 20, flexWrap: "wrap", gap: 16
      }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px", margin: 0 }}>
            Revenue Recovery Operations Hub
          </h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: "4px 0 0" }}>
            Autonomous economic control plane intercepting and recovering failed digital payments.
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {/* Simulate Payment Failure */}
          <button
            onClick={handleSimulateFailure}
            disabled={simulating}
            className="btn btn-secondary"
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
          >
            <Play size={14} color="var(--google-blue)" />
            <span>{simulating ? "Simulating..." : "Simulate Payment Failure"}</span>
          </button>

          {/* Run Sweep */}
          <button
            onClick={handleRunSweep}
            disabled={runningSweep}
            className="btn btn-primary"
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
          >
            <Sparkles size={14} />
            <span>{runningSweep ? "Executing Sweep..." : "Run Autonomous Sweep"}</span>
          </button>

          {/* Emergency Kill Switch */}
          <button
            onClick={handleToggleKillSwitch}
            disabled={togglingKillSwitch}
            className={summary?.kill_switch_active ? "btn btn-danger" : "btn btn-secondary"}
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
            title="Deterministic hard safety cutoff"
          >
            <Power size={14} color={summary?.kill_switch_active ? "var(--google-red)" : "var(--text-secondary)"} />
            <span>{summary?.kill_switch_active ? "Kill Switch ENGAGED" : "Kill Switch Off"}</span>
          </button>
        </div>
      </div>

      {/* Top 4 Google-Style Clean Metric Cards */}
      <div style={{
        display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: 16, marginBottom: 20
      }}>
        {/* At Risk Volume */}
        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>
              Total Failed Revenue At Risk
            </span>
            <AlertTriangle size={16} color="var(--google-yellow-dark)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px" }}>
            {summary?.total_at_risk_display || "₹0.00"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Across {summary?.total_opportunities || 0} failed checkout transactions
          </div>
        </div>

        {/* Recovered Revenue */}
        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--google-green)" }}>
              Gross Recovered Revenue
            </span>
            <CheckCircle2 size={16} color="var(--google-green)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--google-green)", letterSpacing: "-0.5px" }}>
            {summary?.total_recovered_display || "₹0.00"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Settled directly via Razorpay UPI & Cards
          </div>
        </div>

        {/* Shadow Price */}
        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--google-blue)" }}>
              Portfolio Shadow Price (λ)
            </span>
            <BarChart2 size={16} color="var(--google-blue)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px" }}>
            {summary?.shadow_price_display || "₹0.00"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Marginal value required for capacity allocation
          </div>
        </div>

        {/* Recovery Capacity */}
        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>
              Recovery Capacity Budget
            </span>
            <Zap size={16} color="var(--google-purple)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px" }}>
            {summary?.capacity_available ?? 5} / {summary?.capacity_limit ?? 5}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Payment links remaining under test mode cap
          </div>
        </div>

        {/* Anti-Blast Capital Saved */}
        <div className="card" style={{ padding: "18px 20px", borderLeft: "4px solid var(--google-green)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--google-green)" }}>
              Anti-Blast Capital Saved
            </span>
            <ShieldCheck size={16} color="var(--google-green)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--google-green)", letterSpacing: "-0.5px" }}>
            {summary?.total_capital_saved_display || "₹0.00"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            {summary?.total_interventions_prevented || 0} wasteful spam blasts prevented
          </div>
        </div>
      </div>

      {/* Main Filter Chips & Live Opportunity Table */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {/* Table Filter Bar */}
        <div style={{
          padding: "14px 20px", borderBottom: "1px solid var(--border)",
          display: "flex", justifyContent: "space-between", alignItems: "center",
          flexWrap: "wrap", gap: 12, background: "#ffffff"
        }}>
          {/* Controls: Source & Status Switchers */}
          <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            {/* Traffic Source Filter */}
            <div style={{ display: "flex", gap: 4, background: "var(--bg-hover)", padding: 4, borderRadius: 20 }}>
              {[
                { id: "ALL" as const, label: `All Sources (${opportunities.length})` },
                { id: "REAL" as const, label: `🟢 Live Gateway (${opportunities.filter((o) => o.source === "real").length})` },
                { id: "SYNTHETIC" as const, label: `🧪 Test Cohort (${opportunities.filter((o) => o.source === "synthetic").length})` },
              ].map((src) => (
                <button
                  key={src.id}
                  onClick={() => setSourceFilter(src.id)}
                  style={{
                    padding: "5px 12px", borderRadius: 16, fontSize: 12, fontWeight: 500,
                    border: "none", cursor: "pointer", transition: "all 0.15s ease",
                    background: sourceFilter === src.id ? "#ffffff" : "transparent",
                    color: sourceFilter === src.id ? "var(--google-blue)" : "var(--text-secondary)",
                    boxShadow: sourceFilter === src.id ? "0 1px 2px rgba(60,64,67,0.15)" : "none"
                  }}
                >
                  {src.label}
                </button>
              ))}
            </div>

            {/* Segmented Status Pills */}
            <div style={{ display: "flex", gap: 4, background: "var(--bg-hover)", padding: 4, borderRadius: 20 }}>
              {[
                { id: "ALL", label: "All Status" },
                { id: "ACTION_NEEDED", label: "⚡ Action Needed" },
                { id: "RECOVERED", label: "🟢 Recovered" },
                { id: "WAITING", label: "⏳ Capacity Bound" },
                { id: "BLOCKED", label: "🛑 Blocked" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setFilterTab(tab.id)}
                  style={{
                    padding: "5px 12px", borderRadius: 16, fontSize: 12, fontWeight: 500,
                    border: "none", cursor: "pointer", transition: "all 0.15s ease",
                    background: filterTab === tab.id ? "#ffffff" : "transparent",
                    color: filterTab === tab.id ? "var(--google-blue)" : "var(--text-secondary)",
                    boxShadow: filterTab === tab.id ? "0 1px 2px rgba(60,64,67,0.15)" : "none"
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
            Showing {filteredOpps.length} opportunities · Auto-sync active
          </div>
        </div>

        {/* Opportunities Data Table */}
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
            <thead>
              <tr style={{ background: "#f8f9fa", borderBottom: "1px solid var(--border)", color: "var(--text-secondary)", fontSize: 11, textTransform: "uppercase" }}>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>ID / Source / Created</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Amount (₹)</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Decline Reason</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Score (IVEN)</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Status</th>
                <th style={{ padding: "10px 16px", fontWeight: 600, textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredOpps.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ padding: "48px 20px", textAlign: "center", color: "var(--text-muted)" }}>
                    <CheckCircle2 size={32} style={{ margin: "0 auto 8px", color: "var(--google-green)" }} />
                    <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)" }}>No opportunities matching criteria</div>
                    <div style={{ fontSize: 12, marginTop: 4 }}>Toggle between Live Gateway and Test Cohort above.</div>
                  </td>
                </tr>
              ) : (
                filteredOpps.map((opp) => (
                  <tr
                    key={opp.id}
                    style={{
                      borderBottom: "1px solid var(--border-subtle)",
                      background: selectedOpp?.id === opp.id ? "var(--google-blue-light)" : "#ffffff",
                      transition: "background 0.15s ease",
                      cursor: "pointer"
                    }}
                    onClick={() => setSelectedOpp(opp)}
                  >
                    {/* ID & Source */}
                    <td style={{ padding: "12px 16px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <span style={{ fontWeight: 600, color: "var(--text-primary)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
                          {opp.id.slice(0, 18)}...
                        </span>
                        {opp.source === "real" ? (
                          <span style={{ fontSize: 9, padding: "2px 6px", borderRadius: 4, background: "#e6f4ea", color: "#137333", fontWeight: 700 }}>
                            LIVE
                          </span>
                        ) : (
                          <span style={{ fontSize: 9, padding: "2px 6px", borderRadius: 4, background: "#f1f3f4", color: "#5f6368", fontWeight: 600 }}>
                            TEST
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                        {new Date(opp.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </div>
                    </td>

                    {/* Amount */}
                    <td style={{ padding: "12px 16px", fontWeight: 700, color: "var(--text-primary)" }}>
                      ₹{(opp.amount_paise / 100).toLocaleString("en-IN")}
                    </td>

                    {/* Reason */}
                    <td style={{ padding: "12px 16px" }}>
                      <div style={{ fontSize: 12, color: "var(--text-primary)", fontWeight: 500 }}>
                        {opp.reason_code.replace(/_/g, " ")}
                      </div>
                      <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>
                        {opp.decline_type} decline · Attempt #{opp.attempt_count}
                      </div>
                    </td>

                    {/* IVEN Score */}
                    <td style={{ padding: "12px 16px" }}>
                      {opp.score ? (
                        <div>
                          <div style={{ fontWeight: 700, color: opp.score.expected_incremental_value_paise > 0 ? "var(--google-green)" : "var(--google-red)" }}>
                            ₹{(opp.score.expected_incremental_value_paise / 100).toFixed(2)}
                          </div>
                          <div style={{ fontSize: 10, color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 4 }}>
                            <span>Lift: +{Math.round(opp.score.incremental_prob * 100)}%</span>
                            {opp.score.source === "CALIBRATED" && (
                              <span style={{ fontSize: 9, padding: "1px 4px", borderRadius: 3, background: "#e8f0fe", color: "var(--google-blue)", fontWeight: 600 }}>
                                Beta(α,β)
                              </span>
                            )}
                          </div>
                        </div>
                      ) : (
                        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Pending</span>
                      )}
                    </td>

                    {/* Status */}
                    <td style={{ padding: "12px 16px" }}>
                      {getStatusBadge(opp.status)}
                    </td>

                    {/* Actions */}
                    <td style={{ padding: "12px 16px", textAlign: "right" }}>
                      <div style={{ display: "inline-flex", alignItems: "center", gap: 6 }} onClick={(e) => e.stopPropagation()}>
                        {/* WhatsApp Recovery Button */}
                        <button
                          onClick={() => setWhatsappModalOpp(opp)}
                          className="btn btn-secondary"
                          style={{ padding: "5px 10px", fontSize: 11, gap: 4, borderRadius: 14 }}
                          title="Open WhatsApp Recovery Preview"
                        >
                          <Smartphone size={13} color="var(--google-green)" />
                          <span>WhatsApp</span>
                        </button>

                        {/* Razorpay Payment Link */}
                        {opp.execution?.link_url && (
                          <a
                            href={opp.execution.link_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-primary"
                            style={{ padding: "5px 10px", fontSize: 11, gap: 4, borderRadius: 14 }}
                          >
                            <span>Pay Link</span>
                            <ExternalLink size={11} />
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* WhatsApp Modal Preview */}
      {whatsappModalOpp && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 100,
          background: "rgba(0,0,0,0.5)", backdropFilter: "blur(4px)",
          display: "flex", alignItems: "center", justifyContent: "center", padding: 20
        }}>
          <div className="card animate-fade-in" style={{
            maxWidth: 480, width: "100%", background: "#ffffff",
            borderRadius: 12, padding: 24, boxShadow: "var(--shadow-dropdown)"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Smartphone size={18} color="var(--google-green)" />
                <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>WhatsApp Customer Intercept</h3>
              </div>
              <button
                onClick={() => setWhatsappModalOpp(null)}
                style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-secondary)" }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 16 }}>
              This verified message is automatically sent to the customer with an active 1-click Razorpay checkout link:
            </p>

            {/* Simulated WhatsApp Bubble */}
            <div style={{
              background: "#dcf8c6", padding: "14px 16px", borderRadius: "10px 10px 0 10px",
              color: "#111b21", fontSize: 13, lineHeight: 1.5, marginBottom: 16,
              border: "1px solid #c1e7a5"
            }}>
              <div style={{ fontWeight: 700, marginBottom: 4 }}>🔔 Payment Incomplete Notification</div>
              <div>Hi buyer,</div>
              <div style={{ marginTop: 4 }}>
                Your payment of <strong>₹{(whatsappModalOpp.amount_paise / 100).toLocaleString("en-IN")}</strong> for <strong>{tenant?.name || "Our Store"}</strong> could not be completed.
              </div>
              <div style={{ marginTop: 6 }}>
                You can complete your payment securely with 1-click via UPI (Google Pay, PhonePe, Paytm), NetBanking, or Cards:
              </div>
              <div style={{ marginTop: 8, padding: "8px 10px", background: "#ffffff", borderRadius: 6, border: "1px solid #c1e7a5", wordBreak: "break-all" }}>
                👉 <a href={whatsappModalOpp.execution?.link_url || "https://rzp.io/i/example"} target="_blank" rel="noreferrer" style={{ color: "var(--google-blue)", fontWeight: 600 }}>
                  {whatsappModalOpp.execution?.link_url || "https://rzp.io/i/test_link"}
                </a>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
              <button onClick={() => setWhatsappModalOpp(null)} className="btn btn-secondary">
                Close
              </button>
              {whatsappModalOpp.execution?.link_url && (
                <a
                  href={`https://api.whatsapp.com/send?phone=919876543210&text=${encodeURIComponent(`Hi, complete your payment securely: ${whatsappModalOpp.execution.link_url}`)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                  style={{ background: "var(--google-green)" }}
                >
                  <Send size={13} />
                  <span>Send via WhatsApp Web</span>
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
