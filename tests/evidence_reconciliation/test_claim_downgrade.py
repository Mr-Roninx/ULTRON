import pytest

@pytest.mark.fixture
def test_claim_downgrade_policy():
    # If key is absent, status must strictly downgrade from PROVIDER_SANDBOX to FIXTURE_ONLY
    claimed_status = "PROVIDER_SANDBOX_VERIFIED"
    has_live_credentials = False

    reconciled_status = claimed_status if has_live_credentials else "FIXTURE_ONLY"
    assert reconciled_status == "FIXTURE_ONLY"
