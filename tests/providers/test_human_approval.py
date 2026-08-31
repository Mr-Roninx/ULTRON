import pytest
from financial.authority import authority_engine, AuthorityLevel

def test_human_approval_authority_boundaries():
    # Sensitive high-risk actions (REFUND, DISCOUNT) require APPROVE
    assert authority_engine.is_authorized("REFUND_PAYMENT", AuthorityLevel.OBSERVE) is False
    assert authority_engine.is_authorized("WAIT", AuthorityLevel.AUTONOMOUS) is True
    assert authority_engine.is_authorized("SEND_PAYMENT_LINK", AuthorityLevel.AUTONOMOUS) is True
