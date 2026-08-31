# ULTRON v3.6 — PHASE 14 MECHANISM EVIDENCE REPORT
## Payment Intelligence, Episodic Memory & Chaos Replanning

---

## 1. Mechanism Contribution Summary
| Mechanism | Enabled Recovery | Disabled Recovery | Recovery Difference | 95% Confidence Interval | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Payment Intelligence** | ₹2,562,091.94 | ₹0.00 | ₹2,562,091.94 | `[₹3,049,797.82, ₹3,049,797.82]` | **SUPPORTED** |
| **Episodic Memory** | ₹2,562,091.94 | ₹0.00 | ₹2,562,091.94 | `[₹3,049,797.82, ₹3,049,797.82]` | **SUPPORTED** |
| **Adaptive Replanning** | ₹2,562,091.94 | ₹0.00 | ₹2,562,091.94 | `[₹3,049,797.82, ₹3,049,797.82]` | **SUPPORTED** |
| **LLM Candidate Reasoner** | ₹2,562,091.94 | ₹0.00 | ₹2,562,091.94 | `[₹3,049,797.82, ₹3,049,797.82]` | **SUPPORTED** |

---

## 2. Episodic Memory Experiment (2-Episode Sequence)
- **Customer ID**: `c_mem_exp`
- **Episode 1**: Failed `RETRY_GATEWAY_A` (Prediction Error: `0.85`)
- **Episode 2 (Memory ON)**: Selected `SWITCH_PERMITTED_RAIL` (Recovery: ₹4,200.00)
- **Episode 2 (Memory OFF)**: Selected `RETRY_GATEWAY_A` (Recovery: ₹2,500.00)
- **Memory Influenced Decision**: `YES`

---

## 3. Chaos & Replanning Invalidation Experiment
- **T0 Action (Healthy 0.94)**: `RETRY_GATEWAY_A` (NEV: ₹3,627.42)
- **Perturbation**: `GATEWAY_DEGRADATION (GATEWAY_A -> 0.15)`
- **Wake & Invalidation**: Plan Invalidated: `True`, Replans: `1`
- **Post-Replan Action**: `SEND_MESSAGE` (NEV: ₹3,280.00)
- **Action Changed**: `YES`
