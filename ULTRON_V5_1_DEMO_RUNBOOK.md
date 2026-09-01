# ULTRON v5.1 — Demonstration & Live Verification Runbook

This runbook guides operators through demonstrating and verifying ULTRON's autonomous economic control plane.

---

## 1. Quick Start Commands

### Seed Synthetic & Real Opportunities
```bash
npm run seed
```

### Run Master Agent Regression (28 Tests)
```bash
npm run test:agent
```

### Run Deterministic Core Hardening (5 Tests)
```bash
npm run test:core
```

### Run Infrastructure Hardening (3 Tests)
```bash
npm run test:infra
```

### Run 8-Experiment Causal Benchmark Suite
```bash
npm run experiments:causal
```

---

## 2. Interactive Mission Demos

### Demo 1: Multi-Opportunity Portfolio Sweep
```bash
npx tsx -e "import { AgentOrchestrator } from './src/agents/orchestrator.js'; AgentOrchestrator.executePortfolioSweep({ capacity: 5 }).then(console.log);"
```

### Demo 2: Concurrent Multi-Mission Batch Execution
```bash
npx tsx -e "import { MissionConcurrencyCoordinator } from './src/agents/concurrency.js'; MissionConcurrencyCoordinator.executeBatch({ opportunityIds: ['synth_02_insufficient_funds_att1', 'synth_04_expired_card'] }).then(console.log);"
```

### Demo 3: Live Razorpay Test Mode Mission & Provider Truth
```bash
npx tsx scripts/test_end_to_end_razorpay_mission.ts
```

### Demo 4: Cryptographic Replay & Divergence Verification
```bash
npx tsx tests/agent/test_replay.ts
```

---

## 3. UI Dashboard Verification

### Start Backend
```bash
npm start
```
*Listens on `http://localhost:3001`*

### Start Frontend Dashboard
```bash
cd frontend && npm run dev
```
*Open `http://localhost:3000` in browser to view the live dashboard, shadow pricing gauge, and 6-stage forensic "Why?" drawer.*
