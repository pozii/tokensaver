"""Shared token counting utilities using tiktoken."""
from __future__ import annotations

import tiktoken

# Maps model name substrings to tiktoken encoding names
_ENCODING_MAP: dict[str, str] = {
    "gpt-4o": "o200k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5": "cl100k_base",
    "claude": "cl100k_base",
    "gemini": "cl100k_base",
    "o1": "o200k_base",
    "o3": "o200k_base",
}

_ENCODING_CACHE: dict[str, tiktoken.Encoding] = {}


def _get_encoding(model: str) -> tiktoken.Encoding:
    model_lower = model.lower()
    encoding_name = "cl100k_base"
    for key, enc in _ENCODING_MAP.items():
        if key in model_lower:
            encoding_name = enc
            break
    if encoding_name not in _ENCODING_CACHE:
        _ENCODING_CACHE[encoding_name] = tiktoken.get_encoding(encoding_name)
    return _ENCODING_CACHE[encoding_name]


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    enc = _get_encoding(model)
    return len(enc.encode(text))


def count_messages_tokens(
    messages: list[dict],
    model: str = "gpt-4o",
    include_overhead: bool = True,
) -> int:
    enc = _get_encoding(model)
    total = 0
    for msg in messages:
        content = msg.get("content") or ""
        if isinstance(content, list):
            # multi-part content (vision)
            content = " ".join(
                part.get("text", "") for part in content if isinstance(part, dict)
            )
        total += len(enc.encode(content))
        if include_overhead:
            total += 4  # role + separators per message
    if include_overhead:
        total += 2  # priming
    return total


def truncate_to_tokens(text: str, max_tokens: int, model: str = "gpt-4o") -> str:
    enc = _get_encoding(model)
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[:max_tokens])


def encoding_name_for(model: str) -> str:
    model_lower = model.lower()
    for key, enc in _ENCODING_MAP.items():
        if key in model_lower:
            return enc
    return "cl100k_base"
