import React from 'react';

export interface TimelineCheckpoint {
  day: number;
  event: string;
  category: 'MACRO' | 'PAYMENT' | 'ULTRON' | 'CHAOS' | 'RELATIONSHIP';
  details: string;
}

export const EconomicTimeline: React.FC<{ checkpoints?: TimelineCheckpoint[] }> = ({ checkpoints }) => {
  const defaultCheckpoints: TimelineCheckpoint[] = [
    { day: 0, event: 'World Genesis', category: 'MACRO', details: 'Initialized 5,000 customers & 50 merchants' },
    { day: 1, event: 'Ananya Textiles Failure', category: 'PAYMENT', details: 'ISO 91 timeout on ₹24,700 card invoice' },
    { day: 1, event: 'ULTRON Semantic Replan', category: 'ULTRON', details: 'ActionRegistry executed SWITCH_GATEWAY' },
    { day: 2, event: 'Mid-Flight Gateway Chaos', category: 'CHAOS', details: 'Gateway A degradation injected (health -> 8%)' },
    { day: 3, event: 'Settlement Reconciliation', category: 'MACRO', details: 'Double-entry clearing balanced ₹24,700' },
    { day: 30, event: 'Subscription Auto-Renewal', category: 'RELATIONSHIP', details: 'Customer retention active, fatigue decayed' },
  ];

  const items = checkpoints || defaultCheckpoints;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 mt-4">
      <h3 className="text-md font-bold text-slate-200 uppercase tracking-wider mb-4">Continuous Economic Timeline</h3>
      <div className="space-y-3">
        {items.map((item, idx) => (
          <div key={idx} className="flex items-start space-x-3 p-2 rounded bg-slate-800/40 border border-slate-700/50">
            <span className="px-2 py-0.5 bg-slate-700 text-cyan-300 text-xs font-mono rounded">
              DAY {item.day}
            </span>
            <div className="flex-1">
              <div className="flex justify-between items-center">
                <p className="text-sm font-semibold text-white">{item.event}</p>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                  {item.category}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{item.details}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
