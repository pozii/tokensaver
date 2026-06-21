# TokenSaver MCP

An MCP (Model Context Protocol) server that minimizes token usage for AI agents.

Built for developers on limited or low-cost AI plans who want to get the most out of every token: **60–97% token savings**.

## Expected Savings

| Scenario | Before | After | Saved |
|---|---|---|---|
| 10-turn conversation history | 40,000 | 8,000 | **80%** |
| Raw HTML webpage fetch | 22,000 | 1,200 | **94%** |
| Bloated system prompt | 600 | 220 | **63%** |
| Repeated tool call (cached) | 1,500 | 50 | **97%** |

---

## Installation

```bash
cd tokensaver-mcp
pip install -e .
```

---

## Claude Desktop / Claude Code Configuration

Add to `claude_desktop_config.json` or `~/.claude/settings.json`:

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

### HTTP/SSE mode (multi-agent scenarios)

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

## Tools

### `count_tokens` — Token counting
Measure token count before sending anything to an API.

```json
{
  "content": "Some long text...",
  "model": "claude-sonnet-4"
}
```

### `compress_context` — Context compression
Summarize long text or conversation history into a dense, re-injectable form.

```json
{
  "text": "3000-token context block...",
  "target_tokens": 600,
  "mode": "extractive"
}
```

- `mode: "extractive"` → Free, fully offline (LSA algorithm)
- `mode: "abstractive"` → Higher quality, requires `ANTHROPIC_API_KEY`

### `cache_store` / `cache_get` / `cache_invalidate` — Result caching
Persist expensive tool results to disk with TTL. The same lookup never runs twice.

```python
# Check cache first
cache_key = make_cache_key("extract_webpage", {"url": "https://example.com"})
result = cache_get(key=cache_key)

if not result["hit"]:
    # Run and store if not cached
    content = extract_webpage(url="https://example.com")
    cache_store(key=cache_key, value=str(content), ttl_seconds=3600)
```

### `extract_webpage` — Web content extraction
Fetch a URL and return only the main readable content — no HTML tags, scripts, ads, or navigation.

```json
{
  "url": "https://example.com/article",
  "max_tokens": 2000
}
```

### `summarize_file` — File/directory summarization
Understand a large codebase without reading every file.

```json
{
  "path": "/home/user/myproject",
  "mode": "structure",
  "max_tokens": 500,
  "max_depth": 3
}
```

### `prune_conversation` — Conversation pruning
Trim long conversation history to reduce token cost on every API call.

```json
{
  "messages": [...],
  "max_output_tokens": 2000,
  "keep_last_n": 4,
  "prune_strategy": "hybrid"
}
```

- `"remove"` → Drop low-value turns (filler acknowledgments)
- `"compress"` → Summarize older turns in place
- `"hybrid"` → Both (recommended)

### `optimize_prompt` — Prompt optimization
Shorten bloated or repetitive system prompts.

```json
{
  "prompt": "Please make sure to always answer...",
  "optimization_level": "medium",
  "preserve_constraints": true
}
```

### `advise_context_window` — Context window advisor
Get targeted recommendations when approaching a model's token limit.

```json
{
  "model": "gpt-4o",
  "current_tokens": 110000,
  "messages": [...]
}
```

Returns: `"status": "warning"` and `"recommendations": ["Run prune_conversation", ...]`

---

## Recommended Workflow

```
At the start of each turn:
  1. count_tokens          → How many tokens am I sending?
  2. advise_context_window → Am I near the limit?

Before any expensive tool call:
  3. cache_get             → Have I done this before?

When fetching web content:
  4. extract_webpage       → Clean text, not raw HTML

When history grows long:
  5. prune_conversation    → Remove filler, compress old turns
  6. compress_context      → Shrink large context blocks

When writing system prompts:
  7. optimize_prompt       → Remove redundant phrasing
```

---

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

38 tests, fully offline (no network required).

---

## Optional: Abstractive Compression

For higher-quality summarization backed by an LLM:

```bash
pip install "tokensaver-mcp[llm]"
```

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-...
```

```json
{
  "tool": "compress_context",
  "mode": "abstractive",
  "target_tokens": 200
}
```

> Note: This mode makes a small LLM API call. Only worthwhile for very large texts (>5,000 tokens)
> where extractive summarization is insufficient.

---

## License

MIT
