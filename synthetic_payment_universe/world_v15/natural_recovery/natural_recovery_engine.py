import random
from typing import Optional, Dict, Any

class NaturalRecoveryEngine:
    """
    Evaluates whether an unassisted payment would have recovered on its own without agent intervention.
    """
    @staticmethod
    def evaluate_natural_recovery(
        payment_id: str,
        failure_code: str,
        customer_sensitivity: str,
        subseed: int = 12345
    ) -> Tuple[bool, int]:
        rng = random.Random(subseed + hash(payment_id) % 10000)

        # Base natural recovery probability by failure code
        # 91 (System error / timeout) has high natural recovery rate (~65%)
        # 51 (Insufficient funds) has moderate rate (~28% around salary)
        # 14 (Invalid card) has very low natural rate (~5%)
        base_rates = {
            "91": 0.65,
            "TO": 0.60,
            "51": 0.28,
            "14": 0.05
        }
        p = base_rates.get(failure_code, 0.35)

        if customer_sensitivity == "NATURAL_RECOVERER":
            p = min(0.95, p + 0.30)
        elif customer_sensitivity == "INTERVENTION_RESISTANT":
            p = min(0.85, p + 0.15)

        would_recover = rng.random() < p
        natural_delay_seconds = int(rng.uniform(1800, 21600)) if would_recover else 0 # 30m to 6h

        return would_recover, natural_delay_seconds
