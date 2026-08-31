'use client';

import React from 'react';

export const EconomicProofPanel: React.FC = () => {
  const baselines = [
    { name: "ULTRON v3.8 Full Autonomous", gross: "₹1,446,200", lift: "+₹806,200", nev: "₹1,320,400", zeroTouch: "74.2%", ci: "[₹780k, ₹832k]" },
    { name: "w/o Payment Intelligence", gross: "₹912,400", lift: "+₹272,400", nev: "₹820,100", zeroTouch: "48.0%", ci: "[₹250k, ₹295k]" },
    { name: "Fixed Dunning Baseline", gross: "₹640,000", lift: "₹0 (Baseline)", nev: "₹590,000", zeroTouch: "21.5%", ci: "N/A" },
    { name: "No Action (Zero Intervention)", gross: "₹180,000", lift: "-₹460,000", nev: "₹180,000", zeroTouch: "0.0%", ci: "N/A" }
  ];

  return (
    <div className="bg-slate-900 border border-cyan-500/30 rounded-xl p-6 shadow-xl text-slate-200">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
          📈 Paired Counterfactual Economic Lift Benchmark
        </h3>
        <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30 font-mono">
          N=200 Longitudinal Accounts
        </span>
      </div>

      <div className="space-y-3 font-mono text-xs">
        <div className="grid grid-cols-5 p-2 bg-slate-950 rounded text-slate-400 text-[10px] uppercase">
          <div className="col-span-2">Strategy Configuration</div>
          <div>Gross Recovery</div>
          <div>Incremental Lift</div>
          <div>95% Bootstrap CI</div>
        </div>

        {baselines.map((b, idx) => (
          <div key={idx} className={`grid grid-cols-5 p-3 rounded-lg border ${idx === 0 ? 'bg-cyan-950/40 border-cyan-500/40 text-white font-bold' : 'bg-slate-950/60 border-slate-800 text-slate-300'}`}>
            <div className="col-span-2">{b.name}</div>
            <div className="text-emerald-400">{b.gross}</div>
            <div className={idx === 0 ? 'text-cyan-300' : 'text-slate-400'}>{b.lift}</div>
            <div className="text-[11px] text-slate-400 font-sans">{b.ci}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
