import pytest
from synthetic_payment_universe.world_v15.observation.blind_firewall import BlindObservationFirewall
from backend.benchmark.firewall import FutureInformationLeakageError

def test_observation_firewall_blocks_lookahead():
    future_data = {"created_at": 1760000500, "amount": 10000.0}
    with pytest.raises(FutureInformationLeakageError):
        BlindObservationFirewall.sanitize(future_data, current_time=1760000000)
