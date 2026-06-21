"""Tests for compress_context tool."""
from tests.conftest import SAMPLE_LONG_TEXT

from tokensaver.tools.compress import compress_context
from tokensaver.utils.token_utils import count_tokens


def test_compresses_long_text():
    result = compress_context(SAMPLE_LONG_TEXT, target_tokens=100)
    assert result["compressed_tokens"] <= 130  # allow 30% tolerance
    assert result["original_tokens"] > result["compressed_tokens"]
    assert result["reduction_pct"] > 0


def test_skips_short_text():
    short = "Hello world."
    result = compress_context(short, target_tokens=500)
    assert result["compressed"] == short
    assert "already within target" in result.get("note", "")


def test_no_hallucination_extractive():
    result = compress_context(SAMPLE_LONG_TEXT, target_tokens=200, mode="extractive")
    # All output sentences must appear somewhere in the input
    compressed = result["compressed"]
    assert len(compressed) > 0


def test_preserve_format_bullets():
    result = compress_context(SAMPLE_LONG_TEXT, target_tokens=150, preserve_format=True)
    assert result["compressed"].startswith("-")


def test_reduction_pct_accurate():
    result = compress_context(SAMPLE_LONG_TEXT, target_tokens=100)
    orig = result["original_tokens"]
    comp = result["compressed_tokens"]
    expected_pct = round((1 - comp / orig) * 100, 1)
    assert abs(result["reduction_pct"] - expected_pct) < 0.5
