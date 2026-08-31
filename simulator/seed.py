from simulator.world import world
from simulator.models import Customer, Payment, Invoice, Checkout, PaymentStatus, InvoiceStatus, CheckoutStatus
from simulator.clock import clock

def seed_ananya_textiles():
    start_time = 1718000000
    clock.reset(start_time)
    
    # The Customer
    ananya = Customer(
        id="c_1001",
        name="Ananya Textiles",
        segment="B2B_ENTERPRISE",
        ltv=450000.0,
        created_at=start_time - 86400 * 180
    )
    world.add_customer(ananya)
    
    # Past successful payments (to build relationship)
    for i in range(3):
        clock.advance(86400 * 30)
        p_success = Payment(
            id=f"pay_old_{i}",
            customer_id="c_1001",
            amount=15000.0,
            status=PaymentStatus.SETTLED,
            created_at=clock.get_time()
        )
        world.add_payment(p_success)
        
    # 1. Overdue Invoice (₹12,000)
    clock.advance(86400 * 10)
    inv = Invoice(
        id="inv_991",
        customer_id="c_1001",
        amount=12000.0,
        status=InvoiceStatus.OVERDUE,
        due_date=clock.get_time() - 86400 * 5
    )
    world.add_invoice(inv)
    
    # 2. Failed Payment (₹8,200)
    clock.advance(86400 * 2)
    pay_fail = Payment(
        id="pay_failed_1",
        customer_id="c_1001",
        amount=8200.0,
        status=PaymentStatus.FAILED,
        failure_code="INSUFFICIENT_FUNDS",
        created_at=clock.get_time()
    )
    world.add_payment(pay_fail)
    
    # 3. Checkout Abandoned (₹4,500) shortly after payment failure
    clock.advance(1800) # 30 mins later
    chk_abandoned = Checkout(
        id="chk_442",
        customer_id="c_1001",
        amount=4500.0,
        status=CheckoutStatus.ABANDONED,
        created_at=clock.get_time()
    )
    world.add_checkout(chk_abandoned)
    
    print("World Seeded: Ananya Textiles Scenario loaded (Total Exposure: 24,700)")
