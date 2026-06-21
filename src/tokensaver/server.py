"""TokenSaver MCP server — registers all token-minimization tools."""
from __future__ import annotations

from fastmcp import FastMCP

from tokensaver.tools.advisor import advise_context_window
from tokensaver.tools.cache import cache_get, cache_invalidate, cache_store
from tokensaver.tools.compress import compress_context
from tokensaver.tools.counter import count_tokens_tool
from tokensaver.tools.extractor import extract_webpage
from tokensaver.tools.optimizer import optimize_prompt
from tokensaver.tools.pruner import prune_conversation
from tokensaver.tools.summarizer import summarize_file

mcp = FastMCP(
    name="tokensaver",
    instructions="""
TokenSaver: minimize token usage for AI agents.

Quick-start workflow:
1. count_tokens — measure before sending anything large
2. advise_context_window — get targeted recommendations when near limit
3. cache_get / cache_store — avoid repeating expensive lookups (97% savings)
4. extract_webpage — fetch URLs as clean text not raw HTML (94% savings)
5. compress_context — shrink long context before re-injection (60-80% savings)
6. prune_conversation — clean up long conversation history (75% savings)
7. optimize_prompt — shorten verbose system prompts (30-65% savings)
8. summarize_file — understand codebases without reading every file

Always cache_get before expensive operations. Always count_tokens before large sends.
""",
)

mcp.tool(name="count_tokens")(count_tokens_tool)
mcp.tool()(compress_context)
mcp.tool()(cache_store)
mcp.tool()(cache_get)
mcp.tool()(cache_invalidate)
mcp.tool()(extract_webpage)
mcp.tool()(summarize_file)
mcp.tool()(prune_conversation)
mcp.tool()(optimize_prompt)
mcp.tool()(advise_context_window)
