import pytest
from backend.providers.models import CanonicalPayment, CanonicalPaymentState

@pytest.mark.fixture
def test_razorpay_ledger_minor_units_precision():
    pmt = CanonicalPayment(
        internal_payment_id="pmt_rzp_led_01",
        provider="razorpay",
        provider_payment_id="pay_rzp_led_01",
        customer_id="c_ananya",
        merchant_id="m_01",
        amount_minor=2470000,
        currency="INR",
        state=CanonicalPaymentState.SETTLED,
        created_at=1760000000,
        updated_at=1760000000
    )
    assert pmt.amount_minor == 2470000
    assert pmt.currency == "INR"
    assert isinstance(pmt.amount_minor, int)
