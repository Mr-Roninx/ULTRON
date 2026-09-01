# ULTRON v5.0 — Phase 3: Real LLM Provider Integration

**Phase Objective**: Integrate the REAL LLM provider into the agent reasoning layer using NVIDIA NIM (`nvidia/nemotron-3.5-lightning-30b-a3b`), establishing strict provider abstraction, context sanitation, structured schema parsing, timeout safeguards, deterministic fallbacks, and comprehensive telemetry logging.

---

## 1. LLM Provider Architecture ([`src/agents/llm_provider.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/llm_provider.ts))

The LLM Provider layer coordinates reasoning calls to NVIDIA NIM:

```
┌────────────────────────────────────────────────────────┐
│                   Context Builder                      │
│     (Strips Secrets, PII, Enforces Temporal Bounds)    │
└───────────────────────────┬────────────────────────────┘
                            │ SanitizedPromptContext
                            ▼
┌────────────────────────────────────────────────────────┐
│                 LLMProvider (NVIDIA NIM)               │
│  (Primary: nemotron-3.5-lightning-30b-a3b, 30s Timeout)│
└─────────────┬────────────────────────────┬─────────────┘
              │ Success                    │ Network Error / Timeout
              ▼                            ▼
┌───────────────────────────┐┌───────────────────────────┐
│   AgentSchemaValidator    ││  Deterministic Heuristic  │
│ (Validates Structured JSON││     Fallback Engine       │
│   into typed AgentIntent) ││ (Preserves Zero Downtime) │
└─────────────┬─────────────┘└─────────────┬─────────────┘
              └──────────────┬─────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│                   Agent Telemetry                      │
│        (Logs invocation to `llm_invocations`)          │
└────────────────────────────────────────────────────────┘
```

---

## 2. Demonstrated Autonomous Reasoning Flow

The integrated LLM reasoning flow executes across 6 sequential stages:

1. **OBSERVE**: Collects normalized decline context (`reason_code`, `decline_type`, `amount_paise`, `attempt_count`).
2. **INVESTIGATE**: Executes read-only tools (`get_gateway_state`, `get_customer_history`, `get_failure_history`).
3. **LLM DIAGNOSE**: Invokes `nvidia/nemotron-3.5-lightning-30b-a3b` with sanitized prompt context to produce structured diagnosis and root cause analysis.
4. **HYPOTHESIZE**: Generates hypotheses regarding customer liquidity, card expiration, and retry feasibility.
5. **PLAN**: Synthesizes a multi-step proposed plan with explicit `validity_assumptions` (e.g. gateway health $\ge 0.75$).
6. **PROPOSE**: Emits structured candidate proposals (`create_agent_proposal`) to the deterministic market.

---

## 3. Real Execution Verification

Live test execution was verified against the NVIDIA NIM endpoint using `scripts/test_llm_explanation.ts`:
- **Endpoint**: `https://integrate.api.nvidia.com/v1/chat/completions`
- **Model**: `nvidia/nemotron-3.5-lightning-30b-a3b`
- **Latency**: ~25-40s (Deep reasoning model)
- **Output**: Verified structured generation of economic rationales, market shadow price explanations, and action authority compliance verdicts for both `AUTHORIZED` and `BLOCKED` payment opportunities.

---

## 4. Safety Invariants Enforced

- **Zero LLM Financial Authority**: The LLM outputs structured proposals, semantic signals ($0.0 \le s \le 1.0$), and natural language explanations. Zero LLM output directly executes a payment link or modifies an authority record.
- **Zero Secrets / PII in Context**: Context Builder automatically filters out API keys, webhook secrets, authorization headers, PAN, CVV, and raw database IDs.
- **Durable Audit Trail**: Every LLM call records prompt hash, completion text, token usage, latency, and model identifier in the `llm_invocations` table.

---

## 5. Test Verification Results

- **Live NVIDIA NIM Decision Explainer (`test_llm_explanation.ts`)**: ✅ PASS
- **LLM Provider Abstraction & Fallback (`test_agent_llm_fallback.ts`)**: ✅ PASS
- **Master Agent Safety Suite (`npm run test:agent`)**: **20 PASSED / 0 FAILED**
- **Deterministic Core Hardening (`npm run test:core`)**: **5 PASSED / 0 FAILED**
- **Hardened Infrastructure (`npm run test:infra`)**: **3 PASSED / 0 FAILED**
