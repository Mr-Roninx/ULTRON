import os
from dotenv import load_dotenv

load_dotenv()

class UltronConfig:
    llm_provider: str = os.getenv("ULTRON_LLM_PROVIDER", "auto")
    hf_token: str | None = os.getenv("HF_TOKEN")
    hf_model: str | None = os.getenv("HF_MODEL")
    local_llm_url: str = os.getenv("LOCAL_LLM_URL", "http://localhost:8000/v1")
    local_llm_model: str | None = os.getenv("LOCAL_LLM_MODEL")
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///ultron.db")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

config = UltronConfig()
