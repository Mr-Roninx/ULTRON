import pytest
from backend.providers.registry import provider_registry
from backend.providers.capabilities import ProviderCapability
from backend.providers.errors import UnsupportedCapabilityError

def test_unsupported_capability_fails_closed():
    rzp = provider_registry.get_provider("razorpay")
    # Razorpay adapter does not support DIRECT_RETRY (uses PAYMENT_LINK_CREATION instead)
    with pytest.raises(UnsupportedCapabilityError):
        rzp.capabilities.require(ProviderCapability.DIRECT_RETRY)
