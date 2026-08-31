import pytest
from synthetic_payment_universe.schema.taxonomy import FailureTaxonomy, FailureCategory

def test_failure_taxonomy_mapping():
    info_91 = FailureTaxonomy.get_code_info("91")
    assert info_91.category == FailureCategory.TRANSIENT
    assert info_91.recoverable_by_retry is True
    assert len(info_91.possible_true_root_causes) > 0

    info_41 = FailureTaxonomy.get_code_info("41")
    assert info_41.category == FailureCategory.HARD_DECLINE
    assert info_41.requires_human_escalation is True
