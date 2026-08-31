import React from 'react';

export const UltronEconomicImpactPanel: React.FC = () => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 mt-4">
      <h3 className="text-md font-bold text-slate-200 uppercase tracking-wider mb-4">Causal Attribution: World With vs. Without ULTRON</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">Control (Natural Recovery)</p>
          <p className="text-lg font-bold text-slate-300 font-mono mt-1">₹16,103.81</p>
          <p className="text-[11px] text-slate-500 mt-1">Passive issuer self-healing</p>
        </div>
        <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">ULTRON Full Net Recovery</p>
          <p className="text-lg font-bold text-emerald-400 font-mono mt-1">₹39,109.71</p>
          <p className="text-[11px] text-slate-500 mt-1">Adaptive replan & routing</p>
        </div>
        <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">Incremental Causal Lift</p>
          <p className="text-lg font-bold text-cyan-400 font-mono mt-1">+₹23,005.90</p>
          <p className="text-[11px] text-emerald-400 mt-1">+142.9% True Economic Lift</p>
        </div>
      </div>
    </div>
  );
};
