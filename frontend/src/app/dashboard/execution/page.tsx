"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Zap, Link as LinkIcon, ExternalLink, CheckCircle2, RefreshCw, Play, AlertTriangle } from "lucide-react";
import { api } from "../../../lib/auth";

interface ExecutionRecord {
  opportunity_id: string;
  razorpay_payment_link_id: string;
  link_url: string;
  status: string;
  idempotency_key: string;
  created_at: string;
}

export default function ExecutionPage() {
  const [records, setRecords] = useState<ExecutionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api<{ records: ExecutionRecord[] }>("/execution/records");
      setRecords(data.records || []);
    } catch {
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  const handleExecuteBatch = async () => {
    setExecuting(true);
    try {
      const res = await api<{ executed_count: number; total_authorized: number }>("/execution/run", {
        method: "POST",
        body: JSON.stringify({}),
      });
      alert(`Execution completed: ${res.executed_count} payment links generated from ${res.total_authorized} authorized opportunities.`);
      fetchRecords();
    } catch (err: any) {
      alert(`Execution error: ${err.message}`);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Execution & Payment Links</h1>
          <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
            Live recovery payment links dispatched through tenant Razorpay gateways with zero-bypass compliance.
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn btn-ghost" onClick={fetchRecords} style={{ gap: 6 }}>
            <RefreshCw size={14} /> Refresh
          </button>
          <button className="btn btn-primary" onClick={handleExecuteBatch} disabled={executing} style={{ gap: 6 }}>
            {executing ? <RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} /> : <Play size={14} />}
            {executing ? "Generating Links…" : "Execute Authorized Batch"}
          </button>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden", minHeight: 360 }}>
        {loading ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300 }}>
            <div style={{ width: 24, height: 24, border: "2px solid var(--electric-blue)", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
          </div>
        ) : records.length === 0 ? (
          <div style={{ padding: "48px 24px", textAlign: "center", color: "var(--text-muted)" }}>
            <AlertTriangle size={32} color="var(--text-muted)" style={{ marginBottom: 12 }} />
            <p style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
              No Execution Records Yet
            </p>
            <p style={{ fontSize: 13, maxWidth: 440, margin: "0 auto" }}>
              When opportunities pass the Action Authority compliance checks and get executed, their hosted Razorpay payment links and statuses will be recorded here.
            </p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Opportunity ID</th>
                  <th>Provider</th>
                  <th>Payment Link</th>
                  <th>Status</th>
                  <th>Idempotency Key</th>
                  <th>Executed At</th>
                </tr>
              </thead>
              <tbody>
                {records.map((rec) => (
                  <tr key={rec.opportunity_id}>
                    <td>
                      <code style={{ fontSize: 11, background: "var(--bg-base)", padding: "2px 6px", borderRadius: 4 }}>
                        {rec.opportunity_id}
                      </code>
                    </td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, fontWeight: 500 }}>
                        <Zap size={13} color="var(--emerald)" /> Razorpay Gateway
                      </div>
                    </td>
                    <td>
                      <a
                        href={rec.link_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--electric-blue)", textDecoration: "none", fontWeight: 500 }}
                      >
                        {rec.razorpay_payment_link_id} <ExternalLink size={11} />
                      </a>
                    </td>
                    <td>
                      <span className={`badge ${rec.status === "paid" ? "badge-green" : "badge-blue"}`}>
                        <CheckCircle2 size={10} /> {rec.status}
                      </span>
                    </td>
                    <td>
                      <code style={{ fontSize: 10, color: "var(--text-muted)" }}>{rec.idempotency_key}</code>
                    </td>
                    <td style={{ fontSize: 12, color: "var(--text-muted)" }}>
                      {new Date(rec.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
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
