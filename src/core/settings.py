import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(override=False)

@dataclass
class Settings:
    # IO & data
    data_dir: str = os.getenv("DATA_DIR", "data")

    # LLM
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "http://localhost:11434")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "qwen2.5:3b-instruct")
    llm_enabled: bool = os.getenv("LLM_ENABLED", "true").lower() == "true"

    # Retrieval - Tăng top_k và max_context để có thông tin đầy đủ hơn
    top_k: int = int(os.getenv("TOP_K", "8"))
    max_context_chars: int = int(os.getenv("MAX_CONTEXT_CHARS", "6000"))

    # Gen length - Tăng max_tokens để có câu trả lời chi tiết hơn
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))

    # Modes - Tắt direct_cite để luôn có phân tích đầy đủ
    direct_cite_first: bool = os.getenv("DIRECT_CITE_FIRST", "false").lower() == "true"
