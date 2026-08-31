import pytest
from backend.providers.razorpay.adapter import RazorpayAdapter
from backend.providers.models import CanonicalCustomer

@pytest.mark.sandbox
def test_razorpay_sandbox_payment_link():
    adapter = RazorpayAdapter(is_sandbox=True)
    cust = CanonicalCustomer(customer_id="c_ananya", name="Ananya Textiles", email="finance@ananya.com", phone="+919876543210")
    link = adapter.create_payment_link(
        internal_payment_id="pmt_rzp_link_01",
        amount_minor=2470000,
        currency="INR",
        customer=cust,
        description="Demo Recovery"
    )
    assert link.provider == "razorpay"
    assert "https://rzp.io/i/" in link.short_url
