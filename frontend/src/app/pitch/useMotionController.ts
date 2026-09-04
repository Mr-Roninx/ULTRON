"use client";

import { useState, useEffect, useRef, useCallback } from "react";

export interface ActDefinition {
  id: number;
  name: string;
  start: number;
  end: number;
  tag: string;
  title: string;
  subtitle: string;
  narrative: string;
}

export const MOTION_ACTS: ActDefinition[] = [
  {
    id: 1,
    name: "The $68B Blindspot",
    start: 0,
    end: 50,
    tag: "Act 1 • The Problem Space (00:00 - 00:50)",
    title: "The $68 Billion Payment Blindspot",
    subtitle: "Why standard retry schedulers burn money on transient errors and blindly blast unrecoverable transactions.",
    narrative: "Every year, over sixty-eight billion dollars in checkout payments vanish into payment gateway declines. Traditional systems respond with blind retries and dunning blasts. But here is the fatal blindspot: up to sixty percent of soft bank timeouts self-heal naturally within two hours. Naive retries take false credit, spam frustrated customers, and waste four rupees on every unneeded payment link.",
  },
  {
    id: 2,
    name: "The Paradigm Shift",
    start: 50,
    end: 100,
    tag: "Act 2 • Economic Reasoning (00:50 - 01:40)",
    title: "The Paradigm Shift: Incremental Value (IVEN)",
    subtitle: "Scoring opportunities not by raw probability, but by true counterfactual incrementality minus operational and fatigue costs.",
    narrative: "ULTRON changes the question completely. We do not ask: can we retry this payment? We ask: is recovering this payment worth spending our next unit of scarce recovery capacity? We calculate the Expected Incremental Value Net: IVEN equals delta P times amount, minus link fees, minus non-linear customer contact fatigue penalties. Hard declines are strictly bounded at zero incremental lift.",
  },
  {
    id: 3,
    name: "7-Stage Machine",
    start: 100,
    end: 150,
    tag: "Act 3 • System Pipeline (01:40 - 02:30)",
    title: "Inside the 7-Stage Deterministic Machine",
    subtitle: "From zero-code drop-in client interception to double-entry ledger truth, without an LLM on the execution path.",
    narrative: "Every failure event enters a strict seven-stage deterministic pipeline. Ingestion verifies HMAC webhooks and drops in via ultron dot js. Perception normalizes codes into hard or soft taxonomy. Economics updates Bayesian Beta posteriors. Market Allocation packs the knapsack. Action Authority runs five veto gates. Resilient Execution creates links with strict circuit-breaker idempotency. And the Truth Engine reconciles bank truth.",
  },
  {
    id: 4,
    name: "The Decision Triad",
    start: 150,
    end: 200,
    tag: "Act 4 • Portfolio Allocation (02:30 - 03:20)",
    title: "The Decision Triad & The Shadow Price (λ)",
    subtitle: "Portfolio-level greedy allocation under capacity constraint K=5, establishing the market equilibrium marginal price.",
    narrative: "Recovery is never all or nothing. Every opportunity resolves into exactly one state of the Decision Triad: ACT, WAIT, or ABSTAIN. Under a test-mode capacity limit of five links, opportunities compete in a greedy knapsack sorted by IVEN. The fifth accepted opportunity sets the market shadow price lambda, currently twenty-three rupees ninety-six paise. Deferred transactions wait for capacity, while negative IVEN items rationally abstain.",
  },
  {
    id: 5,
    name: "Action Authority",
    start: 200,
    end: 250,
    tag: "Act 5 • Compliance Gate (03:20 - 04:10)",
    title: "Action Authority: The Deterministic Veto",
    subtitle: "Independent two-stage compliance barrier that stops economic greed from violating fraud rules or retry caps.",
    narrative: "Crucially, economic value never bypasses compliance. Action Authority is a decoupled deterministic gate with unconditional veto power. It evaluates five rules: hard decline check, three-attempt retry cap, emergency kill switch, confidence recheck, and capacity recheck. Even a high-value stolen card with fifty thousand rupees is stopped dead at Gate 1, returning an immutable BLOCKED verdict.",
  },
  {
    id: 6,
    name: "Causal Truth & Impact",
    start: 250,
    end: 300,
    tag: "Act 6 • Causal Truth & ROI (04:10 - 05:00)",
    title: "Causal Truth, Cryptographic Ledger & ROI",
    subtitle: "Proving twenty-two percent net recovered GMV via five percent holdout paired Student t-tests and SHA-256 chained accounting.",
    narrative: "Our cardinal rule: link created is never recovered. Settlement is recognized only when the bank confirms funds paid. Every penny is recorded in an immutable SHA-256 chained double-entry ledger. And with a continuous five percent holdout control group, paired Student t-tests prove a verified twenty-two percent net revenue recovery lift while cutting wasted messaging costs by sixty-four percent.",
  },
];

export function useMotionController() {
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [activeActIndex, setActiveActIndex] = useState<number>(0);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(performance.now());
  const synthRef = useRef<SpeechSynthesis | null>(null);

  // Audio tone synthesizer
  const playTone = useCallback((freq: number, type: OscillatorType = "sine", duration: number = 0.15, gainVal: number = 0.05) => {
    if (isMuted || typeof window === "undefined") return;
    try {
      if (!audioCtxRef.current) {
        const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        if (AudioContextClass) audioCtxRef.current = new AudioContextClass();
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
      // AudioContext unavailable
    }
  }, [isMuted]);

  // Speech narration
  const speakNarrative = useCallback((actIndex: number) => {
    if (isMuted || typeof window === "undefined") return;
    try {
      if (!synthRef.current && window.speechSynthesis) {
        synthRef.current = window.speechSynthesis;
      }
      const synth = synthRef.current;
      if (!synth) return;

      synth.cancel();
      const act = MOTION_ACTS[actIndex];
      if (!act) return;

      const utter = new SpeechSynthesisUtterance(act.narrative);
      utter.rate = 1.05;
      utter.pitch = 1.0;
      utter.volume = isMuted ? 0 : 0.9;

      const voices = synth.getVoices();
      const englishVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Samantha")));
      if (englishVoice) utter.voice = englishVoice;

      synth.speak(utter);
    } catch {
      // Speech synthesis error
    }
  }, [isMuted]);

  const setTime = useCallback((time: number) => {
    const clamped = Math.max(0, Math.min(300, time));
    setCurrentTime(clamped);

    const actIdx = MOTION_ACTS.findIndex(a => clamped >= a.start && clamped < a.end);
    const targetIdx = actIdx === -1 ? MOTION_ACTS.length - 1 : actIdx;

    if (targetIdx !== activeActIndex) {
      setActiveActIndex(targetIdx);
      speakNarrative(targetIdx);
      playTone(523.25, "sine", 0.1, 0.04);
    }
  }, [activeActIndex, playTone, speakNarrative]);

  const togglePlay = useCallback(() => {
    setIsPlaying(prev => {
      const next = !prev;
      if (next) {
        speakNarrative(activeActIndex);
        playTone(440, "sine", 0.1, 0.04);
      } else {
        if (synthRef.current) synthRef.current.pause();
        playTone(330, "sine", 0.1, 0.04);
      }
      return next;
    });
  }, [activeActIndex, playTone, speakNarrative]);

  const toggleMute = useCallback(() => {
    setIsMuted(prev => {
      const next = !prev;
      if (next && synthRef.current) {
        synthRef.current.cancel();
      } else if (!next) {
        speakNarrative(activeActIndex);
      }
      return next;
    });
  }, [activeActIndex, speakNarrative]);

  const seekRelative = useCallback((seconds: number) => {
    setTime(currentTime + seconds);
    playTone(550, "sine", 0.08, 0.03);
  }, [currentTime, playTone, setTime]);

  const jumpToAct = useCallback((actIndex: number) => {
    if (actIndex >= 0 && actIndex < MOTION_ACTS.length) {
      setTime(MOTION_ACTS[actIndex].start);
      playTone(659.25, "sine", 0.12, 0.04);
    }
  }, [playTone, setTime]);

  const restart = useCallback(() => {
    setTime(0);
    playTone(600, "triangle", 0.15, 0.05);
  }, [playTone, setTime]);

  // Master animation tick loop
  useEffect(() => {
    lastTimeRef.current = performance.now();

    const loop = (timestamp: number) => {
      const delta = (timestamp - lastTimeRef.current) / 1000;
      lastTimeRef.current = timestamp;

      if (isPlaying) {
        setCurrentTime(t => {
          const nextTime = t + delta;
          if (nextTime >= 300) {
            setIsPlaying(false);
            return 300;
          }
          const actIdx = MOTION_ACTS.findIndex(a => nextTime >= a.start && nextTime < a.end);
          const targetIdx = actIdx === -1 ? MOTION_ACTS.length - 1 : actIdx;
          if (targetIdx !== activeActIndex) {
            setActiveActIndex(targetIdx);
            speakNarrative(targetIdx);
          }
          return nextTime;
        });
      }
      animFrameRef.current = requestAnimationFrame(loop);
    };

    animFrameRef.current = requestAnimationFrame(loop);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isPlaying, activeActIndex, speakNarrative]);

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        e.preventDefault();
        togglePlay();
      } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        seekRelative(-10);
      } else if (e.code === "ArrowRight") {
        e.preventDefault();
        seekRelative(10);
      } else if (["Digit1", "Digit2", "Digit3", "Digit4", "Digit5", "Digit6"].includes(e.code)) {
        e.preventDefault();
        const num = parseInt(e.code.replace("Digit", ""), 10) - 1;
        jumpToAct(num);
      } else if (e.code === "KeyR") {
        e.preventDefault();
        restart();
      } else if (e.code === "KeyM") {
        e.preventDefault();
        toggleMute();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [jumpToAct, restart, seekRelative, toggleMute, togglePlay]);

  return {
    currentTime,
    isPlaying,
    isMuted,
    activeActIndex,
    currentAct: MOTION_ACTS[activeActIndex],
    setTime,
    togglePlay,
    toggleMute,
    seekRelative,
    jumpToAct,
    restart,
  };
}
