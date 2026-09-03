"use client";

import React, { useState, useEffect, useCallback } from "react";
import { CheckCircle2, Sparkles } from "lucide-react";
import { api } from "../../../lib/auth";

interface MarketDecision {
  opportunity_id: string;
  decision: "ACT" | "WAIT" | "ABSTAIN";
  rank_in_batch: number;
  shadow_price_paise_at_decision: number;
  reason: string;
  amount_paise?: number;
  expected_incremental_value_paise?: number;
  incremental_prob?: number;
}

interface MarketRunResponse {
  total_opportunities: number;
  capacity?: number;
  capacity_limit?: number;
  accepted_count: number;
  deferred_count: number;
  abstained_count: number;
  shadow_price_paise: number;
  shadow_price_display: string;
  items?: MarketDecision[];
  decisions?: MarketDecision[];
}

export default function MarketPage() {
  const [marketData, setMarketData] = useState<MarketRunResponse | null>(null);
  const [banditData, setBanditData] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const fetchMarket = useCallback(async () => {
    try {
      const [data, analytics] = await Promise.all([
        api<MarketRunResponse>("/market/run"),
        api<any>("/dashboard/analytics").catch(() => null),
      ]);
      setMarketData(data);
      if (analytics?.bandit) {
        setBanditData(analytics.bandit);
      }
    } catch {
      setMarketData(null);
    }
  }, []);

  useEffect(() => {
    fetchMarket();
  }, [fetchMarket]);

  const handleRunAllocation = async () => {
    setRunning(true);
    setFeedback(null);
    try {
      const res = await api<MarketRunResponse>("/market/run", { method: "POST", body: JSON.stringify({}) });
      setMarketData(res);
      setFeedback(`Portfolio allocation completed: Accepted ${res.accepted_count} under capacity cap of ${res.capacity_limit || res.capacity || 5}. Shadow price: ${res.shadow_price_display}.`);
    } catch (err: any) {
      alert("Allocation failed: " + err.message);
    } finally {
      setRunning(false);
    }
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case "ACT":
        return <span className="badge badge-green">ACT (ACCEPTED)</span>;
      case "WAIT":
        return <span className="badge badge-amber">WAIT (CAPACITY BOUND)</span>;
      case "ABSTAIN":
        return <span className="badge badge-gray">ABSTAIN (NEGATIVE IVEN)</span>;
      default:
        return <span className="badge badge-gray">{decision}</span>;
    }
  };

  const items = marketData?.decisions || marketData?.items || [];

  return (
    <div className="animate-fade-in" style={{ maxWidth: 1440, margin: "0 auto", width: "100%" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px", margin: "0 0 4px 0" }}>
            Recovery Market & Portfolio Knapsack Allocation
          </h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: 0 }}>
            Greedy fractional allocation of scarce recovery capacity sorted by Expected Incremental Value (IVEN).
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button
            onClick={handleRunAllocation}
            disabled={running}
            className="btn btn-primary"
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
          >
            <Sparkles size={14} />
            <span>{running ? "Solving Knapsack..." : "Run Portfolio Allocation"}</span>
          </button>
        </div>
      </div>

      {feedback && (
        <div style={{ padding: "12px 16px", borderRadius: 8, background: "var(--google-green-light)", border: "1px solid #ceead6", color: "var(--google-green-hover)", fontSize: 13, fontWeight: 500, marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
          <CheckCircle2 size={16} />
          <span>{feedback}</span>
        </div>
      )}

      {/* Top 4 Summary Cards */}
      <div style={{
        display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
        gap: 16, marginBottom: 20
      }}>
        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 4 }}>
            Shadow Price (λ)
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: "var(--google-blue)" }}>
            {marketData?.shadow_price_display || "₹0.00"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Marginal value of 1 additional link
          </div>
        </div>

        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "var(--google-green)", marginBottom: 4 }}>
            Accepted (ACT)
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: "var(--google-green)" }}>
            {marketData?.accepted_count ?? 0}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Passed greedy economic threshold
          </div>
        </div>

        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "var(--google-yellow-dark)", marginBottom: 4 }}>
            Deferred (WAIT)
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: "var(--text-primary)" }}>
            {marketData?.deferred_count ?? 0}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Positive IVEN but capacity constrained
          </div>
        </div>

        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 4 }}>
            Abstained (ABSTAIN)
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: "var(--text-primary)" }}>
            {marketData?.abstained_count ?? 0}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Intervention not worth operational cost
          </div>
        </div>
      </div>

      {/* Decisions Table */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)" }}>
            Batch Allocation Results ({items.length})
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
            Sorted by Expected Incremental Value (paise)
          </div>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
            <thead>
              <tr style={{ background: "#f8f9fa", borderBottom: "1px solid var(--border)", color: "var(--text-secondary)", fontSize: 11, textTransform: "uppercase" }}>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Rank</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Opportunity ID</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Decision</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Expected IVEN (₹)</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" }}>
                    Click "Run Portfolio Allocation" to rank and allocate pending opportunities.
                  </td>
                </tr>
              ) : (
                items.map((item, idx) => (
                  <tr key={item.opportunity_id || idx} style={{ borderBottom: "1px solid var(--border-subtle)", background: "#ffffff" }}>
                    <td style={{ padding: "12px 16px", fontWeight: 700, color: "var(--text-secondary)" }}>
                      #{item.rank_in_batch ?? idx + 1}
                    </td>
                    <td style={{ padding: "12px 16px", fontFamily: "var(--font-mono)", fontSize: 12 }}>
                      {item.opportunity_id}
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      {getDecisionBadge(item.decision)}
                    </td>
                    <td style={{ padding: "12px 16px", fontWeight: 700, color: (item.expected_incremental_value_paise || 0) > 0 ? "var(--google-green)" : "var(--google-red)" }}>
                      ₹{((item.expected_incremental_value_paise || 0) / 100).toFixed(2)}
                    </td>
                    <td style={{ padding: "12px 16px", color: "var(--text-secondary)", fontSize: 12 }}>
                      {item.reason}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reinforcement Learning Bandit Observability */}
      {banditData && (
        <div className="card" style={{ marginTop: 24, padding: 0, overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center", background: "#f8f9fa" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Sparkles size={18} color="var(--google-purple)" />
              <div>
                <h2 style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                  Reinforcement Learning: Thompson Sampling & Adaptive Capacity Pacer
                </h2>
                <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: "2px 0 0" }}>
                  Live Beta-Binomial conjugate posteriors and convex Lagrangian shadow price multiplier.
                </p>
              </div>
            </div>
            {banditData.pacer && (
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <span className="badge badge-blue">
                  WINDOW: {banditData.pacer.time_window}
                </span>
                <span className="badge badge-green">
                  ARM: {banditData.pacer.active_arm}
                </span>
                <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-primary)" }}>
                  λ = {banditData.pacer.lambda}
                </span>
              </div>
            )}
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
              <thead>
                <tr style={{ background: "#ffffff", borderBottom: "1px solid var(--border)", color: "var(--text-secondary)", fontSize: 11, textTransform: "uppercase" }}>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>Context Key (Reason:Tier)</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>P(Intervention)</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>P(Natural)</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>Incremental Lift</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>Pulls</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600, textAlign: "right" }}>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {(!banditData.arms || banditData.arms.length === 0) ? (
                  <tr>
                    <td colSpan={6} style={{ padding: "24px 16px", textAlign: "center", color: "var(--text-muted)" }}>
                      Bandit prior distributions initialized. Live posteriors adapt as opportunities are scored and reconciled.
                    </td>
                  </tr>
                ) : (
                  banditData.arms.map((arm: any) => (
                    <tr key={arm.context_key} style={{ borderBottom: "1px solid var(--border-subtle)", background: "#ffffff" }}>
                      <td style={{ padding: "12px 16px", fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600 }}>
                        {arm.context_key}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        {(arm.expected_p_interv * 100).toFixed(1)}%
                      </td>
                      <td style={{ padding: "12px 16px", color: "var(--text-secondary)" }}>
                        {(arm.expected_p_nat * 100).toFixed(1)}%
                      </td>
                      <td style={{ padding: "12px 16px", fontWeight: 700, color: arm.expected_incremental_lift > 0 ? "var(--google-green)" : "var(--text-secondary)" }}>
                        +{(arm.expected_incremental_lift * 100).toFixed(1)}%
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        {arm.pull_count}
                      </td>
                      <td style={{ padding: "12px 16px", textAlign: "right" }}>
                        <span className="badge badge-green">
                          {arm.confidence.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
