import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world, load_world

def test_world_persists_across_reloads(tmp_path):
    w1 = create_world(master_seed=999, profile=WorldProfile.TINY, storage_dir=str(tmp_path))
    db_path = w1.db_path

    # Reload world from SQLite database
    w2 = load_world(db_path)
    assert w2 is not None
    assert w2.identity.world_id == w1.identity.world_id
    assert w2.identity.master_seed == 999
