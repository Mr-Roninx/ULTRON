import os
import pytest
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world, snapshot_world, restore_world

def test_world_snapshot_and_restore(tmp_path):
    w = create_world(master_seed=333, profile=WorldProfile.TINY, storage_dir=str(tmp_path))
    w.advance_to(1760007200)

    snap_path = snapshot_world(w)
    assert os.path.exists(snap_path)

    restored_db = os.path.join(tmp_path, "restored_world.db")
    restored_world = restore_world(snap_path, restored_db)
    assert restored_world.identity.current_time == 1760007200
    assert restored_world.identity.master_seed == 333
