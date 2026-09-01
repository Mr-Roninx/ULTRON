"use client";

import React, { useState, useEffect, useCallback } from "react";
import { ScrollText, Database, Code, History, RefreshCw, AlertTriangle, ShieldCheck } from "lucide-react";
import { api } from "../../../lib/auth";

interface AuditRecord {
  id: string;
  tenant_id: string;
  actor_id: string;
  actor_type: string;
  action: string;
  resource_type: string;
  resource_id: string;
  payload?: any;
  ip_address?: string;
  timestamp: string;
}

export default function AuditPage() {
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAudit = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api<{ records: AuditRecord[]; ledger?: any[] }>("/audit/records");
      setRecords(data.records || []);
    } catch {
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAudit();
  }, [fetchAudit]);

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Forensic Audit Trail & Ledger</h1>
          <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
            Tamper-evident log of every API interaction, economic scoring pass, and compliance decision.
          </p>
        </div>
        <button className="btn btn-ghost" onClick={fetchAudit} style={{ gap: 6 }}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden", minHeight: 360 }}>
        {loading ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300 }}>
            <div style={{ width: 24, height: 24, border: "2px solid var(--electric-blue)", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
          </div>
        ) : records.length === 0 ? (
          <div style={{ padding: "48px 24px", textAlign: "center", color: "var(--text-muted)" }}>
            <ShieldCheck size={32} color="var(--emerald)" style={{ marginBottom: 12 }} />
            <p style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
              Audit Trail Active
            </p>
            <p style={{ fontSize: 13, maxWidth: 440, margin: "0 auto" }}>
              Every action performed on your tenant account (API calls, allocations, authorizations, executions) is written to durable storage as it happens.
            </p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column" }}>
            {records.map((rec) => (
              <div
                key={rec.id}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 16,
                  padding: "16px 20px",
                  borderBottom: "1px solid var(--border)",
                }}
              >
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: "50%",
                    background: "var(--bg-hover)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "var(--electric-blue)",
                    flexShrink: 0,
                    marginTop: 2,
                  }}
                >
                  <Database size={14} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, display: "flex", alignItems: "center", gap: 8 }}>
                      <span>{rec.action}</span>
                      <span className="badge badge-gray" style={{ fontSize: 10 }}>{rec.resource_type}</span>
                      {rec.actor_type && <span className="badge badge-blue" style={{ fontSize: 10 }}>{rec.actor_type}</span>}
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "monospace" }}>
                      {new Date(rec.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                    </div>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>
                    Resource ID: <code style={{ fontSize: 11 }}>{rec.resource_id}</code> · Actor: <code style={{ fontSize: 11 }}>{rec.actor_id}</code> {rec.ip_address && `· IP: ${rec.ip_address}`}
                  </div>
                  {rec.payload && (
                    <pre
                      style={{
                        background: "rgba(0,0,0,0.2)",
                        padding: "8px 12px",
                        borderRadius: 6,
                        fontSize: 11,
                        color: "var(--text-muted)",
                        overflowX: "auto",
                        marginTop: 6,
                      }}
                    >
                      {typeof rec.payload === "string" ? rec.payload : JSON.stringify(rec.payload, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
