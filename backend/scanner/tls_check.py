import asyncio
import ssl
import socket
from datetime import datetime
from typing import Optional, Dict


def _sync_get_cert(hostname: str, port: int = 443) -> Optional[Dict]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((hostname, port), timeout=6) as raw:
            with ctx.wrap_socket(raw, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()          # (name, protocol, bits)
                version = ssock.version() or ""  # e.g. "TLSv1.3"

                if not cert:
                    return None

                subject = dict(x[0] for x in cert.get("subject", []) if x)
                issuer  = dict(x[0] for x in cert.get("issuer",  []) if x)

                return {
                    "issuer": issuer.get("organizationName", issuer.get("commonName", "—")),
                    "subject": subject.get("commonName", hostname),
                    "expires": cert.get("notAfter", "—"),
                    "grade": _grade(version, cipher[0] if cipher else "", cert),
                }
    except Exception:
        return None


def _grade(version: str, cipher_name: str, cert: dict) -> str:
    # Check expiry first
    not_after = cert.get("notAfter", "")
    if not_after:
        try:
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            if expiry < datetime.utcnow():
                return "F"
        except Exception:
            pass

    if "TLSv1.3" in version:
        return "A+"
    if "TLSv1.2" in version:
        if any(x in cipher_name for x in ("ECDHE", "DHE", "GCM", "CHACHA")):
            return "A"
        return "B"
    if "TLSv1.1" in version or ("TLSv1" in version and "TLSv1." not in version):
        return "C"
    # Unknown / older
    return "B"


async def get_cert_info(hostname: str, port: int = 443) -> Optional[Dict]:
    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _sync_get_cert, hostname, port),
            timeout=9.0,
        )
    except Exception:
        return None
