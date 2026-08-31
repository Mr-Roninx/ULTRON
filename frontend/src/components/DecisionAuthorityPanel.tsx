'use client';

import React from 'react';

export const DecisionAuthorityPanel: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-amber-500/30 rounded-xl p-6 shadow-xl text-slate-200">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
          ⚖️ Action Decision Authority & NEV Ranking
        </h3>
        <span className="text-xs px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-500/30 font-mono">
          Deterministic Governance
        </span>
      </div>

      <div className="space-y-4 text-xs font-mono">
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400 uppercase">LLM Proposed Candidates vs Calculated NEV</div>
          <div className="mt-2 space-y-1.5">
            <div className="flex justify-between items-center p-2 rounded bg-amber-950/40 border border-amber-500/30 text-amber-300">
              <span className="font-bold">1. RETRY_GATEWAY_A (Selected)</span>
              <span className="font-mono">NEV: ₹10,926.49</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-slate-900 border border-slate-800 text-slate-300">
              <span>2. SEND_PAYMENT_LINK</span>
              <span className="font-mono">NEV: ₹5,830.00</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-slate-900 border border-slate-800 text-slate-400">
              <span>3. WAIT (LLM Preferred)</span>
              <span className="font-mono">NEV: ₹1,235.00</span>
            </div>
          </div>
        </div>

        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400 uppercase">Decision Authority Invariant</div>
          <p className="text-slate-300 text-[11px] mt-1 font-sans">
            The Action Decision Authority strictly executes the action yielding maximum Net Expected Value (NEV), overriding the LLM preference for WAIT. Zero financial or policy authority is delegated to the model.
          </p>
        </div>
      </div>
    </div>
  );
};
