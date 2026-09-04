"use client";

import React, { useEffect, useRef, useState, useMemo, useCallback } from "react";
import Link from "next/link";
import {
  Shield,
  ArrowRight,
  Play,
  Pause,
  Check,
  X,
  AlertTriangle,
  Zap,
  Activity,
  Lock,
  Volume2,
  VolumeX,
  Maximize2,
  Minimize2,
  FileText,
} from "lucide-react";
import "./presentation.css";

/* ═══════════════════════════════════════════════════════════════════════════
   NARRATION SCRIPTS — CEO KEYNOTE VOICE (COMBINED TOTAL: 4m 45s / 285s)
   Proud. Bold. Clear. Short punchy sentences. Deliberate pauses.
   ═══════════════════════════════════════════════════════════════════════════ */

export const TOTAL_KEYNOTE_SECONDS = 285; // Exactly 4 minutes 45 seconds

export const SLIDE_TIMINGS = [
  { id: "hook",         title: "01 / The Hook",             duration: 33, range: "00:00 - 00:33", targetWords: 68 },
  { id: "problem",      title: "02 / The Problem",          duration: 35, range: "00:34 - 01:09", targetWords: 68 },
  { id: "solution",     title: "03 / The Solution",         duration: 37, range: "01:10 - 01:47", targetWords: 67 },
  { id: "architecture", title: "04 / Architecture",         duration: 37, range: "01:48 - 02:25", targetWords: 69 },
  { id: "innovation",   title: "05 / Innovation",           duration: 34, range: "02:26 - 03:00", targetWords: 63 },
  { id: "ai-boundary",  title: "06 / LLM vs Determinism",   duration: 37, range: "03:01 - 03:38", targetWords: 71 },
  { id: "razorpay",     title: "07 / Razorpay Integration", duration: 35, range: "03:39 - 04:14", targetWords: 63 },
  { id: "conclusion",   title: "08 / Conclusion",           duration: 37, range: "04:15 - 04:45", targetWords: 68 },
];

const NARRATIONS: string[] = [
  // 01 — HOOK (00:00 - 00:33 | 33s)
  `Here is a number that should make every payment leader in this room uncomfortable: twenty-seven percent. That is the exact share of recovered payments that were going to come back on their own. Today, systems fire links blindly, burning four rupees per attempt and destroying customer trust for money already coming home. We built ULTRON to answer one question: is this payment worth chasing with your next unit of limited recovery capacity?`,

  // 02 — PROBLEM (00:34 - 01:09 | 35s)
  `Let me show you what the industry hides behind failed payments: three massive invisible costs. First, operational spend: four rupees burned per link, whether the customer pays or not. Second, exponential customer fatigue: the fourth retry costs six times the second in brand damage. And third, counterfactual waste: spending real money to recover revenue that was already yours. Current retry logic is not recovery. It is waste disguised as action.`,

  // 03 — SOLUTION (01:10 - 01:47 | 37s)
  `So we built something fundamentally different: ULTRON, an autonomous economic control plane. Every failed payment becomes a Recovery Opportunity competing for scarce capacity. Every opportunity resolves to exactly one of three deterministic decisions. Act: fire the link when incremental value exceeds cost. Wait: defer when capacity is saturated. Or Abstain: do nothing. In ULTRON, abstaining is not a failure. Abstaining is the core feature that stops value destruction.`,

  // 04 — ARCHITECTURE (01:48 - 02:25 | 37s)
  `Inside ULTRON, seven deterministic stages execute without a single black box. We intercept and deduplicate the webhook, perceive the decline type, and compute counterfactual delta scoring in exact integer paise. Next, our portfolio auction clears under a hard cap of five links per run, exposing the shadow price cutoff. Five compliance vetoes inspect fraud and velocity before triggering Razorpay APIs and appending to an immutable SHA-256 ledger. Seven stages. Zero guesswork.`,

  // 05 — INNOVATION (02:26 - 03:00 | 34s)
  `Three breakthroughs separate ULTRON from every retry tool in fintech. First, incremental probability: we only act when our intervention meaningfully beats natural recovery. Second, shadow pricing: we expose the exact rupee threshold where additional attempts destroy portfolio value. And third, two-stage governance: economics proposes the opportunity, but compliance holds absolute veto power. We never force an action just because a probability is positive.`,

  // 06 — LLM VS DETERMINISM (03:01 - 03:38 | 37s)
  `Here is our fundamental architectural law: zero LLMs on the financial execution path. When moving money, hallucinations are fatal. That is why IVEN math, portfolio clearing, five compliance vetoes, and Razorpay payment links are one hundred percent deterministic TypeScript. What does our LLM do? NVIDIA's Nemotron-3.5 operates strictly as a read-only forensic explainer, translating audit logs into plain English for merchants and Razorpay Agent Studio. Zero execution privileges. Decoupled by design.`,

  // 07 — RAZORPAY INTEGRATION (03:39 - 04:14 | 35s)
  `ULTRON does not compete with Razorpay's AI stack. It completes it. We form a unified AI triad. Razorpay Vulcan optimizes in-flight routing at checkout across three thousand signals. When routing fails, ULTRON takes over post-settlement recovery with deterministic economics and Nemotron forensic explainability. Finally, Razorpay Agent Studio, powered by Claude, consumes ULTRON's audit records for merchant operations. Three frontier models, one seamless payment lifecycle.`,

  // 08 — CONCLUSION (04:15 - 04:45 | 37s)
  `Let me leave you with this: ULTRON is not another retry bot. It is an economic control plane. Every decision grounded in counterfactual math. Every action verified by deterministic compliance. Every outcome recorded in an immutable ledger. Stop asking if a payment can be recovered. The only question that matters is: is it worth your scarce capacity? That system is ULTRON. And we are proud to launch it. Thank you.`,
];

/* ═══════════════════════════════════════════════════════════════════════════
   SLIDE CONFIG
   ═══════════════════════════════════════════════════════════════════════════ */

const SLIDES = [
  { id: "hook",        stage: "01 / 08", category: "The Hook",              navTitle: "Hook" },
  { id: "problem",     stage: "02 / 08", category: "The Problem",           navTitle: "Problem" },
  { id: "solution",    stage: "03 / 08", category: "The Solution",          navTitle: "Solution" },
  { id: "architecture",stage: "04 / 08", category: "Architecture",          navTitle: "Architecture" },
  { id: "innovation",  stage: "05 / 08", category: "Innovation",            navTitle: "Innovation" },
  { id: "ai-boundary", stage: "06 / 08", category: "LLM vs Determinism",    navTitle: "AI Boundary" },
  { id: "razorpay",    stage: "07 / 08", category: "Razorpay Integration",  navTitle: "Razorpay Fit" },
  { id: "conclusion",  stage: "08 / 08", category: "Conclusion",            navTitle: "Conclusion" },
];

/* ── Female Voice Detection Helpers ── */
const FEMALE_VOICE_KEYWORDS = [
  "zira",
  "jenny",
  "aria",
  "samantha",
  "victoria",
  "karen",
  "neerja",
  "sonia",
  "hazel",
  "susan",
  "ava",
  "allison",
  "serena",
  "fiona",
  "clara",
  "uk english female",
  "female",
  "woman",
  "girl",
];

const MALE_VOICE_KEYWORDS = [
  "david",
  "mark",
  "george",
  "james",
  "guy",
  "richard",
  "ravi",
  "google us english",
  "male",
];

function isFemaleVoice(v: SpeechSynthesisVoice): boolean {
  const name = v.name.toLowerCase();
  if (MALE_VOICE_KEYWORDS.some((kw) => name.includes(kw))) return false;
  return FEMALE_VOICE_KEYWORDS.some((kw) => name.includes(kw));
}

function findBestFemaleVoice(voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice | null {
  if (!voices || voices.length === 0) return null;
  const enVoices = voices.filter((v) => v.lang.toLowerCase().startsWith("en"));

  // 1. English voice matching female keywords
  for (const kw of FEMALE_VOICE_KEYWORDS) {
    const found = enVoices.find((v) => v.name.toLowerCase().includes(kw));
    if (found) return found;
  }
  // 2. Any language matching female keywords
  for (const kw of FEMALE_VOICE_KEYWORDS) {
    const found = voices.find((v) => v.name.toLowerCase().includes(kw));
    if (found) return found;
  }
  // 3. Any English voice that does not explicitly match male keywords
  const nonMale = enVoices.find(
    (v) => !MALE_VOICE_KEYWORDS.some((kw) => v.name.toLowerCase().includes(kw))
  );
  if (nonMale) return nonMale;

  return enVoices[0] || voices[0] || null;
}

function cleanVoiceLabel(name: string): string {
  return name
    .replace(/^Microsoft\s+/i, "")
    .replace(/\s+Desktop\s*/i, "")
    .replace(/\s+Online\s+\(Natural\)\s*/i, " Natural ")
    .replace(/\s*-\s*English.*$/i, "")
    .replace(/\s*\(.*?\)\s*/g, "")
    .trim();
}

/* ═══════════════════════════════════════════════════════════════════════════
   COMPONENT
   ═══════════════════════════════════════════════════════════════════════════ */

export default function LuxuryFintechPresentationPage() {
  const [active, setActive] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [progress, setProgress] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [showScriptModal, setShowScriptModal] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoiceName, setSelectedVoiceName] = useState<string>("");
  const slideRefs = useRef<(HTMLElement | null)[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const elapsedTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const synthRef = useRef<SpeechSynthesisUtterance | null>(null);
  const keepAliveRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [gate, setGate] = useState<"ok" | "hard" | "cap" | "kill">("ok");
  const [isFullscreen, setIsFullscreen] = useState(false);
  const speechDoneRef = useRef(false);
  const advanceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /* ── Preload & monitor available voices for female CEO voice ── */
  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;

    const initVoices = () => {
      const list = window.speechSynthesis.getVoices();
      if (list && list.length > 0) {
        setVoices(list);
        setSelectedVoiceName((curr) => {
          if (curr && list.some((v) => v.name === curr)) return curr;
          const best = findBestFemaleVoice(list);
          return best ? best.name : list[0]?.name || "";
        });
      }
    };

    initVoices();
    window.speechSynthesis.onvoiceschanged = initVoices;
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, []);

  const femaleVoiceList = useMemo(() => {
    const females = voices.filter(isFemaleVoice);
    if (females.length > 0) return females;
    const en = voices.filter((v) => v.lang.toLowerCase().startsWith("en"));
    return en.length > 0 ? en : voices;
  }, [voices]);

  /* ── Master Keynote 4m 45s Timer ── */
  useEffect(() => {
    if (playing) {
      elapsedTimerRef.current = setInterval(() => {
        setElapsedSeconds((prev) => {
          if (prev >= TOTAL_KEYNOTE_SECONDS) {
            return TOTAL_KEYNOTE_SECONDS;
          }
          return prev + 1;
        });
      }, 1000);
    } else {
      if (elapsedTimerRef.current) {
        clearInterval(elapsedTimerRef.current);
        elapsedTimerRef.current = null;
      }
    }
    return () => {
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    };
  }, [playing]);

  /* ── Fullscreen toggle ── */
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().then(() => setIsFullscreen(true)).catch(() => {});
    } else {
      document.exitFullscreen().then(() => setIsFullscreen(false)).catch(() => {});
    }
  }, []);

  useEffect(() => {
    const handler = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", handler);
    return () => document.removeEventListener("fullscreenchange", handler);
  }, []);

  /* ── Scroll Observer ── */
  useEffect(() => {
    const obs: IntersectionObserver[] = [];
    slideRefs.current.forEach((el, i) => {
      if (!el) return;
      const o = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              el.classList.add("is-visible");
              if (!playing) setActive(i);
            }
          });
        },
        { threshold: 0.2 }
      );
      o.observe(el);
      obs.push(o);
    });
    return () => obs.forEach((o) => o.disconnect());
  }, [playing]);

  /* ── Navigate to slide ── */
  const goTo = useCallback((i: number) => {
    const el = slideRefs.current[i];
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      setActive(i);
      setProgress(0);
      const startOffset = SLIDE_TIMINGS.slice(0, i).reduce((acc, curr) => acc + curr.duration, 0);
      setElapsedSeconds(startOffset);
    }
  }, []);

  /* ── Stop speech ── */
  const stopSpeech = useCallback(() => {
    if (keepAliveRef.current) {
      clearInterval(keepAliveRef.current);
      keepAliveRef.current = null;
    }
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setSpeaking(false);
  }, []);

  /* ── Speak narration (calls onEnd when speech finishes) ── */
  const speak = useCallback(
    (text: string, onEnd?: () => void) => {
      if (typeof window === "undefined" || !window.speechSynthesis) {
        onEnd?.();
        return;
      }
      stopSpeech();

      const utt = new SpeechSynthesisUtterance(text);
      utt.rate = 0.90;   // Confident, crisp CEO keynote pace
      utt.pitch = 1.15;  // Slightly elevated pitch for natural female voice timbre
      utt.volume = 1.0;

      const currentVoices = window.speechSynthesis.getVoices();
      let chosenVoice: SpeechSynthesisVoice | null = null;
      if (selectedVoiceName) {
        chosenVoice = currentVoices.find((v) => v.name === selectedVoiceName) || null;
      }
      if (!chosenVoice) {
        chosenVoice = findBestFemaleVoice(currentVoices);
      }
      if (chosenVoice) {
        utt.voice = chosenVoice;
      }

      utt.onstart = () => {
        setSpeaking(true);
        // Chromium keepalive heartbeat: keeps TTS engine alive past 15 seconds
        if (keepAliveRef.current) clearInterval(keepAliveRef.current);
        keepAliveRef.current = setInterval(() => {
          if (typeof window !== "undefined" && window.speechSynthesis && window.speechSynthesis.speaking) {
            window.speechSynthesis.pause();
            window.speechSynthesis.resume();
          }
        }, 8000);
      };

      const finish = () => {
        if (keepAliveRef.current) {
          clearInterval(keepAliveRef.current);
          keepAliveRef.current = null;
        }
        setSpeaking(false);
        onEnd?.();
      };

      utt.onend = finish;
      utt.onerror = finish;
      synthRef.current = utt;
      window.speechSynthesis.speak(utt);
    },
    [selectedVoiceName, stopSpeech]
  );

  /* ── Autoplay engine — SPEECH-DRIVEN (Combined 4m 45s flow) ── */
  useEffect(() => {
    if (!playing) {
      if (timerRef.current) clearInterval(timerRef.current);
      if (advanceTimeoutRef.current) clearTimeout(advanceTimeoutRef.current);
      stopSpeech();
      return;
    }

    speechDoneRef.current = false;
    const currentTiming = SLIDE_TIMINGS[active] || { duration: 35 };
    const estimatedMs = currentTiming.duration * 1000;

    // Start narration — when it finishes, wait 1s pause then advance smoothly
    speak(NARRATIONS[active], () => {
      speechDoneRef.current = true;
      advanceTimeoutRef.current = setTimeout(() => {
        const next = active + 1;
        if (next < SLIDES.length) {
          goTo(next);
          setActive(next);
        } else {
          setPlaying(false);
          setProgress(100);
          setElapsedSeconds(TOTAL_KEYNOTE_SECONDS);
        }
      }, 1000);
    });

    // Progress bar: smooth fill over estimated duration
    const tick = 400;
    const totalTicks = Math.ceil(estimatedMs / tick);
    let count = 0;

    timerRef.current = setInterval(() => {
      count++;
      const pct = Math.min((count / totalTicks) * 100, speechDoneRef.current ? 100 : 95);
      setProgress(pct);
      if (speechDoneRef.current) {
        setProgress(100);
        if (timerRef.current) clearInterval(timerRef.current);
      }
    }, tick);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (advanceTimeoutRef.current) clearTimeout(advanceTimeoutRef.current);
    };
  }, [playing, active, speak, stopSpeech, goTo]);

  /* ── Toggle autoplay ── */
  const togglePlay = useCallback(() => {
    if (playing) {
      setPlaying(false);
      stopSpeech();
      if (advanceTimeoutRef.current) clearTimeout(advanceTimeoutRef.current);
    } else {
      if (active >= SLIDES.length - 1) {
        goTo(0);
        setElapsedSeconds(0);
      }
      setPlaying(true);
      setProgress(0);
    }
  }, [playing, stopSpeech, active, goTo]);

  const headerProgress = ((active + 1) / SLIDES.length) * 100;

  const formatTimer = (totalSecs: number) => {
    const m = Math.floor(totalSecs / 60);
    const s = totalSecs % 60;
    return `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div className="deck-viewport">
      <div className="deck-3d-background" />
      <div className="deck-3d-scrim" />

      {/* ── HEADER ── */}
      <header className="deck-header">
        <div className="deck-progress-line">
          <div className="deck-progress-fill" style={{ width: `${headerProgress}%` }} />
        </div>
        <div className="deck-logo">
          <div className="deck-logo-badge"><Shield size={14} /></div>
          <div className="deck-logo-text">
            <span className="deck-logo-title">ULTRON</span>
            <span className="deck-logo-sub">Recovery Control Plane</span>
          </div>
        </div>
        <div className="deck-meta-center">
          <span className="deck-counter">{SLIDES[active].stage}</span>
          <span className="deck-stage-title">{SLIDES[active].category}</span>
          <div className={`deck-timer-badge ${playing ? "is-playing" : ""}`}>
            <span>⏱️</span>
            <span>{formatTimer(elapsedSeconds)} / 04:45</span>
          </div>
          {playing && (
            <div className="autoplay-progress-bar">
              <div className="autoplay-progress-fill" style={{ width: `${(elapsedSeconds / TOTAL_KEYNOTE_SECONDS) * 100}%` }} />
            </div>
          )}
        </div>
        <div className="deck-controls">
          <div className="deck-voice-badge" title="Female CEO Keynote Voice">
            <span className="deck-voice-icon">🎙️</span>
            <select
              aria-label="Select Voice"
              className="deck-voice-select"
              value={selectedVoiceName}
              onChange={(e) => {
                setSelectedVoiceName(e.target.value);
                if (speaking) stopSpeech();
              }}
            >
              {femaleVoiceList.length > 0 ? (
                femaleVoiceList.map((v) => (
                  <option key={v.name} value={v.name}>
                    {cleanVoiceLabel(v.name) || "Female Voice"}
                  </option>
                ))
              ) : (
                <option value="">Female Voice</option>
              )}
            </select>
          </div>

          <button className="deck-btn" onClick={() => setShowScriptModal(true)} title="View Combined 4m 45s Speech Script">
            <FileText size={13} /> Full Script
          </button>

          <button className="deck-btn deck-btn-primary" onClick={togglePlay} style={{ gap: "6px" }}>
            {playing ? <Pause size={13} /> : <Play size={13} />}
            {playing ? "Pause Keynote" : "Play Keynote (4m 45s)"}
          </button>
          {speaking && (
            <>
              <button className="deck-btn" onClick={stopSpeech} title="Mute narration">
                <VolumeX size={13} />
              </button>
              <div className="speaking-indicator">
                <div className="speaking-bar" />
                <div className="speaking-bar" />
                <div className="speaking-bar" />
                <div className="speaking-bar" />
                <div className="speaking-bar" />
              </div>
            </>
          )}
          <button className="deck-btn" onClick={toggleFullscreen} title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}>
            {isFullscreen ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
          </button>
          <Link href="/dashboard" className="deck-btn deck-btn-primary">
            Dashboard <ArrowRight size={13} />
          </Link>
        </div>
      </header>

      {/* ── NAV RAIL ── */}
      <nav className="deck-nav-rail">
        {SLIDES.map((s, i) => (
          <div key={s.id} className={`deck-nav-item ${active === i ? "active" : ""}`} onClick={() => { if (playing) { stopSpeech(); setPlaying(false); } goTo(i); }}>
            <span className="deck-nav-tooltip">{s.navTitle}</span>
            <div className="deck-nav-dot" />
          </div>
        ))}
      </nav>

      {/* ═══════════════════════════════════════════════════════════════════
         01 — HOOK
         ═══════════════════════════════════════════════════════════════════ */}
      <section ref={(el) => { slideRefs.current[0] = el; }} id="hook" className="deck-slide">
        <div className="particles-container">
          {[...Array(8)].map((_, i) => <div key={i} className="particle" />)}
        </div>
        <div className="deck-slide-inner">
          <div className="kicker reveal d1"><span className="kicker-dot" /> THE HOOK</div>
          <h1 className="headline shimmer-text reveal d2">
            27% of recovered payments<br />
            didn't need your help.
          </h1>
          <p className="subline reveal d3">
            Your retry system spent ₹4.00 per link, degraded customer trust, and claimed credit for payments that were going to settle on their own. <strong>What if your recovery system was smart enough to do nothing when nothing was the right answer?</strong>
          </p>

          <div className="stat-row reveal-scale d4">
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-rose" style={{ color: "#e11d48" }}>₹3,200+</span>
              <span className="stat-label">Wasted Daily</span>
              <span className="stat-sub">Average Indian merchant, blind retry</span>
            </div>
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-rose" style={{ color: "#d97706" }}>27%</span>
              <span className="stat-label">Natural Recovery</span>
              <span className="stat-sub">Would pay without any intervention</span>
            </div>
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-emerald" style={{ color: "#059669" }}>1 question</span>
              <span className="stat-label">ULTRON Asks</span>
              <span className="stat-sub">"Is this worth our next unit of capacity?"</span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
         02 — PROBLEM (dark)
         ═══════════════════════════════════════════════════════════════════ */}
      <section ref={(el) => { slideRefs.current[1] = el; }} id="problem" className="deck-slide dark">
        <div className="particles-container">
          {[...Array(8)].map((_, i) => <div key={i} className="particle" />)}
        </div>
        <div className="deck-slide-inner">
          <div className="kicker reveal d1"><AlertTriangle size={12} style={{ color: "#e11d48" }} /> THE PROBLEM</div>
          <h1 className="headline reveal d2">
            Every retry you fire<br />
            <span className="muted">costs more than the</span><br />
            <span className="accent-rose">payment you're chasing.</span>
          </h1>
          <p className="subline reveal d3">
            Traditional retry systems treat every failure the same — stolen cards, insufficient funds, gateway timeouts. <strong>They blast links at all of them. The result is three invisible costs bleeding your margins dry.</strong>
          </p>

          <div className="cols-3 reveal d4">
            <div className="content-block">
              <span className="block-num">01</span>
              <span className="block-title">Operational Spend</span>
              <span className="block-body">₹4.00 per link — gateway fees, SMS delivery, infrastructure overhead. Fired whether the customer pays or not. 100 failures = ₹400 burned.</span>
              <span className="block-tag" style={{ background: "rgba(225,29,72,0.15)", color: "#fb7185" }}>FIXED: 400 PAISE / LINK</span>
            </div>
            <div className="content-block">
              <span className="block-num">02</span>
              <span className="block-title">Customer Fatigue</span>
              <span className="block-body">Each retry degrades trust. ULTRON models this as an escalating penalty: ₹0 → ₹2.50 → ₹7.50 → ₹15+. The 4th attempt costs 6× the 2nd.</span>
              <span className="block-tag" style={{ background: "rgba(217,119,6,0.15)", color: "#fbbf24" }}>CURVE: EXPONENTIAL</span>
            </div>
            <div className="content-block">
              <span className="block-num">03</span>
              <span className="block-title">Counterfactual Waste</span>
              <span className="block-body">27% of recoveries settle naturally. Every link sent to them is pure waste — you spent ₹4.00 to recover money that was already coming back.</span>
              <span className="block-tag" style={{ background: "rgba(124,58,237,0.15)", color: "#a78bfa" }}>ΔP ≈ 0 → WASTE</span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
         03 — SOLUTION
         ═══════════════════════════════════════════════════════════════════ */}
      <section ref={(el) => { slideRefs.current[2] = el; }} id="solution" className="deck-slide">
        <div className="deck-slide-inner">
          <div className="kicker reveal d1"><span className="kicker-dot" /> THE SOLUTION</div>
          <h1 className="headline reveal d2">
            An economic control plane<br />
            for <span className="accent">failed payments.</span>
          </h1>
          <p className="subline reveal d3">
            ULTRON treats every failed payment as a <strong>Recovery Opportunity</strong> competing against every other opportunity for scarce, costly recovery capacity. It resolves each to exactly one of three rational decisions.
          </p>

          <div className="triad-strip reveal d4">
            <div className="triad-block act-block">
              <div className="triad-decision badge-pulse-act">ACT</div>
              <div className="triad-desc">
                IVEN is positive and ranks within the top K=5. Intervention meaningfully improves recovery odds above the natural baseline. Send the payment link.
              </div>
              <div className="triad-rule">IVEN &gt; 0 AND Rank ≤ K</div>
            </div>
            <div className="triad-block wait-block">
              <div className="triad-decision badge-pulse-wait">WAIT</div>
              <div className="triad-desc">
                IVEN is positive but didn't make the capacity cut. Queued for the next allocation batch. Capacity is scarce — the shadow price sets the cutoff.
              </div>
              <div className="triad-rule">IVEN &gt; 0 AND Rank &gt; K</div>
            </div>
            <div className="triad-block abstain-block">
              <div className="triad-decision badge-pulse-abstain">ABSTAIN</div>
              <div className="triad-desc">
                Costs exceed incremental value. The customer will likely pay on their own. Do nothing. Save ₹4.00 per link plus customer goodwill.
              </div>
              <div className="triad-rule">IVEN ≤ 0 OR confidence = LOW</div>
            </div>
          </div>

          <div className="divider reveal d5" />
          <p className="subline reveal d5" style={{ marginBottom: 0 }}>
            <strong>The anti-blast advantage:</strong> While traditional systems fire 100 links, ULTRON sends 5 — and proves mathematically that every one was worth sending.
          </p>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
         04 — ARCHITECTURE (dark)
         ═══════════════════════════════════════════════════════════════════ */}
      <section ref={(el) => { slideRefs.current[3] = el; }} id="architecture" className="deck-slide dark">
        <div className="particles-container">
          {[...Array(8)].map((_, i) => <div key={i} className="particle" />)}
        </div>
        <div className="deck-slide-inner">
          <div className="kicker reveal d1"><span className="kicker-dot" /> ARCHITECTURE</div>
          <h1 className="headline shimmer-text reveal d2">
            Seven stages.<br />
            <span className="accent-blue">Zero guesswork.</span>
          </h1>
          <p className="subline reveal d3">
            Every failed payment passes through a deterministic pipeline. <strong>No stage is skipped. Every decision is stored at the moment it's made — never generated after the fact.</strong>
          </p>

          <div className="pipeline-flow reveal-scale d4">
            {[
              { n: "01", name: "Intercept",  desc: "HMAC-verified webhook + dedup" },
              { n: "02", name: "Perceive",   desc: "Classify hard / soft / unknown" },
              { n: "03", name: "Score",      desc: "IVEN = ΔP × Amount − Costs" },
              { n: "04", name: "Allocate",   desc: "Rank by IVEN, cap K=5, λ" },
              { n: "05", name: "Authorize",  desc: "5 compliance checks" },
              { n: "06", name: "Execute",    desc: "Razorpay link + circuit breaker" },
              { n: "07", name: "Reconcile",  desc: "Provider truth + SHA-256 ledger" },
            ].map((s, i) => (
              <div key={i} className="pipeline-step">
                <span className="step-num">STAGE {s.n}</span>
                <span className="step-name">{s.name}</span>
                <span className="step-desc">{s.desc}</span>
              </div>
            ))}
          </div>

          <div className="stat-row reveal d5" style={{ marginTop: 36 }}>
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-blue">K = 5</span>
              <span className="stat-label">Capacity Cap</span>
              <span className="stat-sub">Payment links per allocation run</span>
            </div>
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-rose">5 checks</span>
              <span className="stat-label">Compliance Gate</span>
              <span className="stat-sub">Independent, deterministic vetoes</span>
            </div>
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-blue">SHA-256</span>
              <span className="stat-label">Ledger Chain</span>
              <span className="stat-sub">Immutable double-entry audit trail</span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
         05 — INNOVATION
         ═══════════════════════════════════════════════════════════════════ */}
      <section ref={(el) => { slideRefs.current[4] = el; }} id="innovation" className="deck-slide">
        <div className="deck-slide-inner">
          <div className="kicker reveal d1"><Zap size={12} style={{ color: "#2563eb" }} /> INNOVATION</div>
          <h1 className="headline reveal d2">
            Four breakthroughs.<br />
            <span className="accent-blue">One control plane.</span>
          </h1>
          <p className="subline reveal d3">
            ULTRON isn't an incremental improvement over retry systems. <strong>It's a fundamentally different operating model built on four core innovations.</strong>
          </p>

          <div className="cols-4 reveal d4">
            <div className="content-block hover-lift">
              <span className="block-num" style={{ color: "#2563eb" }}>INNOVATION 01</span>
              <span className="block-title">Incremental Lift (ΔP)</span>
              <span className="block-body">We don't ask "what's the recovery probability?" We ask "how much <em>better</em> does intervention make it versus natural recovery?" ΔP isolates true causal lift.</span>
              <span className="block-tag" style={{ background: "#dbeafe", color: "#1e40af" }}>ΔP = P(ACT) − P(NATURAL)</span>
            </div>
            <div className="content-block hover-lift">
              <span className="block-num" style={{ color: "#2563eb" }}>INNOVATION 02</span>
              <span className="block-title">Shadow Pricing (λ)</span>
              <span className="block-body">The shadow price is the IVEN of the marginal accepted opportunity. It exposes the exact boundary where an extra retry destroys value instead of creating it.</span>
              <span className="block-tag" style={{ background: "#dbeafe", color: "#1e40af" }}>λ = MARGINAL IVEN CUTOFF</span>
            </div>
            <div className="content-block hover-lift">
              <span className="block-num" style={{ color: "#2563eb" }}>INNOVATION 03</span>
              <span className="block-title">Two-Stage Separation</span>
              <span className="block-body">Economics proposes (Stage 1: IVEN ranking), compliance disposes (Stage 2: 5 deterministic checks). A strong economic case can still be vetoed on compliance.</span>
              <span className="block-tag" style={{ background: "#dbeafe", color: "#1e40af" }}>ECONOMICS → COMPLIANCE VETO</span>
            </div>
            <div className="content-block hover-lift">
              <span className="block-num" style={{ color: "#7c3aed" }}>INNOVATION 04</span>
              <span className="block-title">NVIDIA NIM Explainer</span>
              <span className="block-body">Powered by <strong>Nemotron-3.5-Lightning-30B</strong> via NVIDIA NIM. Translates multi-variable math into forensic audit explanations. Zero LLMs on execution path.</span>
              <span className="block-tag" style={{ background: "#ede9fe", color: "#6d28d9" }}>NVIDIA NEMOTRON-3.5 · ZERO EXEC</span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
         06 — LLM VS DETERMINISM (dark)
         ═══════════════════════════════════════════════════════════════════ */}
      <section ref={(el) => { slideRefs.current[5] = el; }} id="ai-boundary" className="deck-slide dark">
        <div className="particles-container">
          {[...Array(8)].map((_, i) => <div key={i} className="particle" />)}
        </div>
        <div className="deck-slide-inner">
          <div className="kicker reveal d1"><Shield size={12} style={{ color: "#059669" }} /> AI GOVERNANCE &amp; ARCHITECTURE</div>
          <h1 className="headline shimmer-text reveal d2">
            Where AI stops.<br />
            Where determinism begins.
          </h1>
          <p className="subline reveal d3">
            Deterministic code moves the money. Frontier generative AI explains why.
          </p>

          <div className="boundary-triad reveal d4">
            {/* 1. Deterministic Core */}
            <div className="boundary-triad-card card-deterministic">
              <span className="boundary-card-badge">
                <Shield size={12} /> Deterministic Code
              </span>
              <div>
                <div className="boundary-card-title">Moves the Money</div>
                <div className="boundary-card-sub">100% mathematical TypeScript</div>
              </div>
              <div className="boundary-card-list">
                <div className="boundary-card-item">
                  <Check size={16} className="boundary-card-icon" />
                  <span><strong>Counterfactual Scoring:</strong> IVEN formula in exact integer paise.</span>
                </div>
                <div className="boundary-card-item">
                  <Check size={16} className="boundary-card-icon" />
                  <span><strong>Portfolio Auction:</strong> Greedy allocation under K=5 capacity cap.</span>
                </div>
                <div className="boundary-card-item">
                  <Check size={16} className="boundary-card-icon" />
                  <span><strong>Action Authority:</strong> 5 deterministic compliance veto gates.</span>
                </div>
                <div className="boundary-card-item">
                  <Check size={16} className="boundary-card-icon" />
                  <span><strong>Payment Execution:</strong> Real Razorpay API link generation.</span>
                </div>
              </div>
              <div className="boundary-card-footer">
                <Check size={13} /> 100% Provable · Zero Hallucination
              </div>
            </div>

            {/* 2. What LLM Can Do */}
            <div className="boundary-triad-card card-llm-can">
              <span className="boundary-card-badge">
                <Zap size={12} /> NVIDIA Nemotron-3.5
              </span>
              <div>
                <div className="boundary-card-title">What the LLM Does</div>
                <div className="boundary-card-sub">Autonomous forensic explainer</div>
              </div>
              <div className="boundary-card-list">
                <div className="boundary-card-item">
                  <Check size={16} className="boundary-card-icon" />
                  <span><strong>Plain-English Auditing:</strong> Translates math into merchant insights.</span>
                </div>
                <div className="boundary-card-item">
                  <Check size={16} className="boundary-card-icon" />
                  <span><strong>Decision Context:</strong> Explains why we ACT, WAIT, or ABSTAIN.</span>
                </div>
                <div className="boundary-card-item">
                  <Check size={16} className="boundary-card-icon" />
                  <span><strong>Agent Studio Feed:</strong> Context layer for Claude merchant ops.</span>
                </div>
                <div className="boundary-card-item">
                  <Check size={16} className="boundary-card-icon" />
                  <span><strong>Post-Hoc Transparency:</strong> Stored log explanations on demand.</span>
                </div>
              </div>
              <div className="boundary-card-footer">
                <Check size={13} /> Read-Only · Zero Financial Risk
              </div>
            </div>

            {/* 3. What LLM Cannot Do */}
            <div className="boundary-triad-card card-llm-cannot">
              <span className="boundary-card-badge">
                <X size={12} /> Strict Red Lines
              </span>
              <div>
                <div className="boundary-card-title">What It Cannot Do</div>
                <div className="boundary-card-sub">Zero execution authority</div>
              </div>
              <div className="boundary-card-list">
                <div className="boundary-card-item">
                  <X size={16} className="boundary-card-icon" />
                  <span><strong>Cannot Decide Actions:</strong> Never outputs ACT / WAIT / ABSTAIN.</span>
                </div>
                <div className="boundary-card-item">
                  <X size={16} className="boundary-card-icon" />
                  <span><strong>Cannot Alter Amounts:</strong> Never touches paise or calculations.</span>
                </div>
                <div className="boundary-card-item">
                  <X size={16} className="boundary-card-icon" />
                  <span><strong>Cannot Trigger Payments:</strong> Zero Razorpay API credentials.</span>
                </div>
                <div className="boundary-card-item">
                  <X size={16} className="boundary-card-icon" />
                  <span><strong>Cannot Bypass Vetoes:</strong> Compliance gates are absolute.</span>
                </div>
              </div>
              <div className="boundary-card-footer">
                <X size={13} /> Zero AI on Financial Execution Path
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
         07 — RAZORPAY INTEGRATION
         ═══════════════════════════════════════════════════════════════════ */}
      <section ref={(el) => { slideRefs.current[6] = el; }} id="razorpay" className="deck-slide alt">
        <div className="deck-slide-inner">
          <div className="kicker reveal d1"><span className="kicker-dot" /> RAZORPAY INTEGRATION</div>
          <h1 className="headline reveal d2">
            ULTRON completes<br />
            Razorpay's AI stack.<br />
            <span className="muted">It doesn't compete.</span>
          </h1>
          <p className="subline reveal d3">
            <strong>Three systems. Three domains. One seamless payment lifecycle.</strong> No overlap. Pure complementarity.
          </p>

          <div className="position-grid reveal d4">
            <div className="position-card" style={{ borderTop: "3px solid #2563eb" }}>
              <span className="pos-label">PRE-AUTHORIZATION</span>
              <span className="pos-name">Razorpay Vulcan</span>
              <span className="pos-desc">
                Set Transformer for in-flight routing. 3,000 signals. Predicts the best payment rail in milliseconds. Built with NVIDIA &amp; AWS.
              </span>
              <span className="pos-domain">DOMAIN → The checkout millisecond</span>
            </div>
            <div className="position-card" style={{ borderTop: "3px solid #111827" }}>
              <span className="pos-label">POST-FAILURE &amp; EXPLAINABILITY</span>
              <span className="pos-name">ULTRON + NVIDIA NIM</span>
              <span className="pos-desc">
                Autonomous economic control plane. Scored via IVEN, capped at K=5, vetted by 5 compliance gates. Uses <strong>NVIDIA NIM Nemotron-3.5-Lightning-30B</strong> for forensic decision explanations. Zero LLMs on execution path.
              </span>
              <span className="pos-domain">DOMAIN → Economic Recovery + Audit Explainer</span>
            </div>
            <div className="position-card" style={{ borderTop: "3px solid #7c3aed" }}>
              <span className="pos-label">BACK-OFFICE</span>
              <span className="pos-name">Agent Studio</span>
              <span className="pos-desc">
                Claude-powered conversational agents. Chargebacks, disputes, reporting. ULTRON's audit logs feed Agent Studio decisions.
              </span>
              <span className="pos-domain">DOMAIN → Merchant operations</span>
            </div>
          </div>

          <div className="ai-triad-banner reveal d5">
            <div className="ai-triad-info">
              <span className="ai-triad-title">⚡ The Frontier AI Triad Across Payment Lifecycles</span>
              <span className="ai-triad-sub">Complementary intelligence from millisecond pre-auth to post-failure recovery and merchant operations</span>
            </div>
            <div className="ai-triad-chips">
              <span className="ai-triad-chip" style={{ background: "rgba(37, 99, 235, 0.12)", color: "#2563eb" }}>
                Pre-Auth: NVIDIA Set Transformer (Vulcan)
              </span>
              <span className="ai-triad-chip" style={{ background: "rgba(16, 185, 129, 0.12)", color: "#059669" }}>
                Recovery Explainer: NVIDIA NIM Nemotron-3.5 (ULTRON)
              </span>
              <span className="ai-triad-chip" style={{ background: "rgba(124, 58, 237, 0.12)", color: "#7c3aed" }}>
                Merchant Ops: Anthropic Claude 3.5 (Agent Studio)
              </span>
            </div>
          </div>

          <div className="divider reveal d5" />

          <div className="stat-row reveal d5">
            <div className="stat-cell">
              <span className="stat-value" style={{ color: "#2563eb" }}>Vulcan fails</span>
              <span className="stat-label">→ ULTRON begins</span>
              <span className="stat-sub">Seamless handoff at authorization failure</span>
            </div>
            <div className="stat-cell">
              <span className="stat-value" style={{ color: "#111827" }}>ULTRON audits</span>
              <span className="stat-label">→ Agent Studio reads</span>
              <span className="stat-sub">Deterministic logs power conversational AI</span>
            </div>
            <div className="stat-cell">
              <span className="stat-value" style={{ color: "#7c3aed" }}>Zero overlap</span>
              <span className="stat-label">→ Full coverage</span>
              <span className="stat-sub">Pre-auth · Post-failure · Back-office</span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
         08 — CONCLUSION (dark)
         ═══════════════════════════════════════════════════════════════════ */}
      <section ref={(el) => { slideRefs.current[7] = el; }} id="conclusion" className="deck-slide dark">
        <div className="particles-container">
          {[...Array(8)].map((_, i) => <div key={i} className="particle" />)}
        </div>
        <div className="deck-slide-inner" style={{ textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div className="kicker reveal d1" style={{ margin: "0 auto 20px" }}><span className="kicker-dot" /> CONCLUSION</div>
          <h1 className="headline shimmer-text reveal d2" style={{ textAlign: "center", maxWidth: "900px" }}>
            The question isn't whether you can recover.<br />
            It's whether it's worth<br />
            <span className="accent">your next unit of recovery capacity.</span>
          </h1>
          <p className="subline reveal d3" style={{ textAlign: "center", maxWidth: "640px" }}>
            Every decision economically grounded. Every action compliance-approved. Every outcome immutably recorded. <strong>ULTRON.</strong>
          </p>

          <div className="stat-row reveal-scale d4" style={{ maxWidth: "800px", width: "100%" }}>
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-emerald" style={{ color: "#059669" }}>IVEN</span>
              <span className="stat-label">Economic Grounding</span>
            </div>
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-rose" style={{ color: "#e11d48" }}>5 checks</span>
              <span className="stat-label">Compliance Gate</span>
            </div>
            <div className="stat-cell hover-lift">
              <span className="stat-value glow-blue" style={{ color: "#2563eb" }}>SHA-256</span>
              <span className="stat-label">Immutable Ledger</span>
            </div>
          </div>

          <div className="reveal d5" style={{ marginTop: "48px" }}>
            <Link href="/dashboard" className="deck-btn deck-btn-primary gradient-border" style={{ padding: "14px 32px", fontSize: "16px", borderRadius: "10px" }}>
              Experience ULTRON Live <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      {/* ── FULL KEYNOTE SCRIPT MODAL (4m 45s Combined Speech) ── */}
      {showScriptModal && (
        <div className="script-modal-backdrop" onClick={() => setShowScriptModal(false)}>
          <div className="script-modal" onClick={(e) => e.stopPropagation()}>
            <div className="script-modal-header">
              <div className="script-modal-title">
                <Shield size={18} style={{ color: "#34d399" }} />
                <span>ULTRON Launch Keynote — Full Combined Speech</span>
                <span className="deck-timer-badge" style={{ marginLeft: "8px" }}>4m 45s Total</span>
              </div>
              <button className="script-modal-close" onClick={() => setShowScriptModal(false)} aria-label="Close script modal">
                <X size={18} />
              </button>
            </div>
            <div className="script-modal-body">
              {SLIDE_TIMINGS.map((timing, idx) => (
                <div
                  key={timing.id}
                  className={`script-card-block ${active === idx ? "active" : ""}`}
                  onClick={() => {
                    goTo(idx);
                    setShowScriptModal(false);
                  }}
                  title="Click to jump to this slide"
                >
                  <div className="script-card-meta">
                    <span className="script-card-tag">{timing.title}</span>
                    <span className="script-card-time">{timing.range} · {timing.duration}s</span>
                  </div>
                  <div className="script-card-text">{NARRATIONS[idx]}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
