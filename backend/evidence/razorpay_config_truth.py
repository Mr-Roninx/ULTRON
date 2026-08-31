import os
from typing import Dict, Any
from pydantic import BaseModel

class RazorpayConfigTruth(BaseModel):
    provider: str = "razorpay"
    environment: str = "TEST"
    endpoint: str = "https://api.razorpay.com/v1"
    key_id_present: bool = False
    key_secret_present: bool = False
    webhook_secret_present: bool = False
    llm_provider_configured: str = "SAFE_DETERMINISTIC_FALLBACK"

class RazorpayConfigInspector:
    """
    Safely inspects Razorpay test configuration from .env without ever logging or exposing secrets.
    """
    @staticmethod
    def inspect() -> Dict[str, Any]:
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
        hf_token = os.getenv("HF_TOKEN")

        report = RazorpayConfigTruth(
            key_id_present=bool(key_id and len(key_id.strip()) > 0),
            key_secret_present=bool(key_secret and len(key_secret.strip()) > 0),
            webhook_secret_present=bool(webhook_secret and len(webhook_secret.strip()) > 0),
            llm_provider_configured="LIVE_HF" if bool(hf_token and len(hf_token.strip()) > 0) else "SAFE_DETERMINISTIC_FALLBACK"
        )
        return report.model_dump()

razorpay_config_inspector = RazorpayConfigInspector()
