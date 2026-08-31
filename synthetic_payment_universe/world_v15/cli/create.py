import argparse
import os
import time
import random
from typing import List, Dict, Any
from synthetic_payment_universe.world_v15.configuration import WorldConfigV15, WorldProfileV15
from synthetic_payment_universe.world_v15.clock import adversarial_clock
from synthetic_payment_universe.world_v15.world import AdversarialEconomicWorld
from synthetic_payment_universe.world_v15.behavior.customer_heterogeneity import HeterogeneousCustomerEntity, CustomerSensitivityType
from synthetic_payment_universe.world_v15.natural_recovery.natural_recovery_engine import NaturalRecoveryEngine

SENSITIVITIES = [
    CustomerSensitivityType.HIGHLY_SENSITIVE,
    CustomerSensitivityType.INTERVENTION_RESISTANT,
    CustomerSensitivityType.COMMUNICATION_SEEKING,
    CustomerSensitivityType.NATURAL_RECOVERER,
    CustomerSensitivityType.NEUTRAL
]

def create_adversarial_world(master_seed: int = 12345, profile_name: str = "dev", storage_dir: str = None) -> AdversarialEconomicWorld:
    adversarial_clock.reset(1760000000)
    profile = WorldProfileV15(profile_name)
    config = WorldConfigV15.from_profile(profile, storage_dir=storage_dir)
    world_id = f"adversarial_{master_seed}_{profile.value}"
    target_dir = os.path.join(config.storage_dir, world_id)
    os.makedirs(target_dir, exist_ok=True)
    db_path = os.path.join(target_dir, "adversarial.db")

    world = AdversarialEconomicWorld(world_id=world_id, master_seed=master_seed, config=config, db_path=db_path)
    rng = random.Random(master_seed)
    now = adversarial_clock.now()

    # 1. Customers
    customers: List[HeterogeneousCustomerEntity] = []
    for c_idx in range(config.customer_count):
        sens = SENSITIVITIES[c_idx % len(SENSITIVITIES)]
        tier = "B2B_ENTERPRISE" if (c_idx % 20 == 0) else ("SMB" if (c_idx % 4 == 0) else "B2C")
        spend = 120000.0 if tier == "B2B_ENTERPRISE" else (22000.0 if tier == "SMB" else 2200.0)

        cust = HeterogeneousCustomerEntity(
            customer_id=f"c_v15_{c_idx:06d}",
            tier=tier,
            sensitivity_type=sens,
            spending_capacity=spend,
            relationship_score=0.90,
            fatigue_rolling_24h=0.0,
            fatigue_rolling_7d=0.0
        )
        customers.append(cust)
        world.customers[cust.customer_id] = cust

    # 2. Payments & Natural Recovery assignment
    payments: List[Dict[str, Any]] = []
    for c_idx, cust in enumerate(customers):
        pid = f"pmt_v15_{c_idx:06d}_01"
        is_success = rng.random() < 0.82
        amt = cust.spending_capacity
        fcode = None if is_success else rng.choice(["91", "51", "14", "TO"])

        # Evaluate latent natural recovery if failed
        would_rec = False
        rec_delay = 0
        if not is_success and fcode:
            would_rec, rec_delay = NaturalRecoveryEngine.evaluate_natural_recovery(
                payment_id=pid,
                failure_code=fcode,
                customer_sensitivity=cust.sensitivity_type.value,
                subseed=master_seed + c_idx
            )

        pmt_dict = {
            "payment_id": pid,
            "customer_id": cust.customer_id,
            "merchant_id": "m_adv_01",
            "amount": amt,
            "status": "SETTLED" if is_success else "FAILED",
            "gateway_id": "GATEWAY_A",
            "failure_code": fcode,
            "natural_recovery_timestamp": (now + rec_delay) if would_rec else None,
            "would_recover_naturally": would_rec,
            "created_at": now
        }
        payments.append(pmt_dict)
        world.payments[pid] = pmt_dict

        if is_success:
            world.ledger.record_transaction(
                transaction_id=pid,
                account_debit="BANK_CASH_GATEWAY_A",
                account_credit="MERCHANT_SETTLEMENT_CLEARING",
                amount=amt,
                timestamp=now
            )

    world.repository.insert_customers(customers)
    world.repository.insert_payments(payments)
    world.repository.insert_ledger_entries(world.ledger.entries)

    return world

def main():
    parser = argparse.ArgumentParser(description="Create ULTRON Adversarial Economic World (SWU-1.5)")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--profile", type=str, default="dev")
    args = parser.parse_args()

    t0 = time.time()
    w = create_adversarial_world(master_seed=args.seed, profile_name=args.profile)
    dur = time.time() - t0
    print(f"Created Adversarial World '{w.world_id}' in {dur:.2f}s!")
    print(f"  Customers: {len(w.customers):,}")
    print(f"  Payments: {len(w.payments):,}")
    print(f"  Ledger Balanced: {w.ledger.verify_ledger_balance()}")

if __name__ == "__main__":
    main()
