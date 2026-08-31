import pytest
import os
from backend.providers.razorpay.adapter import RazorpayAdapter

@pytest.mark.sandbox
def test_razorpay_sandbox_connection():
    adapter = RazorpayAdapter(is_sandbox=True)
    health = adapter.health_check()
    assert health["provider"] == "razorpay"
    assert health["status"] == "HEALTHY"
    assert health["sandbox"] is True
