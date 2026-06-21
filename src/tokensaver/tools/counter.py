"""count_tokens tool — estimate token usage before sending."""
from __future__ import annotations

from tokensaver.utils.token_utils import (
    count_messages_tokens,
    count_tokens,
    encoding_name_for,
)


def count_tokens_tool(
    content: str | list[dict],
    model: str = "gpt-4o",
    include_message_overhead: bool = True,
) -> dict:
    """
    Estimate token count for text or a message list before sending to an API.
    Use this to decide whether to compress, prune, or skip content.

    Args:
        content: Plain string OR list of {"role": "...", "content": "..."} dicts.
        model: Model name — used to pick the right tokenizer encoding.
        include_message_overhead: Add per-message role/separator overhead (4 tokens each).

    Returns:
        token_count, encoding_used, model
    """
    encoding = encoding_name_for(model)
    if isinstance(content, str):
        n = count_tokens(content, model)
    else:
        n = count_messages_tokens(content, model, include_message_overhead)
    return {"token_count": n, "encoding_used": encoding, "model": model}
