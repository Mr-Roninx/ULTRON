import random
from typing import List, Tuple
from simulator.models import (
    Customer, Payment, Invoice, Checkout, Gateway, 
    PaymentStatus, InvoiceStatus, CheckoutStatus
)
from simulator.world import FinancialWorld
from backend.benchmark.models import BenchmarkOpportunity

class SeededWorldGenerator:
    """
    Deterministic seeded generator that produces synthetic financial worlds.
    Guarantees bit-for-bit reproducibility for identical seeds.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate(self, start_time: int = 1718000000) -> Tuple[FinancialWorld, List[BenchmarkOpportunity]]:
        self.rng = random.Random(self.seed)
        world = FinancialWorld()
        opportunities: List[BenchmarkOpportunity] = []
        
        # 1. Setup Gateways
        gateways = [
            Gateway(id="gw_razorpay", name="Razorpay", health=1.0, supported_rails=["UPI", "CARD", "NETBANKING"], failure_rate=0.02),
            Gateway(id="gw_stripe", name="Stripe Global", health=1.0, supported_rails=["CARD"], failure_rate=0.01),
            Gateway(id="gw_paytm", name="Paytm Payments Bank", health=0.98, supported_rails=["UPI", "WALLET"], failure_rate=0.04),
        ]
        for gw in gateways:
            world.add_gateway(gw)

        # 2. Setup 200 Customers across segments
        segments = [
            ("B2B_ENTERPRISE", 0.15, (200000.0, 1000000.0)),
            ("SMB", 0.35, (30000.0, 200000.0)),
            ("RETAIL", 0.30, (5000.0, 30000.0)),
            ("D2C", 0.20, (1000.0, 15000.0)),
        ]
        
        customers: List[Customer] = []
        cust_id_counter = 1000
        for seg_name, weight, (min_ltv, max_ltv) in segments:
            count = int(200 * weight)
            for _ in range(count):
                cust_id_counter += 1
                c_id = f"c_{cust_id_counter}"
                ltv = round(self.rng.uniform(min_ltv, max_ltv), 2)
                created_at = start_time - self.rng.randint(30, 365) * 86400
                recent_contacts = self.rng.choices([0, 1, 2, 3], weights=[0.5, 0.3, 0.15, 0.05])[0]
                recent_responses = self.rng.randint(0, recent_contacts) if recent_contacts > 0 else 0
                prior_recoveries = self.rng.choices([0, 1, 2, 3, 4], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
                complaints = self.rng.choices([0, 1, 2], weights=[0.85, 0.12, 0.03])[0]
                opt_out = self.rng.random() < 0.02  # 2% opt-out
                
                customer = Customer(
                    id=c_id,
                    name=f"Customer {cust_id_counter} ({seg_name})",
                    segment=seg_name,
                    ltv=ltv,
                    created_at=created_at,
                    recent_contacts=recent_contacts,
                    recent_responses=recent_responses,
                    successful_prior_recoveries=prior_recoveries,
                    complaints=complaints,
                    opt_out=opt_out,
                    silence_duration=self.rng.randint(0, 86400 * 30)
                )
                customers.append(customer)
                world.add_customer(customer)

        # 3. Generate Historical Settled Payments (~1500)
        pay_id_counter = 2000
        for cust in customers:
            num_past = self.rng.randint(3, 10)
            for i in range(num_past):
                pay_id_counter += 1
                p_id = f"pay_hist_{pay_id_counter}"
                amt = round(self.rng.uniform(100.0, cust.ltv * 0.15), 2)
                p = Payment(
                    id=p_id,
                    customer_id=cust.id,
                    amount=amt,
                    status=PaymentStatus.SETTLED,
                    rail=self.rng.choice(["UPI", "CARD", "NETBANKING"]),
                    gateway_id=self.rng.choice(["gw_razorpay", "gw_stripe", "gw_paytm"]),
                    created_at=start_time - self.rng.randint(5, 60) * 86400
                )
                world.add_payment(p)

        # 4. Generate Recovery Opportunities:
        # Category A: Failed Payments (~150 active opportunities)
        failure_profiles = [
            ("TIMEOUT", "TRANSIENT", "UPI", 0.20),
            ("NETWORK_ERROR", "TRANSIENT", "CARD", 0.15),
            ("GATEWAY_TIMEOUT", "GATEWAY_PROBLEM", "NETBANKING", 0.10),
            ("INSUFFICIENT_FUNDS", "LIQUIDITY_RELATED", "UPI", 0.25),
            ("LIMIT_EXCEEDED", "LIQUIDITY_RELATED", "CARD", 0.10),
            ("3D_SECURE_FAILED", "CUSTOMER_ACTION_REQUIRED", "CARD", 0.10),
            ("EXPIRED_CARD", "CREDENTIAL_PROBLEM", "CARD", 0.05),
            ("DO_NOT_HONOR", "NON_RETRYABLE", "CARD", 0.05),
        ]
        
        opp_id_counter = 100
        target_custs_for_failures = self.rng.sample(customers, k=min(120, len(customers)))
        for cust in target_custs_for_failures:
            pay_id_counter += 1
            opp_id_counter += 1
            p_id = f"pay_fail_{pay_id_counter}"
            
            f_code, f_type, rail, _ = self.rng.choices(
                failure_profiles, 
                weights=[w for _, _, _, w in failure_profiles]
            )[0]
            
            amt_scale = {"B2B_ENTERPRISE": (10000.0, 150000.0), "SMB": (3000.0, 30000.0), "RETAIL": (500.0, 5000.0), "D2C": (200.0, 2000.0)}
            min_a, max_a = amt_scale[cust.segment]
            amt = round(self.rng.uniform(min_a, max_a), 2)
            
            amt_bucket = self._classify_bucket(amt)
            
            p = Payment(
                id=p_id,
                customer_id=cust.id,
                amount=amt,
                status=PaymentStatus.FAILED,
                failure_code=f_code,
                rail=rail,
                gateway_id="gw_razorpay" if rail == "UPI" else "gw_stripe",
                created_at=start_time
            )
            world.add_payment(p)
            
            opportunities.append(BenchmarkOpportunity(
                opportunity_id=f"opp_{opp_id_counter}",
                customer_id=cust.id,
                customer_name=cust.name,
                customer_segment=cust.segment,
                customer_ltv=cust.ltv,
                entity_type="PAYMENT",
                entity_id=p_id,
                initial_amount=amt,
                failure_type=f_code,
                payment_rail=rail,
                channel=rail,
                created_at=start_time,
                days_overdue=0,
                amount_bucket=amt_bucket
            ))

        # Category B: Overdue Invoices (~40 active opportunities)
        inv_id_counter = 3000
        target_custs_for_invoices = self.rng.sample([c for c in customers if c.segment in ["B2B_ENTERPRISE", "SMB"]], k=35)
        for cust in target_custs_for_invoices:
            inv_id_counter += 1
            opp_id_counter += 1
            inv_id = f"inv_{inv_id_counter}"
            
            amt = round(self.rng.uniform(5000.0, 80000.0), 2)
            days_overdue = self.rng.randint(3, 30)
            
            inv = Invoice(
                id=inv_id,
                customer_id=cust.id,
                amount=amt,
                status=InvoiceStatus.OVERDUE,
                due_date=start_time - days_overdue * 86400
            )
            world.add_invoice(inv)
            
            opportunities.append(BenchmarkOpportunity(
                opportunity_id=f"opp_{opp_id_counter}",
                customer_id=cust.id,
                customer_name=cust.name,
                customer_segment=cust.segment,
                customer_ltv=cust.ltv,
                entity_type="INVOICE",
                entity_id=inv_id,
                initial_amount=amt,
                failure_type="INVOICE_OVERDUE",
                payment_rail="BANK_TRANSFER",
                channel="EMAIL",
                created_at=start_time,
                days_overdue=days_overdue,
                amount_bucket=self._classify_bucket(amt)
            ))

        # Category C: Abandoned Checkouts (~45 active opportunities)
        chk_id_counter = 4000
        target_custs_for_checkouts = self.rng.sample([c for c in customers if c.segment in ["RETAIL", "D2C", "SMB"]], k=45)
        for cust in target_custs_for_checkouts:
            chk_id_counter += 1
            opp_id_counter += 1
            chk_id = f"chk_{chk_id_counter}"
            
            amt = round(self.rng.uniform(400.0, 8000.0), 2)
            
            chk = Checkout(
                id=chk_id,
                customer_id=cust.id,
                amount=amt,
                status=CheckoutStatus.ABANDONED,
                created_at=start_time - self.rng.randint(1800, 7200)
            )
            world.add_checkout(chk)
            
            opportunities.append(BenchmarkOpportunity(
                opportunity_id=f"opp_{opp_id_counter}",
                customer_id=cust.id,
                customer_name=cust.name,
                customer_segment=cust.segment,
                customer_ltv=cust.ltv,
                entity_type="CHECKOUT",
                entity_id=chk_id,
                initial_amount=amt,
                failure_type="CHECKOUT_ABANDONED",
                payment_rail="UPI",
                channel="WHATSAPP",
                created_at=start_time,
                days_overdue=0,
                amount_bucket=self._classify_bucket(amt)
            ))

        return world, opportunities

    def _classify_bucket(self, amount: float) -> str:
        if amount < 1000.0:
            return "MICRO"
        elif amount < 5000.0:
            return "LOW"
        elif amount < 25000.0:
            return "MEDIUM"
        elif amount < 75000.0:
            return "HIGH"
        else:
            return "ENTERPRISE"

def generate_world(seed: int, start_time: int = 1718000000) -> Tuple[FinancialWorld, List[BenchmarkOpportunity]]:
    generator = SeededWorldGenerator(seed=seed)
    return generator.generate(start_time=start_time)
