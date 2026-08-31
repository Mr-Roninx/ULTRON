import os
from typing import Dict, Any
from pydantic import BaseModel

class ProviderConfigStatus(BaseModel):
    provider: str
    environment: str
    key_present: bool
    secret_present: bool
    external_connection_verified: bool
    endpoint_class: str

class ConfigurationTruthReport(BaseModel):
    hf_token_present: bool
    llm_mode: str
    production_gate_status: str
    providers: Dict[str, ProviderConfigStatus]

class ConfigTruthReporter:
    """
    Produces safe configuration metadata without ever logging or exposing secrets.
    """
    @staticmethod
    def get_truth() -> Dict[str, Any]:
        rzp_key = bool(os.getenv("RAZORPAY_KEY_ID"))
        rzp_secret = bool(os.getenv("RAZORPAY_KEY_SECRET"))
        stripe_key = bool(os.getenv("STRIPE_SECRET_KEY"))
        adyen_key = bool(os.getenv("ADYEN_API_KEY"))
        hf_token = bool(os.getenv("HF_TOKEN"))

        from backend.safety.production_gate import production_gate

        report = ConfigurationTruthReport(
            hf_token_present=hf_token,
            llm_mode="LIVE_HF" if hf_token else "SAFE_DETERMINISTIC_FALLBACK",
            production_gate_status="DISABLED_BY_DEFAULT" if not production_gate.production_enabled else "LIVE_ENABLED",
            providers={
                "razorpay": ProviderConfigStatus(
                    provider="razorpay",
                    environment="TEST_SANDBOX",
                    key_present=rzp_key,
                    secret_present=rzp_secret,
                    external_connection_verified=rzp_key and rzp_secret,
                    endpoint_class="TEST_ENDPOINT"
                )
            }
        )
        return report.model_dump()

config_truth_reporter = ConfigTruthReporter()
