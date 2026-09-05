<p align="center">
  <img src="docs/assets/hero_banner.jpg" alt="ULTRON — Autonomous Economic Control Plane" width="100%" />
</p>

<h1 align="center">🛡️ ULTRON</h1>

<h3 align="center">
  Autonomous Economic Control Plane for Failed-Payment Recovery
</h3>

<p align="center">
  <em>ULTRON doesn't ask "can we recover this payment?" — It asks<br/>"is recovering this payment <strong>worth spending our next unit of limited recovery capacity?</strong>"<br/>and only acts when the answer survives a deterministic compliance check.</em>
</p>

<br/>

<p align="center">
  <a href="https://ultron-power.vercel.app/dashboard" target="_blank"><img src="https://img.shields.io/badge/⚡_Live_Working_Website-ultron--power.vercel.app-00DC82?style=for-the-badge&logo=vercel&logoColor=white" alt="Live Working Website" /></a>
  <a href="https://ultron-power.vercel.app/showcase" target="_blank"><img src="https://img.shields.io/badge/🎨_Product_Showcase-Interactive_Demo-7928CA?style=for-the-badge&logo=next.js&logoColor=white" alt="Product Showcase" /></a>
</p>

<p align="center">
  <a href="#-architecture"><img src="https://img.shields.io/badge/Architecture-8_Stage_Pipeline-0d1117?style=for-the-badge&logo=buffer&logoColor=3b82f6" alt="Architecture" /></a>
  <a href="#-tech-stack"><img src="https://img.shields.io/badge/Stack-TypeScript_+_React_+_SQLite_+_Postgres-0d1117?style=for-the-badge&logo=typescript&logoColor=3178C6" alt="Stack" /></a>
  <a href="#-real-money-production-vs-sandbox-test-mode"><img src="https://img.shields.io/badge/Razorpay-Test_Sandbox_+_Real_Money_Live-0d1117?style=for-the-badge&logo=razorpay&logoColor=528FF0" alt="Razorpay" /></a>
  <a href="#-strategic-positioning-ultron-vs-razorpay-2026-ai-vulcan--agent-studio"><img src="https://img.shields.io/badge/AI_Comparison-ULTRON_vs_Vulcan_&_Studio-7928CA?style=for-the-badge&logo=anthropic&logoColor=white" alt="AI Comparison" /></a>
  <a href="#-api-reference"><img src="https://img.shields.io/badge/API-RESTful_v11.0-0d1117?style=for-the-badge&logo=fastapi&logoColor=10b981" alt="API" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Backend_LOC-25,000+-blue?style=flat-square" alt="Backend LOC" />
  <img src="https://img.shields.io/badge/Frontend_Routes-18-purple?style=flat-square" alt="Frontend Routes" />
  <img src="https://img.shields.io/badge/Enterprise_Pillars-11-success?style=flat-square" alt="Enterprise Pillars" />
  <img src="https://img.shields.io/badge/Test_Suites-89-green?style=flat-square" alt="Tests" />
  <img src="https://img.shields.io/badge/Modules-150+-orange?style=flat-square" alt="Modules" />
  <img src="https://img.shields.io/badge/Version-11.0.0_Enterprise-cyan?style=flat-square" alt="Version" />
</p>

<p align="center">
  🌐 <strong>Real Working Website:</strong> <a href="https://ultron-power.vercel.app/dashboard" target="_blank"><strong>https://ultron-power.vercel.app/dashboard</strong></a>
  &nbsp;·&nbsp;
  🎙️ <strong>Executive Launch Keynote:</strong> <a href="https://ultron-power.vercel.app/presentation" target="_blank"><strong>https://ultron-power.vercel.app/presentation</strong></a>
</p>

---

## 📋 Table of Contents

- [🌐 Live Working Website](#-live-working-website)
- [Why ULTRON Exists](#-why-ultron-exists)
- [Core Philosophy](#-core-philosophy)
- [⚡ The Six Core Breakthroughs](#-the-six-core-breakthroughs)
- [⚔️ Strategic Positioning: ULTRON vs. Razorpay 2026 AI (Vulcan & Agent Studio)](#-strategic-positioning-ultron-vs-razorpay-2026-ai-vulcan--agent-studio)
- [Architecture](#-architecture)
- [The 8-Stage Pipeline](#-the-8-stage-pipeline)
- [Advanced Economic Engine](#-advanced-economic-engine)
- [🤖 AI Agent System & Specialist Network](#-ai-agent-system--specialist-network)
- [🏛️ The 11 Pillars of ULTRON V11 Enterprise](#-the-11-pillars-of-ultron-v11-enterprise)
- [⚡ Real Money (Production) vs Sandbox (Test Mode)](#-real-money-production-vs-sandbox-test-mode)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Core Schema](#-core-schema)
- [Security & Enterprise Features](#-security--enterprise-features)
- [Testing](#-testing)
- [Docker Deployment](#-docker-deployment)
- [Design Principles](#-design-principles)
- [License](#-license)

---

## 🌐 Live Working Website

Experience the live ULTRON autonomous recovery control plane running in production on Vercel:

<div align="center">
  <br/>
  <a href="https://ultron-power.vercel.app/dashboard" target="_blank">
    <img src="https://img.shields.io/badge/🚀_LAUNCH_LIVE_DASHBOARD-ultron--power.vercel.app%2Fdashboard-00DC82?style=for-the-badge&logo=vercel&logoColor=white" alt="Launch Live Dashboard" />
  </a>
  <a href="https://ultron-power.vercel.app/presentation" target="_blank">
    <img src="https://img.shields.io/badge/🎙️_KEYNOTE_PRESENTATION-4m_45s_Executive_Speech-7928CA?style=for-the-badge&logo=slides&logoColor=white" alt="Launch Keynote Presentation" />
  </a>
  <br/><br/>
  <strong>🔗 Direct Dashboard URL:</strong> <a href="https://ultron-power.vercel.app/dashboard" target="_blank"><strong>https://ultron-power.vercel.app/dashboard</strong></a>
  <br/>
  <strong>🎙️ Interactive Launch Keynote Deck:</strong> <a href="https://ultron-power.vercel.app/presentation" target="_blank"><strong>https://ultron-power.vercel.app/presentation</strong></a>
  <br/>
  <strong>🎨 Interactive Failure Lab & Showcase:</strong> <a href="https://ultron-power.vercel.app/showcase" target="_blank"><strong>https://ultron-power.vercel.app/showcase</strong></a>
  <br/><br/>
</div>

> ⚡ **Cloud Deployment Note:** The live website connects to our cloud PostgreSQL instance, demonstrating real-time portfolio allocation, live economic shadow pricing, Bayesian calibration curves, and deterministic compliance verification without requiring local setup.

---

## 🧠 Why ULTRON Exists

Razorpay, Stripe, Adyen, and Zuora already do smart **per-payment retry timing**. That is **not** what ULTRON builds.

ULTRON is the **layer above it** — a system that treats every failed payment as a **Recovery Opportunity** competing against every other opportunity for **scarce, costly recovery capacity** (payment links, human attention, contact budget), and that can rationally choose to do **nothing** when acting isn't worth it.

```
Traditional Retry Systems          ULTRON Control Plane
┌──────────────────────┐          ┌──────────────────────────────────────────────┐
│  Payment fails →     │          │  Payment fails →                             │
│  Wait X minutes →    │          │  Normalize into RecoveryOpportunity →        │
│  Retry again         │          │  Score incremental recovery probability →    │
│                      │          │  Compete against portfolio for capacity →    │
│  (No economics.      │          │  Run deterministic compliance gate →         │
│   No portfolio view. │          │  Execute only if AUTHORIZED →               │
│   No "do nothing"    │          │  Reconcile against provider truth →          │
│   option.)           │          │  Learn from outcome (Bayesian update)        │
└──────────────────────┘          └──────────────────────────────────────────────┘
```

> **Key Insight:** A payment that was going to recover on its own is worth acting on **only if** our intervention meaningfully improves the odds. ULTRON quantifies this via `incremental_prob = intervention_recovery_prob − natural_recovery_prob`.

---

## 💎 Core Philosophy

<table>
<tr>
<td width="60">🎯</td>
<td><strong>Incremental Value, Not Raw Probability</strong><br/>Score by how much <em>better</em> intervention makes recovery odds vs. natural recovery — not just "can we recover?"</td>
</tr>
<tr>
<td>⚖️</td>
<td><strong>Portfolio-Level Allocation</strong><br/>All opportunities compete for limited capacity under explicit budget constraints. The system exposes a <strong>shadow price</strong> — the value of the marginal accepted opportunity.</td>
</tr>
<tr>
<td>🛡️</td>
<td><strong>Two-Stage Decision Architecture</strong><br/>Economic decision (ACT/WAIT/ABSTAIN) → then deterministic compliance veto. Economics and compliance are <em>intentionally separate stages</em>.</td>
</tr>
<tr>
<td>🤖</td>
<td><strong>LLM as Explainer, Never as Executor</strong><br/>If an LLM is used, it may only <em>explain</em> a decision in natural language. No LLM sits on the execution path.</td>
</tr>
<tr>
<td>📊</td>
<td><strong>Model-Estimated, Not Measured Fact</strong><br/>Every probability shown is visibly labeled as <strong>model-estimated</strong> — because the true counterfactual is never observed.</td>
</tr>
<tr>
<td>📝</td>
<td><strong>Built-In Audit Trail</strong><br/>Every stage writes its reasoning to a durable log as it happens. The "Why?" screen reads stored fields, never generates explanations after the fact.</td>
</tr>
</table>

---

## ⚡ The Six Core Breakthroughs

ULTRON departs fundamentally from traditional retry tools through six interconnected mathematical and architectural innovations:

| # | Breakthrough | Mathematical / Architectural Foundation | Real-World Impact |
|:---:|:---|:---|:---|
| **01** | **Incremental Lift ($\Delta P$)** | $\Delta P = \max(0, P(\text{ACT}) - P(\text{NATURAL}))$ | Isolates true causal recovery. Never spends money claiming credit for payments that settle naturally. |
| **02** | **Shadow Pricing ($\lambda$)** | $\lambda^* = \text{IVEN}_{(K)}$ via Dual-Mirror Descent | Dynamically prices scarce contact capacity, mathematically clearing the portfolio at the marginal threshold. |
| **03** | **Two-Stage Sovereign Separation** | Stage 1 (Economics) $\to$ Stage 2 (Deterministic Veto) | Compliance (hard declines, RBI 3-attempt caps, kill switches) can veto any economic case without exception. |
| **04** | **Live Bayesian Calibration** | Beta-Binomial conjugate posteriors: $\text{Beta}(\alpha_0 + k, \beta_0 + n - k)$ | Probability tables continuously learn from incoming settlement webhooks; rare codes regularize to global prior. |
| **05** | **Causal Attribution Engine** | Difference-in-Differences (DiD) ATT with 5% synthetic holdout | Computes Average Treatment Effect on the Treated with automated parallel-trends validation ($\Delta_{\text{pre}} < 15\%$). |
| **06** | **Autonomous AI Agent Subsystem** | 8-Phase Loop, MCP JSON-RPC 2.0, 64-dim Vector Memory, Multi-Provider Cascade | Investigates failures via specialist agents with zero execution risk — strict invariant: **No LLM on financial path**. |

---

## ⚔️ Strategic Positioning: ULTRON vs. Razorpay 2026 AI (Vulcan & Agent Studio)

In 2026, Razorpay unveiled two flagship AI platforms: **Agent Studio** (built on Anthropic's Claude Agent SDK) and **Vulcan** (India's first transformer foundation model for payments, built with NVIDIA & AWS). 

While both represent major technological leaps, they solve problems on opposite sides of the financial lifecycle. **ULTRON is neither an in-flight router nor an open conversational bot** — it is the **autonomous economic control plane and fiduciary guardrail** that sits between transaction failure and merchant action.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PAYMENT LIFECYCLE                                              │
│                                                                                                  │
│   [Checkout & Routing]             [Post-Failure Recovery]           [Back-Office Operations]    │
│                                                                                                  │
│    Razorpay VULCAN                      ULTRON                         Razorpay AGENT STUDIO     │
│   ────────────────────             ─────────────────                  ──────────────────────     │
│   • In-flight set transformer      • Post-failure economic plane      • Claude Agent SDK         │
│   • Millisecond routing            • Counterfactual IVEN calculus     • Conversational ops       │
│   • Multi-rail authorization       • Shadow-price capacity auction    • Chargeback dispute kits  │
│   • "Can we authorize this?"       • Deterministic Action Authority   • No-code merchant agents  │
│                                    • "Is it worth our capacity?"      • "Automate my backoffice" │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 📊 Comparative Architecture & Economics

| Dimension | Razorpay Vulcan | Razorpay Agent Studio | 🛡️ ULTRON Control Plane |
| :--- | :--- | :--- | :--- |
| **Primary Mission** | Maximize checkout authorization rates & detect network fraud | Automate manual merchant workflows using LLM agents | Maximize net recovery yield under scarce operational capacity |
| **Operational Timing** | **In-flight** (millisecond authorization window) | **Asynchronous / Reactive** (triggered by events/prompts) | **Post-flight** (immediately following authorization failure) |
| **Core AI / Math Engine** | **Set Transformer** (3,000 signals, non-sequential field tokens, AWS SageMaker) | **Generative LLM** (Anthropic Claude Agent SDK + tool use) | **Bayesian Estimation + Lagrangian Portfolio Allocation** |
| **Core Question Answered** | *"Which banking rail gives the highest probability of authorization right now?"* | *"Can an AI agent handle this operational task instead of a human?"* | *"Is recovering this payment worth spending our next unit of scarce recovery capacity?"* |
| **Execution Authority** | Gateway-internal transaction routing logic | Autonomous Agent with direct tool-execution permissions | **Two-Stage Gate**: Stage 1 Economic Optimization, Stage 2 **Deterministic Compliance Veto** |
| **LLM on Financial Path** | **None** (pure transformer embeddings, not a language model) | **Direct** (LLM decides tool parameters, messaging, retry timing) | **Strictly Prohibited** (LLM only explains pre-computed ledger logs; zero financial authority) |
| **Economic Calculus** | Binary authorization probability ($P_{success}$) | Task completion & gross recovery | **Incremental Value ($IVEN$)**: $\Delta P \times \text{Paise} - C_{ops} - C_{fatigue}$ |
| **Counterfactual Awareness** | Blind to counterfactuals (evaluates only in-flight attempt) | Blind (assumes all recovered revenue was caused by the agent) | **Explicit Natural vs. Intervention Recovery**: isolates true causal lift ($\Delta P$) |
| **Capacity & Scarcity** | Elastic cloud inference capacity | Unconstrained (retries as many payments as configured) | **Hard Capacity Caps**: derives marginal **Shadow Price ($\lambda$)** per run |
| **Auditability** | Deep learning black box (proprietary architecture) | Non-deterministic prompt transcripts | **Deterministic Immutable Ledger**: every decision replayed from discrete fields |
| **Alignment of Interest** | Gateway volume (earns MDR fees on transaction attempts) | Platform stickiness & Claude SDK compute consumption | **Merchant Balance Sheet**: prevents blast fatigue & wasted unit costs |

---

### 🔍 Deep Dive: The Three Core Distinctions

#### 1. In-Flight Routing (Vulcan) vs. Post-Failure Economic Allocation (ULTRON)
- **Vulcan's domain** is the checkout millisecond: predicting which bank pipe, card network, or UPI switch has the highest probability of success. It treats failure as a transient routing problem.
- **ULTRON's domain** begins after Vulcan and the upstream gateway have failed. When a payment fails, ULTRON does not ask "how do we retry this right now?" It treats the failed payment as an asset on the merchant's balance sheet that must compete for scarce budget, customer attention, and contact quotas.
- *Synergy:* ULTRON does not replace Vulcan. Instead, Vulcan’s error codes and route telemetry feed directly into ULTRON’s **Perception Engine** as prior signals.

#### 2. Generative Agent Execution (Agent Studio) vs. Deterministic Action Authority (ULTRON)
- **The LLM Execution Danger:** Placing an LLM (like Claude) directly on the financial execution path creates non-deterministic drift, uncalibrated spending, and hallucinated action risks during banking outages.
- **ULTRON Rule #6:** *No LLM sits on the execution path.* ULTRON utilizes deterministic mathematical models for all scoring ($IVEN$), constrained optimization for allocation, and a strict 5-check compliance gate (**Action Authority**) that can veto economic decisions regardless of potential upside. In ULTRON, LLMs are used strictly as post-hoc natural language explainers reading immutable audit logs.
- **The Anti-Blast Advantage:** While unconstrained agent bots blast payment links for every failed subscription, ULTRON calculates customer fatigue cost ($C_{fatigue}$) and natural recovery probability ($P_{natural}$). If a customer will settle naturally on Monday morning, ULTRON issues an **ABSTAIN** decision, saving messaging fees, gateway charges, and customer goodwill.

#### 3. The Gateway Conflict of Interest: Why ULTRON Must Be Independent
Payment gateways earn fees on processing attempts, payment link dispatches, and transaction volume. Gateways have **no structural incentive** to tell a merchant: *"Do nothing. Do not send this payment link. Let the user pay on their own tomorrow."*

ULTRON is the merchant’s fiduciary guardian. Because ULTRON is independent of transaction attempt fees, its objective function is strictly aligned with the merchant's net cash recovery and brand preservation.

---

### 🧩 The Enterprise Coexistence Stack

In modern fintech architecture, Vulcan, Agent Studio, and ULTRON form a unified, complementary hierarchy:

```
1. PRE-CHECKOUT & ROUTING  ──►  Razorpay Vulcan (Foundation Model)
                                Maximize millisecond success rates across UPI/Cards.

2. PAYMENT FAILURE EVENT   ──►  ULTRON Perception & Economics Engine
                                Screen raw webhooks. Calculate natural vs. intervention odds.
                                Filter out low-lift and high-fatigue opportunities.

3. CAPACITY ALLOCATION     ──►  ULTRON Recovery Market
                                Auction scarce daily WhatsApp/Payment Link quotas.
                                Establish shadow price (λ) for the batch.

4. COMPLIANCE & SAFETY     ──►  ULTRON Action Authority
                                Deterministic veto on hard decline codes and exhausted users.

5. DISPATCH & WORKFLOWS    ──►  Razorpay Agent Studio / Official SDK
                                Execute approved recovery links, or trigger Dispute 
                                Responder for chargebacks approved by finance.
```

---

## 🏗 Architecture

<p align="center">
  <img src="docs/assets/pipeline_flow.jpg" alt="ULTRON 8-Stage Pipeline Architecture" width="100%" />
</p>

ULTRON processes every failed payment through a strict **8-stage deterministic pipeline** where each stage reads from and writes to durable state, producing an immutable, mathematically provable decision trail across 150+ TypeScript modules.

```mermaid
graph LR
    A[🔔 1. Event Fabric] --> B[👁 2. Perception]
    B --> C[🧮 3. Bayesian IVEN]
    C --> D[📊 4. Recovery Market]
    D --> E[🛡 5. Action Authority]
    E --> F[🤖 6. AI Agent Reasoning]
    F --> G[⚡ 7. Resilient Execution]
    G --> H[✅ 8. Truth Engine]
    H -.->|Closed-Loop Bayesian Feedback| C
    
    style A fill:#1e3a5f,stroke:#3b82f6,color:#f1f5f9
    style B fill:#1e3a5f,stroke:#8b5cf6,color:#f1f5f9
    style C fill:#1e3a5f,stroke:#f59e0b,color:#f1f5f9
    style D fill:#1e3a5f,stroke:#10b981,color:#f1f5f9
    style E fill:#1e3a5f,stroke:#ef4444,color:#f1f5f9
    style F fill:#1e3a5f,stroke:#8b5cf6,color:#f1f5f9
    style G fill:#1e3a5f,stroke:#06b6d4,color:#f1f5f9
    style H fill:#1e3a5f,stroke:#22c55e,color:#f1f5f9
```

---

## 🔗 The 8-Stage Pipeline

### Stage 1 — 🔔 Event Fabric
> **Webhook ingestion with timing-safe HMAC-SHA256 verification and distributed idempotency guard**

| Capability | Implementation |
|---|---|
| Webhook endpoint | `POST /webhooks/razorpay/:tenant_id` |
| Signature verification | Timing-safe HMAC-SHA256 against per-tenant secrets |
| Event deduplication | By `event_id` and `payment_id` lookups via Redis & SQLite |
| Multi-event support | `payment.failed`, `payment_link.paid`, `payment_link.expired` |
| Simulation endpoint | `POST /internal/simulate-webhook/:tenant_id` (source=`synthetic`) |
| Source labeling | Real webhooks → `source='real'` · Simulations → `source='synthetic'` |

Every incoming event is verified, deduplicated, and routed to the Perception layer. The simulation endpoint is completely isolated and unconditionally labels all ingested records as `synthetic`.

---

### Stage 2 — 👁 Perception
> **Decline taxonomy classification, temporal cycle extraction, and opportunity normalization**

The Perception layer transforms raw Razorpay payment failure payloads into standardized `RecoveryOpportunity` records using a deterministic decline taxonomy:

```
┌────────────────────────────────┬────────────────────────────────────────┐
│  HARD DECLINES (irrecoverable) │  stolen_card, lost_card, pickup_card,  │
│  → Zero incremental value      │  restricted_card, card_stolen_lost     │
├────────────────────────────────┼────────────────────────────────────────┤
│  SOFT DECLINES (recoverable)   │  insufficient_funds, expired_card,     │
│  → Candidates for intervention │  generic_decline, bank_gateway_timeout,│
│                                │  do_not_honor, otp_timeout             │
├────────────────────────────────┼────────────────────────────────────────┤
│  UNKNOWN (unrecognized)        │  Any unmatched code →                  │
│  → Safe fallback, no crash     │  pipeline continues with low confidence│
└────────────────────────────────┴────────────────────────────────────────┘
```

Each opportunity also receives:
- **Customer profile** with trust score (default `0.65` for new customers)
- **Temporal signals** (salary deposit window 28th–5th, nocturnal banking maintenance 02:00–04:00 IST)
- **Attempt count** derived from prior opportunity history
- **Tenant scoping** for multi-merchant row-level isolation

---

### Stage 3 — 🧮 Economic Reasoning
> **Bayesian probability estimation, cost modeling, and Expected Incremental Value (IVEN) computation**

The Economic Reasoning engine computes a comprehensive `Score` for each opportunity:

```
IVEN = (incremental_prob × amount_paise) − operational_cost − fatigue_cost

where:
  incremental_prob = P(recovery | intervention) − P(recovery | no intervention)
  operational_cost = ₹4.00 (400 paise fixed per payment link)
  fatigue_cost     = f(attempt_count)  →  [₹0, ₹2.50, ₹7.50, ₹15+]
```

**IVEN Priority Bands (Phase 7):**
- **`STRONG`** ($\ge ₹150.00$): Highest expected ROI; allocated first.
- **`MODERATE`** ($₹50.00\text{--}₹149.99$): Positive economic lift; standard recovery queue.
- **`WEAK`** ($₹0.01\text{--}₹49.99$): Marginal return; cleared only when capacity is abundant.
- **`NEGATIVE`** ($\le ₹0.00$): Unconditional `ABSTAIN` (prevents capital and goodwill loss).

**Probability Sources:**
- **Static Baseline Table:** Conservative default for cold-start reason codes.
- **Hierarchical Bayesian Calibration:** Beta-Binomial conjugate updating continuously adjusting priors from settlement events ($N \ge 100$, lift $> 5\%$, $p < 0.05$).
- **Thompson Sampling Bandit:** Exploration vs. exploitation balancing using Marsaglia-Tsang Gamma sampler with Box-Muller variates.

---

### Stage 4 — 📊 Recovery Market
> **Portfolio-level greedy allocation with shadow pricing and Lagrangian Dual-Mirror budget pacing**

The Recovery Market treats opportunities as competing for **scarce recovery capacity**:

```
  Input: All non-terminal opportunities with scores
    │
    ├─ Filter: confidence='low' or IVEN ≤ 0 → ABSTAIN (exits ranking)
    ├─ Filter: 5% deterministic holdout      → ABSTAIN (counterfactual control)
    │
    ├─ Sort remaining by IVEN descending
    │
    ├─ Top K (capacity limit = 5) → ACT
    ├─ Remainder                   → WAIT (deferred to subsequent cycle)
    │
    └─ Shadow Price = IVEN of the Kth (marginal) accepted opportunity
```

| Concept | Definition |
|---|---|
| **Shadow Price ($\lambda$)** | The IVEN of the marginal accepted opportunity — the exact boundary where additional retries turn negative. |
| **Capacity ($K$)** | Configurable per-tenant limit (hard cap of 5 payment links per run in Test Mode). |
| **Dual-Mirror Budget Pacer** | Online subgradient descent dynamically adjusting $\lambda(t)$ to pace contact budget across intraday spikes. |
| **Anti-Blast Valuation** | Computes capital saved by abstaining: messaging fees (₹0.85), provider fees (₹4.00), and customer goodwill (₹5.00–₹50.00). |
| **5% Synthetic Holdout** | Deterministic djb2 hash assigns 5% to uncontacted control for Difference-in-Differences causal attribution. |

---

### Stage 5 — 🛡 Action Authority
> **Independent, deterministic compliance gate with multi-level kill switch — absolute veto supremacy**

**Action Authority is an independent, deterministic gate that runs _after_ market allocation and can veto any ACT decision.** Economics proposes, compliance disposes.

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │  Check 1: Hard Decline Check     → BLOCKED if decline_type='hard'      │
  │  Check 2: Retry Cap Check        → BLOCKED if attempt_count ≥ 3 (RBI)  │
  │  Check 3: Kill Switch Check      → BLOCKED if emergency switch engaged │
  │  Check 4: Confidence Recheck     → ABSTAIN if confidence='low'         │
  │  Check 5: Capacity Recheck       → WAIT if not in top K batch          │
  └────────────────────────────────────────────────────────────────────────┘

  Verdict: AUTHORIZED | BLOCKED | ABSTAIN | WAIT
```

**Multi-Level Kill Switch Hierarchy:**
- 🔴 **Global Kill Switch** — halts all link creation and execution across all tenants immediately.
- 🟠 **Tenant Kill Switch** — halts recovery actions for an individual merchant.
- 🟡 **Provider Kill Switch** — isolates a specific payment gateway (Razorpay, Cashfree, Stripe) upon external incident.

---

### Stage 6 — 🤖 Autonomous AI Agent Subsystem
> **8-phase autonomous agent loop with specialist routing, MCP tooling, and zero financial execution authority**

When an opportunity is authorized, the Autonomous Agent Subsystem performs forensic analysis, hypothesis generation, and tone-calibrated outreach formulation:

```
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  Agent Loop: OBSERVE → HYPOTHESIZE → PLAN → ACT (Tools) → REFLECT → PROPOSE  │
  └──────────────────────────────────────────────────────────────────────────────┘
```

| Capability | Architecture & Safeguards |
|---|---|
| **Specialist Network** | 4 domain specialists: `PerceptionAgent`, `StrategyAgent`, `OutreachAgent`, and `ComplianceCopilot`. |
| **Model Context Protocol (MCP)** | JSON-RPC 2.0 server with 5 diagnostic tools: card network status, interaction history, retry simulation, discount elasticity, risk profiling. |
| **Multi-Provider Cascade** | Claude 3.5 Sonnet $\to$ Gemini 1.5 Pro $\to$ GPT-4o $\to$ Deterministic Fallback with 60s circuit breakers. |
| **64-Dim Vector Memory** | In-memory orthogonal semantic projection with 90-day exponential temporal decay firewall. |
| **Human-in-the-Loop (HITL)** | High-ticket transactions ($> ₹25,000$) escalate to human review with 30-minute SLA fallback. |
| **Strict AI Red Line** | **No LLM sits on the execution path.** Language models only investigate and explain; all execution is 100% deterministic code. |

---

### Stage 7 — ⚡ Resilient Execution
> **Idempotent payment link creation with client pool, circuit breaker, rate limiter, and persistent DLQ**

Only `AUTHORIZED` opportunities surviving Action Authority and agent safety checks reach Execution:

| Safeguard | Implementation Details |
|---|---|
| **Zero-Bypass Authority Assertion** | Re-evaluates authority verdict before every API call — strictly blocks bypass. |
| **Client Pool** | Dynamically resolves encrypted AES-256-GCM credentials per tenant and environment (`test` vs `live`). |
| **Idempotency** | Local SQLite + remote Razorpay `reference_id` deduplication prevents duplicate links. |
| **Persistent DLQ** | Failed dispatches write to `dlq_jobs` with exponential backoff (`[0.5, 2, 5, 15, 60]` minutes) and automatic HITL escalation. |
| **Circuit Breaker** | 3-state pattern (CLOSED $\to$ OPEN $\to$ HALF_OPEN) with 5-failure trip and 60s cooldown probing. |
| **Omnichannel Dispatch** | Payment link delivery via WhatsApp (Meta Cloud API), Email (Resend / SMTP), and native SMS. |

---

### Stage 8 — ✅ Truth Engine & Authoritative Reconciliation
> **Provider truth reconciliation, SHA-256 double-entry ledger, and closed-loop Bayesian feedback**

The Truth Engine is the **final arbiter** of recovery outcomes. It follows the invariant:

```
  PROVIDER TRUTH  >  RECONCILIATION  >  LOCAL FINANCIAL STATE
```

| Component | Architecture |
|---|---|
| **Provider Truth Evaluator** | Extracts canonical settlement state from official Razorpay API responses. |
| **Canonical State Machine** | Enforces validated lifecycle transitions across 18 terminal and intermediate states. |
| **Double-Entry Ledger** | Cryptographic SHA-256 hash chaining: $\text{Hash}_t = \text{SHA256}(\text{Hash}_{t-1} \parallel \text{EntryData})$. |
| **Causal Attribution (DiD)** | Computes Average Treatment Effect on the Treated (ATT) against the 5% synthetic holdout. |
| **Bayesian Feedback Loop** | Reconciled settlements update Beta conjugate posteriors and Thompson Sampling distributions. |

---

## 📈 Advanced Economic Engine

### Bayesian Probability Calibration

```
Prior:       Beta(α₀, β₀)  ← from static probability table
Observation: k successes in n trials
Posterior:   Beta(α₀ + k,  β₀ + (n − k))

Auto-Promotion Gate:
  • Sample size ≥ 100
  • Lift vs. baseline > 5%
  • Z-test p-value < 0.05
```

### Thompson Sampling (Explore/Exploit)

For each decline context, ULTRON maintains Beta-distributed arms and samples recovery probabilities using the **Marsaglia & Tsang (2000) Gamma distribution sampler** with Box-Muller Normal variates. This allows the system to:
- **Explore** uncertain decline codes that may have high recovery rates
- **Exploit** well-understood codes with proven intervention lift
- **Converge** to optimal allocation as observation count grows

### Anti-Blast Engine (Value of Inaction)

ULTRON uniquely quantifies the **value of not acting**:
- 📬 WhatsApp messaging fee saved: ₹0.85 per prevented message
- 🔗 Razorpay link overhead saved: ₹4.00 per prevented link
- 💚 Customer goodwill preserved: ₹5.00 – ₹50.00 (fraud blocks save ₹50)

---

## 🤖 AI Agent System & Specialist Network

ULTRON includes an enterprise multi-agent recovery orchestrator operating under strict economic and safety constraints:

```mermaid
graph TD
    D[🔄 24/7 Recovery Daemon] --> P[📊 Portfolio Agent]
    P --> O[🎯 Agent Orchestrator]
    
    subgraph Specialists ["Specialist Network"]
        O --> S1[👁 Perception Specialist]
        O --> S2[📋 Strategy Specialist]
        O --> S3[📨 Outreach Specialist]
        O --> S4[🛡 Compliance Copilot]
        O --> S5[🏪 Merchant Copilot]
    end
    
    subgraph Safeguards ["Safety & Security Firewall"]
        TF[⏳ Temporal Firewall]
        LG[🔁 Loop Guard]
        TR[🧰 Read/Proposal Tool Registry]
        MEM[(🧠 Episodic & Semantic Memory)]
    end
    
    Specialists --> Safeguards
    Safeguards --> M[📈 Market Allocator]
    M --> A[🛡 Action Authority Gate]
    A --> E[⚡ Execution Layer]
    E --> R[✅ Reconciler & Learning Loop]
    
    style D fill:#1e293b,stroke:#3b82f6,color:#f1f5f9
    style O fill:#1e293b,stroke:#8b5cf6,color:#f1f5f9
    style Safeguards fill:#0f172a,stroke:#ef4444,color:#f1f5f9
    style Specialists fill:#0f172a,stroke:#10b981,color:#f1f5f9
```

### 👥 The 5 Domain Specialist Agents

| Specialist | Implementation File | Mission & Capabilities |
|---|---|---|
| **👁 Perception Specialist** | `agents/specialists/perception_agent.ts` | Deep decline context extraction, banking rail health correlation, card bin profiling, and failure pattern clustering. |
| **📋 Strategy Specialist** | `agents/specialists/strategy_agent.ts` | Counterfactual scenario formulation, optimal recovery window modeling, dynamic price-elasticity estimation, and holdout assignment. |
| **📨 Outreach Specialist** | `agents/specialists/outreach_agent.ts` | Channel-specific recovery payload formulation (WhatsApp vs. SMS vs. Email), cooling-off cadence, and message fatigue tracking. |
| **🛡 Compliance Copilot** | `agents/specialists/compliance_copilot.ts` | Real-time regulatory auditing (RBI recurring e-mandates, DPDP privacy standards), chargeback dispute pre-screening, and KYC validation. |
| **🏪 Merchant Copilot** | `agents/specialists/merchant_copilot.ts` | Human-in-the-loop review interface, natural language decision explanation generation, and merchant manual override processing. |

### 🛡️ Autonomous Safety Architecture & Guardrails

| Guardrail Layer | Implementation File | Functionality |
|---|---|---|
| **Temporal Firewall** | `agents/temporal_firewall.ts` | Enforces non-retroactive state sequencing, cooling-off windows, and prevents action replay attacks. |
| **Loop Guard** | `agents/loop_guard.ts` | Detects cycles and halting state anomalies, preventing runaway recursive LLM loops with automatic circuit breaking. |
| **Tool Registry** | `agents/tool_registry.ts` | 15+ strictly segregated tools divided into **Read Tools** (read-only telemetry) and **Proposal Tools** (requires Action Authority review). |
| **Memory System** | `agents/memory.ts` | Dual-tier **Episodic Memory** (historical failure traces & run histories) and **Semantic Memory** (merchant-specific behavioral patterns). |
| **Replanning Engine** | `agents/replan_engine.ts` | Dynamic multi-step recovery replanning when environmental conditions change (e.g., bank outage cleared). |
| **Wait / Wake Daemon** | `agents/wait_wake.ts` | Asynchronous suspension of opportunities awaiting optimal recovery windows without blocking system workers. |

---

## 🏛️ The 11 Pillars of ULTRON V11 Enterprise

ULTRON V11 transforms the research prototype into an enterprise-grade, horizontally scalable autonomous economic control plane while strictly upholding all non-negotiable core invariants:

| Pillar | Focus Area | Architectural Deliverable |
|:---:|:---|:---|
| **01** | **TypeScript Strict Mode** | `"strict": true`, `"noUncheckedIndexedAccess": true`, and branded types (`Paise`, `TenantId`, `OpportunityId`, `Probability`) in `src/types/branded.ts`. |
| **02** | **PostgreSQL & Supabase RLS** | Dual-engine `DatabaseAdapter` supporting SQLite & Supabase PostgreSQL with pool connection scaling and tenant-isolated Row-Level Security. |
| **03** | **OpenTelemetry Tracing** | End-to-end W3C `traceparent` context propagation linking frontend requests, API gateway, worker tasks, and external Razorpay spans. |
| **04** | **Enterprise Security** | Strict production CORS allowlist, Content Security Policy, JWT access+refresh rotation with Redis blacklist, Argon2id hashing, and API key scopes. |
| **05** | **Resilient Execution Triad** | Database-persisted Dead Letter Queue (`dlq_jobs`) with exponential backoff, persistent Redis circuit breakers, and unified `JobScheduler`. |
| **06** | **Multi-Tenant RLS Isolation** | Centralized `tenant_guard.ts` middleware enforcing strict tenant isolation across all 16 route modules, queries, and background agent loops. |
| **07** | **Enhanced Economics & DiD** | Persistent `bayesian_priors` table, IVEN Priority Bands (`STRONG`, `MODERATE`, `WEAK`, `NEGATIVE`), and Difference-in-Differences causal ATT engine. |
| **08** | **Observability Dashboard** | Next.js 16 App Router across **18 production routes** including Tenant Command Center, Economic Intelligence, Audit Explorer, and Presentation Keynote. |
| **09** | **Enterprise API Gateway** | Centralized Zod validation with RFC 7807 problem details, multi-tier sliding-window rate limiting, API versioning (`/v1/`, `/v2/`), and OpenAPI 3.1 generator. |
| **10** | **Decoupled Distributed Workers** | Redis-backed background job queue (`src/queue/job_queue.ts`, `LPUSH`/`BRPOP`), decoupled worker process (`src/worker.ts`), and Docker Compose horizontal scaling. |
| **11** | **Kubernetes Probes & 99.9% SLO** | 3-tier health checks (`/health/live`, `/health/ready`, `/health/deep`), Google SRE multi-window error budget burn rate tracking, and operations runbook. |

---

## ⚡ Real Money (Production) vs Sandbox (Test Mode)

ULTRON provides strict, zero-leak isolation between **Test Sandbox** and **Real Money (Production)** execution modes, with a one-click dashboard switcher:

| Dimension | 🧪 Test Mode (Sandbox) | ⚡ Production Mode (Real Money) |
|---|---|---|
| **Credentials** | `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` (`rzp_test_...`) | `RAZORPAY_LIVE_KEY_ID` / `RAZORPAY_LIVE_KEY_SECRET` (`rzp_live_...`) or encrypted per-tenant AES-256 vault |
| **Payment Links** | Real Razorpay Test payment links (simulated settlement) | Real Razorpay Live payment links (actual customer money recovery) |
| **Data Partitioning** | `environment = 'test'` (scoped opportunities & ledger) | `environment = 'live'` (isolated real money pipeline) |
| **Allocation & Authority** | Scoped strictly to sandbox opportunities | Scoped strictly to production opportunities |
| **Safety Guardrails** | Standard rate limits | High-visibility emerald badge, confirmation modal, strict fail-closed credentials |
| **Client Pool Isolation** | Resolves test SDK client | Strictly rejects if live keys are absent — **zero test credential leak** |

### Switching Environments in Dashboard
Operators and merchants can toggle modes instantly via the top navigation bar:
- **`🧪 Test`**: Simulates failed payments, tests webhooks, and evaluates recovery without financial risk.
- **`⚡ Live`**: Activates real-money recovery mode using live Razorpay credentials and real customer payment links.

---

## 🛠 Tech Stack

<table>
<tr>
<th align="left">Layer</th>
<th align="left">Technology</th>
<th align="left">Purpose</th>
</tr>
<tr>
<td>Runtime</td>
<td><img src="https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=node.js&logoColor=white" /></td>
<td>Server runtime (via tsx for TypeScript execution)</td>
</tr>
<tr>
<td>Language</td>
<td><img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" /></td>
<td>End-to-end type safety across backend + frontend</td>
</tr>
<tr>
<td>API</td>
<td><img src="https://img.shields.io/badge/Express-000000?style=flat-square&logo=express&logoColor=white" /></td>
<td>REST API server with middleware pipeline</td>
</tr>
<tr>
<td>Database</td>
<td><img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" /></td>
<td>Zero-setup embedded storage (file-based)</td>
</tr>
<tr>
<td>Cloud DB</td>
<td><img src="https://img.shields.io/badge/Supabase-3FCF8E?style=flat-square&logo=supabase&logoColor=white" /></td>
<td>PostgreSQL cloud sync for production deployments</td>
</tr>
<tr>
<td>Cache</td>
<td><img src="https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white" /></td>
<td>Rate limiting, session cache, and budget tracking</td>
</tr>
<tr>
<td>Frontend</td>
<td><img src="https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white" /></td>
<td>React-based dashboard with Tailwind CSS</td>
</tr>
<tr>
<td>Payments</td>
<td><img src="https://img.shields.io/badge/Razorpay-528FF0?style=flat-square&logo=razorpay&logoColor=white" /></td>
<td>Official Node SDK — Seamless Test Sandbox & Real Money Production</td>
</tr>
<tr>
<td>Messaging</td>
<td><img src="https://img.shields.io/badge/WhatsApp-25D366?style=flat-square&logo=whatsapp&logoColor=white" /></td>
<td>Meta Cloud API for recovery notifications</td>
</tr>
<tr>
<td>Email</td>
<td><img src="https://img.shields.io/badge/Resend-000000?style=flat-square&logo=minutemailer&logoColor=white" /></td>
<td>Transactional email delivery</td>
</tr>
<tr>
<td>Security</td>
<td><img src="https://img.shields.io/badge/Helmet-000000?style=flat-square&logo=helmet&logoColor=white" /></td>
<td>HSTS, CSP, and security headers</td>
</tr>
<tr>
<td>Validation</td>
<td><img src="https://img.shields.io/badge/Zod-3E67B1?style=flat-square&logo=zod&logoColor=white" /></td>
<td>Runtime schema validation</td>
</tr>
<tr>
<td>LLM</td>
<td><img src="https://img.shields.io/badge/NVIDIA_NIM-76B900?style=flat-square&logo=nvidia&logoColor=white" /></td>
<td>Decision explanations only — never on execution path</td>
</tr>
<tr>
<td>Observability</td>
<td><img src="https://img.shields.io/badge/Pino-000000?style=flat-square&logo=pino&logoColor=white" /></td>
<td>Structured JSON logging + Prometheus metrics</td>
</tr>
<tr>
<td>Infrastructure</td>
<td><img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" /></td>
<td>Multi-container deployment with NGINX reverse proxy</td>
</tr>
</table>

---

## 📁 Project Structure

```
ultron/
├── src/                          # Backend source (150+ TypeScript modules, 25 subsystems)
│   ├── server.ts                 # Express API server entry point & route registration
│   ├── worker.ts                 # Decoupled distributed background worker process
│   │
│   ├── webhooks/                 # Stage 1: Event Fabric
│   │   ├── razorpay.ts           #   HMAC-verified webhook handlers (real + simulated)
│   │   ├── queue.ts              #   Webhook delivery queue with replay
│   │   └── whatsapp.ts           #   WhatsApp Cloud API webhook receiver
│   │
│   ├── perception/               # Stage 2: Perception
│   │   └── normalizer.ts         #   Decline taxonomy & opportunity normalization
│   │
│   ├── economics/                # Stage 3: Economic Reasoning
│   │   ├── scorer.ts             #   Bayesian IVEN computation engine & bands
│   │   ├── bayesian_calibration.ts  # Beta-Binomial conjugate posterior calibration
│   │   ├── bandit_policy.ts      #   Thompson Sampling (Marsaglia-Tsang Gamma)
│   │   └── anti_blast_engine.ts  #   Value-of-inaction & 5% holdout calculator
│   │
│   ├── market/                   # Stage 4: Recovery Market
│   │   ├── allocator.ts          #   Greedy portfolio allocation with shadow price λ
│   │   └── capacity_policy.ts    #   Dual-Mirror budget pacer & Lagrangian multipliers
│   │
│   ├── authority/                # Stage 5: Action Authority
│   │   └── gate.ts               #   5-check compliance gate + multi-level kill switch
│   │
│   ├── agents/                   # Stage 6: Autonomous AI Agent Subsystem (Phases 1-8)
│   │   ├── agent_loop.ts         #   Iterative Observe-Reason-Act loop
│   │   ├── reasoning_engine.ts   #   Chain-of-Thought hypothesis generator
│   │   ├── specialist_router.ts  #   Specialist delegation (Perception, Strategy, Outreach, Compliance)
│   │   ├── trace_stream.ts       #   Server-Sent Events (SSE) live execution stream
│   │   ├── daemon.ts             #   24/7 background autonomous recovery daemon
│   │   ├── memory/               #   64-dim vector projection & 90-day decay firewall
│   │   ├── mcp/                  #   Model Context Protocol JSON-RPC 2.0 server & tools
│   │   ├── llm/providers/        #   Multi-provider cascade (Claude, Gemini, OpenAI, Fallback)
│   │   ├── hitl/                 #   Human-in-the-Loop manager with 30m SLA monitors
│   │   └── autonomous/           #   Goal decomposition, rail monitors, adaptive strategy, alerts
│   │
│   ├── execution/                # Stage 7: Resilient Execution
│   │   ├── executor.ts           #   Razorpay payment link creation & client pool
│   │   ├── circuit_breaker.ts    #   Redis-backed 3-state circuit breaker
│   │   ├── dlq.ts                #   Persistent Dead Letter Queue with exponential backoff
│   │   ├── rate_limiter.ts       #   Tiered sliding-window rate limiters
│   │   └── job_scheduler.ts      #   Unified background maintenance scheduler
│   │
│   ├── truth/                    # Stage 8: Truth Engine & Reconciliation
│   │   ├── canonical_state_machine.ts   # 18-state payment lifecycle FSM
│   │   ├── provider_truth.ts     #   Authoritative Razorpay API response evaluator
│   │   ├── double_entry_ledger.ts  #   Cryptographic SHA-256 hash-chained ledger
│   │   ├── causal_analysis_engine.ts  #  Diff-in-Diff ATT estimation (<15% parallel trends)
│   │   └── reconciliation_sla.ts #   Settlement SLA monitoring
│   │
│   ├── reconciliation/           # Authoritative reconciliation & Bayesian feedback
│   ├── security/                 # AES-256 vault, JWT rotation, tenant_guard, API key scopes
│   ├── gateway/                  # Zod RFC 7807 validation, rate tiers, versioning, OpenAPI 3.1
│   ├── queue/                    # Distributed Redis job queue (LPUSH/BRPOP)
│   ├── cache/                    # Redis client manager & distributed caching
│   ├── db/                       # DatabaseAdapter (SQLite WAL ↔ PostgreSQL RLS) & migrations
│   ├── observability/            # OpenTelemetry tracing, Prometheus metrics, health probes
│   ├── notifications/            # Meta WhatsApp Cloud API & Resend email dispatchers
│   ├── providers/                # Client pool (Razorpay Test/Live, Cashfree, Stripe)
│   ├── routes/                   # 16 Express route modules (REST, SSE, MCP)
│   └── types/                    # Branded primitive types (Paise, TenantId, Probability)
│
├── frontend/                     # Next.js 16 (Turbopack) Dashboard (18 routes)
│   └── src/app/
│       ├── presentation/         #   Launch Keynote Deck (8 slides, speech synthesis, 4m 45s script)
│       ├── dashboard/            #   Operations Hub
│       │   ├── page.tsx          #   Primary Recovery Hub & "Why?" modal
│       │   ├── command-center/   #   Tenant Command Center (portfolio health & kill switch)
│       │   ├── economics/        #   Economic Intelligence (Bayesian curves & causal ATT)
│       │   ├── audit/            #   Cryptographic Audit Timeline & hash verifier
│       │   ├── setup/            #   Zero-code integration & webhook wizard
│       │   └── settings/         #   API keys, team RBAC, provider discovery
│       ├── login/ & signup/      #   Merchant authentication & onboarding
│       ├── showcase/             #   Interactive failure lab demo sandbox
│       └── product/              #   Public product information & pricing
│
├── tests/                        # 89 Enterprise Automated Test Suites across 8 domains
├── scripts/                      # 86 Operational, validation, and migration scripts
├── docs/                         # Numbered architectural specifications (01-11) & V11 runbook
├── docker-compose.yml            # 5-service stack (PostgreSQL, Redis, Backend, Worker, Jaeger)
└── ultron.db                     # Embedded SQLite database (WAL mode)
```

---

## 🚀 Getting Started

You can test and explore ULTRON in two ways:
1. **Instantly via the Live Cloud Dashboard:** Visit [**https://ultron-power.vercel.app/dashboard**](https://ultron-power.vercel.app/dashboard) (no setup required).
2. **Locally on your machine:** Follow the quick 5-step guide below to pull, execute, and run tests.

---

### Prerequisites

- **Node.js** ≥ 18.x
- **npm** ≥ 9.x
- **Razorpay Test Mode** keys ([sign up for free test keys](https://dashboard.razorpay.com))
- *Note:* SQLite is file-based and embedded (`ultron.db`) — **zero database server setup is required**.

---

### Step 1: Pull or Clone the Codebase

#### Fresh Installation:
```bash
git clone https://github.com/Mr-Roninx/ULTRON.git
cd ULTRON
```

#### If you already have the repository:
```bash
git pull origin main
```

#### Install All Dependencies:
```bash
# 1. Install Backend Dependencies
npm install

# 2. Install Frontend Next.js Dashboard Dependencies
cd frontend && npm install && cd ..
```

---

### Step 2: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your Razorpay Test Mode credentials (or keep defaults for synthetic tests):

```env
# Required for execution & authentication
JWT_SECRET=your_super_secret_jwt_key
AES_MASTER_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
RAZORPAY_KEY_ID=rzp_test_YOUR_KEY_ID
RAZORPAY_KEY_SECRET=YOUR_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET=rzp_whsec_YOUR_SECRET

# Portfolio Configuration
PORT=3001
MAX_LINKS_PER_RUN=5

# Optional Integrations
APP_URL=https://ultron-power.vercel.app
NVIDIA_API_KEY=nvapi-YOUR_KEY        # Natural language decision explainer
RESEND_API_KEY=re_YOUR_KEY           # Email recovery notifications
DATABASE_URL=postgresql://...        # Optional Supabase cloud synchronization
```

---

### Step 3: Initialize Database & Seed Scenarios

ULTRON uses an embedded SQLite database (`ultron.db`) with WAL mode enabled. Initialize the schema and seed the canonical test scenarios:

```bash
# Apply schema migrations
npm run db:migrate

# Seed synthetic test scenarios (hard declines, soft declines, and holdout groups)
npm run seed
```

---

### Step 4: Execute & Run the Application

Start the local development stack:

#### Terminal 1 — Backend API & 24/7 Autonomous Recovery Daemon:
```bash
npm run dev
```
*The backend starts at `http://localhost:3001` and automatically starts the 24/7 autonomous recovery daemon.*

#### Terminal 2 — Next.js Operations Dashboard:
```bash
cd frontend && npm run dev
```
*The frontend dashboard starts at `http://localhost:3000`.*

#### Interactive Test Endpoints & Live Views:
- 📊 **Operations Hub:** [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
- 🎙️ **Executive Launch Keynote (4m 45s Speech):** [http://localhost:3000/presentation](http://localhost:3000/presentation)
- 🎛️ **Tenant Command Center:** [http://localhost:3000/dashboard/command-center](http://localhost:3000/dashboard/command-center)
- 📈 **Economic Intelligence & Bayesian Curves:** [http://localhost:3000/dashboard/economics](http://localhost:3000/dashboard/economics)
- 📜 **Cryptographic Audit Timeline:** [http://localhost:3000/dashboard/audit](http://localhost:3000/dashboard/audit)
- 🛒 **Demo Merchant Storefront:** [http://localhost:3001/demo-store](http://localhost:3001/demo-store) (test real failure interception)
- 🌐 **Live Production Cloud Dashboard:** [https://ultron-power.vercel.app/dashboard](https://ultron-power.vercel.app/dashboard)
- 🎨 **Live Product Showcase:** [https://ultron-power.vercel.app/showcase](https://ultron-power.vercel.app/showcase)

---

### Step 5: Run Automated Tests

ULTRON ships with **165 test & verification scripts** (80 structured test suites across 7 test directories in `tests/` + 85 automated validation and scenario scripts in `scripts/`). Verify your installation using the commands below:

```bash
# 1. Quick System Health & Dependency Probe
curl http://localhost:3001/health
curl http://localhost:3001/health/deep

# 2. Master V6 Acceptance Test Battery (27 suites, 100% pass)
npm test

# 3. Complete Forensic Truth Verification
npm run verify:v6-truth

# 4. End-to-End Webhook & Recovery Pipeline Integration
npm run test:integration

# 5. Stage-by-Stage Module Tests (8-Stage Pipeline)
npm run test:perception        # Stage 2: Decline taxonomy classification
npm run test:economics         # Stage 3: Bayesian IVEN calculation & bands
npm run test:market            # Stage 4: Portfolio knapsack & shadow price
npm run test:authority         # Stage 5: Deterministic compliance checks
npm run test:agent             # Stage 6: Autonomous multi-agent reasoning & MCP
npm run test:execution         # Stage 7: Payment link dispatch & DLQ
npm run test:truth             # Stage 8: Double-entry ledger & reconciliation

# 6. Stress & Concurrency Testing
npm run stress:all             # System-wide concurrency & load stress test
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|:---:|---|
| `JWT_SECRET` | ✅ | Secret for JWT authentication tokens |
| `AES_MASTER_KEY` | ✅ | 256-bit hex key for credential encryption in vault |
| `RAZORPAY_KEY_ID` | ✅ | Razorpay Test Mode Key ID |
| `RAZORPAY_KEY_SECRET` | ✅ | Razorpay Test Mode Key Secret |
| `RAZORPAY_WEBHOOK_SECRET` | ✅ | Razorpay webhook signature verification secret |
| `PORT` | ❌ | Server port (default: `3001`) |
| `MAX_LINKS_PER_RUN` | ❌ | Payment links per execution batch (default: `5`) |
| `DATABASE_URL` | ❌ | PostgreSQL connection string for Supabase / remote sync |
| `DATABASE_POOL_SIZE` | ❌ | Maximum connection pool size (default: `15`) |
| `REDIS_URL` | ❌ | Redis connection string (default: in-memory fallback) |
| `NVIDIA_BASE_URL` | ❌ | NVIDIA NIM base endpoint (default: `https://integrate.api.nvidia.com/v1`) |
| `NVIDIA_API_KEY` | ❌ | NVIDIA NIM API key for LLM explanations |
| `LLM_MODEL` | ❌ | NVIDIA LLM model (default: `nvidia/nemotron-3.5-lightning-30b-a3b`) |
| `DISABLE_LLM_SCORING_INFLUENCE` | ❌ | Pure deterministic scoring mode when `true` (default: `false`) |
| `RESEND_API_KEY` | ❌ | Resend API key for transactional email recovery |
| `RESEND_FROM_EMAIL` | ❌ | Sender email address for Resend notifications |
| `APP_URL` | ❌ | Frontend web application URL for CORS and links |
| `SUPABASE_URL` | ❌ | Supabase project URL |
| `SUPABASE_KEY` | ❌ | Supabase service/anon key |

> ⚠️ **Never commit `.env` to version control.** The `.gitignore` already excludes it.

---

## 📡 API Reference

### Authentication & Merchant Onboarding

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/v1/auth/signup` | `POST` | Public | Merchant registration & tenant workspace initialization |
| `/v1/auth/login` | `POST` | Public | Email/password JWT token authentication |
| `/v1/auth/send-otp` | `POST` | Public | Dispatch one-time authentication passcode |
| `/v1/auth/verify-otp` | `POST` | Public | Verify OTP code and issue session token |
| `/v1/auth/demo-login` | `POST` | Public | Instant demo merchant session generator |
| `/v1/auth/me` | `GET` | JWT | Current authenticated merchant & tenant metadata |
| `/v1/auth/tenant` | `PATCH` | JWT | Update merchant capacity limit and environment |

### Core Pipeline & Recovery Operations

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/webhooks/razorpay/:tenant_id` | `POST` | HMAC | Ingest real Razorpay payment failure/success webhooks |
| `/internal/simulate-webhook/:tenant_id` | `POST` | HMAC | Ingest synthetic test scenarios (unconditionally source=`synthetic`) |
| `/v1/events` | `POST` | API Key | Universal canonical event ingestion gateway (Odoo/external) |
| `/v1/events/ping` | `POST` | API Key / JWT | Web application heartbeat & origin connection handshake |
| `/opportunities` | `GET` | JWT | List all recovery opportunities for current merchant |
| `/opportunities/score-all` | `POST` | JWT | Run batch economic IVEN scoring across all opportunities |
| `/opportunities/:id/score` | `GET` | JWT | Inspect IVEN, cost breakdown, and model-estimated probabilities |
| `/opportunities/:id/authority` | `GET` | JWT | Check 5-stage deterministic compliance checks for opportunity |
| `/opportunities/:id/explain` | `GET/POST` | JWT | LLM natural language narrative explaining recovery decision |
| `/market/run` | `GET/POST` | JWT+Operator | Run greedy portfolio allocation under capacity limit |
| `/authority/run` | `GET/POST` | JWT+Operator | Run batch compliance gate across all allocated opportunities |
| `/authority/evaluate/:id` | `GET/POST` | JWT | Run compliance checks and return verdict on specific opportunity |
| `/authority/kill-switch` | `GET/POST` | JWT+Admin | Check status or toggle global/tenant emergency kill switch |
| `/execution/run` | `POST` | JWT+Operator | Execute batch payment link creation for authorized opportunities |
| `/execution/batch` | `POST` | JWT+Operator | Alias for `/execution/run` batch dispatch |
| `/execution/opportunity/:id` | `POST` | JWT+Operator | Execute payment link creation for a single authorized opportunity |
| `/execution/records` | `GET` | JWT | List execution records and created payment links |

### Dashboard & Observability

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/dashboard/summary` | `GET` | JWT | Real-time recovery metrics, shadow price, anti-blast savings |
| `/dashboard/analytics` | `GET` | JWT | Bank-by-bank failure rates, gross causal lift, budget pacing state |
| `/dashboard/reconcile-poll` | `POST` | JWT | Trigger manual reconciliation against provider truth |
| `/health` | `GET` | Public | System status, database pool metrics, and cache telemetry |
| `/health/live` | `GET` | Public | Kubernetes liveness probe |
| `/health/ready` | `GET` | Public | Kubernetes readiness probe |
| `/health/deep` | `GET` | Public | Deep dependency check (SQLite, PostgreSQL, Redis, Razorpay) |
| `/metrics` | `GET` | Public | Prometheus exposition format metrics scrape endpoint |
| `/audit/records` | `GET` | JWT | Immutable audit trail logs with actor, action, and timestamp |

### Enterprise Features & AI Agent Daemon

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/v1/api-keys` | `GET/POST` | JWT+Admin | Generate and manage scoped API keys (`events:write`, etc.) |
| `/v1/integrations` | `GET/POST` | JWT | Multi-provider configuration and discovery |
| `/v1/notifications` | `GET/POST` | JWT | Omnichannel recovery alerts (WhatsApp, Email) |
| `/v1/webhooks/queue` | `GET/POST` | JWT | Webhook delivery queue telemetry and dead-letter replay |
| `/v1/playground` | `GET/POST` | JWT | Interactive recovery sandbox & counterfactual lift simulator |
| `/agents/status` | `GET` | JWT+Admin | Check 24/7 autonomous recovery daemon state and sweep counts |
| `/agents/daemon/status` | `GET` | JWT+Admin | Full daemon status with active interval and capacity settings |
| `/agents/daemon/start` | `POST` | JWT+Admin | Start 24/7 background autonomous sweep loop |
| `/agents/daemon/stop` | `POST` | JWT+Admin | Pause 24/7 background autonomous sweep loop |
| `/agents/daemon/sweep` | `POST` | JWT+Admin | Trigger an immediate manual recovery sweep cycle |
| `/agents/tools` | `GET` | JWT+Admin | Inspect tool registry and permission controls |
| `/agents/runs` | `GET` | JWT+Admin | List agent mission traces and replanning telemetry |

---

## 📊 Core Schema

All records use these exact field names — every feature reads and writes against this contract:

```mermaid
erDiagram
    RecoveryOpportunity ||--|| Score : "1:1"
    RecoveryOpportunity ||--|| AllocationDecision : "1:1"
    RecoveryOpportunity ||--|{ AuthorityCheck : "1:N"
    RecoveryOpportunity ||--o| ExecutionRecord : "0..1"
    RecoveryOpportunity ||--|{ LedgerEntry : "1:N"

    RecoveryOpportunity {
        string id PK
        string tenant_id
        enum source "real|synthetic"
        int amount_paise
        string currency
        string reason_code
        enum decline_type "hard|soft|unknown"
        int attempt_count
        string customer_id
        float customer_trust_score
        string created_at
        enum status "pending|scored|allocated|authorized|deferred|blocked|abstained|executing|recovered|not_recovered"
        string razorpay_event_id
    }

    Score {
        string opportunity_id FK
        float natural_recovery_prob
        float intervention_recovery_prob
        float incremental_prob
        int operational_cost_paise
        int fatigue_cost_paise
        int expected_incremental_value_paise
        enum confidence "low|medium|high"
    }

    AllocationDecision {
        string opportunity_id FK
        enum decision "ACT|WAIT|ABSTAIN"
        int rank_in_batch
        int shadow_price_paise_at_decision
        string reason
    }

    AuthorityCheck {
        string opportunity_id FK
        string check_name
        bool passed
        string reason
    }

    ExecutionRecord {
        string opportunity_id FK
        string razorpay_payment_link_id
        string link_url
        string status
        string idempotency_key
        string created_at
    }

    LedgerEntry {
        string id PK
        string opportunity_id FK
        enum event_type "webhook_received|reconciled|recovered|not_recovered"
        int amount_paise
        string timestamp
        string raw_payload_ref
    }
```

---

## 🔒 Security & Enterprise Features

<table>
<tr>
<td width="200"><strong>🔑 Authentication</strong></td>
<td>JWT-based with bcrypt password hashing. Configurable token expiry.</td>
</tr>
<tr>
<td><strong>👥 RBAC</strong></td>
<td>Three roles: <code>ADMIN</code> (full access), <code>OPERATOR</code> (pipeline operations), <code>VIEWER</code> (read-only dashboards)</td>
</tr>
<tr>
<td><strong>🏢 Multi-Tenancy</strong></td>
<td>Full tenant isolation — every query is scoped, every webhook is per-tenant.</td>
</tr>
<tr>
<td><strong>🔐 Credential Vault</strong></td>
<td>AES-256-GCM encrypted credential storage with per-tenant secrets.</td>
</tr>
<tr>
<td><strong>🛡️ Webhook Verification</strong></td>
<td>Multi-secret rotation support, timestamp freshness checks, IP allowlisting.</td>
</tr>
<tr>
<td><strong>📊 Prometheus Metrics</strong></td>
<td>Counter, histogram, and gauge metrics exported at <code>/metrics</code>.</td>
</tr>
<tr>
<td><strong>🏥 Health Probes</strong></td>
<td>3-tier Kubernetes-compatible: <code>/health/live</code>, <code>/health/ready</code>, <code>/health/deep</code>.</td>
</tr>
<tr>
<td><strong>📝 Audit Logging</strong></td>
<td>Every API access logged with user, action, resource, and timestamp.</td>
</tr>
<tr>
<td><strong>🔄 SSE Realtime</strong></td>
<td>Server-Sent Events broadcaster for live dashboard updates per tenant.</td>
</tr>
<tr>
<td><strong>🗄️ PII Masking</strong></td>
<td>Automatic masking of emails, phone numbers, and card data in logs.</td>
</tr>
</table>

---

## 🧪 Testing

ULTRON ships with **165 test & verification scripts** (80 structured test suites across 7 test directories in `tests/` + 85 automated validation and scenario scripts in `scripts/`):

```bash
# Run all 27 V6 phase acceptance tests (including Live Money Environment)
npm test                       # Alias for npm run test:v6-all

# Comprehensive forensic truth verification
npm run verify:v6-truth        # Verifies 100% truth consistency across all deliverables
npm run verify:test-counts     # Verifies cross-file test count consistency

# Individual pipeline stage tests (8-Stage Pipeline)
npm run test:perception        # Decline taxonomy classification (Stage 2)
npm run test:economics         # IVEN computation & Bayesian engine (Stage 3)
npm run test:market            # Portfolio allocation & shadow pricing (Stage 4)
npm run test:authority         # Compliance gate & kill switch (Stage 5)
npm run test:agent             # Autonomous multi-agent reasoning & MCP (Stage 6)
npm run test:execution         # Payment link creation & idempotency (Stage 7)
npm run test:truth             # State consistency & reconciliation (Stage 8)

# AI Agent System safety tests
npm test tests/agent/test_agent_prompt_injection.ts  # Prompt injection firewall
npm test tests/agent/test_agent_tool_injection.ts    # Tool execution safety
npm test tests/agent/test_agent_temporal_firewall.ts # Non-retroactive time firewall

# Advanced test suites
npm run test:core              # Core hardening & edge-case stress tests
npm run test:infra             # Infrastructure resilience & pool tests
npm run test:integration       # End-to-end integration & pipeline flow
npm run stress:all             # Comprehensive system-wide stress testing
npm run test:black-box         # Black-box acceptance criteria verification

# V6 Phase-specific suites (Phases 4–12 + Live Money)
npm run test:v6-phase4         # Tenancy & Auth Platform
npm run test:v6-phase5         # Canonical Event Connector
npm run test:v6-phase6         # Razorpay Provider Adapter
npm run test:v6-phase7         # Unified Ledger & Reconciliation
npm run test:v6-phase8         # Economic Engine & Bayesian Calibration
npm run test:v6-phase9         # Action Authority & Multi-Level Kill Switch
npm run test:v6-phase10        # Execution Layer & Token Bucket Limiter
npm run test:v6-phase11        # Specialist Agents & Human-in-the-Loop Review
npm run test:v6-phase12        # Simulation Harness & Synthetic Generator
npm test tests/v6/test_live_money_environment.ts # Production isolation & client pool

# Counterfactual and agent demos
npm run experiments:causal     # Intervention effectiveness & causal lift
npm run demo:agent             # Autonomous multi-agent recovery demo
npm run demo:real-recovery     # Real payment recovery verification
```

---

## 🐳 Docker Deployment

ULTRON ships with a complete 4-service Docker Compose configuration:

```bash
# Start all services
docker compose up -d

# Services:
#   ultron-postgres   → PostgreSQL 15 (port 5432)
#   ultron-redis      → Redis 7 (port 6379)
#   ultron-backend    → ULTRON API (port 3001)
#   ultron-frontend   → Next.js Dashboard (port 3000)
#   ultron-nginx      → Reverse Proxy (port 80)
```

```yaml
# Architecture
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   NGINX     │────▶│   Backend    │────▶│  PostgreSQL  │
│   :80       │     │   :3001      │     │   :5432      │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
┌─────────────┐     ┌──────▼───────┐
│  Frontend   │     │    Redis     │
│   :3000     │     │   :6379      │
└─────────────┘     └──────────────┘
```

---

## 📐 Design Principles

> These are **non-negotiable** and enforced throughout the codebase:

| # | Principle | Enforcement |
|:---:|---|---|
| 1 | Every failed payment becomes a `RecoveryOpportunity` record | Pipeline rejects raw webhook processing |
| 2 | Score by **incremental** probability, not raw | `incremental_prob = intervention − natural` |
| 3 | Every opportunity resolves to **ACT / WAIT / ABSTAIN** | Tri-state decision enum enforced in types |
| 4 | Portfolio-level allocation with **shadow price** | Greedy sort by IVEN with capacity cutoff |
| 5 | Action Authority is a **separate deterministic gate** | Two-stage: economic → compliance veto |
| 6 | LLM may only **explain**, never execute | `llm/explainer.ts` — no LLM on execution path |
| 7 | Every stage writes reasoning to **durable log** | Ledger + audit trail built from stored fields |
| 8 | Probabilities labeled as **model-estimated** | `probability_disclaimer` field on every Score |
| 9 | **Dual-Mode Execution** — Test Sandbox + Real Money Live | Safe 5-link cap in Test Mode; encrypted AES-256 vault & fail-closed credentials in Live |

---

## ⚠️ Disclaimer

> **ULTRON provides dual-mode operational capability:** an isolated **Test Sandbox** (capped at 5 payment links with synthetic/test keys) and an enterprise **Real Money Live Mode** (protected by AES-256 encrypted credential vaults, tenant isolation, and deterministic Action Authority gates). All counterfactual probability metrics and recovery lift estimates displayed across the dashboard are explicitly **model-estimated** — because true counterfactual outcomes are fundamentally unobservable for any individual real payment.

---

<p align="center">
  <sub>Built with 🧠 economic reasoning and ⚡ autonomous execution</sub>
  <br/>
  <sub>All monetary values in paise (₹) · Dual Environment (Test Sandbox + Real Money Live)</sub>
  <br/>
  <sub>🌐 Production Dashboard: <a href="https://ultron-power.vercel.app/dashboard" target="_blank">https://ultron-power.vercel.app/dashboard</a></sub>
</p>

