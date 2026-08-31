import React, { useState } from 'react';

export type StressScenarioType =
  | 'NATURAL_RECOVERY_HEAVY'
  | 'HIGH_FATIGUE'
  | 'GATEWAY_STRESS'
  | 'LIQUIDITY_SHOCK'
  | 'CUSTOMER_CHURN'
  | 'MERCHANT_STRESS'
  | 'MULTI_OPPORTUNITY';

export const EconomicStressTestPanel: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState<StressScenarioType>('NATURAL_RECOVERY_HEAVY');
  const [running, setRunning] = useState<boolean>(false);

  const scenarioDetails: Record<StressScenarioType, { desc: string; expectedVerdict: string; netLift: string }> = {
    NATURAL_RECOVERY_HEAVY: {
      desc: 'Customer retries on own within 2h. Interventions cause fatigue with ₹0 incremental recovery.',
      expectedVerdict: 'NEUTRAL_OR_NEGATIVE_LIFT',
      netLift: '₹0 (Saved Naturally)'
    },
    HIGH_FATIGUE: {
      desc: 'Repeated outreach drives fatigue above 0.85, triggering customer opt-out and churn.',
      expectedVerdict: 'NEGATIVE_EFFECT',
      netLift: '-₹1,250 (Churn Externality)'
    },
    GATEWAY_STRESS: {
      desc: 'Switching traffic overwhelms secondary gateway capacity, degrading auth rate for all merchants.',
      expectedVerdict: 'NEGATIVE_EXTERNALITY',
      netLift: '-₹450 (Network Spillover)'
    },
    LIQUIDITY_SHOCK: {
      desc: 'Salary delay across cohort; outreach before salary day yields zero conversion.',
      expectedVerdict: 'WAIT_OPTIMAL',
      netLift: '₹18,500 (Delayed Recovery)'
    },
    CUSTOMER_CHURN: {
      desc: 'At-risk customer churns if contacted aggressively; conservative waiting preserves account.',
      expectedVerdict: 'CONSERVATIVE_DOMINATES',
      netLift: '+₹45,000 LTV Preserved'
    },
    MERCHANT_STRESS: {
      desc: 'Receivables backlog requires priority recovery without creating excessive support ticket burden.',
      expectedVerdict: 'POSITIVE_EFFECT',
      netLift: '+₹38,200 Recovered'
    },
    MULTI_OPPORTUNITY: {
      desc: 'Agent capacity limits force optimal greedy ranking across 5 concurrent failed payments.',
      expectedVerdict: 'POSITIVE_EFFECT',
      netLift: '+₹112,000 Capacity-Bounded'
    }
  };

  const current = scenarioDetails[selectedScenario];

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-xl font-bold text-amber-400 tracking-wider">
            JUDGE MODE // ECONOMIC STRESS TEST & ADVERSARIAL REALITY
          </h2>
          <p className="text-xs text-slate-400 mt-1">Simulates realistic negative externalities, natural recovery, and adverse policies</p>
        </div>
        <span className="px-3 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-full text-xs font-mono">
          ADVERSARIAL REALITY ACTIVE
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-6">
        {(Object.keys(scenarioDetails) as StressScenarioType[]).map((sc) => (
          <button
            key={sc}
            onClick={() => setSelectedScenario(sc)}
            className={`px-3 py-2 text-xs font-mono rounded border transition-all ${
              selectedScenario === sc
                ? 'bg-amber-500/30 text-amber-200 border-amber-500 font-bold'
                : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
            }`}
          >
            {sc.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-800 mb-4">
        <p className="text-xs text-slate-400 uppercase font-mono">Scenario Mechanism</p>
        <p className="text-sm text-slate-200 mt-1">{current.desc}</p>
        <div className="flex justify-between items-center mt-3 pt-3 border-t border-slate-800/80">
          <div>
            <span className="text-xs text-slate-400">Expected Causal Verdict: </span>
            <span className="text-xs font-bold text-amber-300 font-mono">{current.expectedVerdict}</span>
          </div>
          <div>
            <span className="text-xs text-slate-400">Net Causal Lift: </span>
            <span className="text-xs font-bold text-cyan-300 font-mono">{current.netLift}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
