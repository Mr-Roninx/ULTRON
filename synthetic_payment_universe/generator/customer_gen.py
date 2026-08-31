import random
from typing import List, Dict, Any, Optional
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import Customer
from synthetic_payment_universe.generator.seeds import MasterSeedManager

LATENT_PROFILES = [
    "PATIENT", "IMPATIENT", "RETRY_PRONE", "SILENT", "HIGH_VALUE", "LOW_VALUE",
    "METHOD_LOYAL", "METHOD_FLEXIBLE", "PAYMENT_FATIGUED", "PROMPT_PAYER",
    "SLOW_PAYER", "DISPUTE_PRONE", "SUPPORT_HEAVY", "PRICE_SENSITIVE"
]

CUSTOMER_SEGMENTS = ["B2C", "SMB", "MID_MARKET", "B2B_ENTERPRISE"]

class CustomerGenerator:
    """
    Generates synthetic customers with realistic latent behavioral profiles,
    liquidity cycles, and probabilistic responsiveness.
    """
    def __init__(self, seed_manager: MasterSeedManager):
        self.seed_mgr = seed_manager

    def generate_customer(self, index: int) -> Customer:
        subseed = self.seed_mgr.get_customer_seed(index)
        rng = random.Random(subseed)

        seg = rng.choices(
            CUSTOMER_SEGMENTS,
            weights=[0.50, 0.30, 0.15, 0.05], # realistic tier distribution
            k=1
        )[0]

        profile = rng.choice(LATENT_PROFILES)
        tenure = rng.randint(30, 1800)
        complaints = rng.choices([0, 1, 2, 3, 4, 5], weights=[0.70, 0.15, 0.08, 0.04, 0.02, 0.01], k=1)[0]
        fatigue = min(1.0, complaints * 0.20 + rng.uniform(0.0, 0.10))

        if seg == "B2B_ENTERPRISE":
            atv = rng.uniform(50000.0, 500000.0)
            base_succ = 0.94
        elif seg == "MID_MARKET":
            atv = rng.uniform(15000.0, 80000.0)
            base_succ = 0.90
        elif seg == "SMB":
            atv = rng.uniform(3000.0, 25000.0)
            base_succ = 0.85
        else: # B2C
            atv = rng.uniform(300.0, 5000.0)
            base_succ = 0.82

        salary_day = rng.choice([1, 5, 28, 30, 31])

        return Customer(
            customer_id=f"c_synth_{index:06d}",
            name=f"Customer Account {index}",
            customer_type=seg,
            segment=seg,
            country="IND",
            currency="INR",
            tenure_days=tenure,
            complaints=complaints,
            contact_count=0,
            fatigue_score=round(fatigue, 3),
            is_opted_out=(fatigue >= 0.90),
            average_transaction_value=round(atv, 2),
            historical_success_rate=round(base_succ, 3),
            latent_profile=profile,
            latent_salary_day=salary_day,
            latent_churn_risk=round(rng.uniform(0.01, 0.15), 3),
            created_at=clock.now() - (tenure * 86400)
        )

    def generate_batch(self, count: int, offset: int = 0) -> List[Customer]:
        return [self.generate_customer(offset + i) for i in range(count)]

    # Probabilistic Customer Behavior Calculations
    @staticmethod
    def evaluate_link_conversion(customer: Customer, offer_discount: bool = False, subseed: int = 0) -> bool:
        rng = random.Random(subseed)
        base_p = 0.65 if customer.segment in ["B2B_ENTERPRISE", "MID_MARKET"] else 0.50
        # Fatigue reduces conversion
        base_p -= (customer.fatigue_score * 0.35)
        if offer_discount:
            base_p += 0.20
        return rng.random() < max(0.05, min(0.95, base_p))

    @staticmethod
    def evaluate_ptp_promise(customer: Customer, subseed: int = 0) -> bool:
        rng = random.Random(subseed)
        base_p = 0.70 - (customer.fatigue_score * 0.30)
        return rng.random() < max(0.10, min(0.90, base_p))
