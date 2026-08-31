from typing import List, Any, Callable
from synthetic_payment_universe.world_v14.repository import SQLiteEmergentRepository

class StreamingPopulationGenerator:
    """
    Chunks population creation to maintain strictly bounded memory even for millions of entities.
    """
    def __init__(self, repository: SQLiteEmergentRepository, chunk_size: int = 500):
        self.repository = repository
        self.chunk_size = chunk_size

    def stream_insert(self, items: List[Any], insert_func: Callable[[List[Any]], None]):
        for i in range(0, len(items), self.chunk_size):
            chunk = items[i:i + self.chunk_size]
            insert_func(chunk)
