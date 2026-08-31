'use client';

import React from 'react';

export const AgentTraceTimeline: React.FC = () => {
  const steps = [
    { step: 1, phase: "OBSERVE", title: "Failure Ingestion", desc: "Detected ISO 91 on Ananya Textiles ₹24,700 CARD transaction.", status: "COMPLETED", tag: "T0" },
    { step: 2, phase: "LLM_REASON", title: "LLM Invocation #1", desc: "HF Qwen proposed candidate set: [WAIT, RETRY_GATEWAY_A, SEND_PAYMENT_LINK]. Preferred: WAIT.", status: "COMPLETED", tag: "LLM #1" },
    { step: 3, phase: "AUTHORITY", title: "Deterministic Decision", desc: "NEV Ranker selected RETRY_GATEWAY_A (₹10,926.49 expected yield). Overrode LLM preference.", status: "COMPLETED", tag: "AUTHORITY" },
    { step: 4, phase: "EXECUTE", title: "Execution & Wait", desc: "Scheduled retry; entered WAIT state on VirtualClock.", status: "COMPLETED", tag: "EXEC" },
    { step: 5, phase: "CHAOS", title: "Mid-Flight Chaos (T+2h)", desc: "Gateway A health dropped to 10% (Simulated outage). Triggered wake-up.", status: "COMPLETED", tag: "T+2h" },
    { step: 6, phase: "REPLAN", title: "LLM Invocation #2", desc: "Plan invalidated. LLM re-invoked; proposed alternate channels: [SEND_MESSAGE, SEND_PAYMENT_LINK].", status: "COMPLETED", tag: "LLM #2" },
    { step: 7, phase: "LEARN", title: "Recovery & Memory", desc: "Alternate channel executed. Observed outcome; updated episodic prediction error memory.", status: "COMPLETED", tag: "LEARN" }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-200">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
          ⏳ Causal Trace Timeline (Golden Demo Demo_04)
        </h3>
        <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30 font-mono">
          2 LLM Invocations | 1 Replan
        </span>
      </div>

      <div className="space-y-3 font-mono text-xs">
        {steps.map((s) => (
          <div key={s.step} className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-cyan-950 border border-cyan-500/40 text-cyan-300 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
              {s.step}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-xs">{s.title}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">{s.tag}</span>
              </div>
              <p className="text-slate-400 text-[11px] mt-1 font-sans">{s.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
