import pytest
from synthetic_payment_universe.world_v13.economy.merchant_economy import MerchantEconomyEntity, MerchantEconomyEngine

def test_merchant_macro_economics():
    merch = MerchantEconomyEntity(merchant_id="m_1")
    MerchantEconomyEngine.record_payment_failure(merch, 50000.0)
    assert merch.outstanding_receivables == 50000.0

    MerchantEconomyEngine.record_payment_success(merch, 50000.0)
    assert merch.recovered_revenue == 50000.0
    assert merch.total_processing_fees == 750.0 # 1.5% fee
