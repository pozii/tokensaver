<div align="center">

# TokenSaver MCP

**Cut your AI API costs by up to 97% — without changing a single prompt.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/MCP-compatible-green)](https://modelcontextprotocol.io)
[![Tests](https://img.shields.io/badge/tests-38%20passing-brightgreen)](#running-tests)

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that gives AI agents ten tools to measure, compress, cache, and prune token usage — so developers on limited plans can do more with less.

</div>

---

## Why TokenSaver?

Every API call sends more tokens than necessary. Conversation history accumulates. Web pages arrive as raw HTML. Tool results get re-fetched on every turn. System prompts bloat over iterations.

TokenSaver intercepts each of these patterns and fixes them at the agent level — no model changes, no prompt engineering, no plan upgrades.

| Scenario | Before | After | Saved |
|---|---:|---:|---:|
| 10-turn conversation history | 40,000 tokens | 8,000 tokens | **80%** |
| Webpage fetch (raw HTML) | 22,000 tokens | 1,200 tokens | **94%** |
| Bloated system prompt | 600 tokens | 220 tokens | **63%** |
| Repeated tool call (cached) | 1,500 tokens | 50 tokens | **97%** |

---

## Tools

| Tool | What it does |
|---|---|
| `count_tokens` | Measure token cost before sending — decide whether to compress first |
| `compress_context` | Shrink long text or conversation history with offline LSA summarization |
| `cache_store` / `cache_get` / `cache_invalidate` | Persist tool results to disk with TTL — never run the same lookup twice |
| `extract_webpage` | Fetch a URL and return only the readable content, not raw HTML |
| `summarize_file` | Get a structural + content summary of any file or directory |
| `prune_conversation` | Remove filler turns and compress old messages in conversation history |
| `optimize_prompt` | Shorten verbose system prompts while preserving constraints |
| `advise_context_window` | Diagnose token bloat and get targeted recommendations |

All tools work **fully offline** — no API key required for core features.

---

## Installation

```bash
pip install -e .
```

> **Python 3.11+ required.** On first use, `compress_context` will auto-download the NLTK `punkt_tab` tokenizer (~2 MB) if not already present.

---

## Setup

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "tokensaver": {
      "command": "python",
      "args": ["-m", "tokensaver"]
    }
  }
}
```

### Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "tokensaver": {
      "command": "python",
      "args": ["-m", "tokensaver"]
    }
  }
}
```

### HTTP/SSE (multi-agent or remote)

```json
{
  "mcpServers": {
    "tokensaver": {
      "command": "python",
      "args": ["-m", "tokensaver", "--transport", "sse", "--port", "8765"]
    }
  }
}
```

---

## Usage

### Recommended workflow

```
Each turn:
  1. count_tokens          → How large is my current context?
  2. advise_context_window → Am I approaching the model's limit?

Before expensive tool calls:
  3. cache_get             → Did I already run this?

When fetching web content:
  4. extract_webpage       → Clean text, not raw HTML

When history grows long:
  5. prune_conversation    → Drop filler turns, compress old ones
  6. compress_context      → Shrink large injected context blocks

When writing system prompts:
  7. optimize_prompt       → Remove redundant phrasing
```

### Tool reference

<details>
<summary><strong>count_tokens</strong> — measure before you send</summary>

```json
{
  "content": "Some long text or list of messages...",
  "model": "claude-sonnet-4",
  "include_message_overhead": true
}
```

Returns `token_count`, `encoding_used`, `model`. Accepts a plain string or an OpenAI-format message list.

</details>

<details>
<summary><strong>compress_context</strong> — shrink long text</summary>

```json
{
  "text": "3,000-token context block...",
  "target_tokens": 600,
  "mode": "extractive"
}
```

`extractive` (default) uses LSA sentence ranking — free, offline, no API call.  
`abstractive` uses `claude-haiku` for higher quality — requires `ANTHROPIC_API_KEY`.

Returns `compressed`, `original_tokens`, `compressed_tokens`, `reduction_pct`.

</details>

<details>
<summary><strong>cache_store / cache_get / cache_invalidate</strong> — skip repeated work</summary>

```python
# Standard pattern: check before running
key = cache_key("extract_webpage", {"url": "https://example.com"})
hit = cache_get(key=key)

if not hit["hit"]:
    result = extract_webpage(url="https://example.com")
    cache_store(key=key, value=str(result), ttl_seconds=3600)
```

Cache is stored on disk at `~/.tokensaver/cache/` and survives server restarts.

</details>

<details>
<summary><strong>extract_webpage</strong> — content, not markup</summary>

```json
{
  "url": "https://example.com/article",
  "max_tokens": 2000,
  "include_links": false,
  "include_metadata": true
}
```

Uses [trafilatura](https://github.com/adbar/trafilatura) with BeautifulSoup as fallback. Returns `content`, `title`, `token_count`, `truncated`.

</details>

<details>
<summary><strong>summarize_file</strong> — understand code without reading it all</summary>

```json
{
  "path": "/home/user/myproject",
  "mode": "both",
  "max_tokens": 500,
  "file_extensions": [".py", ".md"],
  "max_depth": 3
}
```

`mode` options: `"structure"` (tree only), `"content"` (summarized text), `"both"`.

</details>

<details>
<summary><strong>prune_conversation</strong> — clean up history</summary>

```json
{
  "messages": [...],
  "max_output_tokens": 2000,
  "keep_last_n": 4,
  "prune_strategy": "hybrid"
}
```

`"remove"` drops filler turns ("Sure!", "Got it.").  
`"compress"` summarizes older turns in place.  
`"hybrid"` does both — recommended for most cases.

Returns the pruned `messages` list, `original_tokens`, `pruned_tokens`, counts of removed/compressed turns.

</details>

<details>
<summary><strong>optimize_prompt</strong> — shorter system prompts</summary>

```json
{
  "prompt": "Please make sure to always answer questions...",
  "optimization_level": "medium",
  "preserve_constraints": true,
  "output_format": "prose"
}
```

`"light"` removes filler phrases. `"medium"` deduplicates sentences. `"aggressive"` restructures.  
`preserve_constraints: true` always keeps sentences containing `never`, `must`, `always`, `do not`.

</details>

<details>
<summary><strong>advise_context_window</strong> — know what to fix</summary>

```json
{
  "model": "gpt-4o",
  "current_tokens": 110000,
  "messages": [...],
  "target_utilization": 0.75
}
```

Returns `status` (`"ok"` / `"warning"` / `"critical"`), `headroom_tokens`, prioritized `recommendations`, and a per-turn breakdown sorted by token cost.

Supports: GPT-4o, GPT-4o-mini, Claude 3–4 series, Gemini 1.5/2.0/2.5, O1/O3, Llama 3, Mistral.

</details>

---

## Optional: LLM-backed summarization

For higher-quality abstractive compression on very large texts (>5,000 tokens):

```bash
pip install "tokensaver-mcp[llm]"
```

Set `ANTHROPIC_API_KEY` in your environment or a `.env` file, then use `mode: "abstractive"` in `compress_context`.

---

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

38 tests — all offline, no API key or network required.

---

## Project Structure

```
src/tokensaver/
  server.py          # FastMCP app, tool registration
  models.py          # Context window table, shared types
  tools/
    counter.py       # count_tokens
    compress.py      # compress_context
    cache.py         # cache_store / cache_get / cache_invalidate
    extractor.py     # extract_webpage
    summarizer.py    # summarize_file
    pruner.py        # prune_conversation
    optimizer.py     # optimize_prompt
    advisor.py       # advise_context_window
  utils/
    token_utils.py   # tiktoken wrapper
    text_utils.py    # sentence splitting, deduplication
```
