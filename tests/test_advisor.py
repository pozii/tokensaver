"""Tests for advise_context_window tool."""
from tests.conftest import SAMPLE_MESSAGES

from tokensaver.tools.advisor import advise_context_window


def test_known_model_ok_status():
    result = advise_context_window("gpt-4o", current_tokens=10_000)
    assert result["context_window"] == 128_000
    assert result["status"] == "ok"
    assert result["target_tokens"] == int(128_000 * 0.75)


def test_warning_status():
    result = advise_context_window("gpt-4o", current_tokens=110_000)
    assert result["status"] == "warning"
    assert len(result["recommendations"]) > 0


def test_critical_status():
    result = advise_context_window("gpt-4o", current_tokens=120_000)
    assert result["status"] == "critical"
    assert any("CRITICAL" in r for r in result["recommendations"])


def test_unknown_model():
    result = advise_context_window("some-unknown-model-xyz", current_tokens=5000)
    assert result["status"] == "unknown"
    assert result["context_window"] is None


def test_per_turn_breakdown():
    result = advise_context_window("claude-sonnet-4", current_tokens=190_000, messages=SAMPLE_MESSAGES)
    assert result["per_turn_breakdown"] is not None
    assert len(result["per_turn_breakdown"]) <= 10
    # Should be sorted by tokens descending
    tokens = [t["tokens"] for t in result["per_turn_breakdown"]]
    assert tokens == sorted(tokens, reverse=True)


def test_claude_model_resolved():
    result = advise_context_window("claude-opus-4", current_tokens=5000)
    assert result["context_window"] == 200_000
    assert result["status"] == "ok"
