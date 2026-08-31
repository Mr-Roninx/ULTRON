# ULTRON: Autonomous Economic Control Plane for Failed-Payment Recovery

**Technical Specification & Test Mode Prototype v1.0**  
*Repository*: [ULTRON (GitHub: Mr-Roninx/ULTRON)](https://github.com/Mr-Roninx/ULTRON.git)  
*Tech Stack*: Node.js (v24 / `node:sqlite`) + TypeScript + Express + React/Next.js + Tailwind CSS + Razorpay Node SDK (Test Mode)

---

## 1. Overview & Problem Definition

Razorpay, Stripe, Adyen, and Zuora already do smart per-payment retry timing. **ULTRON is the layer above retry timing**: a system that treats every failed payment as a **Recovery Opportunity** competing against every other opportunity for scarce, costly recovery capacity (payment links, customer fatigue budget), and that can rationally choose to do **nothing** when acting isn't economically justified.

### The Core Paradigm
- **Standard Systems Ask**: *"Can we recover this payment?"*
- **ULTRON Asks**: *"Is recovering this payment worth spending our next unit of limited recovery capacity — and does action survive deterministic compliance rules?"*

---

## 2. Non-Negotiable Architectural Principles

1. **Opportunity-First Ingestion**: Raw webhook events are never acted upon directly; every failure is normalized into a `RecoveryOpportunity` record before entering the pipeline.
2. **Incremental Economic Value ($\text{IVEN}$)**: Scored by incremental recovery probability ($\Delta = P_{\text{intervention}} - P_{\text{natural}}$), operational delivery cost (₹4.00), and customer fatigue penalties.
3. **Discrete Decision Triad**: Every opportunity resolves to exactly one of three states: `ACT`, `WAIT`, or `ABSTAIN`.
4. **Portfolio Greedy Allocation & Shadow Price**: Under capacity constraints ($K=5$ links per batch run), greedy ranking allocates capacity and exposes the marginal accepted opportunity's value as a market shadow price ($\lambda$).
5. **Two-Stage Architecture (Economic Allocation vs Action Authority)**: Economic ranking (Stage 1) is decoupled from deterministic compliance vetoes (Stage 2). Action Authority evaluates **every opportunity** in the portfolio and can veto an `ACT` decision independent of economics.
6. **Market-Bypass Safeguard**: `confidence_recheck` in Action Authority is designed as an independent fail-closed safeguard against market-bypass scenarios (e.g. unallocated execution attempts reaching the gate directly), ensuring low-confidence opportunities can never be executed even if the market stage is skipped.
7. **Zero LLM on Execution Path**: Zero LLMs sit on the decision or execution path.
8. **Durable Stored Audit Trail**: The "Why?" screen is assembled strictly by reading stored SQLite records, never synthesized at view time.
9. **Strict Financial Accounting**: The "$ Recovered" dashboard KPI reflects **strictly real, reconciled payments**, never synthetic estimations.

---

## 3. The 7-Stage Pipeline

```
  Stage 1: Event Fabric Ingestion (HMAC-SHA256 verification & deduplication)
    │
    ▼
  Stage 2: Perception Normalization (hard / soft / unknown taxonomy & customer profiling)
    │
    ▼
  Stage 3: Economic Reasoning Engine (Incremental probability Δ, fatigue curve, IVEN)
    │
    ▼
  Stage 4: Recovery Market Greedy Allocator (Cap K=5 ranking, Shadow price λ calculation)
    │
    ▼
  Stage 5: Action Authority Compliance Gate (5 deterministic checks across all opportunities)
    │
    ▼
  Stage 6: Execution Engine (Zero-bypass assertion, Razorpay Test Mode link creation)
    │
    ▼
  Stage 7: Truth Engine & UI Dashboard (Dual-path webhook & fallback polling settlement)
```

---

## 4. Ingestion & Testing Safety Rule (CRITICAL)

> [!IMPORTANT]
> **Never POST to `/webhooks/razorpay` from a test script.**
> - Real incoming Razorpay webhook traffic lands at `POST /webhooks/razorpay` (records assigned `source: 'real'`).
> - Test scripts and simulation traffic must use `POST /internal/simulate-webhook` (records assigned `source: 'synthetic'` unconditionally).
> - Run `npm run db:reset` (`npx tsx scripts/reset_db.ts`) before any demo or recording to ensure a fresh, unpolluted database state.

---

## 5. Getting Started & Running Locally

### Prerequisites
- Node.js v20+ (tested on Node v24)
- Razorpay Test Mode Keys configured in `.env` (copy from `.env.example`)

### Installation & Launch
```bash
# 1. Install dependencies
npm install
cd frontend && npm install && cd ..

# 2. Reset database to clean schema
npm run db:reset

# 3. Start Backend API Daemon (Port 3001)
npm start

# 4. Start Frontend UI Dashboard (Port 3000)
cd frontend && npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** to interact with the ULTRON Control Plane.

---

## 6. Verification & Test Suite

ULTRON includes a comprehensive test suite covering all 7 stages and safety tripwires:

```bash
# Run isolated test suites for each stage
npm run test:webhook     # Stage 1: Ingestion, HMAC verification, deduplication
npm run test:perception  # Stage 2: Decline taxonomy & customer trust score
npm run test:economics   # Stage 3: IVEN economic scoring & cost models
npm run test:market      # Stage 4: Portfolio greedy allocation & shadow price
npm run test:authority   # Stage 5: 5 compliance checks & kill switch
npm run test:execution   # Stage 6: Real Razorpay SDK link creation & idempotency
npm run test:truth       # Stage 7: Webhook reconciliation & poller fallback

# Verify market-bypass safeguard (Fix 3)
npx tsx scripts/test_authority_bypass.ts

# Execute full end-to-end real recovery verification with Razorpay provider proof (Fix 2)
npx tsx scripts/demo_real_recovery_verification.ts

# Verify test isolation tripwire (Fix 5)
npm run verify:no-fake-webhooks
```
