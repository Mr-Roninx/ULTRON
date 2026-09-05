"use client";

import React, { useEffect, useState, useCallback } from "react";
import { 
  ShieldAlert, ShieldCheck, Activity, Zap, Play, RefreshCw, 
  Radio, CheckCircle2, Clock, AlertTriangle, ArrowUpRight
} from "lucide-react";
import { useAuth, api } from "../../../lib/auth";
import { sseClient, SSEConnectionState } from "../../../lib/sse-client";
import { IVENBadge } from "../../../components/IVENBadge";

interface LiveOpportunity {
  id: string;
  amount_paise: number;
  reason_code: string;
  decline_type: string;
  customer_id: string;
  status: string;
  created_at: string;
  score?: {
    iven_band?: "STRONG" | "MODERATE" | "WEAK" | "NEGATIVE";
    expected_incremental_value_paise: number;
    intervention_recovery_prob: number;
    natural_recovery_prob: number;
    incremental_prob: number;
  };
  decision?: {
    decision: "ACT" | "WAIT" | "ABSTAIN";
    rank_in_batch: number;
    shadow_price_paise_at_decision: number;
  };
  authority?: {
    verdict: "AUTHORIZED" | "BLOCKED" | "PENDING";
    reason?: string;
  };
}

interface CommandMetrics {
  active_links_count: number;
  prevented_blast_count: number;
  prevented_loss_paise: number;
  kill_switch_active: boolean;
  shadow_price_paise: number;
  capacity_used: number;
  capacity_limit: number;
  estimated_recovery_rate_pct: number;
}

export default function TenantCommandCenter() {
  const { tenant } = useAuth();
  const [connectionState, setConnectionState] = useState<SSEConnectionState>("DISCONNECTED");
  const [metrics, setMetrics] = useState<CommandMetrics>({
    active_links_count: 0,
    prevented_blast_count: 0,
    prevented_loss_paise: 0,
    kill_switch_active: false,
    shadow_price_paise: 3500,
    capacity_used: 0,
    capacity_limit: 5,
    estimated_recovery_rate_pct: 42.5,
  });
  const [opportunities, setOpportunities] = useState<LiveOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggeringLoop, setTriggeringLoop] = useState(false);
  const [togglingKillSwitch, setTogglingKillSwitch] = useState(false);
  const [lastEventTime, setLastEventTime] = useState<string>("");

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [summaryRes, oppsRes] = await Promise.allSettled([
        api<any>("/v1/dashboard/summary"),
        api<any>("/v1/opportunities?limit=15"),
      ]);

      if (summaryRes.status === "fulfilled" && summaryRes.value) {
        const d = summaryRes.value;
        setMetrics({
          active_links_count: d.active_links_count || d.in_flight_count || 0,
          prevented_blast_count: d.anti_blast_count || d.abstained_count || 0,
          prevented_loss_paise: d.anti_blast_saved_paise || 0,
          kill_switch_active: d.kill_switch_active ?? tenant?.kill_switch_active ?? false,
          shadow_price_paise: d.shadow_price_paise || 3500,
          capacity_used: d.capacity_used || 0,
          capacity_limit: d.capacity_limit || 5,
          estimated_recovery_rate_pct: d.recovery_rate_pct || 42.5,
        });
      }

      if (oppsRes.status === "fulfilled" && oppsRes.value) {
        const rawOpps = Array.isArray(oppsRes.value) ? oppsRes.value : (oppsRes.value.opportunities || []);
        setOpportunities(rawOpps);
      }
    } catch (err) {
      console.warn("Error loading command center telemetry:", err);
    } finally {
      setLoading(false);
    }
  }, [tenant]);

  // Connect to SSE for real-time telemetry
  useEffect(() => {
    sseClient.connect();
    const unsubState = sseClient.onStateChange((st) => setConnectionState(st));

    const unsubOpp = sseClient.subscribe("OPPORTUNITY_UPDATED", (msg) => {
      setLastEventTime(new Date().toLocaleTimeString());
      if (msg.data?.opportunity) {
        setOpportunities((prev) => {
          const exists = prev.some((o) => o.id === msg.data.opportunity.id);
          if (exists) {
            return prev.map((o) => (o.id === msg.data.opportunity.id ? { ...o, ...msg.data.opportunity } : o));
          }
          return [msg.data.opportunity, ...prev.slice(0, 14)];
        });
      }
    });

    const unsubSweep = sseClient.subscribe("SWEEP_COMPLETED", () => {
      setLastEventTime(new Date().toLocaleTimeString());
      fetchData();
    });

    fetchData();

    return () => {
      unsubState();
      unsubOpp();
      unsubSweep();
    };
  }, [fetchData]);

  const handleTriggerAgentLoop = async () => {
    try {
      setTriggeringLoop(true);
      await api("/v1/agent/run", { method: "POST", body: JSON.stringify({ trigger_source: "COMMAND_CENTER" }) });
      await fetchData();
    } catch (err: any) {
      alert(`Agent execution notice: ${err.message || "Cycle dispatched to queue"}`);
    } finally {
      setTriggeringLoop(false);
    }
  };

  const handleToggleKillSwitch = async () => {
    const nextState = !metrics.kill_switch_active;
    const confirmMsg = nextState
      ? "EMERGENCY SAFETY STOP: Are you sure you want to engage the Kill Switch? All automated payment link creation will immediately halt."
      : "Resume Automated Operations: Disengage the Kill Switch and allow Action Authority to resume creating payment links?";

    if (!window.confirm(confirmMsg)) return;

    try {
      setTogglingKillSwitch(true);
      await api("/v1/tenants/kill-switch", {
        method: "POST",
        body: JSON.stringify({ active: nextState }),
      });
      setMetrics((prev) => ({ ...prev, kill_switch_active: nextState }));
    } catch (err: any) {
      alert(`Failed to toggle Kill Switch: ${err.message}`);
    } finally {
      setTogglingKillSwitch(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner: Real-Time Telemetry State */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-zinc-900/90 border border-zinc-800 shadow-xl backdrop-blur-md">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-400" />
              Tenant Command Center
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-zinc-800 text-zinc-300 border border-zinc-700">
              V11 Sovereign Control
            </span>
          </div>
          <p className="text-sm text-zinc-400">
            Autonomous portfolio dispatch, deterministic compliance gating, and live SSE event stream.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Real-time connection badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs font-mono">
            <Radio
              className={`w-3.5 h-3.5 ${
                connectionState === "CONNECTED"
                  ? "text-emerald-400 animate-pulse"
                  : connectionState === "RECONNECTING"
                  ? "text-amber-400 animate-spin"
                  : "text-zinc-500"
              }`}
            />
            <span className="text-zinc-300">
              {connectionState === "CONNECTED"
                ? "LIVE SSE"
                : connectionState === "RECONNECTING"
                ? "RECONNECTING (<2s)"
                : "OFFLINE"}
            </span>
            {lastEventTime && <span className="text-zinc-500 text-[10px]">({lastEventTime})</span>}
          </div>

          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 transition"
            title="Refresh telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>

          <button
            onClick={handleTriggerAgentLoop}
            disabled={triggeringLoop || metrics.kill_switch_active}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-xs shadow-lg shadow-indigo-600/20 transition"
          >
            <Play className={`w-3.5 h-3.5 ${triggeringLoop ? "animate-spin" : ""}`} />
            <span>{triggeringLoop ? "Reasoning..." : "Trigger AI Cycle"}</span>
          </button>
        </div>
      </div>

      {/* Emergency Kill Switch & Safety Bar */}
      <div
        className={`p-4 rounded-xl border flex flex-col md:flex-row items-center justify-between gap-4 transition-all ${
          metrics.kill_switch_active
            ? "bg-rose-950/40 border-rose-600/50 shadow-lg shadow-rose-950/30"
            : "bg-emerald-950/20 border-emerald-800/30"
        }`}
      >
        <div className="flex items-center gap-3">
          {metrics.kill_switch_active ? (
            <ShieldAlert className="w-6 h-6 text-rose-400 animate-pulse" />
          ) : (
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm text-white">
                {metrics.kill_switch_active
                  ? "KILL SWITCH ENGAGED — SYSTEM HALTED"
                  : "Action Authority Normal Operations"}
              </span>
              <span
                className={`text-[10px] uppercase font-mono px-2 py-0.5 rounded font-bold ${
                  metrics.kill_switch_active
                    ? "bg-rose-500 text-white"
                    : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                }`}
              >
                {metrics.kill_switch_active ? "HALTED" : "ENFORCED"}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              {metrics.kill_switch_active
                ? "Autonomous payment link dispatch is strictly disabled. No customer outreach will occur."
                : "Deterministic compliance checks are active. High-conviction opportunities execute within budget."}
            </p>
          </div>
        </div>

        <button
          onClick={handleToggleKillSwitch}
          disabled={togglingKillSwitch}
          className={`px-4 py-2 rounded-lg text-xs font-bold font-mono tracking-wide transition border shadow-md ${
            metrics.kill_switch_active
              ? "bg-emerald-600 hover:bg-emerald-500 text-white border-emerald-500"
              : "bg-rose-600 hover:bg-rose-700 text-white border-rose-500 hover:shadow-rose-600/20"
          }`}
        >
          {togglingKillSwitch
            ? "Switching..."
            : metrics.kill_switch_active
            ? "RESUME OPERATIONS"
            : "ENGAGE EMERGENCY KILL SWITCH"}
        </button>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-zinc-900/80 border border-zinc-800">
          <div className="text-xs text-zinc-400 font-medium">Batch Capacity Bound</div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-white">
              {metrics.capacity_used} / {metrics.capacity_limit}
            </span>
            <span className="text-xs font-mono text-indigo-400">Test Cap (5 max)</span>
          </div>
          <div className="mt-3 w-full bg-zinc-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-indigo-500 h-1.5 rounded-full transition-all"
              style={{ width: `${Math.min(100, (metrics.capacity_used / metrics.capacity_limit) * 100)}%` }}
            />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-zinc-900/80 border border-zinc-800">
          <div className="text-xs text-zinc-400 font-medium">Marginal Shadow Price</div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-white">
              ₹{(metrics.shadow_price_paise / 100).toFixed(2)}
            </span>
            <span className="text-xs font-mono text-amber-400">Admission Cutoff</span>
          </div>
          <p className="text-[11px] text-zinc-500 mt-2">Opportunities with IVEN below this threshold receive WAIT/ABSTAIN.</p>
        </div>

        <div className="p-4 rounded-xl bg-zinc-900/80 border border-zinc-800">
          <div className="text-xs text-zinc-400 font-medium">Anti-Blast Goodwill Saved</div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-emerald-400">
              ₹{(metrics.prevented_loss_paise / 100).toFixed(2)}
            </span>
            <span className="text-xs font-mono text-zinc-400">{metrics.prevented_blast_count} blocked</span>
          </div>
          <p className="text-[11px] text-zinc-500 mt-2">Capital & customer fatigue saved by rationally abstaining.</p>
        </div>

        <div className="p-4 rounded-xl bg-zinc-900/80 border border-zinc-800">
          <div className="text-xs text-zinc-400 font-medium">Recovery Rate (Model-Estimated*)</div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-white">
              {metrics.estimated_recovery_rate_pct.toFixed(1)}%
            </span>
            <span className="text-[10px] text-zinc-500 font-sans">*Estimated</span>
          </div>
          <p className="text-[11px] text-zinc-500 mt-2">Estimated recovery probability over natural counterfactual baseline.</p>
        </div>
      </div>

      {/* Live Pipeline Feed Table */}
      <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 overflow-hidden shadow-lg">
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              In-Flight Opportunities & Two-Stage Authority Gate
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Stage 1: Economic Reasoning & Market Rank • Stage 2: Action Authority Compliance Veto
            </p>
          </div>
          <span className="text-xs text-zinc-500 font-mono">Showing latest {opportunities.length}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-zinc-950/60 text-zinc-400 border-b border-zinc-800 uppercase tracking-wider font-mono text-[11px]">
              <tr>
                <th className="py-3 px-4">Opportunity</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Decline Reason</th>
                <th className="py-3 px-4">Economic IVEN Band</th>
                <th className="py-3 px-4">Stage 1 Decision</th>
                <th className="py-3 px-4">Stage 2 Authority</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60 font-mono">
              {opportunities.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-zinc-500 font-sans">
                    No active recovery opportunities in pipeline. Trigger an AI cycle or send a test webhook.
                  </td>
                </tr>
              ) : (
                opportunities.map((opp) => {
                  const ivenPaise = opp.score?.expected_incremental_value_paise;
                  const decision = opp.decision?.decision || (opp.status === "abstained" ? "ABSTAIN" : opp.status === "blocked" ? "WAIT" : "ACT");
                  const isBlocked = opp.status === "blocked" || opp.decline_type === "hard";

                  return (
                    <tr key={opp.id} className="hover:bg-zinc-800/30 transition">
                      <td className="py-3 px-4 font-semibold text-zinc-200">
                        <div className="flex items-center gap-1.5">
                          <span>{opp.id.slice(0, 16)}</span>
                          <ArrowUpRight className="w-3 h-3 text-zinc-500" />
                        </div>
                        <span className="text-[10px] text-zinc-500 font-sans block">
                          Customer: {opp.customer_id}
                        </span>
                      </td>

                      <td className="py-3 px-4 font-bold text-white">
                        ₹{(opp.amount_paise / 100).toFixed(2)}
                      </td>

                      <td className="py-3 px-4">
                        <span className="text-zinc-300 font-sans block">{opp.reason_code}</span>
                        <span
                          className={`text-[10px] uppercase px-1.5 py-0.2 rounded inline-block font-mono ${
                            opp.decline_type === "hard"
                              ? "bg-rose-950 text-rose-400 border border-rose-800"
                              : "bg-zinc-800 text-zinc-400"
                          }`}
                        >
                          {opp.decline_type}
                        </span>
                      </td>

                      <td className="py-3 px-4">
                        <IVENBadge
                          band={opp.score?.iven_band}
                          valuePaise={ivenPaise}
                          size="sm"
                        />
                      </td>

                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                            decision === "ACT"
                              ? "bg-emerald-950/60 text-emerald-400 border border-emerald-600/40"
                              : decision === "WAIT"
                              ? "bg-amber-950/60 text-amber-400 border border-amber-600/40"
                              : "bg-zinc-800 text-zinc-400 border border-zinc-700"
                          }`}
                        >
                          {decision}
                        </span>
                      </td>

                      <td className="py-3 px-4">
                        {isBlocked ? (
                          <span className="inline-flex items-center gap-1 text-rose-400 font-semibold text-[11px]">
                            <ShieldAlert className="w-3.5 h-3.5" />
                            VETOED
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold text-[11px]">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            APPROVED
                          </span>
                        )}
                      </td>

                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${
                            opp.status === "recovered"
                              ? "bg-emerald-500/20 text-emerald-300"
                              : opp.status === "executing"
                              ? "bg-indigo-500/20 text-indigo-300 animate-pulse"
                              : opp.status === "blocked"
                              ? "bg-rose-500/20 text-rose-300"
                              : "bg-zinc-800 text-zinc-400"
                          }`}
                        >
                          {opp.status}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        <div className="p-3 bg-zinc-950/80 border-t border-zinc-800 text-[11px] text-zinc-500 flex items-center justify-between">
          <span>* All probabilities and recovery values are model-estimated counterfactuals.</span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-zinc-400" />
            Live SSE Event Loop Active
          </span>
        </div>
      </div>
    </div>
  );
}
