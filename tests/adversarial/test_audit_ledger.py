import sys
import os
import unittest
import copy

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.audit.ledger import audit_ledger, AuditEvent
from simulator.clock import clock
from simulator.world import world
from simulator.models import Customer, Payment, PaymentStatus

class TestAdversarialAuditLedger(unittest.TestCase):
    def setUp(self):
        audit_ledger.reset()
        world.reset()
        clock.reset()

    def test_genesis_hash_and_sequential_chaining(self):
        """Verify genesis block has previous_hash='GENESIS' and chain hashes link sequentially."""
        e1 = audit_ledger.log("TEST_EVENT_1", "ACTOR_1", {"key1": "val1"}, mission_id="m_1")
        self.assertEqual(e1.previous_hash, "GENESIS")
        self.assertTrue(len(e1.current_hash) == 64)

        e2 = audit_ledger.log("TEST_EVENT_2", "ACTOR_2", {"key2": "val2"}, mission_id="m_1")
        self.assertEqual(e2.previous_hash, e1.current_hash)

        e3 = audit_ledger.log("TEST_EVENT_3", "ACTOR_3", {"key3": "val3"}, mission_id="m_1")
        self.assertEqual(e3.previous_hash, e2.current_hash)

        valid, error = audit_ledger.verify_chain()
        self.assertTrue(valid, f"Chain verification failed: {error}")

    def test_payload_tampering_detected(self):
        """Tampering with an event's payload in the middle of the chain must be caught by verify_chain."""
        e1 = audit_ledger.log("EVENT_1", "ACTOR", {"amount": 100}, mission_id="m_1")
        e2 = audit_ledger.log("EVENT_2", "ACTOR", {"amount": 200}, mission_id="m_1")
        e3 = audit_ledger.log("EVENT_3", "ACTOR", {"amount": 300}, mission_id="m_1")

        # Tamper e2's payload object in the chain list
        tampered_event = AuditEvent(
            event_id=e2.event_id,
            mission_id=e2.mission_id,
            timestamp=e2.timestamp,
            actor=e2.actor,
            event_type=e2.event_type,
            input_hash=e2.input_hash,
            previous_hash=e2.previous_hash,
            current_hash=e2.current_hash,
            payload={"amount": 999999} # Modified!
        )
        audit_ledger._chain[1] = tampered_event

        valid, error = audit_ledger.verify_chain()
        self.assertFalse(valid)
        self.assertIn("Tampered", error)

    def test_previous_hash_tampering_detected(self):
        """Tampering with previous_hash pointer breaks the chain."""
        e1 = audit_ledger.log("EVENT_1", "ACTOR", {"step": 1})
        e2 = audit_ledger.log("EVENT_2", "ACTOR", {"step": 2})

        tampered_e2 = AuditEvent(
            event_id=e2.event_id,
            mission_id=e2.mission_id,
            timestamp=e2.timestamp,
            actor=e2.actor,
            event_type=e2.event_type,
            input_hash=e2.input_hash,
            previous_hash="FORGED_HASH_000000",
            current_hash=e2.current_hash,
            payload=e2.payload
        )
        audit_ledger._chain[1] = tampered_e2

        valid, error = audit_ledger.verify_chain()
        self.assertFalse(valid)
        self.assertIn("Broken hash chain", error)

    def test_event_deletion_detected(self):
        """Deleting an event in the middle breaks forward hash linking."""
        audit_ledger.log("EVENT_1", "ACTOR", {"step": 1})
        audit_ledger.log("EVENT_2", "ACTOR", {"step": 2})
        audit_ledger.log("EVENT_3", "ACTOR", {"step": 3})

        # Delete middle event
        del audit_ledger._chain[1]

        valid, error = audit_ledger.verify_chain()
        self.assertFalse(valid)
        self.assertIn("Broken hash chain", error)

    def test_event_reordering_detected(self):
        """Reordering events breaks the chain."""
        audit_ledger.log("EVENT_1", "ACTOR", {"step": 1})
        audit_ledger.log("EVENT_2", "ACTOR", {"step": 2})

        # Swap events
        audit_ledger._chain[0], audit_ledger._chain[1] = audit_ledger._chain[1], audit_ledger._chain[0]

        valid, error = audit_ledger.verify_chain()
        self.assertFalse(valid)

    def test_financial_actions_logged_to_audit_ledger(self):
        """Adding financial entities logs immutable audit events."""
        world.add_customer(Customer(id="c_1", name="Alpha", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=500.0, status=PaymentStatus.CREATED, created_at=0))
        world.update_payment_status("p_1", PaymentStatus.INITIATED.value)

        trace = audit_ledger.get_trace()
        self.assertEqual(len(trace), 3)
        valid, _ = audit_ledger.verify_chain()
        self.assertTrue(valid)

if __name__ == '__main__':
    unittest.main()
