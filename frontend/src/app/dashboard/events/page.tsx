"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import {
  Radio,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ShieldAlert,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Search,
  Code,
  Zap,
  Play,
  Pause,
  Terminal,
  RotateCcw,
  Inbox,
  Layers,
  Sparkles,
  Clock,
} from "lucide-react";
import { api, useAuth } from "../../../lib/auth";

interface EventLog {
  id: string;
  tenant_id: string;
  event_id?: string;
  payment_id?: string;
  source: string;
  status: "ACCEPTED" | "REJECTED" | "DEDUPLICATED" | "UNAUTHORIZED";
  status_code: number;
  rejection_reason?: string;
  opportunity_id?: string;
  raw_payload: string;
  origin?: string;
  created_at: string;
}

interface WebhookDeliveryItem {
  id: string;
  tenant_id: string;
  source: string;
  event_id?: string;
  event_type: string;
  payload: string;
  headers?: string;
  status: "PENDING" | "PROCESSING" | "DELIVERED" | "FAILED" | "DEAD_LETTER";
  attempts: number;
  max_attempts: number;
  last_error?: string;
  next_retry_at?: string;
  delivered_at?: string;
  created_at: string;
}

export default function LiveEventsPage() {
  const { tenant, token } = useAuth();
  const [activeTab, setActiveTab] = useState<"stream" | "queue">("stream");

  // Stream Tab State
  const [logs, setLogs] = useState<EventLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isInjecting, setIsInjecting] = useState(false);
  const [injectionSuccess, setInjectionSuccess] = useState<string | null>(null);

  // Queue Tab State
  const [queueDeliveries, setQueueDeliveries] = useState<WebhookDeliveryItem[]>([]);
  const [queueLoading, setQueueLoading] = useState(false);
  const [queueFilter, setQueueFilter] = useState<string>("ALL");
  const [replayingId, setReplayingId] = useState<string | null>(null);
  const [replayToast, setReplayToast] = useState<string | null>(null);

  const fetchLogs = useCallback(async (isSilent = false) => {
    if (!isSilent) setRefreshing(true);
    try {
      const data = await api<{ success: boolean; count: number; logs: EventLog[] }>(
        "/v1/events/stream?limit=100"
      );
      if (data && data.logs) {
        setLogs(data.logs);
      }
    } catch (err: any) {
      console.error("Failed to fetch event stream:", err);
    } finally {
      if (!isSilent) {
        setRefreshing(false);
        setLoading(false);
      }
    }
  }, []);

  const fetchQueue = useCallback(async () => {
    setQueueLoading(true);
    try {
      const data = await api<{ success: boolean; deliveries: WebhookDeliveryItem[] }>(
        "/v1/webhooks/queue?limit=100"
      );
      if (data && data.deliveries) {
        setQueueDeliveries(data.deliveries);
      }
    } catch (err: any) {
      console.error("Failed to fetch webhook queue:", err);
    } finally {
      setQueueLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchLogs(false);
    fetchQueue();
  }, [fetchLogs, fetchQueue]);

  const [isSseConnected, setIsSseConnected] = useState(false);

  // Real-Time SSE Push Connection
  useEffect(() => {
    if (!token || typeof window === "undefined") return;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
    const sseUrl = `${apiUrl}/v1/events/live-stream?token=${encodeURIComponent(token)}`;
    let eventSource: EventSource | null = null;

    try {
      eventSource = new EventSource(sseUrl);

      eventSource.addEventListener("CONNECTED", () => {
        setIsSseConnected(true);
      });

      eventSource.addEventListener("EVENT_INGESTED", (evt: MessageEvent) => {
        try {
          const parsed = JSON.parse(evt.data);
          if (parsed && parsed.data) {
            setLogs((prev) => {
              const incoming = parsed.data;
              if (prev.some((l) => l.id === incoming.id || (incoming.event_id && l.event_id === incoming.event_id))) {
                return prev;
              }
              return [incoming, ...prev].slice(0, 100);
            });
          }
        } catch (e) {
          console.error("SSE parse error:", e);
        }
      });

      eventSource.onerror = () => {
        setIsSseConnected(false);
      };
    } catch (e) {
      console.warn("Could not initiate SSE stream, using polling fallback:", e);
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [token]);

  // Real-time polling fallback loop (active if SSE is reconnecting or on queue tab)
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      if (activeTab === "stream") {
        if (!isSseConnected) {
          fetchLogs(true);
        }
      } else {
        fetchQueue();
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, activeTab, isSseConnected, fetchLogs, fetchQueue]);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Replay single delivery
  const handleReplayDelivery = async (deliveryId: string) => {
    setReplayingId(deliveryId);
    setReplayToast(null);
    try {
      const res = await api<any>(`/v1/webhooks/queue/${deliveryId}/replay`, {
        method: "POST",
      });
      if (res && res.success) {
        setReplayToast(`Webhook delivery ${deliveryId.slice(0, 14)} successfully replayed!`);
      } else {
        setReplayToast(`Replay failed: ${res?.error || "Unknown error"}`);
      }
      await fetchQueue();
      await fetchLogs(true);
      setTimeout(() => setReplayToast(null), 4000);
    } catch (e: any) {
      setReplayToast(`Replay error: ${e.message}`);
    } finally {
      setReplayingId(null);
    }
  };

  // Retry all dead-letter webhooks
  const handleRetryAllDeadLetter = async () => {
    try {
      const res = await api<any>("/v1/webhooks/queue/retry-all", { method: "POST" });
      setReplayToast(`Requeued ${res?.requeued_count || 0} dead-letter deliveries.`);
      await fetchQueue();
      setTimeout(() => setReplayToast(null), 4000);
    } catch (e: any) {
      console.error(e);
    }
  };

  // Enqueue sample test delivery
  const handleEnqueueTestWebhook = async () => {
    try {
      await api("/v1/webhooks/queue/enqueue-test", { method: "POST" });
      setReplayToast("Test webhook enqueued successfully.");
      await fetchQueue();
      setTimeout(() => setReplayToast(null), 4000);
    } catch (e: any) {
      console.error(e);
    }
  };

  // Quick Test Event Injections
  const injectSampleEvent = async (type: "valid_failed" | "malformed" | "duplicate") => {
    setIsInjecting(true);
    setInjectionSuccess(null);
    try {
      let payload: any = {};
      const uniqueNum = Date.now();

      if (type === "valid_failed") {
        payload = {
          event_id: `evt_sim_${uniqueNum}`,
          source: "CLIENT_SDK",
          provider: "razorpay",
          environment: tenant?.environment || "test",
          payment_id: `pay_sim_${uniqueNum}`,
          amount_paise: 45000,
          currency: "INR",
          status: "failed",
          failure_code: "INSUFFICIENT_FUNDS",
          failure_description: "Live Stream Test: Customer account balance depleted",
          customer_reference: "customer_live_test@example.com",
          customer_email: "customer_live_test@example.com",
          occurred_at: new Date().toISOString(),
          metadata: { page: "/checkout", simulated: true },
        };
      } else if (type === "malformed") {
        payload = {
          event_id: `evt_bad_${uniqueNum}`,
          amount_paise: -500,
          currency: "INVALID_CURRENCY",
          failure_code: "",
        };
      } else if (type === "duplicate") {
        if (logs.length > 0 && logs[0].event_id) {
          payload = {
            event_id: logs[0].event_id,
            source: "CLIENT_SDK",
            provider: "razorpay",
            payment_id: logs[0].payment_id || `pay_${uniqueNum}`,
            amount_paise: 25000,
            currency: "INR",
            status: "failed",
            failure_code: "CARD_EXPIRED",
            customer_reference: "cust_stream_dup@example.com",
          };
        } else {
          payload = {
            event_id: `evt_dup_${uniqueNum}`,
            source: "CLIENT_SDK",
            provider: "razorpay",
            payment_id: `pay_${uniqueNum}`,
            amount_paise: 25000,
            currency: "INR",
            status: "failed",
            failure_code: "CARD_EXPIRED",
            customer_reference: "cust_stream_dup@example.com",
          };
        }
      }

      await api("/v1/events", {
        method: "POST",
        body: JSON.stringify(payload),
      }).catch((e) => {
        console.log("Expected server response for test event:", e.message);
      });

      setInjectionSuccess(`Test ${type.replace("_", " ")} event dispatched!`);
      await fetchLogs(false);
      setTimeout(() => setInjectionSuccess(null), 4000);
    } catch (err: any) {
      console.error("Injection error:", err);
    } finally {
      setIsInjecting(false);
    }
  };

  // Metrics computation
  const stats = useMemo(() => {
    const total = logs.length;
    const accepted = logs.filter((l) => l.status === "ACCEPTED").length;
    const rejected = logs.filter((l) => l.status === "REJECTED" || l.status === "UNAUTHORIZED").length;
    const deduplicated = logs.filter((l) => l.status === "DEDUPLICATED").length;
    return { total, accepted, rejected, deduplicated };
  }, [logs]);

  // Queue metrics
  const queueStats = useMemo(() => {
    const total = queueDeliveries.length;
    const delivered = queueDeliveries.filter((q) => q.status === "DELIVERED").length;
    const deadLetter = queueDeliveries.filter((q) => q.status === "DEAD_LETTER").length;
    const pending = queueDeliveries.filter((q) => q.status === "PENDING" || q.status === "PROCESSING").length;
    return { total, delivered, deadLetter, pending };
  }, [queueDeliveries]);

  // Filtering stream logs
  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      if (selectedStatus !== "ALL") {
        if (selectedStatus === "REJECTED") {
          if (log.status !== "REJECTED" && log.status !== "UNAUTHORIZED") return false;
        } else if (log.status !== selectedStatus) {
          return false;
        }
      }

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesId = log.id.toLowerCase().includes(q);
        const matchesEventId = (log.event_id || "").toLowerCase().includes(q);
        const matchesPaymentId = (log.payment_id || "").toLowerCase().includes(q);
        const matchesOppId = (log.opportunity_id || "").toLowerCase().includes(q);
        const matchesReason = (log.rejection_reason || "").toLowerCase().includes(q);
        const matchesPayload = log.raw_payload.toLowerCase().includes(q);
        return matchesId || matchesEventId || matchesPaymentId || matchesOppId || matchesReason || matchesPayload;
      }

      return true;
    });
  }, [logs, selectedStatus, searchQuery]);

  // Filtering queue deliveries
  const filteredQueue = useMemo(() => {
    return queueDeliveries.filter((d) => {
      if (queueFilter !== "ALL" && d.status !== queueFilter) return false;
      return true;
    });
  }, [queueDeliveries, queueFilter]);

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 1200, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "linear-gradient(135deg, rgba(59,130,246,0.2), rgba(16,185,129,0.2))",
              border: "1px solid rgba(59,130,246,0.3)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <Radio size={16} color="var(--electric-blue)" />
            </div>
            <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Live Ingestion Stream & Webhook Queue</h1>
            <span style={{
              fontSize: 11, padding: "3px 10px", borderRadius: 12, fontWeight: 700,
              background: !autoRefresh
                ? "rgba(255,255,255,0.08)"
                : isSseConnected
                ? "rgba(59,130,246,0.18)"
                : "rgba(16,185,129,0.15)",
              color: !autoRefresh
                ? "var(--text-muted)"
                : isSseConnected
                ? "var(--electric-blue)"
                : "var(--emerald)",
              display: "inline-flex", alignItems: "center", gap: 6,
              border: isSseConnected ? "1px solid rgba(59,130,246,0.3)" : "none"
            }}>
              <span style={{
                width: 7, height: 7, borderRadius: "50%",
                background: !autoRefresh
                  ? "var(--text-muted)"
                  : isSseConnected
                  ? "var(--electric-blue)"
                  : "var(--emerald)",
                boxShadow: !autoRefresh
                  ? "none"
                  : isSseConnected
                  ? "0 0 10px var(--electric-blue)"
                  : "0 0 8px var(--emerald)"
              }} />
              {!autoRefresh ? "PAUSED" : isSseConnected ? "REAL-TIME SSE (0ms)" : "STREAMING (POLL 3s)"}
            </span>
          </div>
          <p style={{ fontSize: 13, color: "var(--text-muted)", margin: 0 }}>
            Inspect incoming payment events, replay failed webhooks, and manage your delivery queue in real-time.
          </p>
        </div>

        {/* Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button
            className={`btn ${autoRefresh ? "btn-ghost" : "primary"}`}
            onClick={() => setAutoRefresh(!autoRefresh)}
            style={{ fontSize: 13, gap: 6 }}
          >
            {autoRefresh ? <Pause size={14} /> : <Play size={14} />}
            {autoRefresh ? "Pause Stream" : "Resume Stream"}
          </button>
          <button
            className="btn btn-ghost"
            onClick={() => {
              if (activeTab === "stream") fetchLogs(false);
              else fetchQueue();
            }}
            disabled={refreshing || queueLoading}
            style={{ fontSize: 13, gap: 6 }}
          >
            <RefreshCw size={14} className={refreshing || queueLoading ? "spin" : ""} />
            Refresh
          </button>
        </div>
      </div>

      {/* Navigation View Switcher Tabs */}
      <div style={{ display: "flex", borderBottom: "1px solid var(--border)", gap: 20 }}>
        <button
          onClick={() => setActiveTab("stream")}
          style={{
            background: "none", border: "none", cursor: "pointer",
            padding: "10px 4px", fontSize: 14, fontWeight: 600,
            color: activeTab === "stream" ? "var(--electric-blue)" : "var(--text-muted)",
            borderBottom: activeTab === "stream" ? "2px solid var(--electric-blue)" : "2px solid transparent",
            display: "flex", alignItems: "center", gap: 8
          }}
        >
          <Radio size={16} /> Live Ingestion Stream ({logs.length})
        </button>

        <button
          onClick={() => setActiveTab("queue")}
          style={{
            background: "none", border: "none", cursor: "pointer",
            padding: "10px 4px", fontSize: 14, fontWeight: 600,
            color: activeTab === "queue" ? "var(--electric-blue)" : "var(--text-muted)",
            borderBottom: activeTab === "queue" ? "2px solid var(--electric-blue)" : "2px solid transparent",
            display: "flex", alignItems: "center", gap: 8
          }}
        >
          <RotateCcw size={16} /> Webhook Delivery Queue & DLQ ({queueDeliveries.length})
          {queueStats.deadLetter > 0 && (
            <span style={{ fontSize: 10, padding: "1px 6px", borderRadius: 8, background: "var(--rose)", color: "white", fontWeight: 700 }}>
              {queueStats.deadLetter} DLQ
            </span>
          )}
        </button>
      </div>

      {replayToast && (
        <div className="animate-fade-in" style={{
          padding: "12px 18px", borderRadius: 8,
          background: "rgba(59,130,246,0.12)", border: "1px solid rgba(59,130,246,0.3)",
          color: "var(--electric-blue)", fontSize: 13, display: "flex", alignItems: "center", gap: 8
        }}>
          <Sparkles size={16} />
          {replayToast}
        </div>
      )}

      {/* VIEW A: LIVE INGESTION STREAM */}
      {activeTab === "stream" && (
        <>
          {/* Quick Action Tester Drawer */}
          <div className="card" style={{
            padding: "14px 20px",
            background: "rgba(255,255,255,0.02)",
            border: "1px dashed var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Zap size={16} color="var(--electric-blue)" />
              <span style={{ fontSize: 13, fontWeight: 600 }}>Test Event Dispatcher:</span>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                Simulate events to verify your monitoring and error logging in real-time.
              </span>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <button
                className="btn btn-ghost"
                onClick={() => injectSampleEvent("valid_failed")}
                disabled={isInjecting}
                style={{ fontSize: 12, padding: "6px 12px", border: "1px solid rgba(16,185,129,0.3)", color: "var(--emerald)" }}
              >
                + Valid Failure (201)
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => injectSampleEvent("malformed")}
                disabled={isInjecting}
                style={{ fontSize: 12, padding: "6px 12px", border: "1px solid rgba(244,63,94,0.3)", color: "var(--rose)" }}
              >
                + Malformed Zod (400)
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => injectSampleEvent("duplicate")}
                disabled={isInjecting}
                style={{ fontSize: 12, padding: "6px 12px", border: "1px solid rgba(245,158,11,0.3)", color: "var(--amber)" }}
              >
                + Duplicate Event (200)
              </button>
            </div>
          </div>

          {injectionSuccess && (
            <div className="animate-fade-in" style={{
              padding: "10px 16px", borderRadius: 8,
              background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.3)",
              color: "var(--emerald)", fontSize: 13, display: "flex", alignItems: "center", gap: 8
            }}>
              <CheckCircle2 size={16} />
              {injectionSuccess}
            </div>
          )}

          {/* Stats Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Total Ingested
              </div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.total.toLocaleString()}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Across all integration origins</div>
            </div>

            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8, borderLeft: "3px solid var(--emerald)" }}>
              <div style={{ fontSize: 12, color: "var(--emerald)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Accepted (201 / 200)
              </div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--emerald)" }}>{stats.accepted.toLocaleString()}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Passed validation & normalized</div>
            </div>

            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8, borderLeft: "3px solid var(--rose)" }}>
              <div style={{ fontSize: 12, color: "var(--rose)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Rejected / Failed (400 / 403)
              </div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--rose)" }}>{stats.rejected.toLocaleString()}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Zod schema or auth mismatches</div>
            </div>

            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8, borderLeft: "3px solid var(--amber)" }}>
              <div style={{ fontSize: 12, color: "var(--amber)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Deduplicated (200)
              </div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--amber)" }}>{stats.deduplicated.toLocaleString()}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Replay prevented by event/pay ID</div>
            </div>
          </div>

          {/* Filter & Search Bar */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
            <div style={{ display: "flex", background: "var(--bg-surface)", padding: 4, borderRadius: 10, border: "1px solid var(--border)", gap: 4 }}>
              {["ALL", "ACCEPTED", "REJECTED", "DEDUPLICATED"].map((status) => {
                const isSelected = selectedStatus === status;
                return (
                  <button
                    key={status}
                    onClick={() => setSelectedStatus(status)}
                    style={{
                      padding: "6px 14px",
                      borderRadius: 6,
                      border: "none",
                      cursor: "pointer",
                      fontSize: 12,
                      fontWeight: 600,
                      transition: "all 0.15s",
                      background: isSelected ? "var(--electric-blue)" : "transparent",
                      color: isSelected ? "white" : "var(--text-secondary)",
                    }}
                  >
                    {status}
                  </button>
                );
              })}
            </div>

            <div style={{ position: "relative", minWidth: 280 }}>
              <Search size={14} color="var(--text-muted)" style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)" }} />
              <input
                type="text"
                placeholder="Search event ID, payload, errors..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: "100%",
                  padding: "8px 12px 8px 34px",
                  background: "var(--bg-surface)",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  color: "var(--text-primary)",
                  fontSize: 13,
                  outline: "none",
                }}
              />
            </div>
          </div>

          {/* Event Stream Table */}
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            {loading ? (
              <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
                <RefreshCw size={24} className="spin" style={{ margin: "0 auto 12px" }} />
                Connecting to Live Ingestion Stream...
              </div>
            ) : filteredLogs.length === 0 ? (
              <div style={{ padding: 48, textAlign: "center", color: "var(--text-muted)" }}>
                <Terminal size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
                <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 4 }}>
                  No Events Found
                </div>
              </div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table className="data-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr style={{ background: "var(--bg-hover)", color: "var(--text-muted)", textAlign: "left", borderBottom: "1px solid var(--border)" }}>
                      <th style={{ padding: "12px 16px", width: 40 }}></th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Status</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Timestamp</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Event / Payment ID</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Source / Origin</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>HTTP Code</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Details / Opportunity</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600, textAlign: "right" }}>Inspect</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLogs.map((log) => {
                      const isExpanded = expandedLogId === log.id;
                      let parsedPayload: any = null;
                      try {
                        parsedPayload = JSON.parse(log.raw_payload);
                      } catch {
                        parsedPayload = log.raw_payload;
                      }

                      return (
                        <React.Fragment key={log.id}>
                          <tr
                            style={{
                              borderBottom: "1px solid var(--border)",
                              background: isExpanded ? "rgba(59,130,246,0.04)" : "transparent",
                              cursor: "pointer",
                            }}
                            onClick={() => setExpandedLogId(isExpanded ? null : log.id)}
                          >
                            <td style={{ padding: "12px 16px", color: "var(--text-muted)" }}>
                              {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                            </td>
                            <td style={{ padding: "12px 16px" }}>
                              {log.status === "ACCEPTED" && (
                                <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(16,185,129,0.15)", color: "var(--emerald)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                                  <CheckCircle2 size={12} /> ACCEPTED
                                </span>
                              )}
                              {log.status === "REJECTED" && (
                                <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(244,63,94,0.15)", color: "var(--rose)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                                  <XCircle size={12} /> REJECTED
                                </span>
                              )}
                              {log.status === "DEDUPLICATED" && (
                                <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(245,158,11,0.15)", color: "var(--amber)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                                  <Copy size={12} /> DEDUPLICATED
                                </span>
                              )}
                              {log.status === "UNAUTHORIZED" && (
                                <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(239,68,68,0.2)", color: "var(--rose)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                                  <ShieldAlert size={12} /> FORBIDDEN
                                </span>
                              )}
                            </td>
                            <td style={{ padding: "12px 16px", whiteSpace: "nowrap" }}>
                              <div style={{ fontSize: 13, fontWeight: 500 }}>
                                {new Date(log.created_at).toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                              </div>
                            </td>
                            <td style={{ padding: "12px 16px", fontFamily: "monospace", fontSize: 12, fontWeight: 600 }}>
                              {log.event_id || log.payment_id || "[no id]"}
                            </td>
                            <td style={{ padding: "12px 16px" }}>
                              <span className="tag" style={{ fontSize: 10, padding: "2px 6px" }}>{log.source}</span>
                            </td>
                            <td style={{ padding: "12px 16px", fontFamily: "monospace", fontWeight: 700 }}>
                              <span style={{ color: log.status_code >= 200 && log.status_code < 300 ? "var(--emerald)" : "var(--rose)" }}>
                                {log.status_code}
                              </span>
                            </td>
                            <td style={{ padding: "12px 16px", maxWidth: 280 }}>
                              {log.rejection_reason ? (
                                <div style={{ color: "var(--rose)", fontSize: 11, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={log.rejection_reason}>
                                  {log.rejection_reason}
                                </div>
                              ) : log.opportunity_id ? (
                                <Link
                                  href="/dashboard/opportunities"
                                  onClick={(e) => e.stopPropagation()}
                                  style={{ color: "var(--electric-blue)", fontSize: 12, textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 4, fontWeight: 500 }}
                                >
                                  <span>Opp: {log.opportunity_id.slice(0, 16)}...</span>
                                  <ExternalLink size={11} />
                                </Link>
                              ) : (
                                <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Processed</span>
                              )}
                            </td>
                            <td style={{ padding: "12px 16px", textAlign: "right" }}>
                              <button
                                className="btn btn-ghost"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setExpandedLogId(isExpanded ? null : log.id);
                                }}
                                style={{ fontSize: 11, padding: "4px 8px" }}
                              >
                                <Code size={12} /> {isExpanded ? "Hide" : "Inspect"}
                              </button>
                            </td>
                          </tr>

                          {isExpanded && (
                            <tr style={{ background: "rgba(0,0,0,0.3)" }}>
                              <td colSpan={8} style={{ padding: "16px 24px", borderBottom: "1px solid var(--border)" }}>
                                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                    <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase" }}>
                                      Raw Event Payload
                                    </div>
                                    <button
                                      className="btn btn-ghost"
                                      onClick={() => copyToClipboard(log.raw_payload, log.id)}
                                      style={{ fontSize: 11, padding: "4px 10px", gap: 5 }}
                                    >
                                      {copiedId === log.id ? <Check size={12} color="var(--emerald)" /> : <Copy size={12} />}
                                      {copiedId === log.id ? "Copied" : "Copy Payload"}
                                    </button>
                                  </div>
                                  <pre style={{
                                    margin: 0, padding: 14, borderRadius: 8, background: "#0a0d14",
                                    border: "1px solid var(--border)", fontFamily: "monospace", fontSize: 12, color: "#93c5fd",
                                    overflowX: "auto", maxHeight: 260
                                  }}>
                                    {typeof parsedPayload === "object" ? JSON.stringify(parsedPayload, null, 2) : String(parsedPayload)}
                                  </pre>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {/* VIEW B: WEBHOOK DELIVERY QUEUE & DLQ */}
      {activeTab === "queue" && (
        <>
          {/* Queue KPI Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase" }}>
                Total Queued Deliveries
              </div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>{queueStats.total.toLocaleString()}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Persisted in SQLite delivery ledger</div>
            </div>

            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8, borderLeft: "3px solid var(--emerald)" }}>
              <div style={{ fontSize: 12, color: "var(--emerald)", fontWeight: 600, textTransform: "uppercase" }}>
                Delivered / Processed
              </div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--emerald)" }}>{queueStats.delivered.toLocaleString()}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Successfully processed & normalized</div>
            </div>

            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8, borderLeft: "3px solid var(--electric-blue)" }}>
              <div style={{ fontSize: 12, color: "var(--electric-blue)", fontWeight: 600, textTransform: "uppercase" }}>
                Pending / In-Flight
              </div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--electric-blue)" }}>{queueStats.pending.toLocaleString()}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Awaiting worker iteration / retry</div>
            </div>

            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8, borderLeft: "3px solid var(--rose)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ fontSize: 12, color: "var(--rose)", fontWeight: 600, textTransform: "uppercase" }}>
                  Dead Letter Queue (DLQ)
                </div>
                {queueStats.deadLetter > 0 && (
                  <button
                    className="btn btn-ghost"
                    onClick={handleRetryAllDeadLetter}
                    style={{ fontSize: 11, padding: "2px 8px", color: "var(--rose)", border: "1px solid rgba(244,63,94,0.3)" }}
                  >
                    Retry All
                  </button>
                )}
              </div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--rose)" }}>{queueStats.deadLetter.toLocaleString()}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Exceeded max retry threshold (5/5)</div>
            </div>
          </div>

          {/* Queue Actions Bar */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
            <div style={{ display: "flex", background: "var(--bg-surface)", padding: 4, borderRadius: 10, border: "1px solid var(--border)", gap: 4 }}>
              {["ALL", "PENDING", "DELIVERED", "FAILED", "DEAD_LETTER"].map((st) => (
                <button
                  key={st}
                  onClick={() => setQueueFilter(st)}
                  style={{
                    padding: "6px 14px", borderRadius: 6, border: "none", cursor: "pointer",
                    fontSize: 12, fontWeight: 600,
                    background: queueFilter === st ? "var(--electric-blue)" : "transparent",
                    color: queueFilter === st ? "white" : "var(--text-secondary)",
                  }}
                >
                  {st}
                </button>
              ))}
            </div>

            <button
              className="btn btn-ghost"
              onClick={handleEnqueueTestWebhook}
              style={{ fontSize: 12, gap: 6, border: "1px solid var(--border)" }}
            >
              <Inbox size={14} /> + Enqueue Test Webhook
            </button>
          </div>

          {/* Delivery Queue Table */}
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            {queueLoading ? (
              <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
                <RefreshCw size={24} className="spin" style={{ margin: "0 auto 12px" }} />
                Loading Webhook Delivery Queue...
              </div>
            ) : filteredQueue.length === 0 ? (
              <div style={{ padding: 48, textAlign: "center", color: "var(--text-muted)" }}>
                <RotateCcw size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
                <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 4 }}>
                  No Queued Webhook Deliveries
                </div>
                <div style={{ fontSize: 12 }}>
                  Click "+ Enqueue Test Webhook" above to test persistent queuing and manual replay.
                </div>
              </div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table className="data-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr style={{ background: "var(--bg-hover)", color: "var(--text-muted)", textAlign: "left", borderBottom: "1px solid var(--border)" }}>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Delivery ID</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Status</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Event Type</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Attempts</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Created At</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600 }}>Last Error / Delivery</th>
                      <th style={{ padding: "12px 16px", fontWeight: 600, textAlign: "right" }}>Replay Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredQueue.map((item) => (
                      <tr key={item.id} style={{ borderBottom: "1px solid var(--border)" }}>
                        <td style={{ padding: "12px 16px", fontFamily: "monospace", fontSize: 12, fontWeight: 600 }}>
                          {item.id.slice(0, 16)}...
                        </td>
                        <td style={{ padding: "12px 16px" }}>
                          {item.status === "DELIVERED" && (
                            <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(16,185,129,0.15)", color: "var(--emerald)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                              <CheckCircle2 size={12} /> DELIVERED
                            </span>
                          )}
                          {item.status === "PENDING" && (
                            <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(59,130,246,0.15)", color: "var(--electric-blue)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                              <Clock size={12} /> PENDING
                            </span>
                          )}
                          {item.status === "PROCESSING" && (
                            <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(245,158,11,0.15)", color: "var(--amber)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                              <RefreshCw size={12} className="spin" /> PROCESSING
                            </span>
                          )}
                          {item.status === "FAILED" && (
                            <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(244,63,94,0.15)", color: "var(--rose)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                              <AlertTriangle size={12} /> FAILED
                            </span>
                          )}
                          {item.status === "DEAD_LETTER" && (
                            <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 700, background: "rgba(239,68,68,0.2)", color: "var(--rose)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                              <ShieldAlert size={12} /> DEAD LETTER
                            </span>
                          )}
                        </td>
                        <td style={{ padding: "12px 16px", fontFamily: "monospace", fontSize: 12 }}>
                          {item.event_type}
                        </td>
                        <td style={{ padding: "12px 16px", fontSize: 12 }}>
                          {item.attempts} / {item.max_attempts}
                        </td>
                        <td style={{ padding: "12px 16px", fontSize: 12, color: "var(--text-secondary)" }}>
                          {new Date(item.created_at).toLocaleTimeString()}
                        </td>
                        <td style={{ padding: "12px 16px", maxWidth: 260, fontSize: 11 }}>
                          {item.last_error ? (
                            <span style={{ color: "var(--rose)" }}>{item.last_error}</span>
                          ) : item.delivered_at ? (
                            <span style={{ color: "var(--emerald)" }}>Delivered {new Date(item.delivered_at).toLocaleTimeString()}</span>
                          ) : (
                            <span style={{ color: "var(--text-muted)" }}>Awaiting execution</span>
                          )}
                        </td>
                        <td style={{ padding: "12px 16px", textAlign: "right" }}>
                          <button
                            className="btn btn-ghost"
                            onClick={() => handleReplayDelivery(item.id)}
                            disabled={replayingId === item.id}
                            style={{ fontSize: 11, padding: "4px 10px", gap: 4, color: "var(--electric-blue)" }}
                          >
                            <RotateCcw size={12} className={replayingId === item.id ? "spin" : ""} />
                            {replayingId === item.id ? "Replaying..." : "Replay"}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
