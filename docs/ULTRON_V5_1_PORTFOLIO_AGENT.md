# ULTRON v5.1 — Portfolio Agent Specification & Invariants

## 1. Overview & Objective

The **Portfolio Agent** (`src/agents/portfolio_agent.ts`) is an autonomous intelligence layer responsible for scanning, ranking, and proposing recovery actions across an entire portfolio of active payment recovery opportunities.

```
+-----------------------------------------------------------------------------+
|                            PORTFOLIO AGENT                                  |
|                                                                             |
|  [Pending Opportunities]                                                   |
|          │                                                                  |
|          ▼                                                                  |
|  ┌──────────────────┐    ┌─────────────────┐    ┌────────────────────────┐  |
|  │ Uncertainty      │    │ Information     │    │ Composite Priority     │  |
|  │ Model (3-Dim)    │───▶│ Value Estimator │───▶│ Ranking (Bounded IVEN) │  |
|  └──────────────────┘    └─────────────────┘    └────────────────────────┘  |
|                                                              │              |
|                                                              ▼              |
|                                                  ┌───────────────────────┐  |
|                                                  │  PortfolioProposal    │  |
|                                                  └───────────────────────┘  |
+--------------------------------------------------------------│--------------+
                                                               ▼
+─────────────────────────────────────────────────────────────────────────────+
|                    DETERMINISTIC FINANCIAL ENGINE                           |
|                                                                             |
|  Recovery Market (Authoritative) ──▶ Action Authority ──▶ Razorpay Executor |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Invariants & Authority Separation

1. **Zero Direct Execution Authority**: The Portfolio Agent CANNOT create payment links, invoke payment SDKs, or authorize financial transactions.
2. **Proposals vs Allocation**: The Portfolio Agent produces a `PortfolioProposal`. The deterministic `Recovery Market` (`src/market/allocator.ts`) remains the sole authority for allocating limited recovery capacity.
3. **No Direct IVEN Mutation**: The agent cannot directly modify or overwrite expected incremental value calculations.
4. **Deterministic Ranking**: Given identical inputs, the composite priority scoring algorithm produces mathematically identical ranks and proposals.
5. **Hard Decline Invariant**: Hard declines are strictly deprioritized (`proposed_action: 'WAIT'`) and cannot consume capacity.

---

## 3. Composite Priority Scoring Formulation

The priority score is a deterministic, bounded linear combination of five normalized signals:

$$\text{PriorityScore} = w_{\text{iven}} \cdot \tilde{\text{IVEN}} + w_{\text{time}} \cdot U_{\text{time}} + w_{\text{gw}} \cdot C_{\text{gw}} - w_{\text{fatigue}} \cdot R_{\text{fatigue}} - w_{\text{expiry}} \cdot R_{\text{expiry}}$$

### Weights (Fixed Configuration Constants)
- $w_{\text{iven}} = 0.40$ (Economic value driver)
- $w_{\text{time}} = 0.25$ (Time urgency)
- $w_{\text{gw}} = 0.15$ (Gateway switch confidence)
- $w_{\text{fatigue}} = 0.10$ (Customer contact fatigue risk)
- $w_{\text{expiry}} = 0.10$ (Payment link / window expiry risk)

### Signal Bounds & Normalization
- $\tilde{\text{IVEN}} = \text{clamp}\left(\frac{\text{IVEN}}{1{,}000{,}000\text{ paise}}, 0, 1\right)$
- $U_{\text{time}} = \text{clamp}\left(\frac{\text{Age}_{\text{hours}}}{72\text{ hours}}, 0, 1\right)$
- $R_{\text{fatigue}} = 0.6 \cdot \min\left(\frac{\text{Attempts}}{5}, 1\right) + 0.4 \cdot (1 - \text{TrustScore})$
- $R_{\text{expiry}} \in [0.0, 1.0]$ based on milestone age thresholds.

---

## 4. Telemetry & Audit Trail

Every execution of `PortfolioAgent.sweep()` generates:
- Total opportunities scanned
- Status distribution breakdown
- Full ranking list with composite scores and decomposed rationales
- Top-$K$ capacity-aligned recommendations
- Persisted in structured telemetry and test verification records
