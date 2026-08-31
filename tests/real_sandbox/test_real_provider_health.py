import pytest
from backend.providers.health import provider_health_service, ProviderHealthStatus

@pytest.mark.fixture
def test_real_provider_health_metrics():
    provider_health_service.record_call("razorpay", latency_ms=110.0, is_success=True)
    m = provider_health_service.get_health("razorpay")
    assert m.status == ProviderHealthStatus.AVAILABLE
    assert m.success_rate_percent >= 90.0
