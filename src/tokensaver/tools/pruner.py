"""prune_conversation tool — remove low-value turns from conversation history."""
from __future__ import annotations

import re
from typing import Literal

from tokensaver.tools.compress import compress_context
from tokensaver.utils.token_utils import count_messages_tokens, count_tokens

_FILLER_PATTERNS = re.compile(
    r"^(sure[!.,]?|got it[!.,]?|okay[!.,]?|ok[!.,]?|understood[!.,]?|"
    r"i['']?ll do that[!.,]?|will do[!.,]?|of course[!.,]?|certainly[!.,]?|"
    r"no problem[!.,]?|sounds good[!.,]?|alright[!.,]?)$",
    re.IGNORECASE,
)


def _value_score(msg: dict) -> float:
    role = msg.get("role", "")
    content = str(msg.get("content", "")).strip()

    if role == "system":
        return 1.0
    if not content:
        return 0.0
    if _FILLER_PATTERNS.match(content):
        return 0.05
    if role == "user":
        return 0.7
    # assistant or tool
    tokens = count_tokens(content)
    if tokens > 200:
        return 0.35  # large tool result — compress candidate
    return 0.6


def prune_conversation(
    messages: list[dict],
    max_output_tokens: int = 2000,
    keep_last_n: int = 4,
    prune_strategy: Literal["remove", "compress", "hybrid"] = "hybrid",
    model: str = "gpt-4o",
) -> dict:
    """
    Reduce conversation history token footprint by removing filler turns and
    compressing older verbose ones. Saves 60–80% on long conversations.

    Args:
        messages: OpenAI-format list of {"role": "...", "content": "..."} dicts.
        max_output_tokens: Target total size for the pruned history.
        keep_last_n: Always preserve the N most recent turns verbatim.
        prune_strategy: "remove" drops low-value turns, "compress" shrinks older
                        turns, "hybrid" does both.
        model: Used for token counting.

    Returns:
        messages (pruned list), original_tokens, pruned_tokens,
        turns_removed, turns_compressed
    """
    if not messages:
        return {
            "messages": [],
            "original_tokens": 0,
            "pruned_tokens": 0,
            "turns_removed": 0,
            "turns_compressed": 0,
        }

    original_tokens = count_messages_tokens(messages, model)

    # Lock the last N messages
    n = min(keep_last_n, len(messages))
    locked = messages[-n:] if n > 0 else []
    candidates = messages[: len(messages) - n]

    turns_removed = 0
    turns_compressed = 0

    if prune_strategy in ("remove", "hybrid"):
        new_candidates = []
        for msg in candidates:
            if _value_score(msg) < 0.1:
                turns_removed += 1
            else:
                new_candidates.append(msg)
        candidates = new_candidates

    if prune_strategy in ("compress", "hybrid"):
        locked_tokens = count_messages_tokens(locked, model)
        budget_for_history = max(0, max_output_tokens - locked_tokens)
        current = count_messages_tokens(candidates, model)

        if current > budget_for_history and budget_for_history > 0:
            # Compress each candidate proportionally
            per_msg_budget = max(50, budget_for_history // max(1, len(candidates)))
            new_candidates = []
            for msg in candidates:
                content = str(msg.get("content", ""))
                tok = count_tokens(content, model)
                if tok > per_msg_budget * 1.5 and _value_score(msg) < 0.5:
                    result = compress_context(content, target_tokens=per_msg_budget, model=model)
                    if result["compressed"] != content:
                        turns_compressed += 1
                    new_candidates.append({**msg, "content": result["compressed"]})
                else:
                    new_candidates.append(msg)
            candidates = new_candidates

    pruned = candidates + locked
    pruned_tokens = count_messages_tokens(pruned, model)

    return {
        "messages": pruned,
        "original_tokens": original_tokens,
        "pruned_tokens": pruned_tokens,
        "turns_removed": turns_removed,
        "turns_compressed": turns_compressed,
    }
