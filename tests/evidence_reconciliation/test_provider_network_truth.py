import pytest
from backend.evidence.network_recorder import network_recorder

@pytest.mark.fixture
def test_outbound_network_recorder():
    network_recorder.clear()
    rec = network_recorder.record_call(
        correlation_id="corr_test_99",
        provider="razorpay",
        operation="payment_link_creation",
        hostname="api.razorpay.com",
        path_category="PAYMENT_LINKS",
        status_code=200,
        latency_ms=115.0,
        evidence_class="FIXTURE"
    )
    assert rec.provider == "razorpay"
    assert rec.status_code == 200
    assert len(network_recorder.get_calls_for_correlation("corr_test_99")) == 1
