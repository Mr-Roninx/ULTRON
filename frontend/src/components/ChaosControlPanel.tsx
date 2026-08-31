'use client';

import React, { useState } from 'react';

export const ChaosControlPanel: React.FC = () => {
  const [chaosInjected, setChaosInjected] = useState(false);

  return (
    <div className="bg-slate-900 border border-purple-500/30 rounded-xl p-6 shadow-xl text-slate-200">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
          ⚡ Longitudinal Chaos & Degradation Control
        </h3>
        <span className="text-xs px-2 py-0.5 rounded bg-purple-950 text-purple-400 border border-purple-500/30 font-mono">
          VirtualClock Perturbation
        </span>
      </div>

      <div className="space-y-4 text-xs">
        <p className="text-slate-400 text-xs font-sans">
          Test real-time environmental volatility by injecting gateway degradation during the agent's mid-flight WAIT state.
        </p>

        <div className="grid grid-cols-2 gap-3 font-mono">
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
            <div className="text-[10px] text-slate-400">Gateway A Telemetry</div>
            <div className={`text-base font-bold ${chaosInjected ? 'text-red-400' : 'text-emerald-400'}`}>
              {chaosInjected ? '10.0% (DEGRADED)' : '96.0% (HEALTHY)'}
            </div>
            <div className="text-[10px] text-slate-500">{chaosInjected ? 'Latency: 4,500ms' : 'Latency: 210ms'}</div>
          </div>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
            <div className="text-[10px] text-slate-400">Agent Adaptive State</div>
            <div className={`text-base font-bold ${chaosInjected ? 'text-amber-300' : 'text-slate-300'}`}>
              {chaosInjected ? 'REPLAN & PIVOT' : 'WAITING_FOR_RETRY'}
            </div>
            <div className="text-[10px] text-slate-500">{chaosInjected ? 'LLM Invocation #2 triggered' : 'Sleeping on VirtualClock'}</div>
          </div>
        </div>

        <button
          onClick={() => setChaosInjected(!chaosInjected)}
          className={`w-full py-2 rounded-lg font-bold transition-all text-xs uppercase tracking-wider font-mono ${
            chaosInjected
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/30 border border-purple-400'
              : 'bg-slate-800 hover:bg-slate-700 text-purple-300 border border-purple-500/40'
          }`}
        >
          {chaosInjected ? '✓ Chaos Active (T+2h Degradation Injected)' : '⚡ Inject Gateway A Outage (T+2h)'}
        </button>
      </div>
    </div>
  );
};
