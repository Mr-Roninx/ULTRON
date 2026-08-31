import random
from typing import Dict, Any, List
from simulator.clock import clock
from synthetic_payment_universe.world_v12.world.world import PersistentWorld
from synthetic_payment_universe.world_v12.entities.customer import Customer
from synthetic_payment_universe.world_v12.entities.merchant import Merchant
from synthetic_payment_universe.world_v12.entities.payment import Payment, PaymentAttempt, Invoice
from synthetic_payment_universe.world_v12.temporal.priority_queue import WorldEvent

TIERS = ["B2C", "SMB", "MID_MARKET", "B2B_ENTERPRISE"]
INDUSTRIES = ["SaaS", "E-commerce", "Logistics", "Healthcare", "Manufacturing", "Fintech"]

class WorldDataPopulator:
    """
    Populates persistent SQLite world tables in streaming chunks with zero RAM overhead.
    """
    def __init__(self, world: PersistentWorld):
        self.world = world
        self.rng = random.Random(world.identity.master_seed)

    def populate(self) -> Dict[str, Any]:
        num_cust = self.world.config.customer_count
        payments_per_cust = self.world.config.payments_per_customer
        now = self.world.identity.simulation_start

        # 1. Merchants (5 to 50 based on scale)
        merchant_count = max(5, num_cust // 50)
        merchants: List[Merchant] = []
        for m_idx in range(merchant_count):
            ind = INDUSTRIES[m_idx % len(INDUSTRIES)]
            merch = Merchant(
                merchant_id=f"m_w12_{m_idx:04d}",
                name=f"{ind} Enterprise {m_idx}",
                industry=ind,
                created_at=now
            )
            merchants.append(merch)
        self.world.repository.insert_merchants_chunk(merchants)

        # 2. Customers and Payments in streaming batches of 500
        total_payments = 0
        chunk_size = 500
        cust_batch: List[Customer] = []
        pmt_batch: List[Payment] = []
        evt_batch: List[WorldEvent] = []

        for c_idx in range(num_cust):
            tier = TIERS[c_idx % len(TIERS)]
            avg_val = 1500.0 if tier == "B2C" else (15000.0 if tier == "SMB" else (65000.0 if tier == "MID_MARKET" else 250000.0))
            cust = Customer(
                customer_id=f"c_w12_{c_idx:06d}",
                tier=tier,
                average_transaction_value=avg_val,
                historical_success_rate=0.86,
                created_at=now
            )
            cust_batch.append(cust)

            merch = merchants[c_idx % len(merchants)]

            for p_idx in range(payments_per_cust):
                pid = f"pmt_w12_{c_idx:06d}_{p_idx:02d}"
                roll = self.rng.random()
                amt = round(self.rng.uniform(avg_val * 0.8, avg_val * 1.2), 2)
                t_pmt = now - (p_idx * 86400 * 2)

                if roll < 0.85:
                    status = "SETTLED"
                    fcode = None
                    # Record double entry ledger
                    self.world.ledger.record_transaction(
                        transaction_id=pid,
                        source_event_id=f"evt_{pid}",
                        account_debit=f"BANK_CASH_{merch.primary_gateway_id}",
                        account_credit="MERCHANT_SETTLEMENT_CLEARING",
                        amount=amt,
                        timestamp=t_pmt
                    )
                elif roll < 0.87:
                    status = "PENDING"
                    fcode = "AMBIGUOUS_SETTLEMENT"
                elif roll < 0.88:
                    status = "DISPUTED"
                    fcode = "CHARGEBACK"
                else:
                    status = "FAILED"
                    fcode = self.rng.choice(["91", "51", "14", "TO", "61"])

                pmt = Payment(
                    payment_id=pid,
                    customer_id=cust.customer_id,
                    merchant_id=merch.merchant_id,
                    amount=amt,
                    status=status,
                    rail="CARD",
                    gateway_id=merch.primary_gateway_id,
                    failure_code=fcode,
                    created_at=t_pmt
                )
                pmt_batch.append(pmt)
                total_payments += 1

                evt_batch.append(WorldEvent(
                    event_id=f"evt_{pid}",
                    event_type=f"PAYMENT_{status}",
                    entity_id=pid,
                    timestamp=t_pmt,
                    payload={"status": status, "amount": amt}
                ))

            # Commit batch
            if len(cust_batch) >= chunk_size:
                self.world.repository.insert_customers_chunk(cust_batch)
                self.world.repository.insert_payments_chunk(pmt_batch)
                self.world.repository.insert_events_chunk(evt_batch)
                cust_batch.clear()
                pmt_batch.clear()
                evt_batch.clear()

        # Final flush
        if cust_batch:
            self.world.repository.insert_customers_chunk(cust_batch)
            self.world.repository.insert_payments_chunk(pmt_batch)
            self.world.repository.insert_events_chunk(evt_batch)

        # Save ledger entries to SQLite
        self.world.repository.insert_ledger_entries(self.world.ledger.entries)

        return {
            "customers": num_cust,
            "merchants": len(merchants),
            "payments": total_payments,
            "ledger_balanced": self.world.ledger.verify_ledger_balance()
        }
