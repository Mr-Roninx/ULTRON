import pytest
from financial.authority import authority_engine, AuthorityLevel

@pytest.mark.fixture
def test_action_authority_rejects_unauthorized_discount():
    # Only APPROVE level can execute APPLY_DISCOUNT
    assert authority_engine.is_authorized("APPLY_DISCOUNT", AuthorityLevel.OBSERVE) is False
