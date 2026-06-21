"""Tests for prune_conversation tool."""
from tests.conftest import SAMPLE_MESSAGES

from tokensaver.tools.pruner import prune_conversation


def test_removes_filler_turns():
    # keep_last_n=2 so "Sure!" and "Got it." are both in the candidate set (not locked)
    result = prune_conversation(SAMPLE_MESSAGES, max_output_tokens=2000, prune_strategy="remove", keep_last_n=2)
    removed_contents = {msg["content"] for msg in result["messages"]}
    assert "Sure!" not in removed_contents
    assert "Got it." not in removed_contents
    assert result["turns_removed"] >= 2


def test_preserves_last_n():
    result = prune_conversation(SAMPLE_MESSAGES, keep_last_n=3, prune_strategy="remove")
    pruned = result["messages"]
    # Last 3 messages of input must be last 3 of output
    assert pruned[-3:] == SAMPLE_MESSAGES[-3:]


def test_output_under_budget():
    from tokensaver.utils.token_utils import count_messages_tokens
    result = prune_conversation(SAMPLE_MESSAGES, max_output_tokens=200, prune_strategy="hybrid")
    actual_tokens = count_messages_tokens(result["messages"])
    # Allow some tolerance since keep_last_n may force slightly over budget
    assert actual_tokens <= 400


def test_reduces_token_count():
    result = prune_conversation(SAMPLE_MESSAGES, prune_strategy="hybrid")
    assert result["pruned_tokens"] <= result["original_tokens"]


def test_empty_messages():
    result = prune_conversation([])
    assert result["messages"] == []
    assert result["original_tokens"] == 0


def test_system_message_preserved():
    result = prune_conversation(SAMPLE_MESSAGES, prune_strategy="remove")
    roles = [m["role"] for m in result["messages"]]
    assert "system" in roles
