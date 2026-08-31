from backend.providers.capabilities import ProviderCapabilitySet, ProviderCapability

def get_razorpay_capabilities() -> ProviderCapabilitySet:
    return ProviderCapabilitySet(
        provider_name="razorpay",
        capabilities={
            ProviderCapability.PAYMENT_RETRIEVAL,
            ProviderCapability.PAYMENT_STATUS_QUERY,
            ProviderCapability.ORDER_RETRIEVAL,
            ProviderCapability.PAYMENT_LINK_CREATION,
            ProviderCapability.PAYMENT_LINK_RETRIEVAL,
            ProviderCapability.PAYMENT_LINK_CANCELLATION,
            ProviderCapability.REFUND,
            ProviderCapability.CAPTURE,
            ProviderCapability.WEBHOOK_VERIFICATION,
            ProviderCapability.CUSTOMER_RETRIEVAL
        }
    )
