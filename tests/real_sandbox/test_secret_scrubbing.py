import pytest
from backend.environments.real_provider import RealProviderEnvironment

@pytest.mark.fixture
def test_observation_context_does_not_contain_secrets():
    env = RealProviderEnvironment("razorpay")
    obs = env.observe_customer("c_ananya")
    # Must not contain API keys or secrets
    assert "key_secret" not in obs
    assert "api_key" not in obs
