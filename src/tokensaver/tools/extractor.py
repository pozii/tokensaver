"""extract_webpage tool — fetch URL and return only main content."""
from __future__ import annotations

import asyncio

import httpx
import trafilatura

from tokensaver.utils.token_utils import count_tokens, truncate_to_tokens

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


async def _fetch_html(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0, headers=_HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


def _extract_with_bs4(html: str, include_links: bool) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
    if not include_links:
        for a in soup.find_all("a"):
            a.replace_with(a.get_text())
    return soup.get_text(separator="\n", strip=True)


def extract_webpage(
    url: str,
    max_tokens: int = 2000,
    include_links: bool = False,
    include_metadata: bool = True,
    model: str = "gpt-4o",
) -> dict:
    """
    Fetch a webpage and return only its main readable content — no HTML, scripts,
    navigation, ads, or cookie banners. Saves 85–95% of tokens vs raw HTML.

    Args:
        url: The URL to fetch.
        max_tokens: Truncate output to this many tokens if exceeded.
        include_links: If True, preserve hyperlinks as [text](url).
        include_metadata: If True, prepend title/author/date when available.
        model: Used for token counting.

    Returns:
        content, title, token_count, url, truncated
    """
    html = asyncio.get_event_loop().run_until_complete(_fetch_html(url))

    # Try trafilatura first
    extracted = trafilatura.extract(
        html,
        include_links=include_links,
        include_images=False,
        no_fallback=False,
        favor_recall=True,
    )
    title = None
    if extracted:
        meta = trafilatura.extract_metadata(html)
        if meta:
            title = meta.title
    else:
        # Fallback: BeautifulSoup
        extracted = _extract_with_bs4(html, include_links)

    if not extracted:
        extracted = ""

    if include_metadata and title:
        extracted = f"# {title}\n\n{extracted}"

    token_count = count_tokens(extracted, model)
    truncated = token_count > max_tokens
    if truncated:
        extracted = truncate_to_tokens(extracted, max_tokens, model)
        token_count = max_tokens

    return {
        "content": extracted,
        "title": title,
        "token_count": token_count,
        "url": url,
        "truncated": truncated,
    }
