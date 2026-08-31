import pytest
from backend.providers.registry import provider_registry

@pytest.mark.fixture
def test_provider_matrix_support_levels():
    providers = provider_registry.list_providers()
    assert "razorpay" in providers

    rzp = provider_registry.get_provider("razorpay")
    assert rzp is not None
    assert rzp.capabilities is not None
