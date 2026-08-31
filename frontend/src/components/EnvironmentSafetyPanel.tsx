import React, { useState } from 'react';

export const EnvironmentSafetyPanel: React.FC = () => {
  const [activeEnv, setActiveEnv] = useState<'SWU' | 'RAZORPAY_TEST' | 'STRIPE_TEST' | 'ADYEN_TEST'>('RAZORPAY_TEST');
  const [killSwitch, setKillSwitch] = useState<boolean>(false);

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mt-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-red-400 tracking-wider">
            ENVIRONMENT CONTROL & FAIL-CLOSED SAFETY GATES
          </h2>
          <p className="text-xs text-slate-400">Strict execution boundary guards & production isolation</p>
        </div>
        <button
          onClick={() => setKillSwitch(!killSwitch)}
          className={`px-4 py-1.5 rounded text-xs font-mono font-bold transition-all ${
            killSwitch
              ? 'bg-red-600 text-white animate-pulse'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          {killSwitch ? 'KILL SWITCH ACTIVE' : 'ENGAGE KILL SWITCH'}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
        {(['SWU', 'RAZORPAY_TEST', 'STRIPE_TEST', 'ADYEN_TEST'] as const).map((env) => (
          <button
            key={env}
            onClick={() => setActiveEnv(env)}
            className={`p-2 rounded text-xs font-mono border transition-all ${
              activeEnv === env
                ? 'bg-cyan-950 text-cyan-200 border-cyan-500 font-bold'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700'
            }`}
          >
            {env}
          </button>
        ))}
      </div>

      <div className="p-3 bg-slate-900/60 rounded border border-slate-800 text-xs font-mono flex justify-between items-center">
        <div>
          <span className="text-slate-500">Current Execution Gate: </span>
          <span className="text-emerald-400 font-bold">{activeEnv} (SANDBOX ONLY)</span>
        </div>
        <div>
          <span className="text-slate-500">Production Mode: </span>
          <span className="text-red-400 font-bold">DISABLED BY DEFAULT</span>
        </div>
      </div>
    </div>
  );
};
