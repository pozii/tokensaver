"""Tests for optimize_prompt tool."""
from tokensaver.tools.optimizer import optimize_prompt

VERBOSE_PROMPT = """
Please make sure to answer all questions clearly and concisely.
It is important that you always provide accurate information.
As an AI assistant, you should never make up facts that are not true.
Please make sure to cite sources when possible.
Keep in mind that the user may not be an expert in the field.
You should also keep in mind that brevity is valued.
When responding, you must always be polite and respectful.
You must never provide harmful advice.
"""


def test_light_reduces_tokens():
    result = optimize_prompt(VERBOSE_PROMPT, optimization_level="light")
    assert result["optimized_tokens"] < result["original_tokens"]
    assert result["reduction_pct"] > 0


def test_medium_reduces_more_than_light():
    light = optimize_prompt(VERBOSE_PROMPT, optimization_level="light")
    medium = optimize_prompt(VERBOSE_PROMPT, optimization_level="medium")
    assert medium["optimized_tokens"] <= light["optimized_tokens"]


def test_preserve_constraints():
    result = optimize_prompt(VERBOSE_PROMPT, preserve_constraints=True, optimization_level="aggressive")
    optimized = result["optimized"].lower()
    assert "never" in optimized or "must" in optimized


def test_bullets_output_format():
    result = optimize_prompt(VERBOSE_PROMPT, output_format="bullets")
    assert result["optimized"].startswith("-")


def test_filler_removed():
    result = optimize_prompt("Please make sure to answer questions. You should help users.", optimization_level="light")
    assert "please make sure to" not in result["optimized"].lower()
