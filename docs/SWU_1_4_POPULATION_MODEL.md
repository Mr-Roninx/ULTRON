# ULTRON-SWU-1.4 Population Model

## 1. Customer Cohorts
- `SALARY_CYCLE_CONSUMER` (35%): Paycheck-aligned liquidity cycles.
- `VOLATILE_INCOME_SMB` (20%): Cashflow-sensitive purchasing patterns.
- `HIGHLY_LOYAL` (15%): High purchase intent and trust resilience.
- `PRICE_SENSITIVE` (15%): Elastic purchase frequency.
- `ENTERPRISE_PROCUREMENT` (5%): Large PO invoices with Net-30/60 terms.
- `SEASONAL_CONSUMER` (5%) & `LOW_ENGAGEMENT` (5%).

## 2. Merchant Lifecycles
- `NEW` $\rightarrow$ `GROWING` $\rightarrow$ `STABLE` $\rightarrow$ `STRESSED` $\rightarrow$ `DECLINING`.
- Transition rules evaluate monthly volume, outstanding receivables, and customer retention.
