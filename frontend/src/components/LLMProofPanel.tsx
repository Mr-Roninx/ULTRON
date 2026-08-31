'use client';

import React, { useState } from 'react';

interface LLMProofPanelProps {
  onClose?: () => void;
}

export const LLMProofPanel: React.FC<LLMProofPanelProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<'latency' | 'influence' | 'authority' | 'security'>('latency');

  return (
    <div className="bg-slate-900 border border-emerald-500/30 rounded-xl p-6 shadow-2xl backdrop-blur-md text-slate-200">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
          <h2 className="text-xl font-bold tracking-wide text-white uppercase flex items-center gap-2">
            ULTRON v3.8 <span className="text-emerald-400 text-xs px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500/40">Production LLM Proof & Reliability Audit</span>
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-mono">ROUTER: router.huggingface.co/v1</span>
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

      {/* Navigation Tabs */}
      <div className="flex gap-2 my-4 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('latency')}
          className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
            activeTab === 'latency' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'text-slate-400 hover:bg-slate-800'
          }`}
        >
          ⚡ Latency & SLA Controller
        </button>
        <button
          onClick={() => setActiveTab('influence')}
          className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
            activeTab === 'influence' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'text-slate-400 hover:bg-slate-800'
          }`}
        >
          📊 Multi-Seed Influence (4-Tier)
        </button>
        <button
          onClick={() => setActiveTab('authority')}
          className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
            activeTab === 'authority' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'text-slate-400 hover:bg-slate-800'
          }`}
        >
          ⚖️ Decision Authority Differential
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
            activeTab === 'security' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'text-slate-400 hover:bg-slate-800'
          }`}
        >
          🛡️ Action Registry & Security
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'latency' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Soft Timeout</div>
              <div className="text-sm font-bold text-white">5,000 ms</div>
              <div className="text-[10px] text-slate-500">Warning & local prep</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Hard Timeout</div>
              <div className="text-sm font-bold text-amber-400">10,000 ms</div>
              <div className="text-[10px] text-slate-500">Instantaneous failover</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Context Reduction</div>
              <div className="text-sm font-bold text-emerald-400">&gt; 70% Bounded</div>
              <div className="text-[10px] text-slate-500">&lt; 2,500 chars / prompt</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Fallback Ladder</div>
              <div className="text-sm font-bold text-cyan-300 font-mono">HF → Local → Safe</div>
              <div className="text-[10px] text-slate-500">Zero blocking hangs</div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'influence' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono">Metric A: Novelty Rate</div>
              <div className="text-lg font-bold text-emerald-400 font-mono">90.0%</div>
              <div className="text-[10px] text-slate-500">Novel proposal expansion</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono">Metric B: Pool Influence</div>
              <div className="text-lg font-bold text-emerald-400 font-mono">100.0%</div>
              <div className="text-[10px] text-slate-500">Candidate set modified</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono">Metric C: Pref Influence</div>
              <div className="text-lg font-bold text-cyan-300 font-mono">66.7%</div>
              <div className="text-[10px] text-slate-500">LLM pref != rule baseline</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono">Metric D: Decision Influence</div>
              <div className="text-lg font-bold text-slate-300 font-mono">0.0%</div>
              <div className="text-[10px] text-slate-500">CANDIDATE_INFLUENCE_ONLY</div>
            </div>
          </div>
          <div className="p-3 bg-slate-950/80 rounded border border-slate-800 text-xs text-slate-400 font-mono">
            Scientific Truth Note: Phase 16 multi-seed testing ($N=30$) proves that the LLM expands candidate options, but deterministic NEV authority maintains 100% control of final decisions.
          </div>
        </div>
      )}

      {activeTab === 'authority' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-950 rounded-lg border border-slate-800">
            <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2">
              LLM Proposal (Intelligence)
            </div>
            <div className="space-y-1.5 text-xs">
              <div><span className="text-slate-400 font-mono">Preferred:</span> <span className="text-white font-bold">WAIT</span></div>
              <div><span className="text-slate-400 font-mono">Candidates:</span> <span className="text-cyan-300">[WAIT, RETRY_GATEWAY_A, SEND_PAYMENT_LINK]</span></div>
              <div><span className="text-slate-400 font-mono">Diagnosis:</span> <span className="text-slate-300">ISO 91 Issuer Unavailable (CARD)</span></div>
            </div>
          </div>
          <div className="p-4 bg-slate-950 rounded-lg border border-slate-800">
            <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
              Deterministic Financial Authority
            </div>
            <div className="space-y-1.5 text-xs">
              <div><span className="text-slate-400 font-mono">Decided:</span> <span className="text-amber-300 font-bold">RETRY_GATEWAY_A</span> (NEV: ₹10,926.49)</div>
              <div><span className="text-slate-400 font-mono">Override:</span> <span className="text-emerald-400 font-bold">ENFORCED</span></div>
              <div><span className="text-slate-400 font-mono">Authority Invariant:</span> <span className="text-slate-300">Zero monetary authority conceded to LLM.</span></div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 space-y-3">
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Authoritative Action Registry Rejections (100% Blocked)
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs font-mono">
            <div className="px-2 py-1.5 bg-red-950/40 border border-red-500/30 rounded text-red-300">TRANSFER_MONEY ✕</div>
            <div className="px-2 py-1.5 bg-red-950/40 border border-red-500/30 rounded text-red-300">DELETE_PAYMENT ✕</div>
            <div className="px-2 py-1.5 bg-red-950/40 border border-red-500/30 rounded text-red-300">EXECUTE_SQL ✕</div>
            <div className="px-2 py-1.5 bg-red-950/40 border border-red-500/30 rounded text-red-300">UPDATE_BALANCE ✕</div>
            <div className="px-2 py-1.5 bg-red-950/40 border border-red-500/30 rounded text-red-300">UNLIMITED_DISCOUNT ✕</div>
            <div className="px-2 py-1.5 bg-red-950/40 border border-red-500/30 rounded text-red-300">BYPASS_POLICY ✕</div>
          </div>
        </div>
      )}
    </div>
  );
};
