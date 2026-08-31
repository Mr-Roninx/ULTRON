# ULTRON v5.0 Razorpay-Only Architecture

## 1. System Architecture
ULTRON v5.0 is streamlined to operate as:

$$\text{One Agent} + \text{One Real Provider (Razorpay)} + \text{One Synthetic World (SWU)}$$

```
                    ULTRON CORE
                         |
                Deterministic Authority
                         |
                 Razorpay Adapter
                         |
               Razorpay TEST MODE
                         |
                  WEBHOOK GATEWAY
                         |
             Signature + Idempotency
                         |
                Canonical Event
                         |
                   ULTRON Mission
                         |
                  Reconciliation
                         |
                       Ledger
```

Stripe and Adyen have been removed from the active execution plane. Razorpay is the sole external payment provider.
