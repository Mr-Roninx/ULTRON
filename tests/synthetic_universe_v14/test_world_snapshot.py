import os
import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_atomic_snapshot(tmp_path):
    w = create_emergent_population_world(master_seed=77, profile_name="tiny", storage_dir=str(tmp_path))
    snap_path = w.snapshot()
    assert os.path.exists(snap_path)
    assert os.path.getsize(snap_path) > 0
