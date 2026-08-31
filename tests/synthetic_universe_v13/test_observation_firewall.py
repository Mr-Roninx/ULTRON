import pytest
from synthetic_payment_universe.world_v13.observation.firewall import CivilizationObservationFirewall
from backend.benchmark.firewall import FutureInformationLeakageError

def test_observation_firewall_blocks_lookahead():
    now = 1760000000
    future_data = {"created_at": now + 500, "amount": 10000.0}
    with pytest.raises(FutureInformationLeakageError):
        CivilizationObservationFirewall.sanitize(future_data, now)
