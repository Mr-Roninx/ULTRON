import argparse
import os
import time
import random
from typing import List, Dict, Any
from synthetic_payment_universe.world_v14.config import WorldConfigV14, WorldProfileV14
from synthetic_payment_universe.world_v14.clock import emergent_clock
from synthetic_payment_universe.world_v14.world import EmergentEconomicWorld
from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity, CustomerCohort, CustomerLifecycleState
from synthetic_payment_universe.world_v14.population.merchant_cohorts import PopulationMerchantEntity, MerchantCohort, MerchantLifecycleState
from synthetic_payment_universe.world_v14.events.micro_events import MicroEconomicEvent

COHORTS_LIST = [
    CustomerCohort.SALARY_CYCLE_CONSUMER,
    CustomerCohort.VOLATILE_INCOME_SMB,
    CustomerCohort.HIGHLY_LOYAL,
    CustomerCohort.PRICE_SENSITIVE,
    CustomerCohort.SEASONAL_CONSUMER,
    CustomerCohort.ENTERPRISE_PROCUREMENT,
    CustomerCohort.LOW_ENGAGEMENT
]

MERCHANT_COHORTS_LIST = [
    MerchantCohort.GROWING_TECH,
    MerchantCohort.STABLE_RETAIL,
    MerchantCohort.SEASONAL_HOSPITALITY,
    MerchantCohort.STRESSED_LOGISTICS,
    MerchantCohort.ENTERPRISE_B2B
]

def create_emergent_population_world(master_seed: int = 12345, profile_name: str = "dev", storage_dir: str = None) -> EmergentEconomicWorld:
    emergent_clock.reset(1760000000)
    profile = WorldProfileV14(profile_name)
    config = WorldConfigV14.from_profile(profile, storage_dir=storage_dir)
    world_id = f"emergent_{master_seed}_{profile.value}"
    target_dir = os.path.join(config.storage_dir, world_id)
    os.makedirs(target_dir, exist_ok=True)
    db_path = os.path.join(target_dir, "emergent.db")

    world = EmergentEconomicWorld(world_id=world_id, master_seed=master_seed, config=config, db_path=db_path)
    rng = random.Random(master_seed)
    now = emergent_clock.now()

    # 1. Populate Merchants
    merchants: List[PopulationMerchantEntity] = []
    for m_idx in range(config.merchant_count):
        cohort = MERCHANT_COHORTS_LIST[m_idx % len(MERCHANT_COHORTS_LIST)]
        m = PopulationMerchantEntity(
            merchant_id=f"m_v14_{m_idx:04d}",
            cohort=cohort,
            industry="SaaS" if cohort == MerchantCohort.GROWING_TECH else "Retail",
            monthly_volume=15000000.0,
            growth_rate=0.04 if cohort == MerchantCohort.GROWING_TECH else 0.01,
            primary_gateway_id="GATEWAY_A"
        )
        merchants.append(m)
        world.merchants[m.merchant_id] = m
    world.repository.insert_merchants(merchants)

    # 2. Populate Customers, Relationships, Emergent Initial Payments
    customers: List[PopulationCustomerEntity] = []
    relationships: List[Dict[str, Any]] = []
    payments_to_insert: List[Dict[str, Any]] = []
    events_to_insert: List[MicroEconomicEvent] = []

    for c_idx in range(config.customer_count):
        cohort = COHORTS_LIST[c_idx % len(COHORTS_LIST)]
        tier = "B2B_ENTERPRISE" if cohort == CustomerCohort.ENTERPRISE_PROCUREMENT else ("SMB" if cohort == CustomerCohort.VOLATILE_INCOME_SMB else "B2C")
        cust = PopulationCustomerEntity(
            customer_id=f"c_v14_{c_idx:06d}",
            cohort=cohort,
            tier=tier,
            spending_capacity=150000.0 if tier == "B2B_ENTERPRISE" else (25000.0 if tier == "SMB" else 2500.0),
            fatigue_score=0.0,
            relationship_score=0.90,
            created_at=now
        )
        customers.append(cust)
        world.customers[cust.customer_id] = cust

        merch = merchants[c_idx % len(merchants)]

        # Relationship
        rel_id = f"rel_{cust.customer_id}_{merch.merchant_id}"
        rel_dict = {
            "relationship_id": rel_id,
            "customer_id": cust.customer_id,
            "merchant_id": merch.merchant_id,
            "trust_score": 0.90,
            "loyalty_score": 0.85,
            "lifetime_spend": 0.0,
            "dispute_count": 0,
            "updated_at": now
        }
        relationships.append(rel_dict)
        world.relationships[(cust.customer_id, merch.merchant_id)] = rel_dict

        # Emergent payment
        pid = f"pmt_v14_{c_idx:06d}_01"
        is_success = rng.random() < 0.86
        amt = cust.spending_capacity
        status = "SETTLED" if is_success else "FAILED"
        fcode = None if is_success else rng.choice(["91", "51", "14", "TO"])

        p_dict = {
            "payment_id": pid,
            "customer_id": cust.customer_id,
            "merchant_id": merch.merchant_id,
            "amount": amt,
            "currency": "INR",
            "status": status,
            "rail": "CARD",
            "gateway_id": "GATEWAY_A",
            "failure_code": fcode,
            "created_at": now
        }
        payments_to_insert.append(p_dict)

        if is_success:
            world.ledger.record_transaction(
                transaction_id=pid,
                source_event_id=f"evt_{pid}",
                account_debit="BANK_CASH_GATEWAY_A",
                account_credit="MERCHANT_SETTLEMENT_CLEARING",
                amount=amt,
                timestamp=now
            )

        events_to_insert.append(MicroEconomicEvent(
            event_id=f"evt_{pid}",
            event_type=f"PAYMENT_{status}",
            entity_id=pid,
            timestamp=now,
            payload={"status": status, "amount": amt}
        ))

        # Schedule future subscription renewal for B2C/SMB
        if c_idx % 2 == 0:
            world.schedule_event(MicroEconomicEvent(
                event_id=f"evt_sub_ren_{c_idx}",
                event_type="SUBSCRIPTION_RENEWAL_DUE",
                entity_id=cust.customer_id,
                timestamp=now + (30 * 86400),
                payload={"amount": amt}
            ))

    world.repository.insert_customers(customers)
    world.repository.insert_relationships(relationships)
    world.repository.insert_payments(payments_to_insert)
    world.repository.insert_economic_events(events_to_insert)
    world.repository.insert_ledger_entries(world.ledger.entries)

    return world

def main():
    parser = argparse.ArgumentParser(description="Create ULTRON Emergent Population World (SWU-1.4)")
    parser.add_argument("--seed", type=int, default=12345, help="Master seed")
    parser.add_argument("--profile", type=str, default="dev", help="World profile")
    args = parser.parse_args()

    t0 = time.time()
    w = create_emergent_population_world(master_seed=args.seed, profile_name=args.profile)
    dur = time.time() - t0
    print(f"Created Emergent Population World '{w.world_id}' in {dur:.2f}s!")
    print(f"  Customers: {len(w.customers):,}")
    print(f"  Merchants: {len(w.merchants):,}")
    print(f"  Ledger Balanced: {w.ledger.verify_ledger_balance()}")

if __name__ == "__main__":
    main()
