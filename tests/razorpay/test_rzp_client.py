import pytest
from backend.providers.razorpay.client import RazorpayClient

@pytest.mark.fixture
def test_razorpay_client_initialization():
    client = RazorpayClient(key_id="rzp_test_mock", key_secret="rzp_secret_mock")
    assert client.key_id == "rzp_test_mock"
    assert "https://api.razorpay.com/v1" in client.BASE_URL
