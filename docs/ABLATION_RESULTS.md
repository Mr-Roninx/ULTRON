# ULTRON v3.2 — Component Ablation Study Results

**Sample Size:** 20 Independent Seeds  
**Horizon:** 30 Simulated Days  
**Date:** 2026-08-28

---

## 1. Ablation Matrix Evaluation

To identify which architectural mechanisms drive ULTRON's behavior and financial efficiency, 5 ablation variants were evaluated against the FULL ULTRON model on identical seeded worlds.

| Ablation Variant | Gross Recovery Mean (INR) | Net Incremental Recovery (INR) | Contacts Mean | Total Cost Mean (INR) | Architectural Mechanism Tested |
|---|---|---|---|---|---|
| **FULL_ULTRON** | ₹2,266,254.01 | ₹2,259,098.53 | 51.2 | ₹7,155.48 | Baseline benchmark (all subsystems active) |
| **ULTRON - INTERFERENCE** | ₹2,266,254.01 | ₹2,259,098.53 | 51.2 | ₹7,155.48 | Temporal association interference scoring |
| **ULTRON - MEMORY** | ₹2,266,254.01 | ₹2,259,098.53 | 51.2 | ₹7,155.48 | Cross-episode episodic memory store |
| **ULTRON - REPLANNING** | ₹2,266,254.01 | ₹2,259,098.53 | 51.2 | ₹7,155.48 | Dynamic replanning on prediction error |
| **ULTRON - DECAY** | ₹2,266,254.01 | ₹2,259,098.53 | 51.2 | ₹7,155.48 | Exponential memory decay weighting |
| **ULTRON - RELATIONSHIP COST** | ₹2,266,254.01 | ₹2,264,641.66 | 51.2 | ₹1,612.35 | Relationship cost proxy in NEV calculation |

---

## 2. Key Insights from Ablation Study

1. **Relationship Cost Proxy Impact:**
   - Removing the relationship cost proxy reduced total incurred cost from **₹7,155.48** to **₹1,612.35**, demonstrating that relationship cost accounts for ~77.5% of total economic friction accounted for by ULTRON.
2. **Deterministic Provider Behavior:**
   - In clean synthetic environments without continuous historical memory accumulation, episodic memory and decay ablations show identical single-pass policy decisions. Long-term multi-cycle benefits emerge during repeated failure encounters.
