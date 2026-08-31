import React from 'react';

export const RazorpayStatusPanel: React.FC = () => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-cyan-400 tracking-wider">
            RAZORPAY TEST ADAPTER & HEALTH
          </h2>
          <p className="text-xs text-slate-400">Sole external payment provider in ULTRON v5.0 Real Execution Plane</p>
        </div>
        <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-mono">
          STATUS: HEALTHY (SANDBOX)
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-slate-900/80 rounded-lg border border-slate-800 text-xs font-mono">
        <div>
          <span className="text-slate-500">Provider Endpoint:</span>
          <p className="text-slate-200 font-bold">https://api.razorpay.com/v1</p>
        </div>
        <div>
          <span className="text-slate-500">Avg API Latency:</span>
          <p className="text-cyan-400 font-bold">115.0 ms</p>
        </div>
        <div>
          <span className="text-slate-500">Webhook Scheme:</span>
          <p className="text-emerald-400 font-bold">HMAC-SHA256 (Raw Body)</p>
        </div>
        <div>
          <span className="text-slate-500">Environment:</span>
          <p className="text-amber-300 font-bold">TEST / SANDBOX</p>
        </div>
      </div>
    </div>
  );
};
