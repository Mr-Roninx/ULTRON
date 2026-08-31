import pytest
from financial.authority import authority_engine, AuthorityLevel

@pytest.mark.fixture
def test_razorpay_action_authority_boundaries():
    # Only AUTONOMOUS level can execute SEND_PAYMENT_LINK
    assert authority_engine.is_authorized("SEND_PAYMENT_LINK", AuthorityLevel.AUTONOMOUS) is True
    # OBSERVE cannot execute financial mutation
    assert authority_engine.is_authorized("SEND_PAYMENT_LINK", AuthorityLevel.OBSERVE) is False
