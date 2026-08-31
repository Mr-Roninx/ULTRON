import argparse
import os
import time
import random
from synthetic_payment_universe.world_v13.config import WorldConfig, WorldProfile
from synthetic_payment_universe.world_v13.world import PersistentEconomicWorld
from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity
from synthetic_payment_universe.world_v13.economy.merchant_economy import MerchantEconomyEntity
from synthetic_payment_universe.world_v13.economy.payment_economy import PaymentCivilizationEntity
from synthetic_payment_universe.world_v13.economy.subscription_economy import SubscriptionCivilizationEntity
from synthetic_payment_universe.world_v13.economy.invoice_economy import InvoiceCivilizationEntity
from synthetic_payment_universe.world_v13.events.event import EconomicEvent
from synthetic_payment_universe.world_v13.clock import economic_clock

TIERS = ["B2C", "SMB", "MID_MARKET", "B2B_ENTERPRISE"]
INDUSTRIES = ["SaaS", "E-commerce", "Logistics", "Healthcare", "Manufacturing", "Fintech"]

def create_economic_civilization(master_seed: int = 12345, profile_name: str = "dev", storage_dir: str = None) -> PersistentEconomicWorld:
    economic_clock.reset(1760000000)
    profile = WorldProfile(profile_name)
    config = WorldConfig.from_profile(profile, storage_dir=storage_dir)
    world_id = f"civilization_{master_seed}_{profile.value}"
    target_dir = os.path.join(config.storage_dir, world_id)
    os.makedirs(target_dir, exist_ok=True)
    db_path = os.path.join(target_dir, "civilization.db")

    world = PersistentEconomicWorld(world_id=world_id, master_seed=master_seed, config=config, db_path=db_path)
    rng = random.Random(master_seed)
    now = economic_clock.now()

    # 1. Merchants
    merchants: List[MerchantEconomyEntity] = []
    for m_idx in range(config.merchant_count):
        ind = INDUSTRIES[m_idx % len(INDUSTRIES)]
        m = MerchantEconomyEntity(
            merchant_id=f"m_civ_{m_idx:04d}",
            industry=ind,
            monthly_volume=10000000.0,
            primary_gateway_id="GATEWAY_A"
        )
        merchants.append(m)
        world.merchants[m.merchant_id] = m
    world.repository.insert_merchants(merchants)

    # 2. Customers, Payments, Subscriptions, Invoices in streaming chunks
    customers: List[CustomerEconomyEntity] = []
    payments: List[PaymentCivilizationEntity] = []
    subscriptions: List[SubscriptionCivilizationEntity] = []
    invoices: List[InvoiceCivilizationEntity] = []
    events: List[EconomicEvent] = []

    for c_idx in range(config.customer_count):
        tier = TIERS[c_idx % len(TIERS)]
        cust = CustomerEconomyEntity(
            customer_id=f"c_civ_{c_idx:06d}",
            tier=tier,
            average_transaction_value=1500.0 if tier == "B2C" else (15000.0 if tier == "SMB" else 85000.0),
            created_at=now
        )
        customers.append(cust)
        world.customers[cust.customer_id] = cust

        merch = merchants[c_idx % len(merchants)]

        # Initial Payment
        pid = f"pmt_civ_{c_idx:06d}_01"
        is_success = rng.random() < 0.85
        amt = round(rng.uniform(cust.average_transaction_value * 0.8, cust.average_transaction_value * 1.2), 2)
        pmt = PaymentCivilizationEntity(
            payment_id=pid,
            customer_id=cust.customer_id,
            merchant_id=merch.merchant_id,
            amount=amt,
            status="SETTLED" if is_success else "FAILED",
            rail="CARD",
            gateway_id="GATEWAY_A",
            failure_code=None if is_success else rng.choice(["91", "51", "14", "TO"]),
            created_at=now
        )
        payments.append(pmt)
        world.payments[pid] = pmt

        if is_success:
            world.ledger.record_transaction(
                transaction_id=pid,
                source_event_id=f"evt_{pid}",
                account_debit="BANK_CASH_GATEWAY_A",
                account_credit="MERCHANT_SETTLEMENT_CLEARING",
                amount=amt,
                timestamp=now
            )

        events.append(EconomicEvent(
            event_id=f"evt_{pid}",
            event_type=f"PAYMENT_{pmt.status}",
            entity_id=pid,
            timestamp=now,
            payload={"status": pmt.status, "amount": amt}
        ))

        # Subscriptions for SMB / B2C
        if c_idx % 2 == 0:
            sid = f"sub_civ_{c_idx:06d}"
            renewal_t = now + (30 * 86400)
            sub = SubscriptionCivilizationEntity(
                subscription_id=sid,
                customer_id=cust.customer_id,
                merchant_id=merch.merchant_id,
                amount=amt,
                interval="MONTHLY",
                current_period_end=renewal_t
            )
            subscriptions.append(sub)
            world.subscriptions[sid] = sub
            world.schedule_event(EconomicEvent(
                event_id=f"evt_sub_ren_{sid}",
                event_type="SUBSCRIPTION_RENEWAL_DUE",
                entity_id=sid,
                timestamp=renewal_t,
                payload={"amount": amt, "customer_id": cust.customer_id}
            ))

        # Invoices for Mid-Market & Enterprise
        if tier in ["MID_MARKET", "B2B_ENTERPRISE"]:
            inv_id = f"inv_civ_{c_idx:06d}"
            due_t = now + (15 * 86400)
            inv = InvoiceCivilizationEntity(
                invoice_id=inv_id,
                buyer_id=cust.customer_id,
                seller_id=merch.merchant_id,
                amount=amt * 3.0,
                due_timestamp=due_t,
                status="ISSUED"
            )
            invoices.append(inv)
            world.invoices[inv_id] = inv
            world.schedule_event(EconomicEvent(
                event_id=f"evt_inv_due_{inv_id}",
                event_type="INVOICE_DUE",
                entity_id=inv_id,
                timestamp=due_t,
                payload={"amount": amt * 3.0, "buyer_id": cust.customer_id}
            ))

    world.repository.insert_customers(customers)
    world.repository.insert_payments(payments)
    world.repository.insert_subscriptions(subscriptions)
    world.repository.insert_invoices(invoices)
    world.repository.insert_economic_events(events)
    world.repository.insert_ledger_entries(world.ledger.entries)

    return world

def main():
    parser = argparse.ArgumentParser(description="Create ULTRON Economic Civilization (SWU-1.3)")
    parser.add_argument("--seed", type=int, default=12345, help="Master seed")
    parser.add_argument("--profile", type=str, default="dev", choices=["tiny", "dev", "standard", "large", "civilization"], help="World profile")
    args = parser.parse_args()

    t0 = time.time()
    w = create_economic_civilization(master_seed=args.seed, profile_name=args.profile)
    dur = time.time() - t0
    print(f"Created Economic Civilization '{w.world_id}' in {dur:.2f}s!")
    print(f"  Customers: {len(w.customers):,}")
    print(f"  Merchants: {len(w.merchants):,}")
    print(f"  Ledger Balanced: {w.ledger.verify_ledger_balance()}")
    print(f"  Database: {w.db_path}")

if __name__ == "__main__":
    main()
