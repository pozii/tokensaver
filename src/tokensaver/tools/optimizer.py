"""optimize_prompt tool — shorten verbose or redundant prompts."""
from __future__ import annotations

import re
from typing import Literal

from tokensaver.utils.text_utils import (
    deduplicate_sentences,
    remove_filler_phrases,
    split_sentences,
    type_token_ratio,
)
from tokensaver.utils.token_utils import count_tokens

_CONSTRAINT_WORDS = re.compile(r"\b(never|always|must|do not|don't|cannot|can't|required|forbidden)\b", re.IGNORECASE)

_PASSIVE_PATTERNS = [
    (re.compile(r"\bshould be (noted|mentioned) that\b", re.IGNORECASE), "note:"),
    (re.compile(r"\bit is (important|critical|essential) (that|to)\b", re.IGNORECASE), ""),
    (re.compile(r"\bplease (make sure|ensure) (to|that)\b", re.IGNORECASE), ""),
    (re.compile(r"\bwhen (responding|answering|replying),?\s*", re.IGNORECASE), ""),
    (re.compile(r"\b(your|the) (goal|objective|task|job) is to\b", re.IGNORECASE), ""),
    (re.compile(r"\byou (are|will be) (acting as|playing the role of)\b", re.IGNORECASE), "you are"),
    (re.compile(r"\bIn (this|the following) (context|scenario|situation),?\s*", re.IGNORECASE), ""),
]


def _apply_light(text: str, preserve_constraints: bool) -> str:
    if preserve_constraints:
        sentences = split_sentences(text)
        protected = [s for s in sentences if _CONSTRAINT_WORDS.search(s)]
        unprotected = [s for s in sentences if not _CONSTRAINT_WORDS.search(s)]
        cleaned = remove_filler_phrases(" ".join(unprotected))
        deduped = deduplicate_sentences(split_sentences(cleaned))
        body = " ".join(deduped)
        return body + (" " + " ".join(protected) if protected else "")
    else:
        text = remove_filler_phrases(text)
        sentences = split_sentences(text)
        return " ".join(deduplicate_sentences(sentences))


def _apply_medium(text: str, preserve_constraints: bool) -> str:
    text = _apply_light(text, preserve_constraints)
    sentences = split_sentences(text)
    if len(sentences) <= 3:
        return text

    # Keep highest type-token-ratio sentences (most information-dense)
    scored = [(s, type_token_ratio(s)) for s in sentences]
    # Protect constraint sentences
    if preserve_constraints:
        keep = [s for s, _ in scored if _CONSTRAINT_WORDS.search(s)]
        remainder = [(s, sc) for s, sc in scored if not _CONSTRAINT_WORDS.search(s)]
    else:
        keep = []
        remainder = scored

    # Keep top 70% by information density
    remainder.sort(key=lambda x: x[1], reverse=True)
    cutoff = max(1, int(len(remainder) * 0.7))
    selected_set = {s for s, _ in remainder[:cutoff]}

    # Rebuild in original order
    ordered = [s for s in sentences if s in selected_set or s in keep]
    return " ".join(ordered)


def _apply_aggressive(text: str, preserve_constraints: bool) -> str:
    text = _apply_medium(text, preserve_constraints)
    for pattern, replacement in _PASSIVE_PATTERNS:
        text = pattern.sub(replacement, text)
    # Collapse multiple spaces
    text = re.sub(r"  +", " ", text).strip()
    return text


def optimize_prompt(
    prompt: str,
    optimization_level: Literal["light", "medium", "aggressive"] = "medium",
    preserve_constraints: bool = True,
    output_format: Literal["prose", "bullets"] = "prose",
    model: str = "gpt-4o",
) -> dict:
    """
    Shorten a verbose or redundant prompt/system prompt while preserving intent.
    Typical savings: 30–65%. Run once on system prompts that accumulate over iterations.

    Args:
        prompt: The prompt text to optimize.
        optimization_level: "light" removes obvious filler, "medium" restructures,
                             "aggressive" rewrites minimally.
        preserve_constraints: Never remove sentences with "never/must/always/do not".
        output_format: "prose" for flowing text, "bullets" for a bulleted list.
        model: Used for token counting.

    Returns:
        optimized, original_tokens, optimized_tokens, reduction_pct
    """
    original_tokens = count_tokens(prompt, model)

    if optimization_level == "light":
        result = _apply_light(prompt, preserve_constraints)
    elif optimization_level == "medium":
        result = _apply_medium(prompt, preserve_constraints)
    else:
        result = _apply_aggressive(prompt, preserve_constraints)

    if output_format == "bullets":
        sentences = split_sentences(result)
        result = "\n".join(f"- {s.rstrip('.')}" for s in sentences if s.strip())

    optimized_tokens = count_tokens(result, model)
    reduction = round((1 - optimized_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0.0

    return {
        "optimized": result,
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "reduction_pct": reduction,
    }
