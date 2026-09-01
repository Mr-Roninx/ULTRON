"use client";

import React, { useState, useEffect, useCallback } from "react";
import { TrendingUp, RefreshCw, Play, CheckCircle2, AlertTriangle, HelpCircle } from "lucide-react";
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
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetchMarket = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api<MarketRunResponse>("/market/run");
      setMarketData(data);
    } catch {
      setMarketData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMarket();
  }, [fetchMarket]);

  const handleRunAllocation = async () => {
    setRunning(true);
    try {
      const res = await api<MarketRunResponse>("/market/run", { method: "POST", body: JSON.stringify({}) });
      setMarketData(res);
    } catch (err: any) {
      alert(`Allocation failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case "ACT":
        return <span className="badge badge-blue">ACT</span>;
      case "WAIT":
        return <span className="badge badge-amber">WAIT</span>;
      case "ABSTAIN":
        return <span className="badge badge-gray">ABSTAIN</span>;
      default:
        return <span className="badge badge-gray">{decision}</span>;
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Recovery Market Allocation</h1>
          <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
            Portfolio optimization allocating scarce recovery capacity by Incremental Value Expected Net (IVEN).
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn btn-ghost" onClick={fetchMarket} style={{ gap: 6 }}>
            <RefreshCw size={14} /> Refresh
          </button>
          <button className="btn btn-primary" onClick={handleRunAllocation} disabled={running} style={{ gap: 6 }}>
            {running ? <RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} /> : <Play size={14} />}
            {running ? "Optimizing Portfolio…" : "Run Portfolio Allocation"}
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
        <div className="card" style={{ padding: 20 }}>
          <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: "rgba(139,92,246,0.1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <TrendingUp size={16} color="var(--violet)" />
            </div>
            <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-secondary)" }}>Portfolio Shadow Price</div>
          </div>
          <div style={{ fontSize: 26, fontWeight: 700 }}>
            {marketData?.shadow_price_display || `₹${((marketData?.shadow_price_paise || 0) / 100).toFixed(2)}`}
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>Marginal value of accepted recovery slot</div>
        </div>

        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-secondary)", marginBottom: 8 }}>Accepted (ACT)</div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--electric-blue)" }}>
            {marketData?.accepted_count || 0}
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>Within capacity limit of {marketData?.capacity_limit || 5}</div>
        </div>

        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-secondary)", marginBottom: 8 }}>Deferred / Abstained</div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--text-muted)" }}>
            {(marketData?.deferred_count || 0) + (marketData?.abstained_count || 0)}
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>Saved contact budget & customer fatigue</div>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden", minHeight: 360 }}>
        {loading ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300 }}>
            <div style={{ width: 24, height: 24, border: "2px solid var(--electric-blue)", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
          </div>
        ) : !marketData || (marketData.items || marketData.decisions || []).length === 0 ? (
          <div style={{ padding: "48px 24px", textAlign: "center", color: "var(--text-muted)" }}>
            <AlertTriangle size={32} color="var(--text-muted)" style={{ marginBottom: 12 }} />
            <p style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
              No Pending Opportunities for Allocation
            </p>
            <p style={{ fontSize: 13, maxWidth: 440, margin: "0 auto" }}>
              The Recovery Market allocates capacity when failed payments are ingested. Once opportunities exist, you can run greedy portfolio allocation here.
            </p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Opportunity ID</th>
                  <th>Decision</th>
                  <th>Shadow Price at Decision</th>
                  <th>Rationale</th>
                </tr>
              </thead>
              <tbody>
                {(marketData.items || marketData.decisions || []).map((d) => (
                  <tr key={d.opportunity_id} style={{ background: d.decision === "ACT" ? "rgba(59,130,246,0.03)" : undefined }}>
                    <td style={{ fontWeight: 700, color: d.decision === "ACT" ? "var(--electric-blue)" : "var(--text-muted)" }}>
                      #{d.rank_in_batch}
                    </td>
                    <td>
                      <code style={{ fontSize: 11, background: "var(--bg-base)", padding: "2px 6px", borderRadius: 4 }}>
                        {d.opportunity_id}
                      </code>
                    </td>
                    <td>{getDecisionBadge(d.decision)}</td>
                    <td style={{ fontWeight: 600 }}>
                      ₹{((d.shadow_price_paise_at_decision || 0) / 100).toFixed(2)}
                    </td>
                    <td style={{ fontSize: 12, color: "var(--text-secondary)", maxWidth: 360 }}>
                      {d.reason}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
