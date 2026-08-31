import pytest
from backend.providers.health import provider_health_service, ProviderHealthStatus

def test_provider_health_telemetry():
    provider_health_service.record_call("razorpay", latency_ms=85.0, is_success=True)
    h = provider_health_service.get_health("razorpay")
    assert h.status == ProviderHealthStatus.AVAILABLE
    assert h.avg_latency_ms > 0

    # Simulate timeout failure
    provider_health_service.record_call("razorpay", latency_ms=8000.0, is_success=False, is_timeout=True)
    h_timeout = provider_health_service.get_health("razorpay")
    assert h_timeout.status == ProviderHealthStatus.TIMEOUT
