"""Configuration module for the agent system."""

from .api_keys import get_openai_api_key, get_serpapi_key, validate_api_keys
from .settings import settings, SYSTEM_MESSAGES

# Export commonly used settings as top-level constants
MODEL_NAME = settings.llm.model_name
TEMPERATURE = settings.llm.temperature
MAX_ITERATIONS = settings.llm.max_iterations

__all__ = [
    'get_openai_api_key',
    'get_serpapi_key',
    'validate_api_keys',
    'MODEL_NAME',
    'TEMPERATURE',
    'MAX_ITERATIONS',
    'SYSTEM_MESSAGES'
]