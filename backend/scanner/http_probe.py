import asyncio
import re
import aiohttp
from typing import Dict, Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = aiohttp.ClientTimeout(total=12, connect=5, sock_read=8)


async def probe_http(fqdn: str) -> Optional[Dict]:
    """Try HTTPS then HTTP; return status, headers, title and raw HTML (≤50 KB)."""
    connector = aiohttp.TCPConnector(ssl=False, limit=1)
    async with aiohttp.ClientSession(
        connector=connector, timeout=TIMEOUT, headers=HEADERS
    ) as session:
        for scheme in ("https", "http"):
            url = f"{scheme}://{fqdn}"
            try:
                async with session.get(
                    url, allow_redirects=True, max_redirects=6
                ) as resp:
                    raw = await resp.read()
                    html = raw[:51200].decode("utf-8", errors="replace")
                    return {
                        "status": resp.status,
                        "url": str(resp.url),
                        "headers": dict(resp.headers),
                        "html": html,
                        "title": _title(html),
                    }
            except asyncio.TimeoutError:
                continue
            except Exception:
                continue
    return None


def _title(html: str) -> str:
    m = re.search(r"<title[^>]*>([^<]{1,250})</title>", html, re.I | re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return "—"
