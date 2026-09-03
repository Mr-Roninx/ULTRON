"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Cpu, Power, Settings, Clock, RefreshCw, BarChart2,
  CheckCircle2, XCircle, AlertTriangle, Play, Square, FastForward
} from "lucide-react";
import { api } from "../../../lib/auth";

interface DaemonConfig {
  interval_seconds: number;
  capacity: number;
}

interface DaemonStatus {
  state: "IDLE" | "SWEEPING" | "SLEEPING" | "STOPPED";
  config: DaemonConfig;
  total_sweeps: number;
  revenue_recovered_paise: number;
  last_sweep_at: string | null;
  next_sweep_at: string | null;
}

interface DaemonSweepLog {
  id: string;
  sweep_number: number;
  started_at: string;
  finished_at: string;
  duration_ms: number;
  status: "SUCCESS" | "PARTIAL" | "FAILED" | "ABORTED";
  opps_scanned: number;
  opps_allocated: number;
  opps_executed: number;
  opps_reconciled: number;
  revenue_recovered_paise: number;
  error_message?: string;
}

export default function AgentCommandCenter() {
  const [status, setStatus] = useState<DaemonStatus | null>(null);
  const [logs, setLogs] = useState<DaemonSweepLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // UI controls
  const [intervalSecs, setIntervalSecs] = useState<number>(30);
  const [capacity, setCapacity] = useState<number>(5);
  const [isUpdating, setIsUpdating] = useState(false);
  const [countdown, setCountdown] = useState<number>(0);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await api("/agents/daemon/status", { method: 'GET' });
      if (data) {
        setStatus(data);
        setError(null);
        if (!isUpdating && data.config) {
          setIntervalSecs(data.config.interval_seconds);
          setCapacity(data.config.capacity);
        }
      }
    } catch (err: any) {
      // Only show error if no previous status exists to avoid disruption during background polling
      if (!status) {
        setError(err.message || 'Connecting to agent daemon...');
      }
    }
  }, [isUpdating, status]);

  const fetchLogs = useCallback(async () => {
    try {
      const data = await api("/agents/daemon/activity", { method: 'GET' });
      if (data?.logs) {
        setLogs(data.logs);
      }
    } catch {
      // Silent retry on next interval
    }
  }, []);

  const refreshAll = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchStatus(), fetchLogs()]);
    setLoading(false);
  }, [fetchStatus, fetchLogs]);

  useEffect(() => {
    refreshAll();
    const timer = setInterval(refreshAll, 5000);
    return () => clearInterval(timer);
  }, [refreshAll]);

  // Update countdown timer locally
  useEffect(() => {
    if (!status?.next_sweep_at || status.state === "STOPPED" || status.state === "IDLE") {
      setCountdown(0);
      return;
    }
    
    const updateCountdown = () => {
      const next = new Date(status.next_sweep_at!).getTime();
      const now = Date.now();
      const diff = Math.max(0, Math.ceil((next - now) / 1000));
      setCountdown(diff);
    };
    
    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, [status?.next_sweep_at, status?.state]);

  const handleStart = async () => {
    setIsUpdating(true);
    try {
      await api("/agents/daemon/start", { method: 'POST', body: JSON.stringify({ interval_seconds: intervalSecs, capacity }) });
      await refreshAll();
    } finally {
      setIsUpdating(false);
    }
  };

  const handleStop = async () => {
    setIsUpdating(true);
    try {
      await api("/agents/daemon/stop", { method: 'POST', body: JSON.stringify({}) });
      await refreshAll();
    } finally {
      setIsUpdating(false);
    }
  };

  const handleManualSweep = async () => {
    setIsUpdating(true);
    try {
      await api("/agents/daemon/sweep", { method: 'POST', body: JSON.stringify({}) });
      await refreshAll();
    } finally {
      setIsUpdating(false);
    }
  };

  const handleUpdateConfig = async () => {
    setIsUpdating(true);
    try {
      await api("/agents/daemon/config", { method: 'POST', body: JSON.stringify({ interval_seconds: intervalSecs, capacity }) });
      await refreshAll();
    } finally {
      setIsUpdating(false);
    }
  };

  if (loading && !status) {
    return <div style={{ padding: 40, color: "var(--text-muted)" }}>Loading agent control plane...</div>;
  }

  const isActive = status?.state === "SWEEPING" || status?.state === "SLEEPING";

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", paddingBottom: 60 }}>
      <div style={{ marginBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, margin: "0 0 8px" }}>Agent Command Center</h1>
          <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: 14 }}>
            Control the ULTRON 24/7 background recovery agent daemon.
          </p>
        </div>
        <button className="btn outline" onClick={refreshAll} disabled={isUpdating}>
          <RefreshCw size={14} className={loading && !isUpdating ? "spin" : ""} /> Refresh
        </button>
      </div>

      {error && (
        <div style={{
          padding: 16, background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
          color: "var(--rose)", borderRadius: 8, marginBottom: 24, display: "flex", alignItems: "center", gap: 10
        }}>
          <AlertTriangle size={18} />
          {error}
        </div>
      )}

      {/* Hero Status Banner */}
      <div className="card" style={{
        background: isActive ? "linear-gradient(135deg, rgba(16,185,129,0.1), rgba(59,130,246,0.1))" : "var(--bg-surface)",
        border: isActive ? "1px solid rgba(16,185,129,0.3)" : "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "space-between", padding: "24px 32px",
        marginBottom: 24
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{
            width: 50, height: 50, borderRadius: 12,
            background: isActive ? "rgba(16,185,129,0.2)" : "var(--bg-hover)",
            color: isActive ? "var(--emerald)" : "var(--text-muted)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: isActive ? "0 0 15px rgba(16,185,129,0.3)" : "none"
          }}>
            <Cpu size={24} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <div className={`status-dot ${isActive ? "active" : ""}`} />
              <span style={{ fontSize: 12, fontWeight: 700, color: isActive ? "var(--emerald)" : "var(--text-muted)", letterSpacing: "1px", textTransform: "uppercase" }}>
                {isActive ? "24/7 Autonomous Mode Active" : "Agent Paused"}
              </span>
            </div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>
              Current State: <span style={{ color: "var(--text-primary)" }}>{status?.state}</span>
            </div>
          </div>
        </div>
        
        {isActive && status?.state === "SLEEPING" && (
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4, textTransform: "uppercase", fontWeight: 600 }}>Next sweep in</div>
            <div style={{ fontSize: 24, fontWeight: 700, color: "var(--electric-blue)", fontVariantNumeric: "tabular-nums" }}>
              {countdown}s
            </div>
          </div>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
        {/* Controls */}
        <div className="card">
          <h3 style={{ margin: "0 0 16px", fontSize: 14, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px" }}>
            Engine Controls
          </h3>
          
          <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
            {!isActive ? (
              <button className="btn primary" onClick={handleStart} disabled={isUpdating} style={{ flex: 1, background: "var(--emerald)", color: "#000" }}>
                <Play size={16} /> Start Autonomous Agent
              </button>
            ) : (
              <button className="btn outline" onClick={handleStop} disabled={isUpdating} style={{ flex: 1, color: "var(--rose)", borderColor: "rgba(244,63,94,0.3)" }}>
                <Square size={16} /> Pause Agent
              </button>
            )}
            <button className="btn outline" onClick={handleManualSweep} disabled={isUpdating || status?.state === "SWEEPING"} title="Trigger sweep immediately">
              <FastForward size={16} /> Sweep Now
            </button>
          </div>

          <h3 style={{ margin: "0 0 16px", fontSize: 14, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px", borderTop: "1px solid var(--border)", paddingTop: 16 }}>
            Configuration
          </h3>
          
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", fontSize: 13, marginBottom: 8, color: "var(--text-secondary)" }}>
              Sweep Interval (seconds): <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>{intervalSecs}s</span>
            </label>
            <input 
              type="range" min="15" max="300" step="15" 
              value={intervalSecs} 
              onChange={e => setIntervalSecs(parseInt(e.target.value))}
              style={{ width: "100%", accentColor: "var(--electric-blue)" }}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", fontSize: 13, marginBottom: 8, color: "var(--text-secondary)" }}>
              Batch Capacity (links per sweep): <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>{capacity}</span>
            </label>
            <input 
              type="range" min="1" max="10" step="1" 
              value={capacity} 
              onChange={e => setCapacity(parseInt(e.target.value))}
              style={{ width: "100%", accentColor: "var(--electric-blue)" }}
            />
          </div>

          <button 
            className="btn outline" 
            onClick={handleUpdateConfig} 
            disabled={isUpdating || (intervalSecs === status?.config.interval_seconds && capacity === status?.config.capacity)}
            style={{ width: "100%" }}
          >
            <Settings size={14} /> Apply Configuration
          </button>
        </div>

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="card" style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px", marginBottom: 8 }}>
              Total Sweeps
            </div>
            <div style={{ fontSize: 32, fontWeight: 700 }}>
              {status?.total_sweeps.toLocaleString() || 0}
            </div>
          </div>
          
          <div className="card" style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px", marginBottom: 8 }}>
              Revenue Recovered
            </div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "var(--emerald)" }}>
              ₹{((status?.revenue_recovered_paise || 0) / 100).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            </div>
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
              *Model-estimated autonomous lift
            </div>
          </div>
          
          <div className="card" style={{ display: "flex", flexDirection: "column", justifyContent: "center", gridColumn: "1 / -1" }}>
             <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px", marginBottom: 12 }}>
              Last Sweep
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-secondary)", fontSize: 14 }}>
              <Clock size={16} />
              {status?.last_sweep_at ? new Date(status.last_sweep_at).toLocaleString() : "Never"}
            </div>
          </div>
        </div>
      </div>

      {/* Activity Log */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: 0, fontSize: 14, textTransform: "uppercase", letterSpacing: "1px" }}>Live Activity Log</h3>
          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Last {logs.length} sweeps</span>
        </div>
        
        {logs.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
            No sweeps recorded yet.
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="data-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "var(--bg-hover)", color: "var(--text-muted)", textAlign: "left" }}>
                  <th style={{ padding: "12px 20px", fontWeight: 600 }}>Sweep #</th>
                  <th style={{ padding: "12px 20px", fontWeight: 600 }}>Timestamp</th>
                  <th style={{ padding: "12px 20px", fontWeight: 600 }}>Status</th>
                  <th style={{ padding: "12px 20px", fontWeight: 600, textAlign: "right" }}>Scanned</th>
                  <th style={{ padding: "12px 20px", fontWeight: 600, textAlign: "right" }}>Allocated</th>
                  <th style={{ padding: "12px 20px", fontWeight: 600, textAlign: "right" }}>Executed</th>
                  <th style={{ padding: "12px 20px", fontWeight: 600, textAlign: "right" }}>Reconciled</th>
                  <th style={{ padding: "12px 20px", fontWeight: 600, textAlign: "right" }}>Duration</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "12px 20px", fontFamily: "monospace", color: "var(--text-secondary)" }}>
                      #{log.sweep_number}
                    </td>
                    <td style={{ padding: "12px 20px" }}>
                      {new Date(log.started_at).toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                    </td>
                    <td style={{ padding: "12px 20px" }}>
                      {log.status === "SUCCESS" && <span style={{ color: "var(--emerald)", display: "flex", alignItems: "center", gap: 4 }}><CheckCircle2 size={14} /> OK</span>}
                      {log.status === "PARTIAL" && <span style={{ color: "var(--amber)", display: "flex", alignItems: "center", gap: 4 }}><AlertTriangle size={14} /> Partial</span>}
                      {log.status === "FAILED" && <span style={{ color: "var(--rose)", display: "flex", alignItems: "center", gap: 4 }}><XCircle size={14} /> Failed</span>}
                      {log.status === "ABORTED" && <span style={{ color: "var(--rose)", display: "flex", alignItems: "center", gap: 4 }}><Power size={14} /> Aborted</span>}
                    </td>
                    <td style={{ padding: "12px 20px", textAlign: "right" }}>{log.opps_scanned}</td>
                    <td style={{ padding: "12px 20px", textAlign: "right" }}>{log.opps_allocated}</td>
                    <td style={{ padding: "12px 20px", textAlign: "right" }}>{log.opps_executed}</td>
                    <td style={{ padding: "12px 20px", textAlign: "right" }}>{log.opps_reconciled}</td>
                    <td style={{ padding: "12px 20px", textAlign: "right", fontFamily: "monospace" }}>{log.duration_ms}ms</td>
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
