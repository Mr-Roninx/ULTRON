# ULTRON v5.1 — Mission Replay & Cryptographic Fingerprinting Specification

## 1. Overview & Objective

The **Mission Replay Engine** (`src/agents/replay.ts`) introduces cryptographic SHA-256 fingerprinting and deterministic trace comparison across autonomous agent missions to ensure forensic auditability and non-repudiation.

---

## 2. Cryptographic Fingerprint Schema

A mission fingerprint represents a SHA-256 hash over the canonical concatenated representation of all causal trajectory components:

$$\text{Fingerprint} = \text{SHA-256}(\text{CanonicalTrace})$$

$$\text{CanonicalTrace} = \text{OPP} \parallel \text{GOAL} \parallel \text{STATES} \parallel \text{TOOLS} \parallel \text{PLANS} \parallel \text{PROPOSALS} \parallel \text{CHECKS} \parallel \text{STATUS}$$

Where:
- $\text{STATES}$: Chronological sequence of agent states (`TRIGGERED->OBSERVE->...->COMPLETE`)
- $\text{TOOLS}$: Hashes of tool names, input hashes, output hashes, and status
- $\text{PLANS}$: Plan versions and preferred action types
- $\text{PROPOSALS}$: Generated proposal types and approval states
- $\text{CHECKS}$: Action Authority 9-point compliance check names and pass/fail boolean verdicts

---

## 3. Replay Verification & Divergence Localization

When verifying a replay run against an original run, `MissionReplayEngine.verifyReplay()` performs differential analysis:

```typescript
export interface ReplayVerificationResult {
  original_run_id: string;
  replay_run_id: string;
  is_match: boolean;
  original_fingerprint: string;
  replay_fingerprint: string;
  divergence_detected: boolean;
  divergence_stage: 'STATE_TRANSITIONS' | 'TOOL_CALLS' | 'AUTHORITY_CHECKS' | 'PROPOSALS' | null;
  divergence_details: string | null;
  verified_at: string;
}
```

If a divergence occurs (e.g. an unexpected tool failure or altered state transition), the engine localizes the exact failure stage immediately.
