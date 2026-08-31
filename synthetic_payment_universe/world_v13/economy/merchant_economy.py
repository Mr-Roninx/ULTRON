from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class MerchantEconomyEntity(BaseModel):
    merchant_id: str
    industry: str = "SaaS"
    monthly_volume: float = 10000000.0
    primary_gateway_id: str = "GATEWAY_A"
    secondary_gateway_id: str = "GATEWAY_B"
    outstanding_receivables: float = 0.0
    recovered_revenue: float = 0.0
    lost_revenue: float = 0.0
    disputed_revenue: float = 0.0
    total_processing_fees: float = 0.0
    active_customers: int = 500
    churned_customers: int = 0

class MerchantEconomyEngine:
    """
    Simulates merchant-level macro financials, processing fee accumulation, and receivables.
    """
    @staticmethod
    def record_payment_success(merchant: MerchantEconomyEntity, amount: float, fee_rate: float = 0.015):
        merchant.recovered_revenue = round(merchant.recovered_revenue + amount, 2)
        fee = round(amount * fee_rate, 2)
        merchant.total_processing_fees = round(merchant.total_processing_fees + fee, 2)

    @staticmethod
    def record_payment_failure(merchant: MerchantEconomyEntity, amount: float):
        merchant.outstanding_receivables = round(merchant.outstanding_receivables + amount, 2)

    @staticmethod
    def record_dispute(merchant: MerchantEconomyEntity, amount: float):
        merchant.disputed_revenue = round(merchant.disputed_revenue + amount, 2)

    @staticmethod
    def record_write_off(merchant: MerchantEconomyEntity, amount: float):
        merchant.outstanding_receivables = max(0.0, round(merchant.outstanding_receivables - amount, 2))
        merchant.lost_revenue = round(merchant.lost_revenue + amount, 2)
