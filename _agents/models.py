from agents.extensions.models.litellm_model import LitellmModel
from config import settings

qwen_max_latest = LitellmModel(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
)
