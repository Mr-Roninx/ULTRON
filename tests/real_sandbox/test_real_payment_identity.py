import pytest
from backend.providers.models import PaymentIdentityMap

@pytest.mark.fixture
def test_payment_identity_mapping():
    id_map = PaymentIdentityMap(
        internal_payment_id="pmt_internal_9988",
        provider="razorpay",
        provider_account_id="acc_demo_01",
        provider_object_id="pay_rzp_9988",
        merchant_reference="merch_ananya_01",
        created_at=1760000000
    )
    assert id_map.internal_payment_id.startswith("pmt_internal_")
    assert id_map.provider_object_id.startswith("pay_")
