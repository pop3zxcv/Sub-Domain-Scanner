import asyncio
from typing import Optional, Dict


def _sync_whois(domain: str) -> Optional[Dict]:
    try:
        import whois  # python-whois package
        data = whois.whois(domain)
        if not data:
            return None

        def _str(v) -> str:
            if isinstance(v, list):
                v = v[0] if v else None
            return str(v)[:200].strip() if v else "—"

        def _date(v) -> str:
            if isinstance(v, list):
                v = v[0] if v else None
            if v is None:
                return "—"
            try:
                return v.strftime("%Y-%m-%d")
            except Exception:
                return str(v)[:20]

        ns = data.name_servers or []
        if isinstance(ns, str):
            ns = [ns]
        ns = sorted({n.lower() for n in ns if n})[:6]

        st = data.status or []
        if isinstance(st, str):
            st = [st]
        st = [s.split()[0] for s in st if s][:4]

        return {
            "domain": domain,
            "registrar": _str(data.registrar),
            "registered": _date(data.creation_date),
            "expires": _date(data.expiration_date),
            "updated": _date(data.updated_date),
            "nameservers": ns,
            "status": st,
            "registrant": _str(data.org or data.name),
        }
    except Exception:
        return None


async def get_whois(domain: str) -> Optional[Dict]:
    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _sync_whois, domain),
            timeout=18.0,
        )
    except Exception:
        return None
