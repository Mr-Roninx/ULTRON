import pytest
from backend.providers.razorpay.capabilities import get_razorpay_capabilities
from backend.providers.capabilities import ProviderCapability

@pytest.mark.fixture
def test_razorpay_explicit_capabilities():
    caps = get_razorpay_capabilities()
    assert caps.supports(ProviderCapability.PAYMENT_LINK_CREATION) is True
    assert caps.supports(ProviderCapability.REFUND) is True
    assert caps.supports(ProviderCapability.WEBHOOK_VERIFICATION) is True
