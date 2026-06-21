"""Entry point: python -m tokensaver"""
from __future__ import annotations

import argparse

from tokensaver.server import mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="TokenSaver MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode (default: stdio for Claude Desktop/Code)",
    )
    parser.add_argument("--port", type=int, default=8765, help="Port for SSE transport")
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
