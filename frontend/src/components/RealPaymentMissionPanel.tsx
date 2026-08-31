import React from 'react';

export const RealPaymentMissionPanel: React.FC = () => {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-amber-400 tracking-wider">
            REAL PAYMENT RECOVERY MISSION
          </h2>
          <p className="text-xs text-slate-400">Autonomous recovery lifecycle for active customer payment failure</p>
        </div>
        <span className="px-3 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-full text-xs font-mono">
          STATUS: RECOVERED
        </span>
      </div>

      <div className="p-4 bg-slate-900/90 rounded-lg border border-slate-800 space-y-3">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-500">Customer:</span>
            <p className="text-slate-200 font-bold">Ananya Textiles</p>
          </div>
          <div>
            <span className="text-slate-500">Amount:</span>
            <p className="text-emerald-400 font-bold">₹24,700.00</p>
          </div>
          <div>
            <span className="text-slate-500">Provider:</span>
            <p className="text-cyan-400 font-bold">Razorpay Test</p>
          </div>
          <div>
            <span className="text-slate-500">Selected Action:</span>
            <p className="text-amber-300 font-bold">SEND_PAYMENT_LINK</p>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800 text-xs text-slate-300 space-y-1">
          <p className="text-slate-400 font-mono">AUTONOMOUS EXECUTION TRACE:</p>
          <p>• Webhook received: <span className="font-mono text-red-400">payment.failed</span> (ISO 91 Issuer Timeout)</p>
          <p>• LLM Diagnostic: Transient failure on primary bank rail; recommend non-intrusive 1-click payment link</p>
          <p>• Deterministic Authority: Authorized under <span className="font-mono text-cyan-300">ActionRegistry</span> permission <span className="font-mono text-slate-200">PAYMENT_LINK_CREATION</span></p>
          <p>• Action Executed: Generated <span className="font-mono text-amber-300">https://rzp.io/i/plink_99812</span> & dispatched via WhatsApp/Email</p>
          <p>• Settlement Webhook: <span className="font-mono text-emerald-400">payment_link.paid</span> verified & reconciled with double-entry ledger</p>
        </div>
      </div>
    </div>
  );
};
