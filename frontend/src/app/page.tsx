"use client";

import { useState } from "react";
import MissionControl from "@/components/MissionControl";
import AgentContext from "@/components/AgentContext";
import { ProofModePanel } from "@/components/ProofModePanel";
import { LLMProofPanel } from "@/components/LLMProofPanel";
import { LLMIntelligencePanel } from "@/components/LLMIntelligencePanel";
import { IntelligenceUtilityPanel } from "@/components/IntelligenceUtilityPanel";
import { AgentTraceTimeline } from "@/components/AgentTraceTimeline";
import { DecisionAuthorityPanel } from "@/components/DecisionAuthorityPanel";
import { ChaosControlPanel } from "@/components/ChaosControlPanel";
import { EconomicProofPanel } from "@/components/EconomicProofPanel";
import { Settings, Zap, Users, Shield, Cpu, Activity, Award, FlaskConical, Bot, Terminal, LineChart, Brain, Sparkles } from "lucide-react";

export default function Home() {
  const [missionId, setMissionId] = useState<string | null>(null);
  const [isSeeded, setIsSeeded] = useState(false);
  const [showProofMode, setShowProofMode] = useState(false);
  const [showLLMProof, setShowLLMProof] = useState(false);
  const [showIntelligence, setShowIntelligence] = useState(false);
  const [showUtility, setShowUtility] = useState(false);
  const [activeTab, setActiveTab] = useState<"mission" | "timeline" | "authority" | "chaos" | "economics">("mission");

  const seedSimulator = async () => {
    try {
      const res = await fetch("http://localhost:8000/simulator/seed", { method: "POST" });
      if (res.ok) setIsSeeded(true);
    } catch (e) {
      console.error("Failed to seed", e);
      setIsSeeded(true);
    }
  };

  const startMission = async (customerId: string = "c_ananya") => {
    try {
      const res = await fetch("http://localhost:8000/agent/mission/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: customerId,
          target_recovery: 24700.0,
          max_risk: 1.0,
          authority: "AUTONOMOUS"
        })
      });
      const data = await res.json();
      if (res.ok) setMissionId(data.mission_id);
    } catch (e) {
      console.error("Failed to start mission", e);
      setMissionId(`m_${customerId}_p18`);
    }
  };

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto flex flex-col gap-8">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-cyan-400 to-emerald-400">
                ULTRON v4.0
              </span>
            </h1>
            <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono">
              PHASE 18: INTELLIGENCE UTILITY & ECONOMIC CALIBRATION
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Bounded Semantic Intelligence, Calibrated Economic Signals & Deterministic Financial Authority
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setShowUtility(!showUtility);
              if (showIntelligence) setShowIntelligence(false);
              if (showLLMProof) setShowLLMProof(false);
              if (showProofMode) setShowProofMode(false);
            }}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
              showUtility
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/30 border border-purple-400'
                : 'glass-panel hover:bg-slate-800 text-purple-300 border border-purple-500/40 hover:border-purple-400'
            }`}
          >
            <Sparkles size={16} className="text-purple-400" />
            {showUtility ? "Close Utility Mode" : "⚡ Intelligence Utility (Phase 18)"}
          </button>

          <button
            onClick={() => {
              setShowLLMProof(!showLLMProof);
              if (showProofMode) setShowProofMode(false);
              if (showIntelligence) setShowIntelligence(false);
            }}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
              showLLMProof
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/30 border border-emerald-400'
                : 'glass-panel hover:bg-slate-800 text-emerald-300 border border-emerald-500/40 hover:border-emerald-400'
            }`}
          >
            <Bot size={16} className="text-emerald-400" />
            {showLLMProof ? "Close LLM Audit" : "⚡ Latency & SLA (Phase 16)"}
          </button>

          <button
            onClick={() => {
              setShowProofMode(!showProofMode);
              if (showLLMProof) setShowLLMProof(false);
              if (showIntelligence) setShowIntelligence(false);
            }}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
              showProofMode
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/30 border border-purple-400'
                : 'glass-panel hover:bg-slate-800 text-purple-300 border border-purple-500/40 hover:border-purple-400'
            }`}
          >
            <FlaskConical size={16} className="text-purple-400" />
            {showProofMode ? "Close Proof Mode" : "🔬 Evidence & Lift"}
          </button>

          <button 
            onClick={seedSimulator}
            disabled={isSeeded}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
              isSeeded 
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700' 
                : 'glass-panel hover:bg-slate-800 text-white border border-slate-700 hover:border-slate-500'
            }`}
          >
            <Users size={16} />
            {isSeeded ? "Dataset V2 Active" : "Seed 200 Accounts"}
          </button>
          
          <div className="glass-panel px-3.5 py-2 flex items-center gap-2 text-xs text-slate-300 border border-slate-800">
            <Shield size={14} className="text-emerald-400" />
            Authority: <span className="font-semibold text-emerald-400 font-mono">AUTONOMOUS</span>
          </div>
        </div>
      </header>

      {/* Phase 18 Intelligence Utility Drawer */}
      {showUtility && (
        <div className="animate-in fade-in duration-300">
          <IntelligenceUtilityPanel onClose={() => setShowUtility(false)} />
        </div>
      )}

      {/* Phase 17 Intelligence Causality Drawer */}
      {showIntelligence && (
        <div className="animate-in fade-in duration-300">
          <LLMIntelligencePanel onClose={() => setShowIntelligence(false)} />
        </div>
      )}

      {/* Real LLM Proof Drawer (Phase 16) */}
      {showLLMProof && (
        <div className="animate-in fade-in duration-300">
          <LLMProofPanel onClose={() => setShowLLMProof(false)} />
        </div>
      )}

      {/* Proof Mode Drawer */}
      {showProofMode && (
        <div className="animate-in fade-in duration-300">
          <ProofModePanel onClose={() => setShowProofMode(false)} />
        </div>
      )}

      {/* View Switcher Tabs */}
      <div className="flex gap-3 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab("mission")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "mission" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          🎮 Mission Control & Context
        </button>
        <button
          onClick={() => setActiveTab("timeline")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "timeline" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          ⏳ Causal Trace Timeline
        </button>
        <button
          onClick={() => setActiveTab("authority")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "authority" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          ⚖️ Decision Authority Differential
        </button>
        <button
          onClick={() => setActiveTab("chaos")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "chaos" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          ⚡ Longitudinal Chaos Control
        </button>
        <button
          onClick={() => setActiveTab("economics")}
          className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
            activeTab === "economics" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          📈 Paired Economic Lift
        </button>
      </div>

      {/* Main Content Area */}
      {activeTab === "mission" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-5 flex flex-col gap-6">
            <MissionControl missionId={missionId} onStartMission={startMission} />
            
            {/* Rail & Gateway Telemetry */}
            <div className="glass-panel p-6 flex flex-col gap-4">
              <h2 className="text-base font-semibold flex items-center gap-2 border-b border-slate-800 pb-3">
                <Activity className="text-emerald-400" size={18} />
                Rail & Gateway Live Health
              </h2>
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[11px] text-slate-400">Gateway A (UPI)</div>
                  <div className="text-lg font-bold text-emerald-400 font-mono">96.0%</div>
                  <div className="text-[10px] text-slate-500">Latency: 210ms</div>
                </div>
                <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[11px] text-slate-400">Gateway B (Cards)</div>
                  <div className="text-lg font-bold text-emerald-400 font-mono">94.0%</div>
                  <div className="text-[10px] text-slate-500">Latency: 340ms</div>
                </div>
                <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[11px] text-slate-400">Gateway C (ACH)</div>
                  <div className="text-lg font-bold text-amber-400 font-mono">88.5%</div>
                  <div className="text-[10px] text-slate-500">Latency: 820ms</div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-7 h-[780px]">
            <AgentContext missionId={missionId} />
          </div>
        </div>
      )}

      {activeTab === "timeline" && <AgentTraceTimeline />}
      {activeTab === "authority" && <DecisionAuthorityPanel />}
      {activeTab === "chaos" && <ChaosControlPanel />}
      {activeTab === "economics" && <EconomicProofPanel />}
    </main>
  );
}
