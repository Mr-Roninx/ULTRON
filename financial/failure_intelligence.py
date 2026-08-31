from enum import Enum

class FailureCategory(str, Enum):
    TRANSIENT = "TRANSIENT"
    CUSTOMER_ACTION_REQUIRED = "CUSTOMER_ACTION_REQUIRED"
    CREDENTIAL_PROBLEM = "CREDENTIAL_PROBLEM"
    LIQUIDITY_RELATED = "LIQUIDITY_RELATED"
    GATEWAY_PROBLEM = "GATEWAY_PROBLEM"
    UNKNOWN = "UNKNOWN"
    NON_RETRYABLE = "NON_RETRYABLE"

from financial.failure_codes import GATEWAY_FAILURE_MAP

class FailureNormalizer:
    def normalize(self, raw_code: str, gateway_id: str) -> str:
        if gateway_id in GATEWAY_FAILURE_MAP:
            return GATEWAY_FAILURE_MAP[gateway_id].get(raw_code, "UNKNOWN_ERROR")
        return "UNKNOWN_ERROR"

class FailureClassifier:
    CLASSIFICATION_MAP = {
        "INSUFFICIENT_FUNDS": FailureCategory.LIQUIDITY_RELATED,
        "LIMIT_EXCEEDED": FailureCategory.LIQUIDITY_RELATED,
        "EXPIRED_CARD": FailureCategory.CREDENTIAL_PROBLEM,
        "INVALID_CVV": FailureCategory.CREDENTIAL_PROBLEM,
        "DO_NOT_HONOR": FailureCategory.NON_RETRYABLE,
        "STOLEN_CARD": FailureCategory.NON_RETRYABLE,
        "3D_SECURE_FAILED": FailureCategory.CUSTOMER_ACTION_REQUIRED,
        "OTP_REQUIRED": FailureCategory.CUSTOMER_ACTION_REQUIRED,
        "TIMEOUT": FailureCategory.TRANSIENT,
        "NETWORK_ERROR": FailureCategory.TRANSIENT,
        "GATEWAY_TIMEOUT": FailureCategory.GATEWAY_PROBLEM,
        "GATEWAY_DOWN": FailureCategory.GATEWAY_PROBLEM,
        "ISSUER_UNAVAILABLE": FailureCategory.TRANSIENT,
        "91": FailureCategory.TRANSIENT,
        "UNKNOWN_ERROR": FailureCategory.UNKNOWN
    }

    def classify(self, normalized_code: str) -> FailureCategory:
        return self.CLASSIFICATION_MAP.get(normalized_code, FailureCategory.UNKNOWN)

class RetryabilityResolver:
    RETRYABLE_CATEGORIES = {
        FailureCategory.TRANSIENT,
        FailureCategory.GATEWAY_PROBLEM,
        FailureCategory.UNKNOWN # can retry unknown to see what happens, or maybe not. Spec says retryable logic. Let's say yes for unknown.
    }
    
    def is_retryable(self, category: FailureCategory) -> bool:
        return category in self.RETRYABLE_CATEGORIES

class ReconciliationResolver:
    def resolve(self, payment_id: str) -> str:
        # In a real system, this would call out to a gateway API.
        # Here we just mock a resolution for simulator tests.
        from simulator.world import world
        from simulator.models import PaymentStatus
        import random
        payment = world.payments.get(payment_id)
        if not payment:
            return PaymentStatus.FAILED.value
            
        # Mock resolution
        if payment.status == PaymentStatus.RECONCILING:
            # Deterministic for tests if needed, but let's just return FAILED as default
            return PaymentStatus.FAILED.value
        return payment.status.value

failure_normalizer = FailureNormalizer()
failure_classifier = FailureClassifier()
retryability_resolver = RetryabilityResolver()
reconciliation_resolver = ReconciliationResolver()
