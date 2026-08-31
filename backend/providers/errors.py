class ProviderError(Exception):
    """Base exception for all payment provider operations."""
    pass

class ProviderAuthenticationError(ProviderError):
    """Authentication or credential configuration failed."""
    pass

class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded on provider API."""
    pass

class ProviderTimeoutError(ProviderError):
    """Provider API request timed out."""
    pass

class ProviderUnavailableError(ProviderError):
    """Provider service is temporarily offline or 5xx."""
    pass

class ProviderInvalidRequestError(ProviderError):
    """Invalid parameters, malformed payload, or 4xx."""
    pass

class WebhookVerificationError(ProviderError):
    """Webhook signature verification failed or payload tampered."""
    pass

class ReconciliationRequiredError(ProviderError):
    """Ambiguous or conflicting external state requires out-of-band reconciliation."""
    pass

class UnsupportedCapabilityError(ProviderError):
    """Attempted to execute an operation not supported by the provider."""
    pass

class EnvironmentSafetyError(ProviderError):
    """Action rejected by environment guard or production gate."""
    pass
