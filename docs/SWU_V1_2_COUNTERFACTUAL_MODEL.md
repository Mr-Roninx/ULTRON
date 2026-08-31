# ULTRON Synthetic Payment Universe v1.2 Counterfactual Model

## 1. 5-Branch World Forking
For every decision point $t$, 5 isolated branches are evaluated:
1. `WAIT`
2. `RETRY`
3. `SEND_PAYMENT_LINK`
4. `SWITCH_GATEWAY`
5. `ESCALATE`

Branches use identical pre-decision latent states and common random numbers, ensuring unbiased causal comparison.
