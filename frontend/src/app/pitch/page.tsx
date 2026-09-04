"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { 
  Play, Pause, RotateCcw, Volume2, VolumeX, Maximize, 
  Video, CheckCircle2, ShieldAlert, Sparkles, 
  ArrowRight, Layers, Lock, Terminal, Activity, ArrowLeft
} from "lucide-react";
import "./pitch.css";

interface PitchScene {
  id: number;
  title: string;
  tagline: string;
  startSec: number;
  endSec: number;
  script: string;
}

const PITCH_SCENES: PitchScene[] = [
  {
    id: 1,
    title: "The Failed Payment Crisis",
    tagline: "The $300B Blind Spot in Digital Payments",
    startSec: 0,
    endSec: 45,
    script: "Every day, millions of digital payments fail. Traditional retry engines ask: 'Can we recover this?' They blast retries indiscriminately, burning processor fees, spamming customers, and taking credit for payments that would have settled naturally. That stops today.",
  },
  {
    id: 2,
    title: "Enter ULTRON: Causal Lift",
    tagline: "Incremental Value of Economic Network (IVEN)",
    startSec: 45,
    endSec: 105,
    script: "Meet ULTRON: the autonomous economic control plane for failed payments. We do not ask 'can we recover this?' We ask: 'Is recovering this payment worth our next unit of scarce recovery capacity?' We score by true causal lift: IVEN equals delta P times amount, minus operational cost and fatigue.",
  },
  {
    id: 3,
    title: "The Recovery Market Auction",
    tagline: "Portfolio Allocation Under Capacity Caps & Shadow Price λ",
    startSec: 105,
    endSec: 165,
    script: "Instead of treating payments in isolation, ULTRON runs a portfolio knapsack auction under explicit capacity limits. Opportunities compete by incremental value. The marginal accepted opportunity sets the Shadow Price lambda. Below that, payments are deferred to WAIT or ABSTAIN, saving thousands in blast fees.",
  },
  {
    id: 4,
    title: "Action Authority: Compliance Veto",
    tagline: "Deterministic Safety Gate (Zero LLM on Financial Path)",
    startSec: 165,
    endSec: 225,
    script: "Economics alone is never allowed to execute. Stage 5 is Action Authority: a deterministic five-check compliance gate. If a card is reported stolen, or retry thresholds are breached, Action Authority immediately vetoes execution. No LLM sits on the financial execution path.",
  },
  {
    id: 5,
    title: "Strategic Positioning",
    tagline: "ULTRON vs. Razorpay Vulcan & Agent Studio",
    startSec: 225,
    endSec: 270,
    script: "Where does ULTRON fit? Razorpay Vulcan optimizes in-flight routing at checkout. Agent Studio automates back-office dispute tasks. ULTRON is the merchant's fiduciary control plane governing post-failure capital allocation, with zero-leak isolation between Test Sandbox and Real Money Live mode.",
  },
  {
    id: 6,
    title: "Forensic Truth & Verification",
    tagline: "SHA-256 Double-Entry Ledger & 165 Automated Tests",
    startSec: 270,
    endSec: 300,
    script: "ULTRON reconciles directly against provider truth into a cryptographic SHA-256 double-entry ledger, backed by 165 automated test suites. Experience autonomous economic recovery today at ultron-power.vercel.app. Intelligence that knows when not to act.",
  },
];

export default function PitchStudioPage() {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentSec, setCurrentSec] = useState<number>(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(true);
  const [sfxEnabled, setSfxEnabled] = useState<boolean>(true);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"live" | "test">("live");

  // Dynamic state for Scene 3 simulation
  const [shadowPrice, setShadowPrice] = useState<number>(23.96);
  const [savedFees, setSavedFees] = useState<number>(148.50);

  // Audio Context for UI Sound Design
  const audioCtxRef = useRef<AudioContext | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const canvasContainerRef = useRef<HTMLDivElement | null>(null);

  // Derive active scene
  const activeSceneIndex = PITCH_SCENES.findIndex(
    (s) => currentSec >= s.startSec && currentSec < s.endSec
  );
  const activeScene = PITCH_SCENES[activeSceneIndex >= 0 ? activeSceneIndex : PITCH_SCENES.length - 1];

  // Play Futuristic Synthesizer SFX
  const playTone = useCallback((freq: number, type: OscillatorType = "sine", duration = 0.2, gainVal = 0.03) => {
    if (!sfxEnabled || typeof window === "undefined") return;
    try {
      if (!audioCtxRef.current) {
        const AudioClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        if (AudioClass) audioCtxRef.current = new AudioClass();
      }
      const ctx = audioCtxRef.current;
      if (!ctx) return;
      if (ctx.state === "suspended") ctx.resume();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch {
      // Audio not supported
    }
  }, [sfxEnabled]);

  // Web Speech API Voiceover Narrator
  const speakText = useCallback((text: string) => {
    if (!voiceEnabled || typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05 * playbackSpeed;
    utterance.pitch = 1.0;
    
    // Pick natural English voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Samantha") || v.name.includes("Daniel")));
    if (preferredVoice) utterance.voice = preferredVoice;

    window.speechSynthesis.speak(utterance);
  }, [voiceEnabled, playbackSpeed]);

  // Main 5-Minute Timer Loop
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentSec((prev) => {
          if (prev >= 300) {
            setIsPlaying(false);
            return 300;
          }
          return prev + 1;
        });
      }, 1000 / playbackSpeed);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, playbackSpeed]);

  // Trigger narration & SFX upon entering a new scene
  const lastSpokenSceneRef = useRef<number>(-1);
  useEffect(() => {
    if (isPlaying && activeScene.id !== lastSpokenSceneRef.current) {
      lastSpokenSceneRef.current = activeScene.id;
      playTone(520, "triangle", 0.3, 0.05);
      speakText(activeScene.script);
    }
    if (!isPlaying) {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    }
  }, [activeScene, isPlaying, speakText, playTone]);

  // Dynamic fee accumulation ticker
  useEffect(() => {
    if (isPlaying && activeScene.id === 3) {
      const t = setInterval(() => {
        setSavedFees((prev) => +(prev + 4.85).toFixed(2));
        setShadowPrice((prev) => +(prev + 0.12).toFixed(2));
      }, 2000);
      return () => clearInterval(t);
    }
  }, [isPlaying, activeScene.id]);

  // Screen / Canvas Recording with MediaRecorder
  const toggleRecording = async () => {
    if (isRecording) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
    } else {
      try {
        if (!navigator.mediaDevices?.getDisplayMedia) {
          alert("Screen recording is not supported in this browser environment. Please use OBS or Screen Studio.");
          return;
        }
        const stream = await navigator.mediaDevices.getDisplayMedia({
          video: { frameRate: 60 },
          audio: true,
        });

        const recorder = new MediaRecorder(stream, { mimeType: "video/webm;codecs=vp9" });
        recordedChunksRef.current = [];

        recorder.ondataavailable = (e) => {
          if (e.data.size > 0) recordedChunksRef.current.push(e.data);
        };

        recorder.onstop = () => {
          const blob = new Blob(recordedChunksRef.current, { type: "video/webm" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `ultron-5min-pitch-presentation-${Date.now()}.webm`;
          a.click();
          URL.revokeObjectURL(url);
          stream.getTracks().forEach((track) => track.stop());
        };

        recorder.start();
        mediaRecorderRef.current = recorder;
        setIsRecording(true);

        // Auto start presentation
        setIsPlaying(true);
        setCurrentSec(0);
      } catch {
        alert("Screen capture was canceled or denied.");
      }
    }
  };

  const jumpToScene = (sec: number) => {
    setCurrentSec(sec);
    playTone(440, "sine", 0.15, 0.04);
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="min-h-screen bg-[#03060c] text-slate-100 flex flex-col items-center justify-between p-4 md:p-8 font-sans select-none">
      {/* Top Bar Navigation */}
      <header className="w-full max-w-6xl flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Link 
            href="/dashboard" 
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition text-xs font-mono"
          >
            <ArrowLeft size={14} /> Back to Dashboard
          </Link>
          <div className="h-4 w-px bg-slate-800" />
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            5-MIN CINEMATIC PITCH STUDIO
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono border transition ${
              voiceEnabled 
                ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-300" 
                : "bg-slate-900 border-slate-800 text-slate-500"
            }`}
          >
            {voiceEnabled ? <Volume2 size={13} /> : <VolumeX size={13} />}
            {voiceEnabled ? "Voice: ON" : "Voice: OFF"}
          </button>

          <button
            onClick={toggleRecording}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-mono font-medium border transition ${
              isRecording 
                ? "bg-rose-500/20 border-rose-500 text-rose-300 animate-pulse" 
                : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20"
            }`}
          >
            <Video size={14} />
            {isRecording ? "🔴 Recording... Stop & Save" : "Start & Record Video"}
          </button>
        </div>
      </header>

      {/* ==================================================================== */}
      {/* THE 16:9 CINEMATIC RECTANGLE CANVAS STAGE                            */}
      {/* ==================================================================== */}
      <main 
        ref={canvasContainerRef}
        className="relative w-full max-w-6xl aspect-video bg-[#050b14] rounded-2xl border border-slate-800/80 shadow-2xl overflow-hidden flex flex-col justify-between cinema-canvas-glow"
      >
        {/* Subtle Cyber Grid Background */}
        <div className="absolute inset-0 cyber-grid opacity-20 pointer-events-none" />

        {/* Ambient Top Glow */}
        <div className="absolute top-0 left-1/4 right-1/4 h-32 bg-cyan-500/10 blur-[100px] pointer-events-none" />

        {/* Canvas HUD Overlay */}
        <div className="relative z-10 w-full p-6 flex items-center justify-between border-b border-slate-800/40 bg-slate-950/40 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-[11px] font-mono text-slate-300">
              <span className={`w-2 h-2 rounded-full ${isPlaying ? "bg-emerald-400 animate-ping" : "bg-slate-600"}`} />
              {isPlaying ? "LIVE SCENE PLAYBACK" : "STANDBY"}
            </div>
            <div className="text-xs font-mono text-slate-400">
              SCENE 0{activeScene.id} / 06 : <span className="text-white font-semibold">{activeScene.title.toUpperCase()}</span>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            <div className="text-slate-400">
              TIME: <span className="text-cyan-400 font-bold">{formatTime(currentSec)}</span> / 05:00
            </div>
            <div className="px-2 py-0.5 rounded bg-cyan-950/50 border border-cyan-800/60 text-cyan-300 text-[10px]">
              4K 60FPS MASTER
            </div>
          </div>
        </div>

        {/* ==================================================================== */}
        {/* SCENE DISPLAY VIEWPORT                                               */}
        {/* ==================================================================== */}
        <div className="relative z-10 flex-1 p-8 md:p-12 flex flex-col justify-center items-center overflow-hidden">

          {/* SCENE 1: THE FAILED PAYMENT CRISIS (0:00 - 0:45) */}
          {activeScene.id === 1 && (
            <div className="w-full h-full flex flex-col md:flex-row items-center justify-between gap-8 animate-fadeIn">
              {/* Left Column: Simulated Razorpay Payment Failure Card */}
              <div className="w-full md:w-1/2 flex flex-col items-center">
                <div className="relative w-full max-w-md bg-slate-900/90 border border-rose-500/40 rounded-2xl p-6 shadow-2xl fail-alert-box">
                  <div className="laser-scanner" />
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-rose-500 animate-pulse" />
                      <span className="text-xs font-mono uppercase tracking-wider text-rose-400">Payment Gateway Failure</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">TXID: rzp_fail_89104</span>
                  </div>

                  <div className="flex flex-col items-center py-4 text-center">
                    <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 mb-3">
                      <ShieldAlert size={32} />
                    </div>
                    <div className="text-3xl font-bold font-mono text-white mb-1">₹15,000.00</div>
                    <div className="text-xs text-rose-400 font-mono mb-4">DELEGATION FAILED: bank_gateway_timeout</div>
                    <div className="text-xs text-slate-300 bg-slate-950/80 p-3 rounded-xl border border-slate-800 w-full text-left font-mono">
                      <p className="text-slate-400 mb-1">Customer: <span className="text-white">Arjun Sharma (arjun@corp.in)</span></p>
                      <p className="text-slate-400 mb-1">Method: <span className="text-white">HDFC Netbanking / UPI</span></p>
                      <p className="text-slate-400">Issuer Response: <span className="text-rose-400">Bank Switch Timeout (504)</span></p>
                    </div>
                  </div>

                  <div className="border-t border-slate-800 pt-3 flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <span>Traditional Action:</span>
                    <span className="text-rose-400 font-semibold animate-pulse">Spam Retries 3x (+₹16.50 Fees Burned)</span>
                  </div>
                </div>
              </div>

              {/* Right Column: Pitch Text Typography */}
              <div className="w-full md:w-1/2 flex flex-col justify-center space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono w-fit">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                  THE $300 BILLION PROBLEM
                </div>
                <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-white leading-tight">
                  Every Day, Billions in Payments <span className="text-rose-400">Fail at Checkout</span>
                </h1>
                <p className="text-sm md:text-base text-slate-300 leading-relaxed">
                  Traditional retry systems treat every failure identically: wait 15 minutes and blast a payment link. 
                </p>
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2 text-xs font-mono">
                  <div className="flex items-center gap-2 text-rose-400">
                    <span>✗</span> Indiscriminate SMS & WhatsApp blasting
                  </div>
                  <div className="flex items-center gap-2 text-rose-400">
                    <span>✗</span> Churning high-value customers with duplicate contact
                  </div>
                  <div className="flex items-center gap-2 text-rose-400">
                    <span>✗</span> Burning gateway fees on payments that would settle naturally
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SCENE 2: ENTER ULTRON (0:45 - 1:45) */}
          {activeScene.id === 2 && (
            <div className="w-full h-full flex flex-col items-center justify-center text-center space-y-6 animate-fadeIn">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
                <Sparkles size={14} />
                THE AUTONOMOUS CONTROL PLANE
              </div>

              <h1 className="text-4xl md:text-6xl font-black tracking-tight shimmer-text">
                ULTRON
              </h1>
              <p className="text-base md:text-xl text-slate-300 max-w-2xl font-light">
                &ldquo;We don&apos;t ask <span className="text-rose-400 line-through">can we recover this payment?</span>&rdquo;<br/>
                We ask: <span className="text-emerald-400 font-semibold">&ldquo;Is recovering this payment worth spending our next unit of scarce recovery capacity?&rdquo;</span>
              </p>

              {/* Formula Card */}
              <div className="w-full max-w-3xl bg-slate-900/90 border border-cyan-500/40 rounded-2xl p-6 shadow-2xl backdrop-blur-xl">
                <div className="text-xs font-mono uppercase tracking-widest text-cyan-400 mb-3">
                  Incremental Value of Economic Network (IVEN)
                </div>
                <div className="text-xl md:text-3xl font-mono font-bold text-white tracking-wide py-2">
                  IVEN = (<span className="text-emerald-400">ΔP</span> × <span className="text-cyan-400">Amount</span>) − <span className="text-amber-400">C<sub>ops</sub></span> − <span className="text-rose-400">C<sub>fatigue</sub></span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-slate-800 text-xs font-mono text-left">
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="text-emerald-400 font-bold block mb-1">ΔP (Causal Lift)</span>
                    <span className="text-slate-400 text-[11px]">P(intervention) − P(natural recovery)</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="text-cyan-400 font-bold block mb-1">Amount</span>
                    <span className="text-slate-400 text-[11px]">Transaction value in paise / rupees</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="text-amber-400 font-bold block mb-1">C<sub>ops</sub> (Unit Cost)</span>
                    <span className="text-slate-400 text-[11px]">₹4.00 Razorpay link + messaging overhead</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="text-rose-400 font-bold block mb-1">C<sub>fatigue</sub> (Goodwill)</span>
                    <span className="text-slate-400 text-[11px]">Customer churn penalty as attempts increase</span>
                  </div>
                </div>
              </div>

              {/* Three Decisions */}
              <div className="flex items-center gap-4 text-xs font-mono">
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-300">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> ACT: Positive Net Lift
                </div>
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/40 text-amber-300">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> WAIT: Await Natural Settle
                </div>
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 border border-rose-500/40 text-rose-300">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-400" /> ABSTAIN: Negative ROI
                </div>
              </div>
            </div>
          )}

          {/* SCENE 3: THE RECOVERY MARKET AUCTION (1:45 - 2:45) */}
          {activeScene.id === 3 && (
            <div className="w-full h-full flex flex-col md:flex-row items-center justify-between gap-8 animate-fadeIn">
              <div className="w-full md:w-1/2 space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono">
                  <Layers size={14} /> PORTFOLIO KNAPSACK ALLOCATOR
                </div>
                <h2 className="text-2xl md:text-4xl font-bold text-white leading-tight">
                  Constrained Capacity & <br/><span className="text-amber-400">Marginal Shadow Price (λ)</span>
                </h2>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Recovery capacity is scarce. ULTRON ranks all failed payments by IVEN under an explicit capacity cap (e.g. 5 payment links). The marginal accepted payment sets the **Shadow Price λ**.
                </p>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="p-4 rounded-xl bg-slate-900 border border-amber-500/30 font-mono">
                    <span className="text-xs text-slate-400 block mb-1">SHADOW PRICE (λ)</span>
                    <span className="text-2xl font-bold text-amber-400">₹{shadowPrice.toFixed(2)}</span>
                    <span className="text-[10px] text-slate-500 block mt-1">Marginal acceptance bar</span>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-900 border border-emerald-500/30 font-mono">
                    <span className="text-xs text-slate-400 block mb-1">ANTI-BLAST SAVINGS</span>
                    <span className="text-2xl font-bold text-emerald-400">+₹{savedFees.toFixed(2)}</span>
                    <span className="text-[10px] text-slate-500 block mt-1">Saved from inaction</span>
                  </div>
                </div>
              </div>

              {/* Right Column: Live Ranked Opportunities */}
              <div className="w-full md:w-1/2 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 font-mono text-xs space-y-2">
                <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-slate-800 text-[11px]">
                  <span>RANK & OPPORTUNITY</span>
                  <span>IVEN YIELD</span>
                  <span>DECISION</span>
                </div>

                {/* Opp 1 */}
                <div className="flex items-center justify-between p-2 rounded bg-emerald-500/10 border border-emerald-500/30 text-slate-200">
                  <div>
                    <span className="text-emerald-400 font-bold mr-2">#1</span>
                    <span>Corp License (₹25,000)</span>
                  </div>
                  <span className="text-emerald-400 font-bold">+₹6,996</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">ACT</span>
                </div>

                {/* Opp 2 */}
                <div className="flex items-center justify-between p-2 rounded bg-emerald-500/10 border border-emerald-500/30 text-slate-200">
                  <div>
                    <span className="text-emerald-400 font-bold mr-2">#2</span>
                    <span>SaaS Annual (₹15,000)</span>
                  </div>
                  <span className="text-emerald-400 font-bold">+₹3,296</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">ACT</span>
                </div>

                {/* Opp 3 */}
                <div className="flex items-center justify-between p-2 rounded bg-emerald-500/10 border border-emerald-500/30 text-slate-200">
                  <div>
                    <span className="text-emerald-400 font-bold mr-2">#3</span>
                    <span>Pro Subscription (₹4,999)</span>
                  </div>
                  <span className="text-emerald-400 font-bold">+₹842</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">ACT</span>
                </div>

                {/* Capacity Threshold Line */}
                <div className="flex items-center gap-2 py-1">
                  <div className="flex-1 h-px bg-amber-400/50" />
                  <span className="text-[10px] text-amber-400 font-bold">CAPACITY CEILING (K = 5) · λ = ₹{shadowPrice.toFixed(2)}</span>
                  <div className="flex-1 h-px bg-amber-400/50" />
                </div>

                {/* Opp 4 - WAIT */}
                <div className="flex items-center justify-between p-2 rounded bg-amber-500/5 border border-amber-500/20 text-slate-400">
                  <div>
                    <span className="text-amber-400 mr-2">#6</span>
                    <span>Insufficient Funds #3 (₹1,800)</span>
                  </div>
                  <span className="text-amber-400 font-medium">+₹14.20</span>
                  <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px]">WAIT</span>
                </div>

                {/* Opp 5 - ABSTAIN */}
                <div className="flex items-center justify-between p-2 rounded bg-rose-500/5 border border-rose-500/20 text-slate-400">
                  <div>
                    <span className="text-rose-400 mr-2">#7</span>
                    <span>Stolen Card (₹4,500)</span>
                  </div>
                  <span className="text-rose-400 font-medium">−₹4.00</span>
                  <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px]">ABSTAIN</span>
                </div>
              </div>
            </div>
          )}

          {/* SCENE 4: ACTION AUTHORITY COMPLIANCE VETO (2:45 - 3:45) */}
          {activeScene.id === 4 && (
            <div className="w-full h-full flex flex-col items-center justify-center space-y-6 animate-fadeIn">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono">
                <Lock size={14} /> DETERMINISTIC TWO-STAGE FIREWALL
              </div>

              <div className="text-center space-y-2">
                <h2 className="text-3xl md:text-5xl font-bold text-white">
                  Action Authority: <span className="text-rose-400">The Compliance Veto</span>
                </h2>
                <p className="text-sm md:text-base text-slate-300 max-w-2xl font-light">
                  Economic merit alone does NOT grant permission to act. Compliance can veto an ACT decision with zero appeal to economics.
                </p>
              </div>

              {/* 5-Check Laser Scanner Visual */}
              <div className="w-full max-w-4xl bg-slate-900/90 border border-slate-800 rounded-2xl p-6 font-mono relative overflow-hidden">
                <div className="laser-scanner" />
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/40 text-center">
                    <span className="text-rose-400 font-bold block mb-1">CHECK 1</span>
                    <span className="text-slate-300 block mb-2">Hard Decline?</span>
                    <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-bold">VETOED 🔴</span>
                  </div>
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-center">
                    <span className="text-emerald-400 font-bold block mb-1">CHECK 2</span>
                    <span className="text-slate-300 block mb-2">Retry Cap &lt; 3</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">PASSED ✅</span>
                  </div>
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-center">
                    <span className="text-emerald-400 font-bold block mb-1">CHECK 3</span>
                    <span className="text-slate-300 block mb-2">Kill Switch OFF</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">PASSED ✅</span>
                  </div>
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-center">
                    <span className="text-emerald-400 font-bold block mb-1">CHECK 4</span>
                    <span className="text-slate-300 block mb-2">Confidence Check</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">PASSED ✅</span>
                  </div>
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-center">
                    <span className="text-emerald-400 font-bold block mb-1">CHECK 5</span>
                    <span className="text-slate-300 block mb-2">Capacity Quota</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">PASSED ✅</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                  <span>Non-Negotiable Rule #6:</span>
                  <span className="text-amber-400 font-bold">NO LLM SITS ON THE FINANCIAL EXECUTION PATH</span>
                </div>
              </div>
            </div>
          )}

          {/* SCENE 5: STRATEGIC POSITIONING (3:45 - 4:30) */}
          {activeScene.id === 5 && (
            <div className="w-full h-full flex flex-col items-center justify-center space-y-6 animate-fadeIn">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
                <Activity size={14} /> 2026 AI FINTECH LANDSCAPE
              </div>

              <div className="text-center space-y-1">
                <h2 className="text-2xl md:text-4xl font-bold text-white">
                  Strategic Positioning: <span className="text-cyan-400">The 3-Tier Enterprise Stack</span>
                </h2>
                <p className="text-xs md:text-sm text-slate-300 font-light">
                  How Razorpay Vulcan, Agent Studio, and ULTRON coexist in harmony
                </p>
              </div>

              {/* 3 Pillars Grid */}
              <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
                {/* Vulcan */}
                <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
                  <div>
                    <span className="text-slate-400 text-[10px] uppercase block mb-1">IN-FLIGHT DECISION</span>
                    <h3 className="text-base font-bold text-white mb-2">Razorpay Vulcan</h3>
                    <p className="text-slate-400 text-[11px] leading-relaxed">
                      Set transformer foundation model. Scores 3,000 signals to pick the best banking rail at checkout.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-cyan-400">
                    &ldquo;Can we authorize this?&rdquo;
                  </div>
                </div>

                {/* ULTRON */}
                <div className="p-5 rounded-2xl bg-cyan-950/40 border border-cyan-500/50 shadow-lg shadow-cyan-500/10 flex flex-col justify-between">
                  <div>
                    <span className="text-emerald-400 text-[10px] uppercase font-bold block mb-1">POST-FAILURE CONTROL</span>
                    <h3 className="text-base font-bold text-white mb-2">🛡️ ULTRON</h3>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      Autonomous economic control plane. Governs scarce recovery capacity, incremental lift ($IVEN$), and deterministic compliance.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-cyan-800/60 text-[11px] text-emerald-400 font-bold">
                    &ldquo;Is it worth acting?&rdquo;
                  </div>
                </div>

                {/* Agent Studio */}
                <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
                  <div>
                    <span className="text-slate-400 text-[10px] uppercase block mb-1">BACK-OFFICE WORKFLOWS</span>
                    <h3 className="text-base font-bold text-white mb-2">Agent Studio</h3>
                    <p className="text-slate-400 text-[11px] leading-relaxed">
                      Claude Agent SDK automation. Generates chargeback dispute packets and bank statement matching.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-purple-400">
                    &ldquo;Automate my back-office&rdquo;
                  </div>
                </div>
              </div>

              {/* Dual Mode Switcher Demo */}
              <div className="flex items-center gap-3 p-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono">
                <span className="text-slate-400">ENVIRONMENT ISOLATION:</span>
                <button 
                  onClick={() => setActiveTab("test")}
                  className={`px-3 py-1 rounded-lg transition ${activeTab === "test" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" : "text-slate-400"}`}
                >
                  🧪 Test Sandbox (5 Link Cap)
                </button>
                <button 
                  onClick={() => setActiveTab("live")}
                  className={`px-3 py-1 rounded-lg transition ${activeTab === "live" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" : "text-slate-400"}`}
                >
                  ⚡ Real Money Live (AES-256 Vault)
                </button>
              </div>
            </div>
          )}

          {/* SCENE 6: FORENSIC TRUTH ENGINE & FINALE (4:30 - 5:00) */}
          {activeScene.id === 6 && (
            <div className="w-full h-full flex flex-col items-center justify-center text-center space-y-6 animate-fadeIn">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
                <CheckCircle2 size={14} /> FORENSIC VERIFICATION ARTIFACT
              </div>

              <h2 className="text-3xl md:text-5xl font-black text-white">
                The Truth Engine: <span className="text-emerald-400">Provider Truth First</span>
              </h2>

              {/* Hash Chain Block Visual */}
              <div className="flex items-center gap-3 font-mono text-xs max-w-2xl w-full justify-center">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-left flex-1">
                  <span className="text-[10px] text-slate-500 block">GENESIS BLOCK</span>
                  <span className="text-cyan-400 font-bold block truncate">0x0000...0000</span>
                  <span className="text-slate-400 text-[10px]">webhook_received</span>
                </div>
                <ArrowRight size={16} className="text-slate-600" />
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-left flex-1">
                  <span className="text-[10px] text-slate-500 block">RECONCILED BLOCK</span>
                  <span className="text-emerald-400 font-bold block truncate">0x3a4b...8172</span>
                  <span className="text-slate-400 text-[10px]">provider_truth</span>
                </div>
                <ArrowRight size={16} className="text-slate-600" />
                <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/50 text-left flex-1">
                  <span className="text-[10px] text-emerald-400 block font-bold">DOUBLE-ENTRY LEDGER</span>
                  <span className="text-white font-bold block">₹25,000 SETTLED</span>
                  <span className="text-emerald-300 text-[10px]">SHA-256 Chained</span>
                </div>
              </div>

              {/* Terminal Pass Readout */}
              <div className="w-full max-w-md bg-slate-950 border border-slate-800 rounded-xl p-3 font-mono text-[11px] text-left text-slate-400 flex items-center gap-3">
                <Terminal size={16} className="text-emerald-400 shrink-0" />
                <div>
                  <span className="text-emerald-400 font-bold">165 TEST SCRIPTS PASSED (100%)</span>
                  <span className="block text-[10px] text-slate-500">27 V6 Suites · 28 Agent Boundary Tests · 0 Failures</span>
                </div>
              </div>

              {/* Live URL Call to Action */}
              <div className="pt-2">
                <a 
                  href="https://ultron-power.vercel.app/dashboard"
                  target="_blank"
                  className="inline-flex items-center gap-2 px-8 py-3 rounded-xl bg-emerald-500 text-slate-950 font-bold font-mono text-sm hover:bg-emerald-400 transition shadow-lg shadow-emerald-500/20"
                >
                  EXPLORE LIVE: ultron-power.vercel.app <ArrowRight size={16} />
                </a>
              </div>
            </div>
          )}

        </div>

        {/* ==================================================================== */}
        {/* TELEPROMPTER SUBTITLES STRIP (Karaoke Live Narration Bar)             */}
        {/* ==================================================================== */}
        <div className="relative z-10 w-full px-8 py-3 bg-slate-950/80 border-t border-slate-800/60 backdrop-blur-md flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-3 overflow-hidden text-ellipsis">
            <span className="text-cyan-400 font-bold shrink-0">SCRIPT CUE:</span>
            <span className="text-slate-300 truncate">{activeScene.script}</span>
          </div>
          <span className="text-slate-500 text-[11px] shrink-0 font-mono">
            {activeScene.startSec}s - {activeScene.endSec}s
          </span>
        </div>
      </main>

      {/* ==================================================================== */}
      {/* CINEMA DECK CONTROLS (Playback, Scrubbing, Scene Buttons)            */}
      {/* ==================================================================== */}
      <footer className="w-full max-w-6xl mt-6 flex flex-col gap-4">
        {/* Scrubber Bar */}
        <div className="flex items-center gap-4">
          <span className="text-xs font-mono text-slate-400">{formatTime(currentSec)}</span>
          <input
            type="range"
            min={0}
            max={300}
            value={currentSec}
            onChange={(e) => setCurrentSec(Number(e.target.value))}
            className="flex-1 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />
          <span className="text-xs font-mono text-slate-400">05:00</span>
        </div>

        {/* Action Controls & Scene Jump Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 text-slate-950 font-bold font-mono text-xs hover:bg-cyan-400 transition"
            >
              {isPlaying ? <Pause size={14} /> : <Play size={14} />}
              {isPlaying ? "PAUSE" : "START PRESENTATION"}
            </button>

            <button
              onClick={() => {
                setCurrentSec(0);
                setIsPlaying(false);
                playTone(300, "sine", 0.1);
              }}
              className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
              title="Restart"
            >
              <RotateCcw size={14} />
            </button>

            <button
              onClick={() => setPlaybackSpeed(playbackSpeed === 1 ? 1.5 : playbackSpeed === 1.5 ? 2 : 1)}
              className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white font-mono text-xs transition"
            >
              {playbackSpeed}x SPEED
            </button>

            <button
              onClick={() => setSfxEnabled(!sfxEnabled)}
              className={`px-3 py-2 rounded-xl border font-mono text-xs transition ${
                sfxEnabled ? "bg-slate-900 border-cyan-500/40 text-cyan-400" : "bg-slate-900 border-slate-800 text-slate-500"
              }`}
            >
              SFX: {sfxEnabled ? "ON" : "OFF"}
            </button>
          </div>

          {/* Jump to Specific Scenes */}
          <div className="flex items-center gap-1.5 overflow-x-auto hud-scroll pb-1">
            {PITCH_SCENES.map((scene) => {
              const isCurrent = activeScene.id === scene.id;
              return (
                <button
                  key={scene.id}
                  onClick={() => jumpToScene(scene.startSec)}
                  className={`px-2.5 py-1.5 rounded-lg text-[11px] font-mono whitespace-nowrap transition border ${
                    isCurrent
                      ? "bg-cyan-500/20 border-cyan-500 text-cyan-300 font-bold"
                      : "bg-slate-900/60 border-slate-800/80 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  {scene.id}. {scene.title.split(":")[0]}
                </button>
              );
            })}
          </div>
        </div>
      </footer>
    </div>
  );
}
