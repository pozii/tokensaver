"""Shared text processing utilities."""
from __future__ import annotations

import re


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using simple regex (no NLTK download required)."""
    # Handle common abbreviations to avoid false splits
    text = re.sub(r"\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|i\.e|e\.g)\.", r"\1<dot>", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"\'])", text)
    restored = [p.replace("<dot>", ".") for p in parts]
    return [s.strip() for s in restored if s.strip()]


def clean_whitespace(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def remove_filler_phrases(text: str) -> str:
    fillers = [
        r"[Pp]lease make sure to\b",
        r"[Ii]t is important (that|to)\b",
        r"[Aa]s an AI (assistant|language model),?\s*",
        r"[Kk]eep in mind (that)?\b",
        r"[Ii] want to emphasize (that)?\b",
        r"[Ii] would like to (point out|note) (that)?\b",
        r"[Ii]t('s| is) worth (noting|mentioning) (that)?\b",
        r"[Yy]ou (should|might want to) (also )?(note|know) (that)?\b",
        r"[Aa]s (I )?mentioned (earlier|above|before),?\s*",
    ]
    for pattern in fillers:
        text = re.sub(pattern, "", text)
    return clean_whitespace(text)


def jaccard_similarity(a: str, b: str) -> float:
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def deduplicate_sentences(sentences: list[str], threshold: float = 0.85) -> list[str]:
    kept: list[str] = []
    for sent in sentences:
        if not any(jaccard_similarity(sent, k) >= threshold for k in kept):
            kept.append(sent)
    return kept


def type_token_ratio(text: str) -> float:
    tokens = text.lower().split()
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)
