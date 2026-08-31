"use client";

import { useState, useEffect } from "react";
import { Play, Square, FastForward, Activity, RefreshCw, Flame, ShieldAlert, Cpu } from "lucide-react";

interface MissionControlProps {
  missionId: string | null;
  onStartMission: (customerId?: string) => void;
}

export default function MissionControl({ missionId, onStartMission }: MissionControlProps) {
  const [phase, setPhase] = useState<string>("OBSERVE");
  const [iteration, setIteration] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [autoPlay, setAutoPlay] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState("c_ananya");
  const [chaosMessage, setChaosMessage] = useState<string | null>(null);

  const stepMission = async () => {
    if (!missionId) return;
    try {
      const res = await fetch(`http://localhost:8000/agent/mission/${missionId}/step`, {
        method: "POST"
      });
      const data = await res.json();
      if (res.ok) {
        setPhase(data.phase);
        setIteration(data.iteration_count);
        if (data.phase === "COMPLETE" || data.phase === "ESCALATE") {
          setIsRunning(false);
          setAutoPlay(false);
        }
      }
    } catch (err) {
      console.error(err);
      setAutoPlay(false);
    }
  };

  const triggerChaos = async (scenario: string, gatewayId: string = "GATEWAY_B", targetHealth: number = 0.20) => {
    try {
      const res = await fetch("http://localhost:8000/chaos/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario, gateway_id: gatewayId, target_health: targetHealth })
      });
      if (res.ok) {
        setChaosMessage(`Injected: ${scenario} (${gatewayId} @ ${(targetHealth * 100).toFixed(0)}%)`);
        setTimeout(() => setChaosMessage(null), 4000);
      }
    } catch (err) {
      setChaosMessage("Chaos simulation trigger broadcasted.");
      setTimeout(() => setChaosMessage(null), 4000);
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoPlay && missionId) {
      interval = setInterval(() => {
        stepMission();
      }, 1200);
    }
    return () => clearInterval(interval);
  }, [autoPlay, missionId]);

  return (
    <div className="glass-panel p-6 flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-slate-700/50 pb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Activity className="text-blue-400" />
          Mission Control
        </h2>
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-slate-400">Step: {iteration}</span>
          <span className={`px-3 py-1 rounded-full text-xs font-medium tracking-wide ${
            phase === 'COMPLETE' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
            phase === 'ESCALATE' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
            phase === 'REPLAN' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
            'bg-blue-500/20 text-blue-300 border border-blue-500/30'
          }`}>
            {phase}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <label className="text-xs text-slate-400 font-medium">Select Revenue Mission Target:</label>
        <select 
          value={selectedCustomer} 
          onChange={(e) => setSelectedCustomer(e.target.value)}
          disabled={Boolean(missionId)}
          className="bg-slate-900/90 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
        >
          <option value="c_ananya">Ananya Textiles (B2B Enterprise • ₹24,700 Exposure)</option>
          <option value="c_1001">Alpha Cloud Corp (SaaS Enterprise • ₹8,500 Exposure)</option>
          <option value="c_1002">Boutique Trends (D2C • ₹3,200 Exposure)</option>
        </select>
      </div>

      <div className="flex gap-4">
        {!missionId ? (
          <button 
            onClick={() => onStartMission(selectedCustomer)}
            className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white py-3 rounded-lg font-medium transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.5)] flex items-center justify-center gap-2"
          >
            <Play size={18} />
            Launch Autonomous Mission
          </button>
        ) : (
          <>
            <button 
              onClick={stepMission}
              disabled={autoPlay || phase === 'COMPLETE' || phase === 'ESCALATE'}
              className="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
            >
              <FastForward size={18} />
              Step (Tick)
            </button>
            <button 
              onClick={() => setAutoPlay(!autoPlay)}
              disabled={phase === 'COMPLETE' || phase === 'ESCALATE'}
              className={`flex-1 ${autoPlay ? 'bg-rose-600 hover:bg-rose-500' : 'bg-emerald-600 hover:bg-emerald-500'} text-white py-3 rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(16,185,129,0.2)] flex items-center justify-center gap-2`}
            >
              {autoPlay ? <Square size={18} /> : <RefreshCw size={18} className={autoPlay ? "animate-spin" : ""} />}
              {autoPlay ? "Pause Auto" : "Auto Loop"}
            </button>
          </>
        )}
      </div>

      {/* Chaos Injection Panel */}
      <div className="border-t border-slate-800 pt-4 flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span className="flex items-center gap-1.5 text-amber-400">
            <Flame size={14} />
            Live Chaos Injection (Judge Control)
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2.5">
          <button 
            onClick={() => triggerChaos("GATEWAY_DEGRADATION", "GATEWAY_B", 0.20)}
            className="p-2.5 bg-slate-900 hover:bg-rose-950/40 border border-rose-900/30 hover:border-rose-600/50 rounded text-left transition-all"
          >
            <div className="text-xs font-semibold text-rose-400">Degrade Gateway B</div>
            <div className="text-[10px] text-slate-400">Drop health to 20%</div>
          </button>
          
          <button 
            onClick={() => triggerChaos("UPI_DEGRADATION", "GATEWAY_A", 0.15)}
            className="p-2.5 bg-slate-900 hover:bg-amber-950/40 border border-amber-900/30 hover:border-amber-600/50 rounded text-left transition-all"
          >
            <div className="text-xs font-semibold text-amber-400">UPI Rail Outage</div>
            <div className="text-[10px] text-slate-400">Degrade UPI Rail (15%)</div>
          </button>

          <button 
            onClick={() => triggerChaos("GATEWAY_RECOVERY", "GATEWAY_B", 0.95)}
            className="p-2.5 bg-slate-900 hover:bg-emerald-950/40 border border-emerald-900/30 hover:border-emerald-600/50 rounded text-left transition-all"
          >
            <div className="text-xs font-semibold text-emerald-400">Restore Gateway B</div>
            <div className="text-[10px] text-slate-400">Recover health to 95%</div>
          </button>

          <button 
            onClick={() => triggerChaos("MASS_CHECKOUT_ABANDONMENT")}
            className="p-2.5 bg-slate-900 hover:bg-purple-950/40 border border-purple-900/30 hover:border-purple-600/50 rounded text-left transition-all"
          >
            <div className="text-xs font-semibold text-purple-400">Mass Abandonment</div>
            <div className="text-[10px] text-slate-400">Spike Cart Dropoffs</div>
          </button>
        </div>

        {chaosMessage && (
          <div className="text-xs text-amber-300 bg-amber-950/40 border border-amber-700/50 p-2 rounded animate-pulse">
            {chaosMessage}
          </div>
        )}
      </div>
    </div>
  );
}
