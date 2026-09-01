"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Activity, Clock, Shield, Search, RefreshCw, Sparkles, CheckCircle2, XCircle, AlertTriangle, ChevronRight, X } from "lucide-react";
import { api } from "../../../lib/auth";

interface Opportunity {
  id: string;
  source: "real" | "synthetic";
  amount_paise: number;
  currency: string;
  reason_code: string;
  decline_type: "hard" | "soft" | "unknown";
  attempt_count: number;
  customer_id: string;
  customer_trust_score: number;
  created_at: string;
  status: string;
}

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedOpp, setSelectedOpp] = useState<Opportunity | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<any>(null);

  const fetchOpportunities = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api<{ opportunities: Opportunity[] }>("/opportunities");
      setOpportunities(data.opportunities || []);
    } catch {
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOpportunities();
  }, [fetchOpportunities]);

  const handleExplain = async (opp: Opportunity) => {
    setSelectedOpp(opp);
    setExplaining(true);
    setAiExplanation(null);
    try {
      const scoreData = await api(`/opportunities/${opp.id}/score`);
      const explainData = await api(`/opportunities/${opp.id}/explain`);
      setAiExplanation({
        score: scoreData,
        explanation: explainData.explanation || explainData.summary,
      });
    } catch (err: any) {
      setAiExplanation({ error: err.message || "Failed to generate AI explanation" });
    } finally {
      setExplaining(false);
    }
  };

  const filtered = opportunities.filter((o) => {
    const q = search.toLowerCase();
    return (
      o.id.toLowerCase().includes(q) ||
      o.customer_id.toLowerCase().includes(q) ||
      o.reason_code.toLowerCase().includes(q) ||
      o.status.toLowerCase().includes(q)
    );
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "recovered":
        return <span className="badge badge-green"><CheckCircle2 size={10} /> Recovered</span>;
      case "executing":
        return <span className="badge badge-violet"><Activity size={10} /> Executing</span>;
      case "authorized":
        return <span className="badge badge-blue"><Shield size={10} /> Authorized</span>;
      case "pending":
        return <span className="badge badge-amber"><Clock size={10} /> Pending</span>;
      case "blocked":
      case "not_recovered":
        return <span className="badge badge-red"><XCircle size={10} /> {status}</span>;
      default:
        return <span className="badge badge-gray">{status}</span>;
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Opportunities Pipeline</h1>
          <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
            Live recovery opportunities ingested via webhook and canonical event streams.
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <div className="input" style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 12px", width: 220 }}>
            <Search size={14} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search ID, customer, reason..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ background: "transparent", border: "none", outline: "none", fontSize: 13, width: "100%", color: "var(--text-primary)" }}
            />
          </div>
          <button className="btn btn-ghost" onClick={fetchOpportunities} style={{ gap: 6 }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden", minHeight: 360 }}>
        {loading ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300 }}>
            <div style={{ width: 24, height: 24, border: "2px solid var(--electric-blue)", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: "48px 24px", textAlign: "center", color: "var(--text-muted)" }}>
            <AlertTriangle size={32} color="var(--text-muted)" style={{ marginBottom: 12 }} />
            <p style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
              {opportunities.length === 0 ? "No Recovery Opportunities Ingested Yet" : "No matching opportunities found"}
            </p>
            <p style={{ fontSize: 13, maxWidth: 440, margin: "0 auto" }}>
              {opportunities.length === 0
                ? "When payments fail on your connected Razorpay account or e-commerce store, they will automatically appear here for economic evaluation."
                : "Try adjusting your search criteria or refresh the pipeline."}
            </p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Opportunity ID</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Reason Code</th>
                  <th>Decline Type</th>
                  <th>Status</th>
                  <th>Created At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((opp) => (
                  <tr key={opp.id}>
                    <td>
                      <code style={{ fontSize: 11, background: "var(--bg-base)", padding: "2px 6px", borderRadius: 4 }}>
                        {opp.id}
                      </code>
                    </td>
                    <td style={{ fontSize: 12 }}>{opp.customer_id}</td>
                    <td style={{ fontWeight: 600 }}>
                      ₹{(opp.amount_paise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td>
                      <code style={{ fontSize: 11, color: "var(--text-secondary)" }}>{opp.reason_code}</code>
                    </td>
                    <td>
                      <span className={`badge ${opp.decline_type === "hard" ? "badge-red" : "badge-gray"}`}>
                        {opp.decline_type}
                      </span>
                    </td>
                    <td>{getStatusBadge(opp.status)}</td>
                    <td style={{ fontSize: 12, color: "var(--text-muted)" }}>
                      {new Date(opp.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </td>
                    <td>
                      <button
                        className="btn btn-ghost"
                        onClick={() => handleExplain(opp)}
                        style={{ padding: "4px 8px", fontSize: 11, gap: 4, color: "var(--electric-blue)" }}
                      >
                        <Sparkles size={12} /> Explain
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* AI Explanation Modal */}
      {selectedOpp && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", zIndex: 100,
          display: "flex", alignItems: "center", justifyContent: "center", padding: 20
        }}>
          <div className="card animate-fade-in" style={{ maxWidth: 600, width: "100%", padding: 24, maxHeight: "80vh", overflowY: "auto" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Sparkles size={18} color="var(--electric-blue)" />
                <h3 style={{ fontSize: 16, fontWeight: 700 }}>AI Economic Reasoning</h3>
              </div>
              <button className="btn btn-ghost" onClick={() => setSelectedOpp(null)} style={{ padding: 4 }}>
                <X size={16} />
              </button>
            </div>

            <div style={{ padding: "12px 14px", borderRadius: 8, background: "var(--bg-surface)", border: "1px solid var(--border)", marginBottom: 16 }}>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Target Opportunity</div>
              <div style={{ fontSize: 14, fontWeight: 600, marginTop: 2 }}>{selectedOpp.id} (₹{(selectedOpp.amount_paise / 100).toFixed(2)})</div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>Reason: {selectedOpp.reason_code} · Decline: {selectedOpp.decline_type}</div>
            </div>

            {explaining ? (
              <div style={{ padding: 32, textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>
                <RefreshCw size={18} style={{ animation: "spin 1s linear infinite", marginBottom: 8 }} />
                <br />Generating deterministic rationale & NVIDIA Nemotron explanation…
              </div>
            ) : aiExplanation?.error ? (
              <div style={{ color: "var(--rose)", fontSize: 13 }}>{aiExplanation.error}</div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {aiExplanation?.score && (
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
                    <div style={{ padding: 10, background: "var(--bg-card)", borderRadius: 8, border: "1px solid var(--border)" }}>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Incremental Recovery Prob</div>
                      <div style={{ fontSize: 15, fontWeight: 700, color: "var(--emerald)" }}>
                        +{(aiExplanation.score.incremental_prob * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div style={{ padding: 10, background: "var(--bg-card)", borderRadius: 8, border: "1px solid var(--border)" }}>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Expected Incremental Value (IVEN)</div>
                      <div style={{ fontSize: 15, fontWeight: 700, color: "var(--electric-blue)" }}>
                        ₹{(aiExplanation.score.expected_incremental_value_paise / 100).toFixed(2)}
                      </div>
                    </div>
                  </div>
                )}
                <div style={{ fontSize: 13, lineHeight: 1.6, color: "var(--text-secondary)", background: "rgba(0,0,0,0.2)", padding: 14, borderRadius: 8 }}>
                  {aiExplanation?.explanation || "Decision evaluated based on Bayesian probability tables and deterministic Action Authority gates."}
                </div>
              </div>
            )}

            <div style={{ marginTop: 20, display: "flex", justifyContent: "flex-end" }}>
              <button className="btn btn-ghost" onClick={() => setSelectedOpp(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
