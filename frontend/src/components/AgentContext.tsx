"use client";

import { useState, useEffect } from "react";
import { Database, AlertTriangle, ShieldCheck, CreditCard, Activity, Cpu, ArrowRight, Zap } from "lucide-react";

interface AgentContextProps {
  missionId: string | null;
}

export default function AgentContext({ missionId }: AgentContextProps) {
  const [context, setContext] = useState<any>(null);

  const fetchContext = async () => {
    if (!missionId) return;
    try {
      const res = await fetch(`http://localhost:8000/agent/mission/${missionId}/context`);
      const data = await res.json();
      if (res.ok) {
        setContext(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (missionId) {
      interval = setInterval(fetchContext, 1000);
      fetchContext();
    }
    return () => clearInterval(interval);
  }, [missionId]);

  if (!context) {
    return (
      <div className="glass-panel p-8 flex flex-col items-center justify-center h-full text-slate-500 gap-4">
        <Cpu size={56} className="opacity-20 text-blue-400" />
        <div className="text-center">
          <p className="text-base text-slate-300 font-medium">No active recovery mission in session.</p>
          <p className="text-xs text-slate-500 mt-1">Start a mission from Mission Control to stream live Payment Intelligence & NEV telemetry.</p>
        </div>
      </div>
    );
  }

  const diag = context.context?.diagnosis || {};
  const mission = context.context?.mission || {};
  const rel = context.context?.relationship_state || {};
  const differential = context.context?.last_regret_evaluation || {};

  return (
    <div className="glass-panel p-6 flex flex-col gap-6 h-full overflow-y-auto">
      <div className="flex items-center justify-between border-b border-slate-700/50 pb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <CreditCard className="text-indigo-400" />
          Payment Intelligence & Revenue Mission
        </h2>
        <div className="text-xs font-mono text-slate-400">
          Mission ID: <span className="text-indigo-300">{missionId}</span>
        </div>
      </div>

      {/* 1. Customer Revenue Mission Overview */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 flex flex-col gap-1">
          <div className="text-xs text-slate-400">Total Customer Exposure</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">
            ₹{(mission.total_exposure || 24700).toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-500">
            {mission.opportunities?.length || 3} Multi-Opportunity Items
          </div>
        </div>

        <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 flex flex-col gap-1">
          <div className="text-xs text-slate-400">Diagnosis Class & Severity</div>
          <div className="text-base font-semibold text-slate-200 flex items-center gap-2">
            <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded text-xs">
              {diag.failure_class || "INFRASTRUCTURE"}
            </span>
            <span className="text-xs font-normal text-slate-400">
              {diag.severity || "MEDIUM"}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-0.5">
            Reason: {diag.primary_reason || "ISSUER_UNAVAILABLE"}
          </div>
        </div>

        <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 flex flex-col gap-1">
          <div className="text-xs text-slate-400">Recoverability Score</div>
          <div className="text-2xl font-bold text-blue-400 font-mono">
            {((diag.recoverability || 0.78) * 100).toFixed(1)}%
          </div>
          <div className="text-[11px] text-emerald-400">
            Retry Eligible: {diag.retry_eligible !== false ? "YES" : "NO"}
          </div>
        </div>
      </div>

      {/* 2. "Why ULTRON?" Explanation Card */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 rounded-xl p-5 border border-indigo-900/40 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
            <Zap size={14} className="text-amber-400" />
            Decision Intelligence: Why ULTRON?
          </span>
          <span className="text-xs text-slate-400">Authority: Fail-Closed Economic NEV</span>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-1">
          <div className="bg-slate-900/80 p-3.5 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400 mb-1 font-medium">LLM Proposed Action:</div>
            <div className="text-sm font-semibold text-indigo-300 font-mono">
              {context.chosen_intent?.preferred_action || "SEND_PAYMENT_LINK"}
            </div>
            <p className="text-xs text-slate-400 mt-1 italic leading-relaxed">
              "{context.chosen_intent?.reasoning || "Suggesting immediate digital payment link delivery."}"
            </p>
          </div>

          <div className="bg-slate-900/80 p-3.5 rounded-lg border border-emerald-900/40">
            <div className="text-xs text-emerald-400 mb-1 font-medium">Action Decision Authority Selected:</div>
            <div className="text-sm font-semibold text-emerald-300 font-mono">
              {context.chosen_intent?.action_type || "RETRY_GATEWAY_B"}
            </div>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Selected highest Net Expected Value (NEV = ₹{(context.chosen_intent?.expected_yield || 18017).toFixed(0)}) considering Gateway B health (94%) and zero relationship friction.
            </p>
          </div>
        </div>
      </div>

      {/* 3. Feasible Actions and Replan Safety */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800">
          <div className="text-xs text-slate-400 mb-2 flex items-center gap-1">
            <ShieldCheck size={14} className="text-emerald-400" />
            Deterministic Feasible Action Space ({context.feasible_actions?.length || 0})
          </div>
          <div className="flex flex-wrap gap-1.5">
            {context.feasible_actions?.map((act: string) => (
              <span key={act} className="px-2 py-1 bg-slate-800/80 text-slate-300 text-xs rounded border border-slate-700 font-mono">
                {act}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800">
          <div className="text-xs text-slate-400 mb-2 flex items-center gap-1">
            <AlertTriangle size={14} className="text-amber-400" />
            Circuit Breaker & Interference State
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-lg font-bold text-slate-200">
                {context.replan_count || 0} <span className="text-xs font-normal text-slate-500">/ 5 Replans</span>
              </div>
              <div className="text-[11px] text-slate-400">Iterations: {context.iteration_count || 0} / 50</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-400">Relationship Sentiment:</div>
              <div className="text-xs font-semibold text-emerald-400 font-mono">{rel.sentiment || "NEUTRAL"}</div>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Live Context Payload */}
      <div className="flex flex-col gap-2">
        <h3 className="text-xs font-medium uppercase tracking-wider text-slate-400">Observational Context Payload</h3>
        <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 max-h-48 overflow-y-auto">
          <pre className="text-[11px] text-slate-300 font-mono leading-relaxed">
            {JSON.stringify(context.context, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
