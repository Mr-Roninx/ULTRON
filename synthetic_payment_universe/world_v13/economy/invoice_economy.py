from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class InvoiceCivilizationEntity(BaseModel):
    invoice_id: str
    buyer_id: str
    seller_id: str
    amount: float
    due_timestamp: int
    status: str = "ISSUED" # ISSUED, DUE, OVERDUE, PARTIALLY_PAID, DISPUTED, PAID, WRITTEN_OFF
    po_number: Optional[str] = None
    grace_period_days: int = 7

class InvoiceEconomyEngine:
    """
    Manages B2B invoice aging, grace period checks, and overdue state transitions.
    """
    @staticmethod
    def update_invoice_status(invoice: InvoiceCivilizationEntity, current_timestamp: int):
        if invoice.status in ["PAID", "WRITTEN_OFF"]:
            return

        if current_timestamp > invoice.due_timestamp + (invoice.grace_period_days * 86400):
            invoice.status = "OVERDUE"
        elif current_timestamp >= invoice.due_timestamp:
            invoice.status = "DUE"
