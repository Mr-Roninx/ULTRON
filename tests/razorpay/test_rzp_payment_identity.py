import pytest
from backend.providers.models import PaymentIdentityMap

@pytest.mark.fixture
def test_razorpay_payment_identity_mapping():
    id_map = PaymentIdentityMap(
        internal_payment_id="pmt_rzp_99",
        provider="razorpay",
        provider_account_id="acc_rzp_demo",
        provider_object_id="pay_rzp_99",
        merchant_reference="merch_ananya_01",
        created_at=1760000000
    )
    assert id_map.provider == "razorpay"
    assert id_map.provider_object_id == "pay_rzp_99"
