import pytest
from backend.safety.rate_limiter import action_rate_limiter

def test_action_rate_limiter_enforcement():
    action_rate_limiter.reset()
    
    cid = "c_rate_test"
    act = "SEND_PAYMENT_LINK" # limit = 2
    
    assert action_rate_limiter.check_and_record(cid, act) is True
    assert action_rate_limiter.check_and_record(cid, act) is True
    # 3rd attempt exceeds limit
    assert action_rate_limiter.check_and_record(cid, act) is False
