import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator

def test_deterministic_customer_reproducibility():
    mgr1 = MasterSeedManager(12345)
    mgr2 = MasterSeedManager(12345)
    mgr3 = MasterSeedManager(54321)

    gen1 = CustomerGenerator(mgr1)
    gen2 = CustomerGenerator(mgr2)
    gen3 = CustomerGenerator(mgr3)

    c1 = gen1.generate_customer(1)
    c2 = gen2.generate_customer(1)
    c3 = gen3.generate_customer(1)

    # Identical seeds must produce identical entities
    assert c1.customer_id == c2.customer_id
    assert c1.average_transaction_value == c2.average_transaction_value
    assert c1.latent_profile == c2.latent_profile

    # Different seed must produce different entity
    assert c1.average_transaction_value != c3.average_transaction_value or c1.latent_profile != c3.latent_profile
