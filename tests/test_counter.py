"""Tests for count_tokens tool."""
import tiktoken

from tokensaver.tools.counter import count_tokens_tool


def test_string_count():
    text = "Hello, world!"
    result = count_tokens_tool(text, model="gpt-4o")
    enc = tiktoken.get_encoding("o200k_base")
    expected = len(enc.encode(text))
    assert result["token_count"] == expected
    assert result["encoding_used"] == "o200k_base"


def test_message_list_count():
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]
    result = count_tokens_tool(messages, model="gpt-4o", include_message_overhead=True)
    assert result["token_count"] > 0
    assert isinstance(result["token_count"], int)


def test_message_list_no_overhead():
    messages = [{"role": "user", "content": "Hello"}]
    with_overhead = count_tokens_tool(messages, model="gpt-4o", include_message_overhead=True)
    without_overhead = count_tokens_tool(messages, model="gpt-4o", include_message_overhead=False)
    assert with_overhead["token_count"] > without_overhead["token_count"]


def test_claude_model_uses_cl100k():
    result = count_tokens_tool("test", model="claude-sonnet-4")
    assert result["encoding_used"] == "cl100k_base"


def test_empty_string():
    result = count_tokens_tool("", model="gpt-4o")
    assert result["token_count"] == 0
