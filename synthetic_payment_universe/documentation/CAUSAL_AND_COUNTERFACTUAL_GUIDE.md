# ULTRON Causal & Counterfactual Evaluation Guide

## 1. Causal Directed Acyclic Graph (DAG)
The synthetic environment models explicit structural causal dependencies:
```text
gateway_health --------------> authorization_probability ------> payment_outcome
                                                                      ^
customer_liquidity ----------> payment_probability -------------------+
                                                                      |
agent_action ----------------> customer_behavior ---------------------+
      |                              ^
      +-> communication_fatigue -----+
```

---

## 2. Common Random Numbers & Counterfactual Branches
For every decision point, 5 paired counterfactual branches are evaluated from the exact same initial state using shared latent seeds:
1. `WAIT`
2. `RETRY`
3. `SEND_PAYMENT_LINK`
4. `SWITCH_GATEWAY`
5. `ESCALATE`

This allows computing unbiased Treatment-Control differences, Regret, and $\Delta\text{NEV}$ without confounding randomness.
