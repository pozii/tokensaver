"""advise_context_window tool — tell agents what to trim when approaching limits."""
from __future__ import annotations

from tokensaver.models import resolve_context_window
from tokensaver.utils.token_utils import count_messages_tokens, count_tokens


def advise_context_window(
    model: str,
    current_tokens: int,
    messages: list[dict] | None = None,
    target_utilization: float = 0.75,
) -> dict:
    """
    Analyze current token usage vs model context window and recommend what to trim.
    Use this meta-tool to know WHERE to apply compress_context, prune_conversation,
    or other tokensaver tools for maximum effect.

    Args:
        model: Model name (e.g. "claude-sonnet-4", "gpt-4o", "gemini-1.5-pro").
        current_tokens: Current total tokens being sent (use count_tokens first).
        messages: Optional conversation history for per-turn breakdown.
        target_utilization: Fraction of context window to target (default 0.75 = 75%).

    Returns:
        model, context_window, current_tokens, target_tokens, headroom_tokens,
        status ("ok"|"warning"|"critical"), recommendations, per_turn_breakdown
    """
    context_window = resolve_context_window(model)

    if context_window is None:
        return {
            "model": model,
            "context_window": None,
            "current_tokens": current_tokens,
            "target_tokens": None,
            "headroom_tokens": None,
            "status": "unknown",
            "recommendations": [
                f"Unknown model '{model}'. Known models include: gpt-4o, claude-sonnet-4, gemini-1.5-pro, etc."
            ],
            "per_turn_breakdown": None,
        }

    target_tokens = int(context_window * target_utilization)
    headroom = context_window - current_tokens
    utilization = current_tokens / context_window

    if utilization <= target_utilization:
        status = "ok"
    elif utilization <= 0.9:
        status = "warning"
    else:
        status = "critical"

    recommendations: list[str] = []

    if status == "ok":
        recommendations.append(
            f"Context usage is healthy ({utilization:.0%} of {context_window:,} token window). "
            f"No action needed. {headroom:,} tokens of headroom."
        )
    elif status == "warning":
        overage = current_tokens - target_tokens
        recommendations.extend([
            f"Approaching context limit ({utilization:.0%} used, target is {target_utilization:.0%}).",
            f"Need to free ~{overage:,} tokens to reach target.",
            "Consider: prune_conversation with strategy='hybrid' to compress older turns.",
            "Consider: compress_context on any large tool results being re-injected.",
        ])
    else:  # critical
        overage = current_tokens - target_tokens
        recommendations.extend([
            f"CRITICAL: {utilization:.0%} of context window used ({current_tokens:,}/{context_window:,} tokens).",
            f"Must free ~{overage:,} tokens immediately.",
            "Action 1: prune_conversation with keep_last_n=3, strategy='hybrid'.",
            "Action 2: compress_context on system prompt if over 300 tokens.",
            "Action 3: Drop or truncate tool results — keep only the most recent.",
            "Action 4: Use summarize_file instead of raw file content.",
        ])

    per_turn_breakdown = None
    if messages:
        breakdown = []
        for i, msg in enumerate(messages):
            content = str(msg.get("content", ""))
            tok = count_tokens(content, model)
            breakdown.append({
                "index": i,
                "role": msg.get("role", "unknown"),
                "tokens": tok,
                "preview": content[:80] + ("..." if len(content) > 80 else ""),
            })
        breakdown.sort(key=lambda x: x["tokens"], reverse=True)
        per_turn_breakdown = breakdown[:10]  # top 10 largest

        if breakdown and status != "ok":
            top = breakdown[0]
            recommendations.append(
                f"Largest turn: [{top['role']}] at index {top['index']} "
                f"({top['tokens']:,} tokens) — compress or drop first."
            )

    return {
        "model": model,
        "context_window": context_window,
        "current_tokens": current_tokens,
        "target_tokens": target_tokens,
        "headroom_tokens": headroom,
        "status": status,
        "recommendations": recommendations,
        "per_turn_breakdown": per_turn_breakdown,
    }
