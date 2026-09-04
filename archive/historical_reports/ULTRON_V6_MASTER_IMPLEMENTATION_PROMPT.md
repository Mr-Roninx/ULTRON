# ULTRON v6 — Master Implementation Prompt (Refined)

**Status:** Ready to drive implementation, conditional on Section 2 (Open Decisions) being answered first.
**Supersedes:** the original 110-section ULTRON v6 master prompt. That document is preserved as source material; this one reorganizes it into priority tiers, removes duplication, and adds the gaps found during review (flagged inline with 🔶).

---

## 0. How to use this document

1. Read Section 1 (product statement) and Section 3 (non-negotiable invariants) — these never change regardless of phase.
2. Get Section 2 (open decisions) answered by a human with product/finance/legal authority. Do not let an implementation agent guess at these.
3. Execute Section 8 (phased plan) in order. Each phase has an explicit gate — do not start phase N+1 until phase N's gate passes.
4. Everything else in this document (data model, security, testing) is reference material the phases point back to.

---

## 1. Product Statement

ULTRON v6 is an external, autonomous payment-recovery platform that connects to a merchant's existing application (OdooX) and payment provider (Razorpay) via API integration. It observes payment failures, investigates recovery opportunities with a bounded AI agent, scores them with deterministic economics, enforces financial authority independently of the AI, executes only permitted recovery actions, verifies outcomes against provider truth, reconciles state, learns from finalized results, and presents everything in one merchant dashboard.

The merchant keeps OdooX and their existing Razorpay integration unchanged. ULTRON is a layer around that system, not a replacement for it. If ULTRON is unreachable, OdooX's ordinary payment flow must be unaffected; only recovery actions pause.

---

## 2. Open Decisions Requiring Human Input 🔶

**Do not let an implementation agent (or Claude Code) fill these in on its own — wrong defaults here are either a compliance problem or a money-safety problem.**

| # | Decision | Why it can't be inferred |
|---|---|---|
| D1 | Regulatory posture: does ULTRON's handling of payment data trigger PCI-DSS scope, and does RBI data-localization apply given Razorpay is an India-regulated aggregator? | Legal/compliance question, not engineering |
| D2 | Customer contact compliance: what consent/opt-in basis justifies ULTRON-initiated payment-link messages to a customer (SMS/email)? Applicable regime (TRAI DND, CAN-SPAM, etc.)? | Legal question; blocks any action type that contacts a customer directly |
| D3 | Initial default policy values: `max_autonomous_recovery_amount`, `max_actions_per_hour`, `max_customer_contacts`, `human_review_threshold` for the pilot tenant | Business risk tolerance, not derivable from code |
| D4 | Partial-payment accounting semantics (§ "PARTIAL vs MISMATCH", when if ever a partial amount counts toward recovery) | Finance/accounting decision |
| D5 | Whether ULTRON ever needs OdooX DB read access, or API/webhook is provably sufficient | Requires actually inspecting OdooX's integration (Phase 1) — see § "compelling technical reason" rule; default assumption is **no DB access** until proven otherwise |
| D6 | Secrets management: where do Razorpay/ULTRON secrets live at rest (KMS, Vault, encrypted column)? | Infra decision affecting §"Secret Security" implementation |
| D7 | Dashboard session auth: password+session, SSO, and whether MFA is required for Owner/Admin roles given live-money exposure | Security posture decision |
| D8 | Currency scope for v6: INR only, or multi-currency from day one? | Affects schema (`amount_paise` assumes INR-style minor units) |
| D9 | Agent worker queue technology and reconciliation job scheduler | Infra choice, constrained by whatever OdooX/ULTRON v5.1 already run on |

Phase 1 (below) should surface D5 with evidence. D1, D2, D3, D4, D6, D7 must be answered by the merchant/product owner before Phase 4 begins. D8, D9 must be answered before Phase 3.

---

## 3. Non-Negotiable Invariants

These hold in every phase, with no configuration flag able to disable them.

**Financial authority separation**
- AI may: observe, investigate, diagnose, hypothesize, plan, propose, learn.
- AI may never: call a Razorpay write API, mark anything recovered, approve Action Authority, modify ledger state, disable the kill switch, or change platform safety limits.
- Only one module (`Executor`) may issue Razorpay write calls. The public API and the agent's tool surface must be structurally incapable of reaching it — not merely policy-restricted.
- A hard runtime assertion (`authorization.status === AUTHORIZED`, or equivalent) gates every write; failure throws, never logs-and-continues.

**Provider truth**
- Razorpay is the only source of truth for payment outcome. OdooX's local status and ULTRON's own execution success are never treated as settlement proof.
- `RECOVERED` requires provider-confirmed payment evidence (API fetch and/or verified webhook). Payment-link creation ≠ recovered. Ambiguous/timeout states resolve to `UNKNOWN` or `PENDING`, never `RECOVERED`.
- No synthetic "paid" webhooks, no faked settlement, ever — including in tests.

**Test/Live separation**
- `RAZORPAY_TEST` and `RAZORPAY_LIVE` are structurally separate environments/credentials. No UI toggle alone activates Live; no silent Test→Live switching; environment is never inferred from key prefix alone.

**Tenant isolation**
- Every tenant-owned row carries `tenant_id`. Every query enforces it from the authenticated session/key, never from request body or path alone. `GET /v1/payments/:id` must fail closed if `tenant_id` doesn't match the caller.

**Kill switches**
- Platform-level and tenant-level kill switches both exist, both stop financial execution and agent autonomous loops, both default engaged (`SAFE`) on first Live activation.

**Idempotency**
- Execution identity = `tenant_id + opportunity_id + action + decision_id`. Duplicate requests return the existing result; they never create a second action.

---

## 4. Architecture

```
ODOOX ── existing payment flow ──▶ RAZORPAY
  │                                    │
  │ (event, non-blocking)              │ webhook / API fetch
  ▼                                    ▼
        ULTRON Event Gateway ──▶ Recovery Core (Agent → Economics → Market → Authority → Executor)
                                        │
                                        ▼
                                   Razorpay (writes only via Executor)
```

- OdooX must not depend on ULTRON for ordinary payment success. If ULTRON is down, OdooX payments continue; a recovery-in-progress pauses safely rather than guessing.
- Two distinct event ownership types: `ODOOX_EVENT` (merchant app observation), `RAZORPAY_WEBHOOK` (provider push), `RAZORPAY_API_FETCH` (provider pull), `ULTRON_RECONCILIATION` (ULTRON's own deterministic resolution). Only the latter three ever produce provider truth.
- 🔶 Deduplication key across the two ingestion paths (resolving D-nothing, this is an engineering default, not an open decision): join on `(environment, provider, provider_payment_id)`. If `provider_payment_id` isn't yet known at OdooX-event time, hold the event as `PROVISIONAL` until the Razorpay-side event arrives to confirm identity, rather than guessing a join.

---

## 5. Data & Tenancy Model

**Core entities:** tenants, organizations, users, memberships, roles, sessions.

**Every tenant-owned table needs `tenant_id`, minimum set:** payments, opportunities, events, provider_connections, executions, reconciliation, ledger, agent_runs, plans, memories, outcomes, analytics, api_keys, audit_records.

**API keys:** prefix + key ID + hashed secret + tenant + environment + scopes + timestamps (`created_at`, `last_used_at`, `expires_at`, `revoked_at`). Raw secret shown once at creation only, format like `ul_live_xxxxxxxxx`.

**Scopes (no scope may include `financial:execute`):**
`events:write`, `events:read`, `payments:read`, `recoveries:read`, `analytics:read`, `agent:read`, `integrations:read`, `integrations:write`.

**Auth surfaces are separate systems:** merchant-to-machine → Bearer API key; dashboard → session auth (🔶 D7 decides mechanism); provider webhooks → Razorpay signature verification, raw body only, verified before parsing.

**Roles and function boundaries:**
| Role | Cannot do |
|---|---|
| Viewer | mutate anything |
| Analyst | configure provider connections |
| Operator | rotate owner credentials |
| Admin | bypass platform safety ceilings |
| Owner | directly mark a provider recovery |

**Property-level protection** — reject any client-supplied change to: `tenant_id`, `environment`, `authority_result`, `recovered`, `amount_paid`, `provider_status`, `ledger_state`, `agent_role`, platform safety limits.

---

## 6. Canonical Event Model

All inbound events normalize to `CanonicalPaymentEvent`:

```
event_id, tenant_id, source, provider, environment,
payment_id, order_id, payment_link_id,
amount_paise, currency, method, status,
failure_code, failure_type, attempt_number,
customer_reference, occurred_at, received_at, correlation_id
```

Strict schema validation on ingestion; reject rather than coerce malformed events. Only emit OdooX event types that actually exist in the current integration (`payment.created/authorized/failed/captured/cancelled/expired` — confirm the real set in Phase 1, don't manufacture types).

---

## 7. Provider Adapter (`src/providers/razorpay/`)

Encapsulates: authentication, payment fetch, payment-link fetch/create, webhook signature verification, event normalization, capability discovery. All Razorpay-specific logic stays inside this boundary.

- Provider connection record: `tenant_id, provider, environment, status, credential_reference`.
- Client instantiated from explicit, immutable environment config — never inferred from key prefix.
- Capability discovery must gate what actions are even offered: don't expose `DISABLE_RECOVERY_TYPE_X` in the UI if it hasn't been verified against the live provider API.
- Webhook secret is stored and handled separately from the API key secret; never surfaced to frontend, agent, logs, or audit UI.

---

## 8. Agent & Deterministic Core Boundary

- Reuse the existing v5.1 agent (21-state lifecycle, budgets, loop guard, memory, planning/replanning, EVOI, portfolio intelligence, learning, replay). Make it tenant-aware; don't rewrite it.
- Agent tool surface: `READ`, `ANALYZE`, `PROPOSE` only. It can emit a recovery *proposal*; it can never emit a provider execution command.
- IVEN stays a deterministic score. The agent may nudge bounded inputs (e.g. `ΔP ∈ [-0.10, +0.10]`); it cannot return a final IVEN value.
- Pipeline is strictly: `Agent Proposal → Deterministic Economics → Recovery Market → Action Authority → Executor`. Authority can veto at any point; nothing downstream (agent, merchant UI, public API) can override that veto.
- Live agent runs are bounded: steps, tool calls, LLM calls, wall time, replans — inherit v5.1 limits unless evidence justifies a change.
- Memory is tenant-scoped, temporally scoped, provenance-tracked; no cross-merchant retrieval. Only finalized provider outcomes become learning signal (`actual_outcome ∈ {1, 0, null}`), and only finalized outcomes become memory episodes.

---

## 9. Live-Money Safety Gates

**Activation handshake (all required, in order):** authenticated tenant with required role → provider connection exists and passes verification → Live credential reference exists → merchant explicitly acknowledges Live mode → ULTRON safety config valid → kill switch available → audit event written → integration becomes `ACTIVE`.

**Rollout modes (default `OBSERVE_ONLY`):** `OBSERVE_ONLY → PROPOSE_ONLY → HUMAN_APPROVAL → AUTONOMOUS_RECOVERY`. Connecting Live credentials never auto-advances this.

**Autonomy levels (default `LEVEL_0`):** `0` observe / `1` analyze+propose / `2` execute predefined low-risk actions / `3` full autonomy under guardrails. Merchant must explicitly opt into higher levels; platform ceilings always override merchant-set policy.

**Per-tenant policy fields:** `allowed_actions, minimum_iven, maximum_recovery_amount, max_actions_per_hour, max_customer_contacts, human_review_threshold, risk_threshold, autonomy_level` — seeded from D3 for the pilot tenant, never left at framework defaults.

**Rollout scoping:** explicit tenant-level allowlist for autonomous recovery (e.g. only `tenant_001`), never a global switch.

**Action allowlist:** start with one verified action (e.g. `SEND_PAYMENT_LINK`); all others `DISABLED` until independently validated against the live provider API.

**Provider failover:** circuit breaker on Razorpay unavailability → no autonomous execution during the outage → affected opportunities go to `WAIT` or `HUMAN_REVIEW`.

---

## 10. Reconciliation, Ledger, Learning

State chain: `Provider → ProviderTruth → Reconciliation → Local State → Execution → Ledger → Learning → Memory`, applied as an atomic transaction where multiple local tables change together.

- Ledger entries require provider-confirmed amounts; `ΣDebit = ΣCredit` must hold; no provider-unconfirmed revenue entries permitted.
- Reconciliation SLA (webhook latency, polling latency) is *measured*, not claimed in advance.
- Replay reproduces decision/reasoning only — never re-executes a live financial action, unless a dedicated, clearly-labeled dry-run mechanism exists.

---

## 11. Dashboard & API Surface

**Dashboard routes:** `/dashboard /payments /recoveries /agent /analytics /integrations /api-keys /policies /audit /settings`. Live vs Test must be visually unambiguous (a persistent `LIVE — REAL PAYMENTS` or `TEST DATA` banner). Merchant-facing "why" explanations for a recovery must be assembled from stored records — financial claims are never LLM-generated free text.

**Minimum v1 API:**
```
POST/GET  /v1/events
GET       /v1/payments, /v1/payments/:id
GET       /v1/recoveries, /v1/recoveries/:id
GET       /v1/analytics/overview, /v1/analytics/recovery
GET/POST  /v1/integrations
POST      /v1/integrations/:id/verify
POST      /v1/integrations/:id/activate
GET/POST  /v1/api-keys
POST      /v1/api-keys/:id/rotate
DELETE    /v1/api-keys/:id
GET       /v1/agent/missions, /v1/agent/missions/:id
GET       /v1/audit
GET       /health, /ready  (optionally /v1/integrations/:id/health)
```
No breaking changes within `/v1`. Health endpoints report DB/provider/agent/queue status without leaking secrets.

---

## 12. Security Requirements

Review against OWASP API Security categories, with a control/test/result/limitation entry for each:
Broken Object-Level Authorization · Broken Authentication · Broken Object Property-Level Authorization · Unrestricted Resource Consumption · Broken Function-Level Authorization · Sensitive Business Flow Abuse · SSRF · Security Misconfiguration · Improper Inventory Management · Unsafe Consumption of APIs.

- Per-tenant rate limits on event ingestion, reads, analytics, exports, agent queries — concrete numbers to be set during Phase 4, not left undefined.
- PII minimization: never send CVV, PAN, payment credentials, or auth headers to the LLM; use tokenized references.
- Secrets (Razorpay API secret, webhook secret, ULTRON API secret) never reach browser, agent, logs, analytics, or public API responses — location decided by D6.

---

## 13. Testing Strategy

**v5.1 regression must keep passing:** `test:agent`, `test:core`, `test:infra`, `test:state-consistency`, `test:causal-stats`, `verify:test-counts`, `experiments:causal`, `build` — via the project's actual package scripts.

**New `tests/v6/` suite (minimum):**
`test_tenant_isolation, test_authentication, test_api_keys, test_scopes, test_object_authorization, test_function_authorization, test_property_authorization, test_event_ingestion, test_event_idempotency, test_webhook_security, test_provider_connection, test_live_test_separation, test_live_activation, test_policy_enforcement, test_agent_tenant_isolation, test_agent_live_boundary, test_financial_boundary, test_kill_switch, test_rate_limits, test_resource_limits, test_odoox_integration, test_recovery_callback, test_end_to_end`.

**Live-money testing rules (hard constraints, not suggestions):**
- No uncontrolled automated scripts against Live. No synthetic "paid" webhooks. No mass testing.
- Every Live test is a merchant-authorized real transaction, human-observed, under a strict amount ceiling, with full provider verification.
- Before the first real autonomous recovery, all of these must pass independently: Observe-only, Human-approval, Provider verification, Reconciliation, Ledger, Kill switch, Tenant isolation, Authority.
- Kill-switch test must measure actual stop latency (active mission → kill signal → agent stops → confirm no provider write after the signal).
- Duplication test: fire a duplicate command in a controlled environment, confirm exactly one provider action results.
- Failure test: one small merchant-authorized failure scenario, confirm no false recovery / no false ledger entry results.
- Success test: one small merchant-authorized live recovery, capturing the full evidence chain (opportunity → decision → authority → provider action → provider payment → reconciliation → ledger → outcome).

---

## 14. Phased Execution Plan (with gates)

| Phase | Work | Gate to advance |
|---|---|---|
| 1 | Inspect real OdooX + ULTRON v5.1 source: payment lifecycle, webhook handling, ID schemes, credential storage, framework. Resolve D5 with evidence. | Written findings doc exists; no assumptions remain about how OdooX actually works |
| 2 | Map OdooX↔Razorpay payment lifecycle precisely (real event types only) | Lifecycle diagram matches source code, not the spec's guesses |
| 3 | Design canonical event contract + resolve D8 (currency scope), D9 (queue/scheduler) | Schema reviewed against real OdooX event shapes |
| 4 | Build tenant/auth/API-key platform; resolve D6 (secrets), D7 (session auth) | `test_tenant_isolation`, `test_authentication`, `test_api_keys`, `test_scopes` all pass |
| 5 | Build OdooX→ULTRON event connector (backend-only credential use) | `test_event_ingestion`, `test_event_idempotency`, `test_odoox_integration` pass; OdooX ordinary payments unaffected by ULTRON downtime (verified, not assumed) |
| 6 | Razorpay provider adapter, webhook + capability discovery | `test_webhook_security`, `test_provider_connection` pass |
| 7 | Make v5.1 engine tenant-aware (no rewrite) | All v5.1 regression scripts still pass; `test_agent_tenant_isolation`, `test_agent_live_boundary`, `test_financial_boundary` pass |
| 8 | Merchant dashboard | Live/Test banner unambiguous in manual review; "why" explanations trace to stored records only |
| 9 | Observe-only mode against real (Test-env) OdooX data | Real failed payments produce opportunities/proposals; zero executions occur |
| 10 | Human-approval mode | A human approves a proposal; execution occurs only after approval; `test_policy_enforcement` passes |
| 11 | Configure limited Live pilot — requires D1–D4 answered, default policy values from D3 applied, allowlisted single tenant, single action type, amount ceiling set | `test_kill_switch`, `test_rate_limits`, `test_resource_limits` pass; full OWASP review documented |
| 12 | One real, merchant-authorized live recovery | Independently Razorpay-confirmed; evidence chain captured end to end |
| 13 | Verify Razorpay provider truth independently (never OdooX DB as proof) | API/webhook confirmation on file |
| 14 | Verify reconciliation + ledger (`ΣDebit=ΣCredit`) + learning pipeline | Ledger balances; only finalized outcomes reached learning/memory |
| 15 | Full security + tenant-isolation test pass | `test_object_authorization`, `test_function_authorization`, `test_property_authorization` all pass |
| 16 | Generate final evidence package and acceptance report | See Section 15 |

**Stop after the verified pilot.** Do not proceed to broader rollout without a separate decision cycle.

---

## 15. Documentation & Evidence Deliverables

**Docs:** `ULTRON_V6_PLATFORM_ARCHITECTURE.md, _API.md, _SECURITY.md, _TENANCY.md, _LIVE_MONEY_MODEL.md, _ODOOX_QUICKSTART.md, _RAZORPAY.md, _RUNBOOK.md`

**Evidence:** `results/v6/{tenant_verification, api_verification, odoox_integration, razorpay_live_verification, reconciliation, security, end_to_end}.json`

**Final reports:** `ULTRON_V6_FINAL_ACCEPTANCE_REPORT.md`, `ULTRON_V6_FINAL_ACCEPTANCE.json`, containing a capability matrix (Implemented / Tested / Runtime Verified / Provider Verified / Status) covering: Merchant Account, Tenant Isolation, API Keys, Event API, OdooX Integration, Razorpay Connection, Webhook, Provider Verification, Agent, Memory, Planning, Replanning, Portfolio, IVEN, Market, Authority, Execution, Reconciliation, Ledger, Learning, Dashboard, Kill Switch, Security, Live Pilot.

**Verdict** must be one of `DEMO_READY / PILOT_READY / LIVE_LIMITED_PILOT / NOT_READY`. Never claim `production-ready` without a separate production certification process. Never classify `LIVE_PROVIDER_VERIFIED` unless an actual live payment was independently confirmed by Razorpay — execution success, link creation, OdooX state, screenshots, or local reconciliation alone are all insufficient; otherwise classify `LIVE_NOT_VERIFIED`.

---

## 16. Absolute Rules (carried forward unchanged)

Do not rewrite OdooX unnecessarily. Do not bypass Razorpay. Do not treat OdooX status as provider truth. Do not give the agent live Razorpay write credentials. Do not let the public API execute financial actions. Do not trust client-supplied tenant IDs. Do not expose secrets to frontend or LLM. Do not fake payment success or webhooks. Do not manually mark payments recovered. Do not silently switch Test→Live. Do not enable autonomous live recovery globally. Do not start with unrestricted live execution. Do not break v5.1 or OdooX's existing flow. Do not build unnecessary microservices.
