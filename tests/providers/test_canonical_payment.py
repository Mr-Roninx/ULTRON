import pytest
from backend.providers.models import CanonicalPayment, CanonicalPaymentState

def test_canonical_payment_precision_minor_units():
    # 24,700.00 INR = 2,470,000 paise
    pmt = CanonicalPayment(
        internal_payment_id="pmt_101",
        provider="razorpay",
        provider_payment_id="pay_101",
        customer_id="c_ananya",
        merchant_id="m_01",
        amount_minor=2470000,
        currency="INR",
        state=CanonicalPaymentState.SETTLED,
        created_at=1760000000,
        updated_at=1760000000
    )
    assert pmt.amount_minor == 2470000
    assert pmt.amount_major == 24700.0
    assert isinstance(pmt.amount_minor, int)
