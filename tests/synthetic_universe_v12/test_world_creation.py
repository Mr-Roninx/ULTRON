import os
import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world

def test_world_creation_and_identity(tmp_path):
    world = create_world(master_seed=12345, profile=WorldProfile.TINY, storage_dir=str(tmp_path))
    assert world.identity.master_seed == 12345
    assert world.identity.world_version == "ULTRON-SWU-1.2"
    assert os.path.exists(world.db_path)
