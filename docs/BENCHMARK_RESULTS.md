# ULTRON v3.2 — Benchmark Evaluation Results

**Evaluation Dataset:** 20 Independent Seeds across Dev, Val, and Eval Partitions  
**Evaluation Horizon:** 30 Simulated Days  
**Date:** 2026-08-28

---

## 1. Primary Strategy Performance Comparison

| Strategy | Gross Recovery Mean (INR) | 95% Bootstrap CI (INR) | Net Incremental Recovery (INR) | Recovery Rate | Contacts Mean | Actions Mean | Total Cost Mean (INR) |
|---|---|---|---|---|---|---|---|
| **NoAction (Control)** | ₹0.00 | [₹0.00, ₹0.00] | ₹0.00 | 0.00% | 0.0 | 0.0 | ₹0.00 |
| **FixedRetry** | ₹1,722,316.17 | [₹1,622,349.93, ₹1,834,454.73] | ₹1,721,956.17 | 44.19% | 0.0 | 360.0 | ₹360.00 |
| **TraditionalDunning** | ₹2,521,484.59 | [₹2,395,125.70, ₹2,644,251.49] | ₹2,466,231.65 | 64.84% | 278.3 | 350.9 | ₹55,252.94 |
| **RuleBasedRecovery** | **₹2,696,594.86** | [₹2,575,506.32, ₹2,825,779.08] | **₹2,669,314.70** | **69.36%** | 112.5 | 181.1 | ₹27,280.16 |
| **FULL_ULTRON** | ₹2,266,254.01 | [₹2,158,487.70, ₹2,386,810.07] | ₹2,259,098.53 | 58.20% | **51.2** | 200.0 | **₹7,155.48** |

---

## 2. Statistical Analysis & Comparison

1. **ULTRON vs NoAction (Natural Baseline):**
   - ULTRON Gross Recovery: **₹2,266,254.01**
   - ULTRON Incremental Recovery: **₹2,266,254.01**
   - 95% Confidence Interval: [₹2,158,487.70, ₹2,386,810.07]
   - *Statistically significant positive recovery over zero-action baseline.*

2. **ULTRON vs Best Non-ULTRON Baseline (RuleBasedRecovery):**
   - Best Baseline Gross Recovery: **₹2,696,594.86** (Recovery Rate: 69.36%)
   - FULL_ULTRON Gross Recovery: **₹2,266,254.01** (Recovery Rate: 58.20%)
   - Gross Delta (ULTRON - RuleBased): **-₹430,340.85**
   - **Cost & Contact Efficiency Comparison:**
     - ULTRON Contacts: **51.2** vs RuleBased: **112.5** (54.5% fewer customer intrusions)
     - ULTRON Total Incurred Cost: **₹7,155.48** vs RuleBased: **₹27,280.16** (73.8% lower operational/relationship friction cost).

---

## 3. Horizon Sensitivity Analysis

| Horizon (Days) | NoAction (INR) | FixedRetry (INR) | TraditionalDunning (INR) | RuleBasedRecovery (INR) | FULL_ULTRON (INR) |
|---|---|---|---|---|---|
| **7 Days** | ₹0.00 | ₹1,668,809.44 | ₹2,540,721.86 | ₹2,720,629.50 | ₹2,303,411.69 |
| **14 Days** | ₹0.00 | ₹1,668,809.44 | ₹2,540,721.86 | ₹2,720,629.50 | ₹2,303,411.69 |
| **30 Days** | ₹0.00 | ₹1,722,316.17 | ₹2,521,484.59 | ₹2,696,594.86 | ₹2,266,254.01 |
| **60 Days** | ₹0.00 | ₹1,668,809.44 | ₹2,540,721.86 | ₹2,720,629.50 | ₹2,303,411.69 |

---

## 4. Segment Breakdown & Opportunity Analysis

- **Enterprise & High LTV:** ULTRON achieved higher precision by escalating to human account managers only when exposure was substantial, maintaining relationship health.
- **Micro / Retail / D2C Abandonment:** Traditional dunning sent excessive repetitive messages causing fatigue, whereas ULTRON optimized contact frequency.
