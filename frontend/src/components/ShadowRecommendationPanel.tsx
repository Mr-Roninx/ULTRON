import React from 'react';

export const ShadowRecommendationPanel: React.FC = () => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-violet-400 tracking-wider">
            SHADOW MODE EVALUATION & CANDIDATE ANALYSIS
          </h2>
          <p className="text-xs text-slate-400">Evaluates live external payment streams with zero external side effects</p>
        </div>
        <span className="px-3 py-1 bg-violet-500/20 text-violet-300 border border-violet-500/30 rounded-full text-xs font-mono">
          SHADOW PASSIVE MODE
        </span>
      </div>

      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-800 text-xs font-mono space-y-2">
        <p className="text-slate-300">• Live Stream Ingested: <span className="text-cyan-300">182 transactions</span></p>
        <p className="text-slate-300">• Proposed Autonomous Interventions: <span className="text-amber-300">42 candidates</span></p>
        <p className="text-slate-300">• Projected Net Economic Value (NEV): <span className="text-emerald-400 font-bold">+₹142,500.00</span></p>
        <p className="text-slate-300">• Actual External Mutations Performed: <span className="text-red-400 font-bold">0 (Zero Side-Effects Guaranteed)</span></p>
      </div>
    </div>
  );
};
