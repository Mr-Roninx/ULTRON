import pytest
from backend.providers.razorpay.adapter import RazorpayAdapter

@pytest.mark.sandbox
def test_razorpay_sandbox_payment_retrieval():
    adapter = RazorpayAdapter(is_sandbox=True)
    pmt = adapter.get_payment("pay_sandbox_demo_01")
    assert pmt.provider == "razorpay"
    assert pmt.amount_minor == 2470000
    assert pmt.currency == "INR"
