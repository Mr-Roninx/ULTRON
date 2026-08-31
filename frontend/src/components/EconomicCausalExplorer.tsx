import React from 'react';

export const EconomicCausalExplorer: React.FC = () => {
  const steps = [
    { title: 'Customer Cohort Demand', detail: 'Emergent purchase intent generated based on salary cycle & trust' },
    { title: 'Payment Attempt', detail: 'Routed into Gateway A with dynamic capacity monitoring' },
    { title: 'Gateway Congestion', detail: 'Load exceeded capacity triggering transient ISO 91 timeout' },
    { title: 'ULTRON Observation', detail: 'Sanitized through firewall (no oracle/future data revealed)' },
    { title: 'Deterministic Intervention', detail: 'SWITCH_GATEWAY executed via ActionRegistry to Gateway B' },
    { title: 'Settlement & Ledger', detail: '₹24,700 balanced debit/credit entry booked to merchant receivables' },
    { title: 'Downstream Feedback', detail: 'Customer trust improved (+5%), future LTV increased' }
  ];

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 mt-4">
      <h3 className="text-md font-bold text-slate-200 uppercase tracking-wider mb-4">Causal Lineage & Provenance Explorer</h3>
      <div className="relative border-l border-slate-800 ml-4 pl-4 space-y-4">
        {steps.map((s, idx) => (
          <div key={idx} className="relative">
            <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-cyan-400 border border-slate-900" />
            <p className="text-xs font-bold text-cyan-300 font-mono">{s.title}</p>
            <p className="text-xs text-slate-400 mt-0.5">{s.detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
