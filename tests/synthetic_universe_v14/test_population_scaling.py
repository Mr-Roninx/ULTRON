import pytest
from synthetic_payment_universe.world_v14.scaling.streaming_generator import StreamingPopulationGenerator

def test_streaming_population_generator(tmp_path):
    class DummyRepo:
        def __init__(self):
            self.total = 0
        def insert_items(self, chunk):
            self.total += len(chunk)

    repo = DummyRepo()
    gen = StreamingPopulationGenerator(repo, chunk_size=50)
    items = list(range(250))
    gen.stream_insert(items, repo.insert_items)
    assert repo.total == 250
