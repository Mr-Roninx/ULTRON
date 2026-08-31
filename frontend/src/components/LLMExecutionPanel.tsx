import React from 'react';

export const LLMExecutionPanel: React.FC = () => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-violet-400 tracking-wider">
            LLM INTELLIGENCE & AUTHORITY ISOLATION
          </h2>
          <p className="text-xs text-slate-400">Semantic reasoning advisor strictly bounded by deterministic authority</p>
        </div>
        <span className="px-3 py-1 bg-violet-500/20 text-violet-300 border border-violet-500/30 rounded-full text-xs font-mono">
          FALLBACK / ADVISOR ONLY
        </span>
      </div>

      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-800 text-xs font-mono space-y-2">
        <p className="text-slate-300">• Mode: <span className="text-cyan-300 font-bold">Safe Deterministic Fallback</span> (HF_TOKEN not in active runtime)</p>
        <p className="text-slate-300">• Secret Isolation: <span className="text-emerald-400 font-bold">ENFORCED</span> (Zero Razorpay credentials accessible to LLM)</p>
        <p className="text-slate-300">• Direct API Calls: <span className="text-emerald-400 font-bold">BLOCKED</span> (LLM cannot invoke external HTTP clients directly)</p>
        <p className="text-slate-300">• Ledger Mutations: <span className="text-emerald-400 font-bold">BLOCKED</span> (Ledger updates execute solely via Reconciliation)</p>
      </div>
    </div>
  );
};
