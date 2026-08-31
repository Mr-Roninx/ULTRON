import pytest
from synthetic_payment_universe.interference.cross_opportunity import interference_engine

def test_cross_opportunity_interference_v12():
    interference_engine.reset()
    cid = "c_overlap_v12"

    interference_engine.register_opportunity(cid, "SUBSCRIPTION", 12000.0, "sub_1")
    interference_engine.register_opportunity(cid, "INVOICE", 85000.0, "inv_1")

    # Outreach on multi-opportunity customer increases global fatigue
    mult = interference_engine.apply_cross_action_interference(cid, "SEND_PAYMENT_LINK")
    assert mult > 1.0
