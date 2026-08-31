import random
from typing import Dict, Any, List
from simulator.world import world
from simulator.models import Customer, Payment, PaymentStatus, Invoice, InvoiceStatus, Checkout, CheckoutStatus
from simulator.clock import clock

FAILURE_CODES_POOL = [
    ("INSUFFICIENT_FUNDS", "51", "gateway_a"),
    ("INSUFFICIENT_FUNDS", "insufficient_funds", "stripe"),
    ("INSUFFICIENT_FUNDS", "ERR_BALANCE", "gateway_b"),
    ("EXPIRED_CARD", "54", "gateway_a"),
    ("EXPIRED_CARD", "expired_card", "stripe"),
    ("INVALID_CVV", "incorrect_cvc", "stripe"),
    ("3D_SECURE_FAILED", "3DS", "gateway_a"),
    ("AUTH_REQUIRED", "authentication_required", "stripe"),
    ("TIMEOUT", "TO", "gateway_a"),
    ("TIMEOUT", "ERR_TIMEOUT", "gateway_b"),
    ("ISSUER_UNAVAILABLE", "91", "gateway_a"),
    ("GATEWAY_DOWN", "96", "gateway_a"),
    ("GATEWAY_DOWN", "ERR_UNAVAILABLE", "gateway_b"),
    ("DO_NOT_HONOR", "05", "gateway_a"),
    ("LIMIT_EXCEEDED", "61", "gateway_a"),
    ("UNKNOWN_ERROR", "BAD_REQUEST_ERROR", "razorpay")
]

RAILS_POOL = ["CARD", "UPI", "BANK_TRANSFER", "ACH", "NET_BANKING"]
GATEWAYS_POOL = ["GATEWAY_A", "GATEWAY_B", "GATEWAY_C", "STRIPE", "RAZORPAY"]

CUSTOMER_SEGMENTS = [
    ("B2B_ENTERPRISE", 50000.0, 250000.0),
    ("B2B_MIDMARKET", 15000.0, 75000.0),
    ("SMB", 3000.0, 20000.0),
    ("CONSUMER", 500.0, 5000.0)
]

def generate_dataset_v2(seed: int = 42, num_customers: int = 200, events_per_customer: int = 10) -> Dict[str, Any]:
    rng = random.Random(seed)
    world.reset()
    now = clock.now()

    # Pre-configure Ananya Textiles as canonical Golden Demo customer (c_1034 / c_ananya)
    ananya = Customer(
        id="c_ananya",
        name="Ananya Textiles",
        segment="B2B_ENTERPRISE",
        ltv=120000.0,
        created_at=0,
        recent_contacts=0,
        recent_responses=2,
        successful_prior_recoveries=3
    )
    world.add_customer(ananya)
    
    # Ananya opportunities
    world.add_payment(Payment(
        id="p_ananya_sub",
        customer_id="c_ananya",
        amount=8200.0,
        status=PaymentStatus.FAILED,
        failure_code="91", # Issuer unavailable
        rail="CARD",
        gateway_id="GATEWAY_B",
        created_at=now,
        metadata={"plan": "enterprise_monthly", "opportunity_type": "subscription"}
    ))
    world.add_invoice(Invoice(
        id="inv_ananya_4500",
        customer_id="c_ananya",
        amount=4500.0,
        status=InvoiceStatus.OVERDUE,
        due_date=now - 86400,
        created_at=now - (86400 * 15)
    ))
    world.add_checkout(Checkout(
        id="chk_ananya_12000",
        customer_id="c_ananya",
        amount=12000.0,
        status=CheckoutStatus.ABANDONED,
        created_at=now - 3600
    ))

    # Generate remaining customers
    for i in range(1, num_customers):
        c_id = f"c_{1000 + i}"
        seg_choice, min_ltv, max_ltv = rng.choice(CUSTOMER_SEGMENTS)
        ltv = round(rng.uniform(min_ltv, max_ltv), 2)
        
        cust = Customer(
            id=c_id,
            name=f"Customer {c_id.upper()}",
            segment=seg_choice,
            ltv=ltv,
            created_at=max(0, now - rng.randint(86400 * 30, 86400 * 365)),
            recent_contacts=rng.randint(0, 3),
            recent_responses=rng.randint(0, 5),
            successful_prior_recoveries=rng.randint(0, 4),
            opt_out=rng.random() < 0.03
        )
        world.add_customer(cust)

        # Generate ~10 payment events per customer
        for j in range(events_per_customer):
            p_id = f"p_{c_id}_{j}"
            f_reason, raw_code, gw = rng.choice(FAILURE_CODES_POOL)
            rail = rng.choice(RAILS_POOL)
            
            # Amount based on segment
            if seg_choice == "B2B_ENTERPRISE":
                amount = round(rng.uniform(5000.0, 45000.0), 2)
            elif seg_choice == "B2B_MIDMARKET":
                amount = round(rng.uniform(2000.0, 15000.0), 2)
            elif seg_choice == "SMB":
                amount = round(rng.uniform(800.0, 5000.0), 2)
            else:
                amount = round(rng.uniform(200.0, 1500.0), 2)

            # Historical vs active failure status
            is_active_failure = (j == events_per_customer - 1)
            p_status = PaymentStatus.FAILED if is_active_failure else (PaymentStatus.SETTLED if rng.random() > 0.3 else PaymentStatus.FAILED)

            p_created = now - rng.randint(0, 86400 * 60) if not is_active_failure else now

            payment = Payment(
                id=p_id,
                customer_id=c_id,
                amount=amount,
                status=p_status,
                failure_code=raw_code if p_status == PaymentStatus.FAILED else None,
                rail=rail,
                gateway_id=gw.upper(),
                created_at=p_created,
                metadata={"opportunity_type": "subscription" if j % 2 == 0 else "one_time"}
            )
            world.add_payment(payment)

            # Some customers also have an overdue invoice or abandoned checkout
            if j == 2 and rng.random() < 0.35:
                world.add_invoice(Invoice(
                    id=f"inv_{c_id}",
                    customer_id=c_id,
                    amount=round(amount * 0.75, 2),
                    status=InvoiceStatus.OVERDUE,
                    due_date=now - 86400,
                    created_at=now - (86400 * 10)
                ))
            if j == 4 and rng.random() < 0.25:
                world.add_checkout(Checkout(
                    id=f"chk_{c_id}",
                    customer_id=c_id,
                    amount=round(amount * 1.2, 2),
                    status=CheckoutStatus.ABANDONED,
                    created_at=now - 7200
                ))

    return {
        "customers_count": len(world.customers),
        "payments_count": len(world.payments),
        "invoices_count": len(world.invoices),
        "checkouts_count": len(world.checkouts)
    }
