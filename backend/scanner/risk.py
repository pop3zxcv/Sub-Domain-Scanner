from typing import Dict, List, Optional

DEV_KEYWORDS = {
    "dev", "develop", "development", "staging", "stage", "test", "testing",
    "qa", "uat", "sandbox", "demo", "preview", "beta", "alpha", "pre",
    "preprod", "debug", "local", "internal", "intranet", "corp",
}
SENSITIVE_KEYWORDS = {
    "admin", "panel", "jenkins", "grafana", "kibana", "prometheus",
    "elastic", "mongo", "redis", "mysql", "postgres", "db", "database",
    "backup", "phpmyadmin", "pma", "adminer", "webmin", "cpanel", "whm",
    "rancher", "k8s", "kubernetes", "vault", "consul", "nomad", "portainer",
    "harbor", "registry", "logstash", "splunk", "sonarqube",
}
SENSITIVE_PORTS = {21, 22, 23, 3306, 5432, 6379, 27017, 5984, 9200, 9300, 5601, 3000, 8080, 9090, 8888}


def calculate_risk(
    sub: str,
    dns: Dict,
    http: Optional[Dict],
    cert: Optional[Dict],
    ports: List[int],
    techs: List[Dict],
) -> int:
    score = 0
    sub_lower = sub.lower()

    if any(k in sub_lower for k in DEV_KEYWORDS):
        score += 25
    if any(k in sub_lower for k in SENSITIVE_KEYWORDS):
        score += 20

    # TLS assessment
    if not cert:
        score += 25
    else:
        grade_scores = {"A+": 0, "A": 5, "B": 20, "C": 35, "F": 60}
        score += grade_scores.get(cert.get("grade", "B"), 15)

    # Outdated technologies
    score += sum(12 for t in techs if t.get("outdated"))

    # Exposed sensitive ports
    score += len(set(ports) & SENSITIVE_PORTS) * 10

    # HTTP error suggests misconfiguration
    if http and http.get("status", 0) in (401, 403):
        score += 8

    # DNS resolves but no HTTP = dangling record
    if not http and (dns.get("A") or dns.get("CNAME")):
        score += 15

    return min(100, max(0, round(score)))


def detect_takeover(dns: Dict, http: Optional[Dict]) -> Dict:
    cname_list = dns.get("CNAME") or []
    cname = cname_list[0].lower() if cname_list else ""
    body = (http or {}).get("html", "").lower() if http else ""
    status = (http or {}).get("status", 0) if http else 0

    PATTERNS = [
        ("GitHub Pages",  "github.io",         "there isn't a github pages site here"),
        ("Heroku",        "herokuapp.com",      "no such app"),
        ("AWS S3",        "s3.amazonaws.com",   "nosuchbucket"),
        ("Netlify",       "netlify.app",        "not found - request id"),
        ("Netlify",       "netlify.com",        "not found - request id"),
        ("Vercel",        "vercel.app",         "deployment not found"),
        ("Azure",         "azurewebsites.net",  "this web app has been stopped"),
        ("Shopify",       "myshopify.com",      "only a few more steps"),
        ("Tumblr",        "tumblr.com",         "there's nothing here"),
        ("Ghost",         "ghost.io",           "failed to resolve"),
        ("Fastly",        "fastly.net",         "please check that this domain has been added"),
        ("Surge.sh",      "surge.sh",           "project not found"),
        ("Pantheon",      "pantheonsite.io",    "404 error unknown site"),
        ("Acquia",        "acquia-sites.com",   "the site you are looking for"),
        ("WP Engine",     "wpengine.com",       "no longer exists"),
        ("Fly.io",        "fly.dev",            "404 not found"),
    ]

    for service, cname_keyword, body_keyword in PATTERNS:
        if cname_keyword in cname and body_keyword in body:
            return {
                "vulnerable": True,
                "service": service,
                "note": f"CNAME points to unclaimed {service} resource",
            }

    if cname and status == 404:
        return {
            "vulnerable": True,
            "service": "Unknown",
            "note": f"CNAME to {cname} returns 404 — possible takeover",
        }

    return {"vulnerable": False, "service": None, "note": None}
