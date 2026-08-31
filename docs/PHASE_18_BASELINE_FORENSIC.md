# ULTRON v4.0 — Phase 18: Forensic Baseline Audit

## 1. Executive Summary & Forensic Baseline
- **Baseline Test Suite**: 228 passed (0 failures, 0 regressions in 77.77s)
- **Phase 17 Historical Evidence**: Preserved immutable under `results/phase17/` and `docs/PHASE_17_*.md`.
- **Phase 17 Evaluated Partition**: Seeds `301–350` ($N=50$).
- **Phase 18 Evaluation Partition**: Dedicated independent partition: Seeds `401–500` ($N=100$).

---

## 2. Phase 17 Empirical Reality (Accepted as Immutable Truth)

| Metric | Phase 17 Measured Value | Scientific Interpretation |
| :--- | :--- | :--- |
| **Candidate Novelty** | **60.0%** | LLM proposes non-default alternatives |
| **Candidate Pool Influence** | **100.0%** | Candidate pool modified in 100% of cases |
| **Semantic Diagnosis Diff** | **100.0%** | Contextual hypothesis differentiated |
| **Mean Information Value ($\Delta\text{NEV}$)** | **INR 0.00** | Candidate expansion alone adds zero economic lift |
| **Final Decision Influence** | **0.0%** | Deterministic NEV ranking selects default action |
| **Mean LLM Regret** | **INR 2,120.80** | LLM preferred action suboptimal vs NEV argmax |
| **Deterministic Authority Invariant** | **100.0% PROVEN** | Zero monetary authority conceded |

---

## 3. Why Candidate Expansion Alone Yielded $\Delta\text{NEV} = 0$
In Phases 16–17, the LLM interacted with the agent loop strictly by appending strings to the candidate action list (e.g. `["WAIT", "RETRY_GATEWAY_A", "SEND_PAYMENT_LINK"]`).

However:
1. The **underlying parameters** feeding the NEV equation (recoverability rate, relationship cost factor, gateway health) remained purely static or rule-driven.
2. If the static parameterization evaluates `RETRY_GATEWAY_A` at ₹10,926.49 and `SEND_PAYMENT_LINK` at ₹5,830.00, simply adding `SEND_PAYMENT_LINK` to the candidate pool cannot change the mathematical argmax outcome unless the **contextual parameters** themselves reflect the semantic diagnosis.
3. Therefore, candidate pool influence collapses to $\Delta\text{NEV} = 0$ at the decision layer.

---

## 4. Phase 18 Architectural Solution: The Intelligence-to-Economics Bridge

Phase 18 introduces a formal, calibrated intelligence pipeline:

```text
WORLD OBSERVABLES (Telemetry, ISO Code, Payment History, Customer State)
  ↓
CONTEXTUAL FEATURE EXTRACTOR (FutureInformationFirewall enforced)
  ↓
LLM REASONING & SEMANTIC SIGNALS (Structured normalized signals in [0.0, 1.0])
  ↓
CALIBRATION ENGINE (Confidence attenuation, uncertainty damping, OOD clipping)
  ↓
BOUNDED ECONOMIC TRANSLATION (Translates to bounded modifiers within ±MAX_IMPACT)
  ↓
CANDIDATE GENERATION & FEASIBILITY (ActionRegistry security check)
  ↓
DETERMINISTIC NEV ENGINE (Scores all candidates using calibrated parameters)
  ↓
ACTION DECISION AUTHORITY (Strict argmax NEV selection; 0% LLM financial authority)
  ↓
EXECUTION & VIRTUAL CLOCK (Idempotent sandbox)
  ↓
OBSERVE → CHAOS 2.0 → REPLAN → LEARN → EPISODIC MEMORY
```

### Invariant Rules:
1. **The LLM never outputs currency values, probability numbers, or financial mutations.**
2. **Every semantic signal is bounded: $0.0 \le \text{value} \le 1.0$, with confidence and uncertainty.**
3. **The deterministic economic engine applies strictly bounded calibration multipliers.**
4. **All evaluations run on independent seeds 401–500 ($N=100$).**
