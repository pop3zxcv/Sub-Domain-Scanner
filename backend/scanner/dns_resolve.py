import asyncio
import dns.asyncresolver
import dns.exception
from typing import Dict, List

resolver = dns.asyncresolver.Resolver()
resolver.timeout = 3
resolver.lifetime = 5


async def _resolve(fqdn: str, rtype: str) -> List[str]:
    try:
        answer = await resolver.resolve(fqdn, rtype)
        if rtype == "MX":
            return [f"{r.preference} {r.exchange.to_text().rstrip('.')}" for r in answer]
        if rtype == "TXT":
            return [" ".join(s.decode("utf-8", errors="replace") for s in r.strings) for r in answer]
        return [r.to_text().rstrip(".") for r in answer]
    except Exception:
        return []


async def resolve_dns(fqdn: str) -> Dict[str, List[str]]:
    """Resolve all common record types for a FQDN, returning a dict."""
    results = await asyncio.gather(
        _resolve(fqdn, "A"),
        _resolve(fqdn, "AAAA"),
        _resolve(fqdn, "CNAME"),
        _resolve(fqdn, "MX"),
        _resolve(fqdn, "TXT"),
        _resolve(fqdn, "NS"),
        return_exceptions=True,
    )

    def safe(r):
        return r if isinstance(r, list) else []

    return {
        "A":     safe(results[0]),
        "AAAA":  safe(results[1]),
        "CNAME": safe(results[2]),
        "MX":    safe(results[3]),
        "TXT":   safe(results[4]),
        "NS":    safe(results[5]),
    }
