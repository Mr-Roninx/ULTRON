import pytest
from synthetic_payment_universe.interference.cross_opportunity import interference_engine

def test_cross_opportunity_interference():
    interference_engine.reset()
    cid = "c_inter_test"

    interference_engine.register_opportunity(cid, "SUBSCRIPTION", 5000.0, "sub_1")
    interference_engine.register_opportunity(cid, "INVOICE", 20000.0, "inv_1")
    interference_engine.register_opportunity(cid, "CHECKOUT", 8000.0, "chk_1")

    # Multi-opportunity customer experiences fatigue escalation upon outreach
    mult = interference_engine.apply_cross_action_interference(cid, "SEND_PAYMENT_LINK")
    assert mult > 1.0
