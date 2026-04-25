import re
from typing import Dict, List


def fingerprint(headers: dict, html: str) -> List[Dict]:
    """Identify technologies from HTTP response headers and HTML body."""
    techs: List[Dict] = []
    seen: set = set()

    h = {k.lower(): v for k, v in (headers or {}).items()}
    body = html or ""
    server = h.get("server", "").lower()
    powered = h.get("x-powered-by", "").lower()
    cookies = h.get("set-cookie", "").lower()

    def add(name: str, cat: str, v: str = "—", outdated: bool = False) -> None:
        if name not in seen:
            seen.add(name)
            techs.append({"name": name, "cat": cat, "v": v, "outdated": outdated})

    # ── Web servers ──────────────────────────────────────────────────────────
    if "nginx" in server:
        m = re.search(r"nginx/([\d.]+)", server)
        ver = m.group(1) if m else "—"
        old = ver != "—" and _ver(ver) < (1, 20, 0)
        add("nginx", "Server", ver, old)
    elif "apache" in server:
        m = re.search(r"apache/([\d.]+)", server)
        ver = m.group(1) if m else "—"
        old = ver != "—" and _ver(ver) < (2, 4, 51)
        add("Apache", "Server", ver, old)
    elif "microsoft-iis" in server:
        m = re.search(r"iis/([\d.]+)", server)
        add("IIS", "Server", m.group(1) if m else "—", False)
    elif "caddy" in server:
        add("Caddy", "Server")
    elif "openresty" in server:
        add("OpenResty", "Server")
    elif "litespeed" in server:
        add("LiteSpeed", "Server")
    elif "gunicorn" in server:
        add("Gunicorn", "Server")
    elif "werkzeug" in server:
        add("Werkzeug", "Server")
    elif "jetty" in server:
        add("Jetty", "Server")
    elif "tomcat" in server:
        add("Tomcat", "Server")

    # ── CDN / Platform (header fingerprints) ─────────────────────────────────
    if "cf-ray" in h or "cloudflare" in server:
        add("Cloudflare", "CDN")
    if "x-vercel-id" in h or "x-vercel-cache" in h:
        add("Vercel", "Platform")
    if "x-nf-request-id" in h:
        add("Netlify", "Platform")
    if "x-github-request-id" in h:
        add("GitHub Pages", "Platform")
    if "x-amz-cf-id" in h or "x-amz-request-id" in h:
        add("AWS CloudFront", "CDN")
    if "x-azure-ref" in h:
        add("Azure CDN", "CDN")
    if "x-akamai-transformed" in h or "akamai" in h.get("x-check-cacheable", ""):
        add("Akamai", "CDN")
    if "fastly-restarts" in h or "x-served-by" in h:
        add("Fastly", "CDN")
    if "x-fly-request-id" in h:
        add("Fly.io", "Platform")
    if "x-render-origin-server" in h:
        add("Render", "Platform")
    if "x-railway-app-id" in h:
        add("Railway", "Platform")

    # ── Languages ─────────────────────────────────────────────────────────────
    if "php" in powered:
        m = re.search(r"php/([\d.]+)", powered)
        ver = m.group(1) if m else "7.x"
        try:
            old = int(ver.split(".")[0]) < 8
        except Exception:
            old = True
        add("PHP", "Lang", ver, old)
    if "asp.net" in powered or "x-aspnet-version" in h:
        add("ASP.NET", "Framework", h.get("x-aspnet-version", "—"), False)
    if "express" in powered:
        add("Express", "Framework")
    if "java" in powered or "jsessionid" in cookies:
        add("Java", "Lang")
    if "ruby" in powered or "rack" in h.get("x-rack-cache", ""):
        add("Ruby", "Lang")
    if "python" in powered or "werkzeug" in server:
        add("Python", "Lang")

    # ── CMS ───────────────────────────────────────────────────────────────────
    if re.search(r"wp-content|wp-json|/wp-includes", body, re.I):
        m = re.search(r'content="WordPress ([\d.]+)', body, re.I)
        ver = m.group(1) if m else "—"
        add("WordPress", "CMS", ver, False)
        if "PHP" not in seen:
            add("PHP", "Lang")
    if re.search(r'content="Drupal', body, re.I) or "/sites/default/files" in body:
        add("Drupal", "CMS")
    if re.search(r'content="Joomla', body, re.I):
        add("Joomla", "CMS")
    if re.search(r"shopify", body, re.I) or "myshopify" in h.get("set-cookie", ""):
        add("Shopify", "Platform")
    if re.search(r'content="Ghost', body, re.I) or "ghost-theme" in body:
        add("Ghost", "CMS")
    if re.search(r"confluence", body, re.I):
        add("Confluence", "Wiki")
    if re.search(r"x-confluence-request-time", str(h), re.I):
        add("Confluence", "Wiki")

    # ── Frontend frameworks ───────────────────────────────────────────────────
    if re.search(r"/_next/|__next|__NEXT_DATA__", body, re.I):
        add("Next.js", "Framework")
        if "React" not in seen:
            add("React", "Frontend")
    elif re.search(r"react-dom|react\.development|react\.production|__react", body, re.I):
        add("React", "Frontend")
    if re.search(r"vue\.js|vue\.min\.js|vue@\d|__vue_app__|__VUE__", body, re.I):
        add("Vue.js", "Frontend")
    if re.search(r"ng-version|angular\.js|angular\.min|platformBrowserDynamic", body, re.I):
        m = re.search(r'ng-version="([\d.]+)"', body)
        add("Angular", "Frontend", m.group(1) if m else "—", False)
    if re.search(r"/_nuxt/|__nuxt|NuxtApp", body, re.I):
        add("Nuxt.js", "Framework")
    if re.search(r"/svelte/|__svelte|SvelteKit", body, re.I):
        add("SvelteKit", "Framework")
    if re.search(r"astro-island|astro:page", body, re.I):
        add("Astro", "Framework")
    if re.search(r"remix-run|__remix", body, re.I):
        add("Remix", "Framework")

    # ── Libraries ─────────────────────────────────────────────────────────────
    m = re.search(r"jquery[/\-@v]?([0-9]+\.[0-9]+\.[0-9]+)", body, re.I)
    if m:
        ver = m.group(1)
        add("jQuery", "Library", ver, int(ver.split(".")[0]) < 3)
    elif re.search(r"jquery\.js|jquery\.min\.js|/jquery/", body, re.I):
        add("jQuery", "Library")

    # ── CSS frameworks ────────────────────────────────────────────────────────
    if re.search(r"bootstrap\.(min\.)?css|bootstrap\.(min\.)?js|bootstrap@", body, re.I):
        m = re.search(r"bootstrap@([0-9]+\.[0-9]+)", body, re.I)
        add("Bootstrap", "UI", m.group(1) if m else "—", False)
    if re.search(r"tailwind(?:css)?", body, re.I) or "tailwind" in h.get("x-powered-by", ""):
        add("Tailwind CSS", "UI")
    if re.search(r"materialize\.css|materialize\.min", body, re.I):
        add("Materialize", "UI")

    # ── Analytics ─────────────────────────────────────────────────────────────
    if re.search(r"google-analytics\.com|gtag\(|googletagmanager\.com", body, re.I):
        add("Google Analytics", "Analytics", "GA4", False)
    if re.search(r"segment\.com/analytics|analytics\.js/", body, re.I):
        add("Segment", "Analytics")
    if re.search(r"mixpanel", body, re.I):
        add("Mixpanel", "Analytics")
    if re.search(r"plausible\.io", body, re.I):
        add("Plausible", "Analytics")
    if re.search(r"hotjar", body, re.I):
        add("Hotjar", "Analytics")
    if re.search(r"hubspot", body, re.I) or "hubspot" in str(h).lower():
        add("HubSpot", "Marketing")
    if re.search(r"intercom", body, re.I):
        add("Intercom", "Support")
    if re.search(r"zendesk", body, re.I):
        add("Zendesk", "Support")

    # ── Backend frameworks ────────────────────────────────────────────────────
    if re.search(r"laravel", body, re.I) or "laravel_session" in cookies:
        add("Laravel", "Framework")
        if "PHP" not in seen:
            add("PHP", "Lang")
    if "_rails_session" in cookies or re.search(r"rails|ruby on rails", body, re.I):
        add("Rails", "Framework")
    if re.search(r"django", body, re.I) or "csrftoken" in cookies:
        add("Django", "Framework")
        if "Python" not in seen:
            add("Python", "Lang")
    if re.search(r"fastapi|starlette", body, re.I):
        add("FastAPI", "Framework")
    if re.search(r"flask", body, re.I):
        add("Flask", "Framework")
    if re.search(r"spring boot|springframewor", body, re.I):
        add("Spring Boot", "Framework")

    return techs


def _ver(s: str):
    parts = (s.split(".") + ["0", "0"])[:3]
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0, 0)
