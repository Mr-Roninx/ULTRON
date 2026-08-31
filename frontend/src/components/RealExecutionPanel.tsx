import React from 'react';

export const RealExecutionPanel: React.FC = () => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-amber-400 tracking-wider">
            JUDGE MODE // REAL SANDBOX DEMONSTRATION
          </h2>
          <p className="text-xs text-slate-400">Live operational execution plane against Razorpay / Stripe test sandboxes</p>
        </div>
        <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-full text-xs font-mono">
          TEST / SANDBOX
        </span>
      </div>

      <div className="p-4 bg-slate-900/90 rounded-lg border border-slate-800 text-xs font-mono space-y-3">
        <div className="flex justify-between items-center border-b border-slate-800 pb-2">
          <span>Active Test Target:</span>
          <span className="text-cyan-300 font-bold">Razorpay Test Sandbox (Ananya Textiles Demo)</span>
        </div>
        <div className="flex justify-between items-center border-b border-slate-800 pb-2">
          <span>Amount:</span>
          <span className="text-emerald-400 font-bold">₹24,700.00 (2,470,000 paise)</span>
        </div>
        <div className="flex justify-between items-center border-b border-slate-800 pb-2">
          <span>Deterministic Action Authorized:</span>
          <span className="text-amber-300 font-bold">SEND_PAYMENT_LINK</span>
        </div>
        <div className="flex justify-between items-center">
          <span>External Link Generated:</span>
          <span className="text-slate-200 underline font-bold">https://rzp.io/i/plink_demo_24700</span>
        </div>
      </div>
    </div>
  );
};
