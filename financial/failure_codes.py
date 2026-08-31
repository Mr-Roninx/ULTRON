# Provider-specific failure code mappings
GATEWAY_FAILURE_MAP = {
    "stripe": {
        "insufficient_funds": "INSUFFICIENT_FUNDS",
        "expired_card": "EXPIRED_CARD",
        "incorrect_cvc": "INVALID_CVV",
        "do_not_honor": "DO_NOT_HONOR",
        "authentication_required": "3D_SECURE_FAILED",
        "api_connection_error": "NETWORK_ERROR",
        "rate_limit": "TIMEOUT",
    },
    "razorpay": {
        "BAD_REQUEST_ERROR": "UNKNOWN_ERROR",
        "GATEWAY_ERROR": "GATEWAY_DOWN",
        "INSUFFICIENT_FUNDS": "INSUFFICIENT_FUNDS",
        "EXCEEDS_LIMIT": "LIMIT_EXCEEDED"
    },
    "adyen": {
        "NotEnoughBalance": "INSUFFICIENT_FUNDS",
        "ExpiredCard": "EXPIRED_CARD",
        "CVCDeclined": "INVALID_CVV",
        "3DNotAuthenticated": "3D_SECURE_FAILED"
    }
}
