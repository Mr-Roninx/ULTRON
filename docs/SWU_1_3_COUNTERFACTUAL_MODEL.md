# ULTRON-SWU-1.3 Counterfactual Model

## 1. 5-Branch Long-Horizon Evaluation
Evaluates 5 isolated counterfactual branches across 30-day horizons:
- `WAIT`: Evaluates natural recovery ($35.4\%$).
- `RETRY`: Evaluates smart issuer retry with gateway health dependencies.
- `SEND_PAYMENT_LINK`: Evaluates dynamic 1-click invoice link conversion vs. fatigue cost.
- `SWITCH_GATEWAY`: Evaluates secondary rail routing without congestion.
- `ESCALATE`: Evaluates human manual intervention.
Common Random Numbers (CRN) ensure identical stochastic draws across all branches.
