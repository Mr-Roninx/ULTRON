from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

from backend.agent.schemas import AgentIntent
from backend.audit.ledger import audit_ledger
from backend.llm.performance import llm_performance_controller, LLMOperatingMode
import uuid
import time

class LLMProvider(ABC):
    @abstractmethod
    def health(self) -> bool:
        pass

    @abstractmethod
    def generate_intent(self, messages: List[Dict[str, str]], schemas: List[Dict[str, Any]]) -> AgentIntent:
        pass

class HuggingFaceProvider(LLMProvider):
    def __init__(
        self,
        api_token: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        base_url: str = "https://router.huggingface.co/v1"
    ):
        self.api_token = api_token or os.environ.get("HF_TOKEN", "")
        self.model_name = model_name or os.environ.get("HF_MODEL", "Qwen/Qwen3.8-2.4T-A95B:novita")
        self.timeout_seconds = timeout_seconds or llm_performance_controller.get_hard_timeout_seconds()
        self.base_url = base_url

    def health(self) -> bool:
        if not self.api_token:
            return False
        try:
            from openai import OpenAI
            client = OpenAI(base_url=self.base_url, api_key=self.api_token, timeout=4.0)
            res = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=2
            )
            return bool(res and res.choices)
        except Exception:
            return False

    def generate_intent(self, messages: List[Dict[str, str]], schemas: List[Dict[str, Any]]) -> AgentIntent:
        if not self.api_token:
            raise ConnectionError("HF_TOKEN not configured.")

        valid_action_types = [
            "WAIT", "RECONCILE", "RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B",
            "RETRY_GATEWAY_C", "SWITCH_PERMITTED_RAIL", "ALTERNATE_RAIL",
            "REQUEST_CUSTOMER_ACTION", "SEND_PAYMENT_LINK", "SEND_MESSAGE",
            "EMAIL", "SMS", "REGISTER_PTP", "ESCALATE", "STOP"
        ]

        system_instruction = (
            "You are an autonomous fintech revenue recovery agent. Output MUST be ONLY a valid JSON object matching this schema:\n"
            "{\n"
            f"  \"action_type\": \"MUST be exactly one of: {valid_action_types}\",\n"
            f"  \"candidate_actions\": [\"list of valid action types from {valid_action_types}\"],\n"
            "  \"preferred_action\": \"string (name of chosen action)\",\n"
            "  \"reasoning\": \"string (clear financial explanation)\",\n"
            "  \"expected_yield\": float (e.g. 5000.0),\n"
            "  \"payload\": {\"payment_id\": \"string\"}\n"
            "}\n"
            "Do NOT include any conversational preamble or thinking before the JSON. Start your output with '{'."
        )
        formatted_messages = [{"role": "system", "content": system_instruction}] + messages

        req_id = f"req_{uuid.uuid4().hex[:8]}"
        start_t = time.time()
        context_len = sum(len(m.get("content", "")) for m in messages)

        try:
            from openai import OpenAI
            import re
            client = OpenAI(base_url=self.base_url, api_key=self.api_token, timeout=self.timeout_seconds)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                max_tokens=llm_performance_controller.max_output_tokens,
                temperature=0.1
            )
            msg = response.choices[0].message
            text = msg.content or getattr(msg, "reasoning_content", "") or ""
            
            # Clean markdown JSON wraps
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            parsed = None
            start_idx = text.find("{")
            end_idx = text.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                try:
                    json_str = text[start_idx:end_idx+1]
                    parsed = json.loads(json_str)
                except Exception:
                    pass

            if not parsed:
                # Truncation or plain text recovery: attempt regex / keyword extraction
                act_match = re.search(r'"action_type"\s*:\s*"([^"]+)"', text)
                reason_match = re.search(r'"reasoning"\s*:\s*"([^"]+)', text)
                pref_match = re.search(r'"preferred_action"\s*:\s*"([^"]+)"', text)
                yield_match = re.search(r'"expected_yield"\s*:\s*([0-9.]+)', text)
                
                if act_match:
                    act = act_match.group(1)
                else:
                    # Scan text for known action keywords
                    act = "WAIT"
                    for candidate in ["RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "SWITCH_PERMITTED_RAIL", "SEND_PAYMENT_LINK", "RETRY", "WAIT", "RECONCILE"]:
                        if candidate in text.upper():
                            act = candidate
                            break

                parsed = {
                    "action_type": act,
                    "candidate_actions": [act, "WAIT"],
                    "preferred_action": pref_match.group(1) if pref_match else act,
                    "reasoning": reason_match.group(1).rstrip(",\"") if reason_match else (text[:200] if text else "Extracted from LLM response."),
                    "expected_yield": float(yield_match.group(1)) if yield_match else 5000.0,
                    "payload": {}
                }

            if parsed:
                # Normalize action_type if needed
                raw_act = str(parsed.get("action_type", "")).upper()
                if raw_act not in valid_action_types:
                    if "LINK" in raw_act or "PAYMENT" in raw_act:
                        parsed["action_type"] = "SEND_PAYMENT_LINK"
                    elif "GATEWAY_B" in raw_act or "SWITCH" in raw_act:
                        parsed["action_type"] = "SWITCH_PERMITTED_RAIL"
                    elif "RETRY" in raw_act:
                        parsed["action_type"] = "RETRY"
                    else:
                        parsed["action_type"] = "WAIT"

                if not parsed.get("candidate_actions"):
                    parsed["candidate_actions"] = [parsed["action_type"], "WAIT"]

                if not parsed.get("payload"):
                    parsed["payload"] = {}

                latency_ms = (time.time() - start_t) * 1000.0
                llm_performance_controller.record_execution(
                    request_id=req_id,
                    provider="HuggingFace",
                    model=self.model_name,
                    latency_ms=latency_ms,
                    status="SUCCESS",
                    fallback_used=False,
                    context_chars=context_len
                )
                from backend.llm.provider_health import provider_health_tracker, ProviderHealthStatus
                provider_health_tracker.record_attempt(
                    provider="HuggingFace",
                    model=self.model_name,
                    credential_available=bool(self.api_token),
                    request_success=True,
                    status=ProviderHealthStatus.AVAILABLE,
                    latency_ms=latency_ms,
                    fallback_used=False
                )

                return AgentIntent(**parsed)
            raise ValueError(f"No valid JSON found in HF output: {text}")

        except Exception as e:
            latency_ms = (time.time() - start_t) * 1000.0
            is_timeout = "timeout" in str(e).lower() or "timed out" in str(e).lower()
            llm_performance_controller.record_execution(
                request_id=req_id,
                provider="HuggingFace",
                model=self.model_name,
                latency_ms=latency_ms,
                status="TIMEOUT" if is_timeout else "ERROR",
                fallback_used=True,
                context_chars=context_len,
                error_message=str(e)
            )

            from backend.llm.provider_health import provider_health_tracker, ProviderHealthStatus
            h_status = ProviderHealthStatus.TIMEOUT if is_timeout else (
                ProviderHealthStatus.CREDIT_EXHAUSTED if "402" in str(e) else (
                    ProviderHealthStatus.RATE_LIMITED if "429" in str(e) else ProviderHealthStatus.OFFLINE
                )
            )
            http_st = 402 if "402" in str(e) else (429 if "429" in str(e) else None)
            provider_health_tracker.record_attempt(
                provider="HuggingFace",
                model=self.model_name,
                credential_available=bool(self.api_token),
                request_success=False,
                status=h_status,
                failure_reason=str(e)[:200],
                http_status=http_st,
                latency_ms=latency_ms,
                fallback_used=True
            )

            if "402" in str(e):
                raise RuntimeError("Hugging Face monthly credits depleted (402).")
            if "429" in str(e):
                raise RuntimeError("Hugging Face API rate limit reached (429).")
            if "401" in str(e) or "403" in str(e):
                raise PermissionError("Hugging Face authentication failed.")
            if is_timeout:
                raise TimeoutError(f"Hugging Face request timed out after {self.timeout_seconds}s.")
            raise ConnectionError(f"Hugging Face invocation failed: {str(e)}")

class LocalQwenProvider(LLMProvider):
    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ):
        self.base_url = (base_url or os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/v1")).rstrip("/")
        self.model_name = model_name or os.environ.get("LOCAL_LLM_MODEL", "qwen2.5:7b")
        self.timeout_seconds = timeout_seconds or llm_performance_controller.get_soft_timeout_seconds()

    def health(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/models", method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate_intent(self, messages: List[Dict[str, str]], schemas: List[Dict[str, Any]]) -> AgentIntent:
        req_id = f"req_local_{uuid.uuid4().hex[:8]}"
        start_t = time.time()
        context_len = sum(len(m.get("content", "")) for m in messages)

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": llm_performance_controller.max_output_tokens,
            "response_format": {"type": "json_object"}
        }

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw_data = json.loads(response.read().decode("utf-8"))
                choice = raw_data.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "")
                parsed = json.loads(content)
                intent = AgentIntent(**parsed)

                latency_ms = (time.time() - start_t) * 1000.0
                llm_performance_controller.record_execution(
                    request_id=req_id,
                    provider="LocalQwen",
                    model=self.model_name,
                    latency_ms=latency_ms,
                    status="SUCCESS",
                    fallback_used=True,
                    context_chars=context_len
                )
                return intent
        except urllib.error.HTTPError as e:
            latency_ms = (time.time() - start_t) * 1000.0
            llm_performance_controller.record_execution(
                request_id=req_id, provider="LocalQwen", model=self.model_name,
                latency_ms=latency_ms, status="ERROR", fallback_used=True, error_message=f"HTTP {e.code}"
            )
            raise ConnectionError(f"Local Qwen HTTP Error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            latency_ms = (time.time() - start_t) * 1000.0
            llm_performance_controller.record_execution(
                request_id=req_id, provider="LocalQwen", model=self.model_name,
                latency_ms=latency_ms, status="TIMEOUT", fallback_used=True, error_message=str(e.reason)
            )
            raise TimeoutError(f"Local Qwen endpoint unreachable at {self.base_url}: {e.reason}")
        except Exception as e:
            latency_ms = (time.time() - start_t) * 1000.0
            llm_performance_controller.record_execution(
                request_id=req_id, provider="LocalQwen", model=self.model_name,
                latency_ms=latency_ms, status="ERROR", fallback_used=True, error_message=str(e)
            )
            raise ValueError(f"Failed to parse Local Qwen response: {str(e)}")

class MockProvider(LLMProvider):
    """Deterministic mock provider for simulation tests."""
    def __init__(self, predefined_intents: Optional[List[AgentIntent]] = None):
        self.predefined_intents = list(predefined_intents) if predefined_intents else []
        self.call_count = 0

    def health(self) -> bool:
        return True

    def generate_intent(self, messages: List[Dict[str, str]], schemas: List[Dict[str, Any]]) -> AgentIntent:
        if self.call_count < len(self.predefined_intents):
            intent = self.predefined_intents[self.call_count]
            self.call_count += 1
            return intent
        return AgentIntent(
            action_type="WAIT",
            reasoning="Default fallback from mock provider.",
            expected_yield=0.0,
            payload={}
        )

class LLMRouter(LLMProvider):
    """
    Multi-provider router implementing automatic failover:
    Primary (Hugging Face) -> Fallback (Local Qwen) -> Safe Failure (WAIT)
    """
    def __init__(
        self,
        primary: Optional[LLMProvider] = None,
        fallback: Optional[LLMProvider] = None,
        active_provider_name: Optional[str] = None,
        mode: Optional[LLMOperatingMode] = None
    ):
        self.mode = mode or llm_performance_controller.mode
        self.active_provider_name = active_provider_name or os.environ.get("ULTRON_LLM_PROVIDER", "auto")
        self.primary = primary or HuggingFaceProvider()
        self.fallback = fallback or LocalQwenProvider()
        self.mock = MockProvider()

    def health(self) -> bool:
        if self.mode == LLMOperatingMode.SAFE_MODE or self.mode == LLMOperatingMode.BENCHMARK_MODE:
            return True
        if self.active_provider_name == "MOCK":
            return True
        if self.active_provider_name == "HF":
            return self.primary.health()
        if self.active_provider_name == "LOCAL_QWEN":
            return self.fallback.health()
        return self.primary.health() or self.fallback.health()

    def generate_intent(self, messages: List[Dict[str, str]], schemas: List[Dict[str, Any]]) -> AgentIntent:
        # Operating mode overrides
        if self.mode == LLMOperatingMode.SAFE_MODE:
            return AgentIntent(
                action_type="WAIT",
                candidate_actions=["WAIT"],
                preferred_action="WAIT",
                reasoning="SAFE_MODE: Deterministic safe policy engaged.",
                expected_yield=0.0,
                payload={}
            )

        if self.mode == LLMOperatingMode.BENCHMARK_MODE or self.active_provider_name == "MOCK":
            return self.mock.generate_intent(messages, schemas)

        # 1. Attempt Primary Provider (Hugging Face)
        try:
            intent = self.primary.generate_intent(messages, schemas)
            audit_ledger.log(
                event_type="LLM_INFERENCE_SUCCESS",
                actor="HF_PROVIDER",
                payload={"provider": "HuggingFace", "action_type": intent.action_type}
            )
            return intent
        except Exception as e_primary:
            audit_ledger.log(
                event_type="LLM_FAILOVER_TRIGGERED",
                actor="LLM_ROUTER",
                payload={"primary_error": str(e_primary), "target": "LocalQwen"}
            )

        # 2. Attempt Fallback Provider (Local Qwen)
        try:
            intent = self.fallback.generate_intent(messages, schemas)
            audit_ledger.log(
                event_type="LLM_INFERENCE_SUCCESS",
                actor="LOCAL_QWEN_PROVIDER",
                payload={"provider": "LocalQwen", "action_type": intent.action_type}
            )
            return intent
        except Exception as e_fallback:
            audit_ledger.log(
                event_type="LLM_FALLBACK_FAILED",
                actor="LLM_ROUTER",
                payload={"fallback_error": str(e_fallback), "terminal": "SAFE_FAILURE"}
            )

        # 3. Safe Failure Fallback (Never crash or hang)
        return AgentIntent(
            action_type="WAIT",
            candidate_actions=["WAIT"],
            preferred_action="WAIT",
            reasoning="Safe failure: All LLM providers failed or were unavailable.",
            expected_yield=0.0,
            payload={}
        )

