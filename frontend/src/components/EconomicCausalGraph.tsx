import React from 'react';

export const EconomicCausalGraph: React.FC = () => {
  const edges = [
    { from: 'CustomerBehavior', to: 'PaymentIntent', desc: 'Intent ~ Bernoulli(P(intent | tier, liquidity))' },
    { from: 'GatewayHealth', to: 'AuthorizationOutcome', desc: 'P(auth) = base * health_score' },
    { from: 'ULTRONAction', to: 'CustomerResponse', desc: 'Response = f(channel, fatigue, liquidity)' },
    { from: 'ULTRONAction', to: 'CommunicationFatigue', desc: 'Fatigue_t+1 = min(1.0, Fatigue_t + delta)' },
    { from: 'CustomerResponse', to: 'RecoveryOutcome', desc: 'Recovery = Link_Paid | Retry_Authorized' },
    { from: 'RecoveryOutcome', to: 'CustomerRelationship', desc: 'Relationship_t+1 = Relationship_t + delta' },
    { from: 'RecoveryOutcome', to: 'MerchantRevenue', desc: 'Settlement clears to merchant bank ledger' }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 mt-4">
      <h3 className="text-md font-bold text-slate-200 uppercase tracking-wider mb-4">Structural Causal Lineage Model</h3>
      <div className="space-y-2">
        {edges.map((e, idx) => (
          <div key={idx} className="flex items-center justify-between p-2.5 bg-slate-800/40 border border-slate-700/50 rounded text-xs font-mono">
            <div className="flex items-center space-x-2">
              <span className="text-cyan-400 font-bold">{e.from}</span>
              <span className="text-slate-500">→</span>
              <span className="text-emerald-400 font-bold">{e.to}</span>
            </div>
            <span className="text-slate-400 text-[11px] font-sans">{e.desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
