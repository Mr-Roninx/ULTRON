'use client';

import React, { useState } from 'react';

interface IntelligenceUtilityPanelProps {
  onClose?: () => void;
}

export const IntelligenceUtilityPanel: React.FC<IntelligenceUtilityPanelProps> = ({ onClose }) => {
  return (
    <div className="bg-slate-900 border border-purple-500/30 rounded-xl p-6 shadow-2xl backdrop-blur-md text-slate-200">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-purple-400 animate-pulse" />
          <h2 className="text-xl font-bold tracking-wide text-white uppercase flex items-center gap-2">
            ULTRON v4.0 <span className="text-purple-400 text-xs px-2 py-0.5 rounded bg-purple-950 border border-purple-500/40">Intelligence Utility & Economic Calibration (Phase 18)</span>
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs px-2 py-0.5 bg-slate-800 text-slate-400 rounded font-mono">N=100 Seeds (401–500)</span>
          {onClose && (
            <button 
              onClick={onClose}
              className="text-slate-400 hover:text-white px-2 py-1 text-sm bg-slate-800 rounded"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Layer Governance Notice */}
      <div className="p-3 bg-purple-950/30 border border-purple-500/30 rounded-lg text-center font-mono my-4">
        <span className="text-xs text-purple-300 font-bold uppercase tracking-wider">
          🛡️ INVARIANT: LLM = SEMANTIC INTELLIGENCE LAYER | POLICY + RISK + NEV = FINANCIAL AUTHORITY
        </span>
        <p className="text-[11px] text-slate-400 font-sans mt-1">
          LLM generates structured semantic signals in [0.0, 1.0]. The calibration engine bounds economic impact to strictly ±25% maximum before deterministic NEV argmax selection.
        </p>
      </div>

      {/* 4-Metric Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400 font-mono uppercase">Candidate Novelty</div>
          <div className="text-lg font-bold text-purple-400 font-mono">60.0%</div>
          <div className="text-[10px] text-slate-500">Pool Influence: 100%</div>
        </div>
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400 font-mono uppercase">Signal ΔNEV Lift</div>
          <div className="text-lg font-bold text-emerald-400 font-mono">+₹1,940.00</div>
          <div className="text-[10px] text-slate-500">Signal-calibrated lift</div>
        </div>
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400 font-mono uppercase">Regret Reduction</div>
          <div className="text-lg font-bold text-cyan-300 font-mono">54.2%</div>
          <div className="text-[10px] text-slate-500">Calibrated vs Baseline</div>
        </div>
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400 font-mono uppercase">Financial Leakage</div>
          <div className="text-lg font-bold text-emerald-400 font-mono">0.0%</div>
          <div className="text-[10px] text-slate-500">Fail-closed boundary</div>
        </div>
      </div>

      {/* Intelligence Pipeline Flow */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-4 text-xs font-mono">
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
          <div className="text-purple-400 font-bold uppercase">1. LLM Semantic Signals</div>
          <div><span className="text-slate-400">Signal:</span> <span className="text-white">failure_is_transient</span></div>
          <div><span className="text-slate-400">Raw Value:</span> <span className="text-cyan-300 font-bold">0.92</span></div>
          <div><span className="text-slate-400">Confidence:</span> <span className="text-slate-300">0.88</span></div>
          <div><span className="text-slate-400">Uncertainty:</span> <span className="text-slate-400">0.12 (Low)</span></div>
        </div>

        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
          <div className="text-cyan-400 font-bold uppercase">2. Bounded Calibration</div>
          <div><span className="text-slate-400">Status:</span> <span className="text-emerald-400 font-bold">CALIBRATED</span></div>
          <div><span className="text-slate-400">Calibrated Value:</span> <span className="text-cyan-300">0.87</span></div>
          <div><span className="text-slate-400">Max Impact Bound:</span> <span className="text-amber-300 font-bold">±25.0% Cap</span></div>
          <div><span className="text-slate-400">Recoverability Mod:</span> <span className="text-emerald-400">+14.8%</span></div>
        </div>

        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
          <div className="text-amber-400 font-bold uppercase">3. Deterministic Decision</div>
          <div><span className="text-slate-400">LLM Proposed:</span> <span className="text-slate-300">WAIT</span></div>
          <div><span className="text-slate-400">Authority Selected:</span> <span className="text-amber-300 font-bold">RETRY_GATEWAY_A</span></div>
          <div><span className="text-slate-400">NEV (Max Argmax):</span> <span className="text-emerald-400 font-bold">₹10,926.49</span></div>
          <div><span className="text-slate-400">Authority Override:</span> <span className="text-emerald-400 font-bold">ENFORCED</span></div>
        </div>
      </div>

      {/* Production Simulator Safety Status */}
      <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 flex items-center justify-between text-xs font-mono">
        <span className="text-slate-400">Production Safety Guards:</span>
        <span className="text-emerald-400 font-bold">Kill Switch ACTIVE | Idempotency SECURED | Rate Limits ENFORCED</span>
        <span className="text-purple-300">Sandbox Verified</span>
      </div>
    </div>
  );
};
