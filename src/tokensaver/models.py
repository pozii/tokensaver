"""Shared data models and constants."""
from __future__ import annotations

from pydantic import BaseModel

MODEL_CONTEXT_WINDOWS: dict[str, int] = {
    # OpenAI
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-4-turbo": 128_000,
    "gpt-4": 8_192,
    "gpt-3.5-turbo": 16_385,
    "o1": 200_000,
    "o1-mini": 128_000,
    "o3": 200_000,
    "o3-mini": 200_000,
    # Anthropic
    "claude-3-5-sonnet": 200_000,
    "claude-3-5-haiku": 200_000,
    "claude-3-opus": 200_000,
    "claude-sonnet-4": 200_000,
    "claude-opus-4": 200_000,
    "claude-haiku-4": 200_000,
    "claude-3-haiku": 200_000,
    "claude-2": 100_000,
    # Google
    "gemini-1.5-pro": 1_048_576,
    "gemini-1.5-flash": 1_048_576,
    "gemini-2.0-flash": 1_048_576,
    "gemini-2.5-pro": 1_048_576,
    "gemini-pro": 32_768,
    # Meta / open source
    "llama-3": 128_000,
    "mistral": 32_768,
}


def resolve_context_window(model: str) -> int | None:
    """Fuzzy match model name against the table."""
    model_lower = model.lower()
    for key, window in MODEL_CONTEXT_WINDOWS.items():
        if key in model_lower or model_lower in key:
            return window
    return None


class Message(BaseModel):
    role: str
    content: str
