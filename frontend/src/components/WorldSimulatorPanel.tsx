import React, { useState } from 'react';

export interface WorldSimulatorStats {
  simulationDay: number;
  activeCustomers: number;
  activeMerchants: number;
  totalGMV: number;
  recoveredRevenue: number;
  naturalRecoveryRate: number;
  ultronRecoveryRate: number;
  gatewayAHealth: number;
  gatewayBHealth: number;
  averageFatigue: number;
  churnRate: number;
  ledgerBalanced: boolean;
}

export const WorldSimulatorPanel: React.FC<{ stats?: Partial<WorldSimulatorStats> }> = ({ stats }) => {
  const current = {
    simulationDay: stats?.simulationDay ?? 30,
    activeCustomers: stats?.activeCustomers ?? 5000,
    activeMerchants: stats?.activeMerchants ?? 50,
    totalGMV: stats?.totalGMV ?? 45000000.0,
    recoveredRevenue: stats?.recoveredRevenue ?? 3850000.0,
    naturalRecoveryRate: stats?.naturalRecoveryRate ?? 0.354,
    ultronRecoveryRate: stats?.ultronRecoveryRate ?? 0.842,
    gatewayAHealth: stats?.gatewayAHealth ?? 0.96,
    gatewayBHealth: stats?.gatewayBHealth ?? 0.92,
    averageFatigue: stats?.averageFatigue ?? 0.18,
    churnRate: stats?.churnRate ?? 0.038,
    ledgerBalanced: stats?.ledgerBalanced ?? true,
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-emerald-400 tracking-wider">
            ULTRON-SWU-1.3 // ECONOMIC CIVILIZATION SIMULATOR
          </h2>
          <p className="text-xs text-slate-400 mt-1">Continuous Multi-Entity Temporal Reality Engine</p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-full text-xs font-mono">
            DAY {current.simulationDay} OF 365
          </span>
          <span className={`px-3 py-1 text-xs font-mono rounded-full border ${current.ledgerBalanced ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40' : 'bg-rose-500/20 text-rose-300 border-rose-500/40'}`}>
            LEDGER: {current.ledgerBalanced ? 'BALANCED (Σ=0)' : 'IMBALANCED'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-800/60 p-4 rounded-lg border border-slate-700">
          <p className="text-xs text-slate-400">Total World GMV</p>
          <p className="text-xl font-bold text-white font-mono mt-1">₹{current.totalGMV.toLocaleString()}</p>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-lg border border-slate-700">
          <p className="text-xs text-slate-400">ULTRON Recovered</p>
          <p className="text-xl font-bold text-emerald-400 font-mono mt-1">₹{current.recoveredRevenue.toLocaleString()}</p>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-lg border border-slate-700">
          <p className="text-xs text-slate-400">Gateway A Health</p>
          <p className="text-xl font-bold text-cyan-400 font-mono mt-1">{(current.gatewayAHealth * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-slate-800/60 p-4 rounded-lg border border-slate-700">
          <p className="text-xs text-slate-400">Avg Customer Fatigue</p>
          <p className="text-xl font-bold text-amber-400 font-mono mt-1">{(current.averageFatigue * 100).toFixed(1)}%</p>
        </div>
      </div>
    </div>
  );
};
