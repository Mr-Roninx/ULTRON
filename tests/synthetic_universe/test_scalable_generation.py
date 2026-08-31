import pytest
from synthetic_payment_universe.generator.universe_builder import SyntheticUniverseBuilder

def test_scalable_chunked_partition_builder():
    builder = SyntheticUniverseBuilder(master_seed=707)
    res = builder.build_partition(
        partition_name="dev",
        customer_count=20,
        payments_per_customer=5
    )

    assert res["customers_generated"] == 20
    assert res["payments_generated"] == 100
    assert res["payment_attempts_generated"] >= 100
    assert res["duration_seconds"] < 2.0
