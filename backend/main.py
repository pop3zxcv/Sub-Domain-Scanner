"""
SubSentry backend — FastAPI + Server-Sent Events
"""
import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from scanner.sources import discover_subdomains
from scanner.dns_resolve import resolve_dns
from scanner.http_probe import probe_http
from scanner.tls_check import get_cert_info
from scanner.port_scan import scan_ports, NMAP_OK
from scanner.fingerprint import fingerprint
from scanner.geo import get_geo, infer_hosting
from scanner.whois_check import get_whois
from scanner.risk import calculate_risk, detect_takeover

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("subsentry")


async def _noop():
    return None

app = FastAPI(title="SubSentry")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_domain(raw: str) -> str:
    d = raw.strip().lower()
    for prefix in ("https://", "http://", "//"):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d.split("/")[0].split("?")[0].split("#")[0]


def _build_result(
    sub: str,
    domain: str,
    result_id: int,
    dns_rec: dict,
    http_res,
    cert,
    geo,
    ports,
    techs,
    source: str,
) -> dict:
    ip   = dns_rec["A"][0]   if dns_rec["A"]    else "—"
    ipv6 = dns_rec["AAAA"][0] if dns_rec["AAAA"] else "—"

    takeover = detect_takeover(dns_rec, http_res)
    risk     = calculate_risk(sub, dns_rec, http_res, cert, ports, techs)
    hosting  = infer_hosting(http_res["headers"] if http_res else {}, geo)

    return {
        "id":           result_id,
        "fqdn":         f"{sub}.{domain}",
        "sub":          sub,
        "domain":       domain,
        "status":       (http_res or {}).get("status", 0),
        "title":        (http_res or {}).get("title", "—"),
        "ip":           ip,
        "ipv6":         ipv6,
        "host":         hosting,
        "country":      geo or {"country": "Unknown", "code": "XX", "flag": "🌐"},
        "techs":        techs,
        "ports":        ports,
        "ssl":          cert,
        "risk":         risk,
        "takeover":     takeover["vulnerable"],
        "takeoverNote": takeover["note"],
        "source":       source,
        "lastSeen":     0,
        "dns":          dns_rec,
    }


# ── Core scan coroutine ───────────────────────────────────────────────────────

async def _scan(domain: str, request: Request) -> AsyncGenerator[dict, None]:
    """
    Yields SSE-compatible dicts:  {"event": str, "data": str (JSON)}
    """

    def ev(event: str, payload: dict) -> dict:
        return {"event": event, "data": json.dumps(payload)}

    # ── Phase 1: discover subdomains ─────────────────────────────────────────
    yield ev("status", {"msg": f"Querying 8 passive sources + DNS wordlist for {domain}…"})

    try:
        subdomains = await asyncio.wait_for(discover_subdomains(domain), timeout=120)
    except asyncio.TimeoutError:
        subdomains = []

    if not subdomains:
        yield ev("status", {"msg": "No subdomains found — scan complete."})
        yield ev("done",   {"total": 0})
        return

    yield ev("status", {"msg": f"Found {len(subdomains)} unique subdomains — probing now…"})
    log.info("Probing %d subdomains for %s", len(subdomains), domain)

    # ── Phase 2: probe each subdomain concurrently ───────────────────────────
    queue: asyncio.Queue = asyncio.Queue()
    id_counter = [0]
    probe_sem  = asyncio.Semaphore(20)   # 20 concurrent HTTP probes
    port_sem   = asyncio.Semaphore(5)    # 5 concurrent nmap jobs

    async def probe_one(sub: str, source: str) -> None:
        fqdn = f"{sub}.{domain}"

        async with probe_sem:
            if await request.is_disconnected():
                return

            # DNS records
            dns_rec = await resolve_dns(fqdn)
            ip = dns_rec["A"][0] if dns_rec["A"] else None

            # Skip subdomains that don't resolve at all
            if not ip and not dns_rec["CNAME"] and not dns_rec["AAAA"]:
                await queue.put(("progress", {}))
                return

            # Run HTTP probe + geo + cert concurrently
            http_res, cert, geo = await asyncio.gather(
                probe_http(fqdn),
                get_cert_info(fqdn) if (ip or dns_rec["AAAA"]) else _noop(),
                get_geo(ip)         if ip else _noop(),
                return_exceptions=True,
            )
            http_res = http_res if isinstance(http_res, dict) else None
            cert     = cert     if isinstance(cert,     dict) else None
            geo      = geo      if isinstance(geo,      dict) else None

            # Port scan — only live hosts to keep things fast
            ports: list = []
            if ip and http_res and http_res.get("status", 0) < 600:
                async with port_sem:
                    try:
                        ports = await asyncio.wait_for(scan_ports(ip), timeout=35)
                    except Exception:
                        ports = []

            techs  = fingerprint(
                http_res["headers"] if http_res else {},
                http_res["html"]    if http_res else "",
            )

            result = _build_result(
                sub, domain, id_counter[0], dns_rec,
                http_res, cert, geo, ports, techs, source,
            )
            id_counter[0] += 1
            await queue.put(("result", result))

    # We need to know which subs came from passive sources vs wordlist
    # (discover_subdomains already merged them; tag all as "multi-source" for now)
    tasks = [
        asyncio.create_task(probe_one(sub, "multi-source"))
        for sub in subdomains
    ]

    # Stream results as they arrive
    finished = 0
    total = len(tasks)

    async def drain_queue():
        nonlocal finished
        while finished < total:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=1.5)
                event_type, data = item
                finished += 1
                yield ev(event_type, data)
            except asyncio.TimeoutError:
                # Send keepalive so the SSE connection stays open
                yield ev("ping", {"probed": finished, "total": total})
            except Exception:
                finished += 1

    async for event in drain_queue():
        if await request.is_disconnected():
            for t in tasks:
                t.cancel()
            return
        yield event

    yield ev("done", {"total": id_counter[0]})


# ── Quick scan ────────────────────────────────────────────────────────────────

async def _quick_scan(domain: str, request: Request) -> AsyncGenerator[dict, None]:
    """
    Fast scan: passive sources only, DNS + HTTP status + geo. No ports/TLS/tech.
    """
    def ev(event: str, payload: dict) -> dict:
        return {"event": event, "data": json.dumps(payload)}

    yield ev("status", {"msg": f"Quick scan: querying passive sources for {domain}…"})

    try:
        subdomains = await asyncio.wait_for(
            discover_subdomains(domain, quick=True), timeout=60
        )
    except asyncio.TimeoutError:
        subdomains = []

    if not subdomains:
        yield ev("status", {"msg": "No subdomains found."})
        yield ev("done",   {"total": 0})
        return

    yield ev("status", {"msg": f"Found {len(subdomains)} subdomains — resolving…"})
    log.info("Quick-probing %d subdomains for %s", len(subdomains), domain)

    queue: asyncio.Queue = asyncio.Queue()
    id_counter = [0]
    sem = asyncio.Semaphore(40)

    async def quick_probe(sub: str) -> None:
        fqdn = f"{sub}.{domain}"
        async with sem:
            if await request.is_disconnected():
                return
            dns_rec = await resolve_dns(fqdn)
            ip = dns_rec["A"][0] if dns_rec["A"] else None
            if not ip and not dns_rec["CNAME"] and not dns_rec["AAAA"]:
                await queue.put(("progress", {}))
                return

            http_res, geo = await asyncio.gather(
                probe_http(fqdn),
                get_geo(ip) if ip else _noop(),
                return_exceptions=True,
            )
            http_res = http_res if isinstance(http_res, dict) else None
            geo      = geo      if isinstance(geo,      dict) else None
            hosting  = infer_hosting(http_res["headers"] if http_res else {}, geo)

            result = {
                "id":           id_counter[0],
                "fqdn":         fqdn,
                "sub":          sub,
                "domain":       domain,
                "status":       (http_res or {}).get("status", 0),
                "title":        (http_res or {}).get("title", ""),
                "ip":           ip or "",
                "ipv6":         dns_rec["AAAA"][0] if dns_rec["AAAA"] else "",
                "host":         hosting,
                "country":      geo or {"country": "Unknown", "code": "XX", "flag": "🌐"},
                "techs":        [],
                "ports":        [],
                "ssl":          None,
                "risk":         0,
                "takeover":     False,
                "takeoverNote": None,
                "source":       "passive",
                "lastSeen":     0,
                "dns":          dns_rec,
            }
            id_counter[0] += 1
            await queue.put(("result", result))

    tasks = [asyncio.create_task(quick_probe(sub)) for sub in subdomains]

    finished = 0
    total = len(tasks)

    async def drain():
        nonlocal finished
        while finished < total:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=1.5)
                event_type, data = item
                finished += 1
                yield ev(event_type, data)
            except asyncio.TimeoutError:
                yield ev("ping", {"probed": finished, "total": total})
            except Exception:
                finished += 1

    async for event in drain():
        if await request.is_disconnected():
            for t in tasks:
                t.cancel()
            return
        yield event

    yield ev("done", {"total": id_counter[0]})


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/scan")
async def scan_endpoint(domain: str, request: Request):
    clean = _clean_domain(domain)
    if not clean:
        return {"error": "domain required"}

    return EventSourceResponse(
        _scan(clean, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering if proxied
        },
    )


@app.get("/api/quick")
async def quick_endpoint(domain: str, request: Request):
    clean = _clean_domain(domain)
    if not clean:
        return {"error": "domain required"}
    return EventSourceResponse(
        _quick_scan(clean, request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/whois")
async def whois_endpoint(domain: str):
    clean = _clean_domain(domain)
    if not clean:
        return {"error": "domain required"}
    data = await get_whois(clean)
    return data or {"error": "WHOIS lookup failed"}


@app.get("/api/status")
async def status_endpoint():
    return {"ok": True, "nmap": NMAP_OK}


# ── Dev entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)
