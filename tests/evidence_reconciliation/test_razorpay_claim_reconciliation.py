import pytest
from backend.providers.registry import provider_registry
from backend.providers.capabilities import ProviderCapability

@pytest.mark.fixture
def test_razorpay_adapter_capability_truth():
    rzp = provider_registry.get_provider("razorpay")
    assert rzp.capabilities.supports(ProviderCapability.PAYMENT_LINK_CREATION) is True
    assert rzp.capabilities.supports(ProviderCapability.REFUND) is True
    assert rzp.is_sandbox is True
