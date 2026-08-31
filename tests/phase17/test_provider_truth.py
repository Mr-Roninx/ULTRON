import pytest
from backend.llm.provider_health import provider_health_tracker, ProviderHealthStatus

def test_provider_health_truth_tracking():
    provider_health_tracker.reset()
    
    # Record mock 402 attempt
    rec = provider_health_tracker.record_attempt(
        provider="HuggingFace",
        model="Qwen3.8-2.4T",
        credential_available=True,
        request_success=False,
        status=ProviderHealthStatus.CREDIT_EXHAUSTED,
        latency_ms=120.0,
        http_status=402,
        fallback_used=True
    )
    
    assert rec.status == ProviderHealthStatus.CREDIT_EXHAUSTED
    assert rec.fallback_used is True
    
    out_file = provider_health_tracker.export_truth()
    assert out_file is not None
