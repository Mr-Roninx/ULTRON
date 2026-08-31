from typing import Dict, Any, Optional
from backend.payment_intelligence.schemas import FailureClass, NormalizedFailure, PaymentFailureRaw
from backend.payment_intelligence.failure_normalizer import failure_normalizer
from backend.payment_intelligence.failure_taxonomy import failure_taxonomy

class FailureClassifier:
    def classify_raw(self, failure_raw: PaymentFailureRaw) -> NormalizedFailure:
        return failure_normalizer.normalize(failure_raw)

    def classify_code(self, raw_code: str, gateway_id: str = "generic", amount: float = 0.0) -> NormalizedFailure:
        raw = PaymentFailureRaw(
            gateway_id=gateway_id,
            raw_code=raw_code,
            amount=amount
        )
        return failure_normalizer.normalize(raw)

    def get_failure_class(self, failure_reason: str) -> FailureClass:
        return failure_taxonomy.get_rule(failure_reason).failure_class

failure_classifier = FailureClassifier()
