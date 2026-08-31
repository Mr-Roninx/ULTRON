import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.episodic import memory_store, EpisodeRecord
from simulator.clock import clock

class TestAdversarialMemoryIntegrity(unittest.TestCase):
    def setUp(self):
        memory_store.memories.clear()
        clock.reset()

    def test_episodic_record_schema_constraints(self):
        """Hostile attempt to store unstructured or futuristic records into memory."""
        record = EpisodeRecord(
            customer_id="c_1",
            failure_type="INSUFFICIENT_FUNDS",
            action_taken="RETRY",
            result="SUCCESS",
            recovery_amount=500.0,
            timestamp=clock.now()
        )
        memory_store.store(record)
        
        mems = memory_store.retrieve("c_1", "INSUFFICIENT_FUNDS")
        self.assertEqual(len(mems), 1)
        self.assertEqual(mems[0].timestamp, 0)

    def test_future_timestamp_rejection_or_isolation(self):
        """Records stored in memory must match virtual clock or past timestamps."""
        clock.advance(500)
        record = EpisodeRecord(
            customer_id="c_1",
            failure_type="GATEWAY_TIMEOUT",
            action_taken="RECONCILE",
            result="FAILED",
            recovery_amount=0.0,
            timestamp=clock.now()
        )
        memory_store.store(record)
        
        retrieved = memory_store.retrieve("c_1", "GATEWAY_TIMEOUT")
        self.assertEqual(retrieved[0].timestamp, 500)

if __name__ == '__main__':
    unittest.main()
