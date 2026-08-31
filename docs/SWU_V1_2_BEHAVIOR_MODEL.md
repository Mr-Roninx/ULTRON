# ULTRON Synthetic Payment Universe v1.2 Behavior Model

## 1. Latent Profiles & Fatigue Accumulation
- Profiles: `SALARY_CYCLE`, `CASHFLOW_VOLATILE`, `PRICE_SENSITIVE`, `LOYAL_CUSTOMER`, `LOW_ENGAGEMENT`, `HIGH_ENGAGEMENT`, `BUSINESS_MONTH_END`, `HIGH_FATIGUE`, `RECOVERY_RESPONSIVE`, `STANDARD`.
- Fatigue: Observable score $\in [0.0, 1.0]$. Outreach actions add channel-specific fatigue deltas ($\Delta \text{Email}=0.05, \Delta \text{SMS}=0.08, \Delta \text{WhatsApp}=0.10, \Delta \text{Voice}=0.20$), reducing conversion probabilities.
