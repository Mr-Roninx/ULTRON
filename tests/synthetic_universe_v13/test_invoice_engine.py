import pytest
from synthetic_payment_universe.world_v13.economy.invoice_economy import InvoiceCivilizationEntity, InvoiceEconomyEngine

def test_b2b_invoice_due_and_overdue_aging():
    now = 1760000000
    inv = InvoiceCivilizationEntity(invoice_id="inv_1", buyer_id="b_1", seller_id="s_1", amount=150000.0, due_timestamp=now + 86400, status="ISSUED")

    InvoiceEconomyEngine.update_invoice_status(inv, now + (2 * 86400))
    assert inv.status == "DUE"

    # Beyond grace period -> OVERDUE
    InvoiceEconomyEngine.update_invoice_status(inv, now + (10 * 86400))
    assert inv.status == "OVERDUE"
