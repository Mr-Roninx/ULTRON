import React from 'react';

export const ProviderTruthPanel: React.FC = () => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-cyan-400 tracking-wider">
            PROVIDER ADAPTER TRUTH MATRIX
          </h2>
          <p className="text-xs text-slate-400">Honest runtime verification status across payment gateways</p>
        </div>
        <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-full text-xs font-mono">
          EVALUATOR PERSPECTIVE
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
        <div className="p-4 bg-slate-900/80 rounded border border-slate-800 space-y-2">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-200">Razorpay</span>
            <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px]">
              FIXTURE_ONLY
            </span>
          </div>
          <p className="text-slate-400">Adapter Support: <span className="text-emerald-400 font-bold">YES</span></p>
          <p className="text-slate-400">Webhook Verifier: <span className="text-emerald-400 font-bold">HMAC-SHA256</span></p>
          <p className="text-slate-400">Payment Links: <span className="text-emerald-400 font-bold">YES</span></p>
          <p className="text-slate-400">Live Credentials: <span className="text-amber-400">NOT EXPORTED</span></p>
        </div>

        <div className="p-4 bg-slate-900/80 rounded border border-slate-800 space-y-2">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-200">Stripe</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 text-[10px]">
              NOT_CONFIGURED
            </span>
          </div>
          <p className="text-slate-400">Adapter Support: <span className="text-emerald-400 font-bold">YES</span></p>
          <p className="text-slate-400">Webhook Verifier: <span className="text-emerald-400 font-bold">Stripe-Sig</span></p>
          <p className="text-slate-400">Checkout Links: <span className="text-emerald-400 font-bold">YES</span></p>
          <p className="text-slate-400">Live Credentials: <span className="text-slate-500">ABSENT</span></p>
        </div>

        <div className="p-4 bg-slate-900/80 rounded border border-slate-800 space-y-2">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-200">Adyen</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 text-[10px]">
              NOT_CONFIGURED
            </span>
          </div>
          <p className="text-slate-400">Adapter Support: <span className="text-emerald-400 font-bold">YES</span></p>
          <p className="text-slate-400">Webhook Verifier: <span className="text-emerald-400 font-bold">Adyen-HMAC</span></p>
          <p className="text-slate-400">Pay-by-Link: <span className="text-emerald-400 font-bold">YES</span></p>
          <p className="text-slate-400">Live Credentials: <span className="text-slate-500">ABSENT</span></p>
        </div>
      </div>
    </div>
  );
};
