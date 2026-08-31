import pytest
from synthetic_payment_universe.schema.taxonomy import FailureTaxonomy, FailureCategory

def test_failure_taxonomy_richness():
    c_91 = FailureTaxonomy.get_code_info("91")
    assert c_91.category == FailureCategory.TRANSIENT
    assert c_91.recoverable_by_retry is True

    c_51 = FailureTaxonomy.get_code_info("51")
    assert c_51.category == FailureCategory.CUSTOMER_ACTION_REQUIRED

    c_41 = FailureTaxonomy.get_code_info("41")
    assert c_41.category == FailureCategory.HARD_DECLINE
