import React from 'react';

export const ProviderEventTimeline: React.FC = () => {
  const events = [
    { time: '12:30:05', provider: 'Razorpay', type: 'payment.failed', code: 'GATEWAY_TIMEOUT', sig: 'VERIFIED' },
    { time: '12:30:08', provider: 'ULTRON', type: 'SEND_PAYMENT_LINK', code: 'DISPATCHED', sig: 'AUTHORIZED' },
    { time: '12:34:19', provider: 'Razorpay', type: 'payment_link.paid', code: 'CAPTURED', sig: 'VERIFIED' },
    { time: '12:34:20', provider: 'Ledger', type: 'LEDGER_SETTLEMENT', code: 'BALANCED', sig: 'CONSERVED' }
  ];

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold text-indigo-400 tracking-wider">
          PROVIDER EVENT TIMELINE & AUDIT
        </h2>
        <span className="text-xs text-slate-400 font-mono">HMAC-SHA256 ENFORCED</span>
      </div>

      <div className="space-y-2">
        {events.map((e, idx) => (
          <div key={idx} className="flex justify-between items-center p-3 bg-slate-900/60 rounded border border-slate-800 text-xs font-mono">
            <div className="flex items-center space-x-3">
              <span className="text-slate-500">{e.time}</span>
              <span className="text-cyan-300 font-bold">[{e.provider}]</span>
              <span className="text-slate-200">{e.type}</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-amber-300">{e.code}</span>
              <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px]">
                {e.sig}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
