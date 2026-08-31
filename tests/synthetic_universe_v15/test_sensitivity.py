import pytest
from synthetic_payment_universe.world_v15.configuration import ParameterRegistryV15

def test_parameter_registry_hashing():
    p1 = ParameterRegistryV15()
    p2 = ParameterRegistryV15()
    assert p1.get_config_hash() == p2.get_config_hash()

    p3 = ParameterRegistryV15(natural_recovery_base_p=0.45)
    assert p1.get_config_hash() != p3.get_config_hash()
