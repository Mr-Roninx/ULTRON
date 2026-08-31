import pytest
from backend.providers.razorpay.adapter import RazorpayAdapter
from backend.providers.models import CanonicalCustomer

@pytest.mark.fixture
def test_razorpay_adapter_operations():
    adapter = RazorpayAdapter(is_sandbox=True)
    cust = CanonicalCustomer(customer_id="c_ananya", name="Ananya Textiles", email="finance@ananya.com", phone="+919876543210")
    link = adapter.create_payment_link(
        internal_payment_id="pmt_rz_test_01",
        amount_minor=2470000,
        currency="INR",
        customer=cust,
        description="Recovery payment"
    )
    assert link.provider == "razorpay"
    assert link.amount_minor == 2470000
    assert link.status == "CREATED"

    pmt = adapter.get_payment("pay_123")
    assert pmt.amount_minor == 2470000
