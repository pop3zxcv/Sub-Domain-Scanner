"""
Multiple free subdomain discovery sources — queried in parallel and deduplicated.
"""
import asyncio
import aiohttp
from typing import Set
from urllib.parse import urlparse


async def _get(session: aiohttp.ClientSession, url: str, **kwargs) -> bytes | None:
    try:
        async with session.get(url, **kwargs) as r:
            if r.status == 200:
                return await r.read()
    except Exception:
        pass
    return None


def _extract_subs(text: str, domain: str) -> Set[str]:
    """Extract bare subdomain labels from a blob of text containing FQDNs."""
    subs: Set[str] = set()
    suffix = f".{domain}"
    for token in text.replace(",", " ").replace('"', " ").replace("'", " ").split():
        token = token.strip().rstrip(".").lower()
        if token.endswith(suffix):
            sub = token[: -len(suffix)]
            # Drop wildcards, multi-level, empty
            if sub and "*" not in sub and len(sub) < 100:
                subs.add(sub)
    return subs


# ── Individual sources ────────────────────────────────────────────────────────

async def crtsh(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    """Certificate Transparency logs via crt.sh."""
    data = await _get(
        session,
        f"https://crt.sh/?q=%.{domain}&output=json",
        timeout=aiohttp.ClientTimeout(total=20),
        headers={"Accept": "application/json"},
    )
    if not data:
        return set()
    try:
        import json
        entries = json.loads(data)
        text = " ".join(e.get("name_value", "") for e in entries)
        return _extract_subs(text.replace("\n", " "), domain)
    except Exception:
        return set()


async def hackertarget(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    """HackerTarget free host search (100 req/day without key)."""
    data = await _get(
        session,
        f"https://api.hackertarget.com/hostsearch/?q={domain}",
        timeout=aiohttp.ClientTimeout(total=15),
    )
    if not data:
        return set()
    text = data.decode("utf-8", errors="replace")
    if "API count exceeded" in text or "error" in text[:50].lower():
        return set()
    subs: Set[str] = set()
    for line in text.splitlines():
        if "," in line:
            fqdn = line.split(",")[0].strip().lower()
            subs.update(_extract_subs(fqdn, domain))
    return subs


async def anubisdb(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    """AnubisDB passive DNS."""
    data = await _get(
        session,
        f"https://jonlu.ca/anubis/subdomains/{domain}",
        timeout=aiohttp.ClientTimeout(total=15),
    )
    if not data:
        return set()
    try:
        import json
        items = json.loads(data)
        text = " ".join(str(i) for i in items)
        return _extract_subs(text, domain)
    except Exception:
        return set()


async def urlscan(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    """URLScan.io public search."""
    data = await _get(
        session,
        f"https://urlscan.io/api/v1/search/?q=page.domain:{domain}&size=200",
        headers={"User-Agent": "SubSentry/1.0"},
        timeout=aiohttp.ClientTimeout(total=15),
    )
    if not data:
        return set()
    try:
        import json
        results = json.loads(data).get("results", [])
        subs: Set[str] = set()
        for r in results:
            fqdn = r.get("page", {}).get("domain", "").lower()
            subs.update(_extract_subs(fqdn, domain))
        return subs
    except Exception:
        return set()


async def alienvault(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    """AlienVault OTX passive DNS (no API key needed for public data)."""
    data = await _get(
        session,
        f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns",
        timeout=aiohttp.ClientTimeout(total=15),
    )
    if not data:
        return set()
    try:
        import json
        records = json.loads(data).get("passive_dns", [])
        text = " ".join(r.get("hostname", "") for r in records)
        return _extract_subs(text, domain)
    except Exception:
        return set()


async def wayback(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    """Wayback Machine CDX API."""
    data = await _get(
        session,
        f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey&limit=5000",
        timeout=aiohttp.ClientTimeout(total=25),
    )
    if not data:
        return set()
    try:
        import json
        rows = json.loads(data)
        subs: Set[str] = set()
        for row in rows[1:]:  # skip header
            if row:
                try:
                    h = urlparse(row[0]).hostname or ""
                    subs.update(_extract_subs(h.lower(), domain))
                except Exception:
                    pass
        return subs
    except Exception:
        return set()


async def threatcrowd(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    """ThreatCrowd API."""
    data = await _get(
        session,
        f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}",
        timeout=aiohttp.ClientTimeout(total=10),
    )
    if not data:
        return set()
    try:
        import json
        resp = json.loads(data)
        text = " ".join(str(s) for s in resp.get("subdomains", []))
        return _extract_subs(text, domain)
    except Exception:
        return set()


async def rapiddns(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    """RapidDNS.io subdomain lookup (HTML scrape)."""
    data = await _get(
        session,
        f"https://rapiddns.io/subdomain/{domain}?full=1",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=aiohttp.ClientTimeout(total=15),
    )
    if not data:
        return set()
    text = data.decode("utf-8", errors="replace")
    return _extract_subs(text, domain)


# ── Wordlist DNS bruteforce ───────────────────────────────────────────────────

async def wordlist_bruteforce(domain: str) -> Set[str]:
    """Resolve each wordlist entry against the target domain."""
    from scanner.wordlist import WORDLIST
    import dns.asyncresolver
    import dns.exception

    resolver = dns.asyncresolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 3

    found: Set[str] = set()
    sem = asyncio.Semaphore(60)

    async def check(sub: str) -> None:
        fqdn = f"{sub}.{domain}"
        async with sem:
            try:
                await resolver.resolve(fqdn, "A")
                found.add(sub)
            except Exception:
                pass

    await asyncio.gather(*[check(s) for s in WORDLIST], return_exceptions=True)
    return found


# ── Main entry point ─────────────────────────────────────────────────────────

async def discover_subdomains(domain: str, quick: bool = False) -> list[str]:
    """Query all sources concurrently, deduplicate, return sorted list."""
    connector = aiohttp.TCPConnector(ssl=False, limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        passive_task = asyncio.gather(
            crtsh(session, domain),
            hackertarget(session, domain),
            anubisdb(session, domain),
            urlscan(session, domain),
            alienvault(session, domain),
            wayback(session, domain),
            threatcrowd(session, domain),
            rapiddns(session, domain),
            return_exceptions=True,
        )
        if quick:
            passive_results = await passive_task
            brute_results: Set[str] = set()
        else:
            passive_results, brute_results = await asyncio.gather(
                passive_task,
                wordlist_bruteforce(domain),
            )

    all_subs: Set[str] = set()
    for r in passive_results:
        if isinstance(r, set):
            all_subs |= r
    all_subs |= brute_results

    # Sanitise: strip wildcard prefixes, drop overly deep labels
    cleaned: Set[str] = set()
    for s in all_subs:
        s = s.strip().lstrip("*.")
        if s and len(s) < 100 and s.count(".") <= 4:
            cleaned.add(s)

    return sorted(cleaned)
