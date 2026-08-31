import React from 'react';

export const RazorpayEventTimeline: React.FC = () => {
  const events = [
    { time: '13:00:01', source: 'Razorpay', event: 'payment.failed', details: 'ISO 91 Issuer Timeout', sig: 'VERIFIED' },
    { time: '13:00:02', source: 'ULTRON', event: 'RealPaymentMission Created', details: 'State: OBSERVING -> PLANNING', sig: 'AUTHORIZED' },
    { time: '13:00:03', source: 'ULTRON', event: 'SEND_PAYMENT_LINK', details: 'https://rzp.io/i/plink_demo_24700', sig: 'ACTION_REGISTRY' },
    { time: '13:02:14', source: 'Razorpay', event: 'payment_link.paid', details: '₹24,700.00 Captured (2,470,000 paise)', sig: 'VERIFIED' },
    { time: '13:02:15', source: 'Reconciliation', event: 'Truth Reconciled', details: 'State: SETTLED -> Ledger Conserved', sig: 'BALANCED' }
  ];

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold text-cyan-400 tracking-wider">
          RAZORPAY EVENT AUDIT TIMELINE
        </h2>
        <span className="text-xs text-slate-400 font-mono">HMAC-SHA256 ENFORCED</span>
      </div>

      <div className="space-y-2">
        {events.map((e, idx) => (
          <div key={idx} className="flex justify-between items-center p-3 bg-slate-900/60 rounded border border-slate-800 text-xs font-mono">
            <div className="flex items-center space-x-3">
              <span className="text-slate-500">{e.time}</span>
              <span className="text-cyan-300 font-bold">[{e.source}]</span>
              <span className="text-slate-200">{e.event}</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-slate-400">{e.details}</span>
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
