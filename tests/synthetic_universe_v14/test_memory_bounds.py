import os
import sys
import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_memory_bounded_execution(tmp_path):
    w = create_emergent_population_world(master_seed=707, profile_name="tiny", storage_dir=str(tmp_path))
    assert sys.getsizeof(w.customers) < 200000000 # Under 200MB
