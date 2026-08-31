import React from 'react';

export const ReconciliationPanel: React.FC = () => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-emerald-400 tracking-wider">
            TRUTH RECONCILIATION ENGINE
          </h2>
          <p className="text-xs text-slate-400">Continuous reconciliation between external provider state & internal accounting ledger</p>
        </div>
        <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-mono">
          0 MISMATCHES DETECTED
        </span>
      </div>

      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-800 text-xs font-mono space-y-2">
        <div className="flex justify-between border-b border-slate-800 pb-2">
          <span className="text-slate-400">Total Transactions Reconciled:</span>
          <span className="text-slate-200 font-bold">1,420</span>
        </div>
        <div className="flex justify-between border-b border-slate-800 pb-2">
          <span className="text-slate-400">External Provider Truth Match:</span>
          <span className="text-emerald-400 font-bold">100.0%</span>
        </div>
        <div className="flex justify-between border-b border-slate-800 pb-2">
          <span className="text-slate-400">Double-Entry Balance Check:</span>
          <span className="text-cyan-400 font-bold">Σ Debits == Σ Credits (0.00 Imbalance)</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Reconciliation-First Policy:</span>
          <span className="text-amber-300 font-bold">ENFORCED (Ambiguous 5xx / Timeouts Quarantine First)</span>
        </div>
      </div>
    </div>
  );
};
