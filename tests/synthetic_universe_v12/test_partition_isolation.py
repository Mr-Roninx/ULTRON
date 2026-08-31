import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world

def test_partition_metadata_isolation(tmp_path):
    w_dev = create_world(master_seed=12345, partition_name="dev", profile=WorldProfile.TINY, storage_dir=str(tmp_path / "dev"))
    w_eval = create_world(master_seed=12345, partition_name="evaluation", profile=WorldProfile.TINY, storage_dir=str(tmp_path / "eval"))

    assert w_dev.identity.partition_name == "dev"
    assert w_eval.identity.partition_name == "evaluation"
    assert w_dev.identity.world_id != w_eval.identity.world_id
