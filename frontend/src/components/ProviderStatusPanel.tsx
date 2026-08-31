import React from 'react';

export interface ProviderHealth {
  name: string;
  status: 'AVAILABLE' | 'DEGRADED' | 'TIMEOUT' | 'OFFLINE';
  latencyMs: number;
  successRate: number;
  environment: string;
}

export const ProviderStatusPanel: React.FC = () => {
  const providers: ProviderHealth[] = [
    { name: 'Razorpay', status: 'AVAILABLE', latencyMs: 115, successRate: 99.4, environment: 'TEST_SANDBOX' },
    { name: 'Stripe', status: 'AVAILABLE', latencyMs: 145, successRate: 99.7, environment: 'TEST_SANDBOX' },
    { name: 'Adyen', status: 'AVAILABLE', latencyMs: 180, successRate: 98.9, environment: 'TEST_SANDBOX' }
  ];

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-cyan-400 tracking-wider">
            PROVIDER CONNECTIVITY & HEALTH
          </h2>
          <p className="text-xs text-slate-400">Real-time payment adapter telemetry and capability matrix</p>
        </div>
        <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-mono">
          3/3 ADAPTERS ACTIVE
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {providers.map((p) => (
          <div key={p.name} className="p-4 bg-slate-900/80 rounded-lg border border-slate-800">
            <div className="flex justify-between items-center">
              <span className="font-bold text-sm text-slate-200">{p.name}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
                {p.status}
              </span>
            </div>
            <div className="mt-3 space-y-1 text-xs text-slate-400 font-mono">
              <div className="flex justify-between">
                <span>Avg Latency:</span>
                <span className="text-cyan-300 font-bold">{p.latencyMs} ms</span>
              </div>
              <div className="flex justify-between">
                <span>Success Rate:</span>
                <span className="text-emerald-300 font-bold">{p.successRate}%</span>
              </div>
              <div className="flex justify-between">
                <span>Environment:</span>
                <span className="text-amber-300">{p.environment}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
