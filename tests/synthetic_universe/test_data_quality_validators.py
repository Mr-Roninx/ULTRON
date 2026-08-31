import pytest
from synthetic_payment_universe.schema.entities import Customer, Merchant, Payment
from synthetic_payment_universe.validators.schema_validator import UniverseSchemaValidator
from synthetic_payment_universe.validators.referential_validator import UniverseReferentialValidator

def test_data_quality_validations():
    c = Customer(customer_id="c_valid_1", name="Valid Corp", average_transaction_value=15000.0)
    m = Merchant(merchant_id="m_valid_1", name="Valid Merch", monthly_volume=100000.0)
    p = Payment(payment_id="p_valid_1", customer_id="c_valid_1", merchant_id="m_valid_1", amount=12000.0)

    # Valid check
    is_valid_s, _ = UniverseSchemaValidator.validate_entities([c], [m], [p])
    assert is_valid_s is True

    is_valid_r, _ = UniverseReferentialValidator.validate_relationships([c], [m], [p])
    assert is_valid_r is True

    # Referential error check
    p_broken = Payment(payment_id="p_broken", customer_id="c_non_existent", merchant_id="m_valid_1", amount=5000.0)
    is_valid_broken, errs_broken = UniverseReferentialValidator.validate_relationships([c], [m], [p_broken])
    assert is_valid_broken is False
    assert len(errs_broken) > 0
