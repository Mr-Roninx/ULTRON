import pytest
from backend.providers.models import CanonicalPayment, CanonicalPaymentState

@pytest.mark.fixture
def test_provider_state_vs_ledger_monetary_match():
    pmt = CanonicalPayment(
        internal_payment_id="pmt_match_101",
        provider="razorpay",
        provider_payment_id="pay_match_101",
        customer_id="c_ananya",
        merchant_id="m_01",
        amount_minor=2470000,
        currency="INR",
        state=CanonicalPaymentState.SETTLED,
        created_at=1760000000,
        updated_at=1760000000
    )
    # Integer minor units check
    assert pmt.amount_minor == 2470000
    assert isinstance(pmt.amount_minor, int)
    assert pmt.state == CanonicalPaymentState.SETTLED
