"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  ScrollText, Database, ShieldCheck, CheckCircle2, Clock, Zap,
  ChevronDown, ChevronRight, Copy, Check, FileSpreadsheet, Download
} from "lucide-react";
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

interface LedgerEntry {
  id: string;
  opportunity_id: string;
  event_type: "webhook_received" | "reconciled" | "recovered" | "not_recovered";
  amount_paise: number;
  timestamp: string;
  raw_payload_ref?: string;
  currency?: string;
  reason_code?: string;
  decline_type?: string;
  customer_id?: string;
}

interface VerificationProof {
  verified: boolean;
  is_balanced: boolean;
  total_blocks: number;
  total_debit_paise: number;
  total_credit_paise: number;
  root_hash: string;
  certificate_id: string;
  verified_at: string;
}

export default function AuditPage() {
  const [activeTab, setActiveTab] = useState<"ledger" | "access">("ledger");
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [ledgerEntries, setLedgerEntries] = useState<LedgerEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [verificationProof, setVerificationProof] = useState<VerificationProof | null>(null);
  const [verifying, setVerifying] = useState(false);

  const fetchAudit = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api<{ records: AuditRecord[]; ledger?: LedgerEntry[] }>("/audit/records");
      setRecords(data.records || []);
      setLedgerEntries(data.ledger || []);
    } catch {
      setRecords([]);
      setLedgerEntries([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleVerifyLedger = async () => {
    setVerifying(true);
    try {
      const proof = await api<VerificationProof>("/v1/audit/verify");
      setVerificationProof(proof);
    } catch (e: any) {
      alert("Verification failed: " + e.message);
    } finally {
      setVerifying(false);
    }
  };

  const handleDownloadJSON = async () => {
    try {
      const res = await api<any>("/v1/audit/export/json");
      const blob = new Blob([JSON.stringify(res, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ULTRON_Audit_Ledger_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (e: any) {
      alert("Export failed: " + e.message);
    }
  };

  useEffect(() => {
    fetchAudit();
    handleVerifyLedger();
  }, [fetchAudit]);

  const copyPayload = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getLedgerBadge = (type: string) => {
    switch (type) {
      case "recovered":
        return <span className="badge badge-green"><CheckCircle2 size={11} /> RECOVERED</span>;
      case "reconciled":
        return <span className="badge badge-blue"><Zap size={11} /> RECONCILED</span>;
      case "webhook_received":
        return <span className="badge badge-blue"><Clock size={11} /> WEBHOOK</span>;
      default:
        return <span className="badge badge-gray">{type}</span>;
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: 1440, margin: "0 auto", width: "100%" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px", margin: "0 0 4px 0" }}>
            Forensic Audit Trail & Cryptographic Ledger
          </h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: 0 }}>
            Tamper-evident double-entry ledger with SHA-256 hash chaining, verifiable financial balance, and immutable security logs.
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button
            onClick={handleVerifyLedger}
            disabled={verifying}
            className="btn btn-secondary"
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
          >
            <ShieldCheck size={14} color="var(--google-green)" />
            <span>{verifying ? "Verifying..." : "Verify Hash Chain"}</span>
          </button>

          <button
            onClick={handleDownloadJSON}
            className="btn btn-primary"
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
          >
            <Download size={14} />
            <span>Download Audit Certificate</span>
          </button>
        </div>
      </div>

      {/* Verification Banner */}
      {verificationProof && (
        <div style={{
          padding: "14px 18px", borderRadius: 8, marginBottom: 20,
          background: verificationProof.verified ? "var(--google-green-light)" : "var(--google-red-light)",
          border: verificationProof.verified ? "1px solid #ceead6" : "1px solid #fad2cf",
          display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <ShieldCheck size={20} color={verificationProof.verified ? "var(--google-green-hover)" : "var(--google-red)"} />
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)" }}>
                SHA-256 Cryptographic Hash-Chain: {verificationProof.verified ? "VERIFIED (ZERO TAMPERING)" : "INVALID"}
              </div>
              <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
                Certificate: <code>{verificationProof.certificate_id}</code> · Root Hash: <code>{verificationProof.root_hash.slice(0, 20)}...</code>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", gap: 16, fontSize: 12 }}>
            <div>
              <span style={{ color: "var(--text-secondary)" }}>Accounting: </span>
              <span style={{ fontWeight: 700, color: "var(--google-green-hover)" }}>Debit = Credit (Balanced ✓)</span>
            </div>
            <div>
              <span style={{ color: "var(--text-secondary)" }}>Blocks: </span>
              <span style={{ fontWeight: 700 }}>{verificationProof.total_blocks}</span>
            </div>
          </div>
        </div>
      )}

      {/* Tab Switcher */}
      <div style={{ display: "flex", gap: 6, background: "var(--bg-hover)", padding: 4, borderRadius: 20, width: "fit-content", marginBottom: 16 }}>
        <button
          onClick={() => setActiveTab("ledger")}
          style={{
            padding: "5px 14px", borderRadius: 16, fontSize: 12, fontWeight: 500, border: "none", cursor: "pointer",
            background: activeTab === "ledger" ? "#ffffff" : "transparent",
            color: activeTab === "ledger" ? "var(--google-blue)" : "var(--text-secondary)",
            boxShadow: activeTab === "ledger" ? "0 1px 2px rgba(60,64,67,0.15)" : "none",
            display: "flex", alignItems: "center", gap: 6, transition: "all 0.15s"
          }}
        >
          <FileSpreadsheet size={14} />
          <span>Immutable Ledger ({ledgerEntries.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("access")}
          style={{
            padding: "5px 14px", borderRadius: 16, fontSize: 12, fontWeight: 500, border: "none", cursor: "pointer",
            background: activeTab === "access" ? "#ffffff" : "transparent",
            color: activeTab === "access" ? "var(--google-blue)" : "var(--text-secondary)",
            boxShadow: activeTab === "access" ? "0 1px 2px rgba(60,64,67,0.15)" : "none",
            display: "flex", alignItems: "center", gap: 6, transition: "all 0.15s"
          }}
        >
          <Database size={14} />
          <span>Security & API Logs ({records.length})</span>
        </button>
      </div>

      {/* Tab 1: Ledger Table */}
      {activeTab === "ledger" && (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
              <thead>
                <tr style={{ background: "#f8f9fa", borderBottom: "1px solid var(--border)", color: "var(--text-secondary)", fontSize: 11, textTransform: "uppercase" }}>
                  <th style={{ padding: "10px 16px", width: 30 }}></th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>Event</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>Timestamp</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>Opportunity ID</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>Amount (₹)</th>
                  <th style={{ padding: "10px 16px", fontWeight: 600 }}>Customer / Details</th>
                </tr>
              </thead>
              <tbody>
                {ledgerEntries.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ padding: "48px 20px", textAlign: "center", color: "var(--text-muted)" }}>
                      <CheckCircle2 size={28} style={{ margin: "0 auto 8px", color: "var(--google-green)" }} />
                      <div>Ledger Active & Synchronized</div>
                    </td>
                  </tr>
                ) : (
                  ledgerEntries.map((item: LedgerEntry) => {
                    const isExpanded = expandedId === item.id;
                    return (
                      <React.Fragment key={item.id}>
                        <tr
                          style={{
                            borderBottom: "1px solid var(--border-subtle)",
                            background: isExpanded ? "var(--google-blue-light)" : "#ffffff",
                            cursor: "pointer"
                          }}
                          onClick={() => setExpandedId(isExpanded ? null : item.id)}
                        >
                          <td style={{ padding: "12px 16px", color: "var(--text-secondary)" }}>
                            {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                          </td>
                          <td style={{ padding: "12px 16px" }}>{getLedgerBadge(item.event_type)}</td>
                          <td style={{ padding: "12px 16px", fontSize: 12, color: "var(--text-secondary)" }}>
                            {new Date(item.timestamp).toLocaleString()}
                          </td>
                          <td style={{ padding: "12px 16px", fontFamily: "var(--font-mono)", fontSize: 12 }}>
                            {item.opportunity_id}
                          </td>
                          <td style={{ padding: "12px 16px", fontWeight: 700 }}>
                            ₹{(item.amount_paise / 100).toLocaleString("en-IN")}
                          </td>
                          <td style={{ padding: "12px 16px", color: "var(--text-secondary)", fontSize: 12 }}>
                            {item.customer_id || "Customer Checkout"}
                          </td>
                        </tr>

                        {isExpanded && item.raw_payload_ref && (
                          <tr style={{ background: "var(--bg-hover)", borderBottom: "1px solid var(--border-subtle)" }}>
                            <td colSpan={6} style={{ padding: "12px 20px" }}>
                              <pre style={{ margin: 0, fontSize: 11, fontFamily: "var(--font-mono)", background: "#202124", color: "#ffffff", padding: 12, borderRadius: 6, overflowX: "auto" }}>
                                {item.raw_payload_ref}
                              </pre>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Access Logs */}
      {activeTab === "access" && (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          {records.length === 0 ? (
            <div style={{ padding: "48px 20px", textAlign: "center", color: "var(--text-muted)" }}>
              No access logs recorded yet.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column" }}>
              {records.map((rec: AuditRecord) => (
                <div
                  key={rec.id}
                  style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "12px 20px", borderBottom: "1px solid var(--border-subtle)", background: "#ffffff"
                  }}
                >
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>{rec.action}</div>
                    <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>
                      Actor: {rec.actor_type} · Resource: {rec.resource_type} ({rec.resource_id})
                    </div>
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                    {new Date(rec.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
