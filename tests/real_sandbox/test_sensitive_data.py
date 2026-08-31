import pytest
from backend.providers.models import CanonicalCustomer

@pytest.mark.fixture
def test_sensitive_customer_data_redaction():
    cust = CanonicalCustomer(customer_id="c_101", name="Ananya Textiles", email="finance@ananya.com", phone="+919876543210")
    d = cust.model_dump()
    # PAN / CVV / raw banking credentials must never exist on model
    assert "pan" not in d
    assert "cvv" not in d
    assert "bank_password" not in d
