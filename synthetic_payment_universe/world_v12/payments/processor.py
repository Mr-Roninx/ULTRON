import random
from typing import Dict, Any, Tuple, Optional
from synthetic_payment_universe.world_v12.entities.payment import Payment, PaymentAttempt
from synthetic_payment_universe.world_v12.entities.ledger import SimulatedDoubleEntryLedger

class SimulatedPaymentProcessor:
    """
    Simulates real-world payment authorization pipeline with routing, latency, and double-entry ledger integration.
    """
    def __init__(self, ledger: SimulatedDoubleEntryLedger):
        self.ledger = ledger

    def process_payment_attempt(
        self,
        payment: Payment,
        gateway_health: float,
        rail: str,
        timestamp: int,
        subseed: int
    ) -> Tuple[PaymentAttempt, bool]:
        rng = random.Random(subseed)
        latency = round(rng.uniform(80.0, 350.0) if gateway_health > 0.5 else rng.uniform(1500.0, 5000.0), 1)

        # Authorization outcome depends causally on gateway health
        success = (rng.random() < gateway_health)

        attempt = PaymentAttempt(
            attempt_id=f"att_{payment.payment_id}_{payment.attempt_count}",
            payment_id=payment.payment_id,
            attempt_number=payment.attempt_count,
            rail=rail,
            gateway_id=payment.gateway_id,
            status="SUCCESS" if success else "FAILED",
            failure_code=None if success else ("91" if gateway_health < 0.3 else "TO"),
            latency_ms=latency,
            timestamp=timestamp
        )

        if success:
            payment.status = "SETTLED"
            payment.failure_code = None
            # Record double-entry ledger transaction: Debit Gateway Cash, Credit Merchant Settlement Clearing
            self.ledger.record_transaction(
                transaction_id=payment.payment_id,
                source_event_id=attempt.attempt_id,
                account_debit=f"BANK_CASH_{payment.gateway_id}",
                account_credit="MERCHANT_SETTLEMENT_CLEARING",
                amount=payment.amount,
                timestamp=timestamp,
                currency=payment.currency
            )
        else:
            payment.status = "FAILED"
            payment.failure_code = attempt.failure_code

        payment.attempt_count += 1
        return attempt, success
