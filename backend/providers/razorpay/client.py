import os
import json
import base64
import time
from typing import Dict, Any, Optional, Tuple
from backend.providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderInvalidRequestError
)

class RazorpayClient:
    """
    Low-level HTTP client for Razorpay REST APIs.
    """
    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None, timeout_seconds: float = 8.0):
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID", "rzp_test_mock_key")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET", "mock_secret")
        self.timeout_seconds = timeout_seconds

    def _get_auth_header(self) -> Dict[str, str]:
        auth_bytes = f"{self.key_id}:{self.key_secret}".encode("utf-8")
        encoded = base64.b64encode(auth_bytes).decode("utf-8")
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }

    def map_http_error(self, status_code: int, response_body: str):
        if status_code == 401:
            raise ProviderAuthenticationError(f"Razorpay 401: Invalid API Key or Secret ({response_body})")
        elif status_code == 429:
            raise ProviderRateLimitError(f"Razorpay 429: Rate limit exceeded ({response_body})")
        elif status_code in (500, 502, 503, 504):
            raise ProviderUnavailableError(f"Razorpay {status_code}: Service Unavailable ({response_body})")
        else:
            raise ProviderInvalidRequestError(f"Razorpay {status_code}: {response_body}")
