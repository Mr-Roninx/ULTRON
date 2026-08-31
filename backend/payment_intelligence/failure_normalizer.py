from typing import Dict, Any, Optional
from backend.payment_intelligence.schemas import (
    PaymentFailureRaw,
    NormalizedFailure,
    FailureClass,
    FailureSeverity
)
from backend.payment_intelligence.failure_taxonomy import failure_taxonomy

GATEWAY_CODE_MAPPINGS: Dict[str, Dict[str, str]] = {
    "stripe": {
        "insufficient_funds": "INSUFFICIENT_FUNDS",
        "card_declined": "DO_NOT_HONOR",
        "expired_card": "EXPIRED_CARD",
        "incorrect_cvc": "INVALID_CVV",
        "processing_error": "TIMEOUT",
        "rate_limit": "TIMEOUT",
        "authentication_required": "AUTH_REQUIRED",
        "3d_secure_failed": "3D_SECURE_FAILED",
        "api_connection_error": "NETWORK_ERROR",
        "account_closed": "CLOSED_ACCOUNT"
    },
    "razorpay": {
        "BAD_REQUEST_ERROR": "UNKNOWN_ERROR",
        "GATEWAY_ERROR": "GATEWAY_DOWN",
        "INSUFFICIENT_FUNDS": "INSUFFICIENT_FUNDS",
        "EXCEEDS_LIMIT": "LIMIT_EXCEEDED",
        "PAYMENT_TIMED_OUT": "TIMEOUT",
        "PAYMENT_FAILED": "DO_NOT_HONOR",
        "AUTH_FAILED": "3D_SECURE_FAILED",
        "BANK_OFFLINE": "ISSUER_UNAVAILABLE"
    },
    "adyen": {
        "NotEnoughBalance": "INSUFFICIENT_FUNDS",
        "ExpiredCard": "EXPIRED_CARD",
        "CVCDeclined": "INVALID_CVV",
        "3DNotAuthenticated": "3D_SECURE_FAILED",
        "IssuerUnavailable": "ISSUER_UNAVAILABLE",
        "AcquirerError": "GATEWAY_DEGRADED",
        "CardBlocked": "BLOCKED_ACCOUNT"
    },
    "gateway_a": {
        "51": "INSUFFICIENT_FUNDS",
        "54": "EXPIRED_CARD",
        "05": "DO_NOT_HONOR",
        "91": "ISSUER_UNAVAILABLE",
        "96": "GATEWAY_DOWN",
        "TO": "TIMEOUT",
        "3DS": "3D_SECURE_FAILED",
        "61": "LIMIT_EXCEEDED"
    },
    "gateway_b": {
        "ERR_BALANCE": "INSUFFICIENT_FUNDS",
        "ERR_EXPIRED": "EXPIRED_CARD",
        "ERR_TIMEOUT": "TIMEOUT",
        "ERR_AUTH": "AUTH_REQUIRED",
        "ERR_NETWORK": "NETWORK_ERROR",
        "ERR_UNAVAILABLE": "GATEWAY_DOWN",
        "51": "INSUFFICIENT_FUNDS",
        "54": "EXPIRED_CARD",
        "05": "DO_NOT_HONOR",
        "91": "ISSUER_UNAVAILABLE",
        "96": "GATEWAY_DOWN",
        "TO": "TIMEOUT",
        "3DS": "3D_SECURE_FAILED"
    },
    "gateway_c": {
        "INSUFFICIENT_FUNDS": "INSUFFICIENT_FUNDS",
        "CARD_EXPIRED": "EXPIRED_CARD",
        "TIMEOUT": "TIMEOUT",
        "GATEWAY_UNAVAILABLE": "GATEWAY_DOWN",
        "AUTH_TIMEOUT": "AUTH_TIMEOUT",
        "51": "INSUFFICIENT_FUNDS",
        "54": "EXPIRED_CARD",
        "05": "DO_NOT_HONOR",
        "91": "ISSUER_UNAVAILABLE",
        "96": "GATEWAY_DOWN"
    }
}

class FailureNormalizer:
    def normalize(self, failure_raw: PaymentFailureRaw) -> NormalizedFailure:
        gateway_key = failure_raw.gateway_id.lower()
        mapping = GATEWAY_CODE_MAPPINGS.get(gateway_key, {})
        
        # Look up raw code in gateway mapping or fallback to raw code directly if matches taxonomy
        normalized_reason = mapping.get(failure_raw.raw_code)
        if not normalized_reason:
            normalized_reason = mapping.get(failure_raw.raw_code.lower())
        if not normalized_reason:
            # Check if raw code is already a standard normalized taxonomy key
            from backend.payment_intelligence.failure_taxonomy import DETERMINISTIC_TAXONOMY
            if failure_raw.raw_code.upper() in DETERMINISTIC_TAXONOMY:
                normalized_reason = failure_raw.raw_code.upper()
            else:
                normalized_reason = "UNKNOWN_ERROR"

        rule = failure_taxonomy.get_rule(normalized_reason)

        return NormalizedFailure(
            failure_class=rule.failure_class,
            failure_reason=normalized_reason,
            severity=rule.severity,
            recoverability=rule.base_recoverability,
            customer_action_required=rule.customer_action_required,
            retry_eligible=rule.retry_eligible,
            typical_recovery_actions=list(rule.typical_recovery_actions),
            prohibited_actions=list(rule.prohibited_actions),
            recommended_investigation=list(rule.recommended_investigation),
            raw_code=failure_raw.raw_code,
            gateway_id=failure_raw.gateway_id
        )

failure_normalizer = FailureNormalizer()
