import React from 'react';

export interface EmergentCivilizationProps {
  populationSize?: number;
  activeMerchants?: number;
  emergentGMV?: number;
  gatewayCongestion?: number;
  averageTrustScore?: number;
  averageFatigueScore?: number;
  simulationDay?: number;
}

export const EconomicCivilizationPanel: React.FC<EmergentCivilizationProps> = ({
  populationSize = 25000,
  activeMerchants = 250,
  emergentGMV = 185000000.0,
  gatewayCongestion = 0.12,
  averageTrustScore = 0.88,
  averageFatigueScore = 0.14,
  simulationDay = 30
}) => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-cyan-400 tracking-wider">
            ULTRON-SWU-1.4 // EMERGENT POPULATION CIVILIZATION
          </h2>
          <p className="text-xs text-slate-400 mt-1">Multi-Cohort Organic Demand & Causal Feedback Engine</p>
        </div>
        <div className="flex space-x-2">
          <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-full text-xs font-mono">
            DAY {simulationDay} / 365
          </span>
          <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-mono">
            LEDGER CONSERVED
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">Total Population</p>
          <p className="text-xl font-bold text-white font-mono mt-1">{populationSize.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">Emergent GMV</p>
          <p className="text-xl font-bold text-emerald-400 font-mono mt-1">₹{emergentGMV.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">Gateway Congestion</p>
          <p className="text-xl font-bold text-amber-400 font-mono mt-1">{(gatewayCongestion * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">Avg Customer Trust</p>
          <p className="text-xl font-bold text-purple-400 font-mono mt-1">{(averageTrustScore * 100).toFixed(1)}%</p>
        </div>
      </div>
    </div>
  );
};
