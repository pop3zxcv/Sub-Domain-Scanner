import aiohttp
from typing import Dict, Optional

_cache: Dict[str, Dict] = {}

FLAG_MAP = {
    "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪", "FR": "🇫🇷", "NL": "🇳🇱",
    "CA": "🇨🇦", "AU": "🇦🇺", "JP": "🇯🇵", "SG": "🇸🇬", "IE": "🇮🇪",
    "IN": "🇮🇳", "CN": "🇨🇳", "BR": "🇧🇷", "RU": "🇷🇺", "KR": "🇰🇷",
    "HK": "🇭🇰", "SE": "🇸🇪", "NO": "🇳🇴", "FI": "🇫🇮", "DK": "🇩🇰",
    "CH": "🇨🇭", "AT": "🇦🇹", "BE": "🇧🇪", "ES": "🇪🇸", "IT": "🇮🇹",
    "PT": "🇵🇹", "PL": "🇵🇱", "CZ": "🇨🇿", "HU": "🇭🇺", "RO": "🇷🇴",
    "UA": "🇺🇦", "TR": "🇹🇷", "IL": "🇮🇱", "ZA": "🇿🇦", "MX": "🇲🇽",
    "AR": "🇦🇷", "CL": "🇨🇱", "CO": "🇨🇴", "TH": "🇹🇭", "PH": "🇵🇭",
    "MY": "🇲🇾", "ID": "🇮🇩", "VN": "🇻🇳", "NZ": "🇳🇿", "TW": "🇹🇼",
    "SA": "🇸🇦", "AE": "🇦🇪", "EG": "🇪🇬", "NG": "🇳🇬", "KE": "🇰🇪",
}

_UNKNOWN = {"country": "Unknown", "code": "XX", "flag": "🌐", "isp": "—", "asn": "—"}


async def get_geo(ip: str) -> Dict:
    if not ip or ip == "—" or ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172."):
        return _UNKNOWN

    if ip in _cache:
        return _cache[ip]

    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,isp,as,org"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("status") == "success":
                        result = {
                            "country": data.get("country", "Unknown"),
                            "code": data.get("countryCode", "XX"),
                            "flag": FLAG_MAP.get(data.get("countryCode", ""), "🌐"),
                            "isp": data.get("isp", "—"),
                            "asn": data.get("as", "—"),
                        }
                        _cache[ip] = result
                        return result
    except Exception:
        pass

    return _UNKNOWN


def infer_hosting(headers: dict, geo: Optional[Dict]) -> Dict:
    h = {k.lower(): v for k, v in (headers or {}).items()}
    server = h.get("server", "").lower()
    org = ((geo or {}).get("asn", "") + " " + (geo or {}).get("isp", "")).lower()

    # Check specific response headers first (most reliable)
    if "cf-ray" in h or "cloudflare" in server:
        return {"name": "Cloudflare", "asn": "AS13335", "color": "#F38020"}
    if "x-vercel-id" in h or "x-vercel-cache" in h:
        return {"name": "Vercel", "asn": "AS16509", "color": "#000000"}
    if "x-nf-request-id" in h:
        return {"name": "Netlify", "asn": "AS54113", "color": "#00C7B7"}
    if "x-github-request-id" in h or "github" in server:
        return {"name": "GitHub Pages", "asn": "AS36459", "color": "#24292E"}

    HOSTING_MAP = [
        ("cloudflare",   {"name": "Cloudflare",      "asn": "AS13335", "color": "#F38020"}),
        ("amazon",       {"name": "Amazon AWS",       "asn": "AS16509", "color": "#FF9900"}),
        ("aws",          {"name": "Amazon AWS",       "asn": "AS16509", "color": "#FF9900"}),
        ("google",       {"name": "Google Cloud",     "asn": "AS15169", "color": "#4285F4"}),
        ("microsoft",    {"name": "Microsoft Azure",  "asn": "AS8075",  "color": "#0078D4"}),
        ("azure",        {"name": "Microsoft Azure",  "asn": "AS8075",  "color": "#0078D4"}),
        ("digitalocean", {"name": "DigitalOcean",     "asn": "AS14061", "color": "#0080FF"}),
        ("fastly",       {"name": "Fastly",           "asn": "AS54113", "color": "#FF282D"}),
        ("vercel",       {"name": "Vercel",           "asn": "AS16509", "color": "#000000"}),
        ("netlify",      {"name": "Netlify",          "asn": "AS54113", "color": "#00C7B7"}),
        ("hetzner",      {"name": "Hetzner",          "asn": "AS24940", "color": "#D50C2D"}),
        ("ovh",          {"name": "OVH",              "asn": "AS16276", "color": "#123F6D"}),
        ("linode",       {"name": "Akamai/Linode",    "asn": "AS63949", "color": "#00B050"}),
        ("akamai",       {"name": "Akamai",           "asn": "AS20940", "color": "#009BDE"}),
        ("vultr",        {"name": "Vultr",            "asn": "AS20473", "color": "#007BFC"}),
        ("github",       {"name": "GitHub Pages",     "asn": "AS36459", "color": "#24292E"}),
        ("contabo",      {"name": "Contabo",          "asn": "AS51167", "color": "#3A86FF"}),
        ("scaleway",     {"name": "Scaleway",         "asn": "AS12876", "color": "#4F0599"}),
        ("leaseweb",     {"name": "LeaseWeb",         "asn": "AS60781", "color": "#00ADEF"}),
        ("rackspace",    {"name": "Rackspace",        "asn": "AS27357", "color": "#ED1C24"}),
    ]

    combined = org + server
    for keyword, info in HOSTING_MAP:
        if keyword in combined:
            asn = (geo or {}).get("asn", info["asn"])
            return {**info, "asn": asn or info["asn"]}

    isp = (geo or {}).get("isp", "Unknown")
    asn = (geo or {}).get("asn", "—")
    return {"name": (isp[:30] if isp and isp != "—" else "Unknown"), "asn": asn, "color": "#6B7280"}
