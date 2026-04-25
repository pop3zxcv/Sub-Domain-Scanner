import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import List

# Ports that matter for security assessment
TARGET_PORTS = "21,22,23,25,53,80,443,3000,3306,5432,5900,6379,8080,8443,8888,9090,9200,27017"

_executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="nmap")

# Detect nmap availability once at import time
try:
    subprocess.run(["nmap", "--version"], capture_output=True, timeout=3, check=True)
    NMAP_OK = True
except Exception:
    NMAP_OK = False


# ── nmap-based scanner ────────────────────────────────────────────────────────

def _nmap_sync(host: str) -> List[int]:
    try:
        import nmap as nmap_lib
        nm = nmap_lib.PortScanner()
        nm.scan(
            hosts=host,
            arguments=f"-p {TARGET_PORTS} -T4 -Pn --open",
        )
        open_ports: List[int] = []
        if host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                for port, state in nm[host][proto].items():
                    if state["state"] == "open":
                        open_ports.append(port)
        return sorted(open_ports)
    except Exception:
        return []


# ── asyncio TCP fallback ──────────────────────────────────────────────────────

async def _tcp_check(host: str, port: int) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=1.2
        )
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return True
    except Exception:
        return False


async def _tcp_scan(host: str) -> List[int]:
    ports = [int(p) for p in TARGET_PORTS.split(",")]
    results = await asyncio.gather(*[_tcp_check(host, p) for p in ports])
    return [p for p, ok in zip(ports, results) if ok]


# ── Public API ────────────────────────────────────────────────────────────────

async def scan_ports(host: str) -> List[int]:
    """Scan ports using nmap if available, else asyncio TCP connect."""
    if NMAP_OK:
        loop = asyncio.get_event_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(_executor, _nmap_sync, host),
                timeout=35.0,
            )
        except Exception:
            pass
    # Fallback
    return await _tcp_scan(host)
