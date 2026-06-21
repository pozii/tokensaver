"""compress_context tool — shrink long text into a dense summary."""
from __future__ import annotations

import math
from typing import Literal

import nltk

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer

from tokensaver.utils.token_utils import count_tokens, truncate_to_tokens


def _extractive_summarize(text: str, target_tokens: int, model: str) -> str:
    current = count_tokens(text, model)
    if current <= target_tokens:
        return text

    # Estimate how many sentences to keep
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    doc_sentences = list(parser.document.sentences)
    n_sentences = max(1, len(doc_sentences))
    ratio = target_tokens / current
    keep_n = max(1, math.ceil(n_sentences * ratio))

    summarizer = LsaSummarizer()
    summary_sentences = summarizer(parser.document, keep_n)
    # Preserve original sentence order
    sentence_texts = [str(s) for s in doc_sentences]
    selected = {str(s) for s in summary_sentences}
    ordered = [s for s in sentence_texts if s in selected]
    result = " ".join(ordered)

    # Final safety truncation if still over
    return truncate_to_tokens(result, target_tokens, model)


def compress_context(
    text: str,
    target_tokens: int = 500,
    mode: Literal["extractive", "abstractive"] = "extractive",
    preserve_format: bool = False,
    model: str = "gpt-4o",
) -> dict:
    """
    Compress long text or conversation history into a dense summary.
    Use before re-injecting large context on repeated turns.

    Extractive mode (default): offline, free, uses LSA sentence ranking.
    Abstractive mode: higher quality but requires ANTHROPIC_API_KEY env var.

    Args:
        text: The content to compress.
        target_tokens: Approximate desired output size in tokens.
        mode: "extractive" (free/offline) or "abstractive" (LLM-backed).
        preserve_format: If True, output as bullet points; else dense prose.
        model: Used for token counting (does not affect which API is called).

    Returns:
        compressed, original_tokens, compressed_tokens, reduction_pct
    """
    original_tokens = count_tokens(text, model)

    # Skip compression if already small enough
    if original_tokens <= int(target_tokens * 1.1):
        return {
            "compressed": text,
            "original_tokens": original_tokens,
            "compressed_tokens": original_tokens,
            "reduction_pct": 0.0,
            "note": "already within target",
        }

    if mode == "abstractive":
        compressed = _abstractive_summarize(text, target_tokens)
    else:
        compressed = _extractive_summarize(text, target_tokens, model)

    if preserve_format:
        lines = compressed.split(". ")
        compressed = "\n".join(f"- {l.strip().rstrip('.')}" for l in lines if l.strip())

    compressed_tokens = count_tokens(compressed, model)
    reduction = round((1 - compressed_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0.0

    return {
        "compressed": compressed,
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "reduction_pct": reduction,
    }


def _abstractive_summarize(text: str, target_tokens: int) -> str:
    try:
        import anthropic  # type: ignore
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=target_tokens + 100,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Compress the following text to approximately {target_tokens} tokens. "
                        "Preserve all factual content, decisions, and constraints. "
                        "Remove filler, repetition, and verbose phrasing. Output only the compressed text:\n\n"
                        + text
                    ),
                }
            ],
        )
        return response.content[0].text
    except ImportError:
        raise RuntimeError(
            "abstractive mode requires the 'anthropic' package: pip install tokensaver-mcp[llm]"
        )
