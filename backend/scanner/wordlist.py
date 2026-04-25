WORDLIST = [
    # ── Web / access ──────────────────────────────────────────────────────────
    "www", "www2", "www3", "web", "web2", "web3", "site", "home", "main",
    "public", "ext", "external", "secure", "go", "click", "link",

    # ── Mail / messaging ──────────────────────────────────────────────────────
    "mail", "mail2", "mail3", "webmail", "email", "email2",
    "smtp", "smtp2", "smtp3", "pop", "pop3", "imap",
    "mx", "mx1", "mx2", "mx3", "relay", "inbound", "outbound",
    "exchange", "owa", "outlook", "autodiscover", "lyncdiscover",
    "newsletter", "subscribe", "mailer", "mailserver",

    # ── API / services ────────────────────────────────────────────────────────
    "api", "api2", "api3", "api4", "api-v1", "api-v2", "api-v3",
    "v1", "v2", "v3", "rest", "graphql", "rpc", "grpc", "soap",
    "api-gateway", "api-proxy", "gateway", "gw", "ws", "wss",
    "microservice", "service", "services", "svc", "backend",
    "webhook", "webhooks", "callback", "event", "events",
    "push", "notifications", "socket", "realtime", "stream",
    "openapi", "swagger",

    # ── Apps / portals ────────────────────────────────────────────────────────
    "app", "apps", "app2", "application", "applications",
    "portal", "eportal", "myportal", "citizenportal", "selfservice",
    "dashboard", "console", "management", "manager",
    "panel", "control", "cpanel", "whm", "plesk", "directadmin",
    "webmin", "admin", "admin2", "admin3", "administrator", "administration",
    "myadmin", "phpmyadmin", "pma", "adminer", "manage",

    # ── Government / public sector ────────────────────────────────────────────
    "services", "eservices", "e-services", "service1", "service2",
    "citizen", "citizens", "mygov", "gov", "government",
    "ministry", "minister", "ministerial",
    "complaints", "complaint", "grievance", "feedback",
    "tender", "tenders", "procurement", "bidding", "eprocurement",
    "license", "licensing", "permit", "permits", "permission",
    "certificate", "certificates", "attestation",
    "registration", "register", "renewal", "renew",
    "inquiry", "inquiries", "enquiry", "enquiries",
    "payment", "pay", "payments", "epayment", "fees", "fine", "fines",
    "appointment", "appointments", "booking", "bookings", "schedule",
    "track", "tracking", "status", "application-status",
    "statistics", "stats", "opendata", "data", "dataset", "datasets",
    "transparency", "disclosure",
    "survey", "forms", "form", "submit",
    "notify", "notifications", "alert", "alerts",
    "report", "reports", "reporting",
    "contact", "contactus",

    # ── UAE / Middle East region specific ─────────────────────────────────────
    "uae", "ae", "abudhabi", "rak", "sharjah", "ajman", "fujairah",
    "arabic", "ar", "en",
    "smart", "digital", "e", "m",
    "vision", "initiative", "strategy",
    "expo", "world",

    # ── Auth / identity ───────────────────────────────────────────────────────
    "auth", "auth2", "login", "signin", "signup", "signout",
    "sso", "saml", "oauth", "oidc", "ldap", "ad",
    "identity", "idp", "idm", "id", "account", "accounts",
    "password", "otp", "2fa", "mfa", "verify",
    "token", "session", "cookie",
    "okta", "auth0", "keycloak", "ping",

    # ── Environments ──────────────────────────────────────────────────────────
    "dev", "dev1", "dev2", "dev3", "develop", "development", "developer",
    "staging", "staging1", "staging2", "staging3", "stage",
    "test", "test1", "test2", "testing",
    "qa", "qa1", "qa2", "uat", "uat1", "uat2",
    "sandbox", "sandbox2", "demo", "demo2",
    "preview", "preview2", "beta", "alpha", "pre", "preprod",
    "prod", "production", "live",
    "canary", "nightly", "rc",

    # ── Documentation / support ───────────────────────────────────────────────
    "docs", "doc", "documentation", "wiki", "kb", "knowledge", "knowledgebase",
    "help", "support", "helpdesk", "servicedesk", "ticketing",
    "faq", "guide", "guides", "manual", "manuals",
    "learn", "training", "tutorial",
    "community", "forum", "discourse", "discuss",

    # ── HR / careers ──────────────────────────────────────────────────────────
    "jobs", "careers", "career", "hr", "recruitment", "recruiting", "hiring",
    "vacancies", "vacancy", "apply",
    "employee", "employees", "staff",
    "hris", "hrms", "payroll",

    # ── Infrastructure / network ──────────────────────────────────────────────
    "vpn", "vpn1", "vpn2", "proxy", "firewall", "waf", "lb", "loadbalancer",
    "haproxy", "nginx", "bastion", "jump",
    "rdp", "ssh", "sftp", "ftp", "ftp2", "ftps",
    "ns1", "ns2", "ns3", "ns4", "dns", "dns1", "dns2",
    "ntp", "ntp1", "ntp2",
    "server1", "server2", "server3", "server4",
    "host1", "host2", "host3",
    "node1", "node2", "node3",
    "cluster", "master", "worker", "workers",
    "origin", "cdn", "cdn1", "cdn2", "edge",

    # ── Storage / CDN ─────────────────────────────────────────────────────────
    "static", "static2", "assets", "asset", "img", "images",
    "files", "upload", "uploads", "download", "downloads",
    "storage", "media", "media2", "content", "contents",
    "s3", "blob", "bucket", "cdn-origin",

    # ── Monitoring / observability ────────────────────────────────────────────
    "status", "uptime", "health", "healthcheck", "ping",
    "monitor", "monitoring", "grafana", "kibana",
    "elastic", "elasticsearch", "prometheus",
    "metrics", "logs", "log", "logging",
    "splunk", "datadog", "newrelic", "dynatrace",
    "zabbix", "nagios", "icinga", "soc", "noc",

    # ── DevOps / CI-CD ────────────────────────────────────────────────────────
    "git", "gitlab", "github", "bitbucket", "svn", "code", "repo",
    "ci", "cd", "jenkins", "travis", "circleci", "build", "deploy",
    "pipeline", "release", "releases", "artifact", "artifacts",
    "registry", "docker", "harbor", "nexus",
    "k8s", "kubernetes", "rancher", "portainer",
    "vault", "consul", "nomad",
    "terraform", "ansible",
    "devops", "sre", "ops", "noc",

    # ── Databases / messaging ─────────────────────────────────────────────────
    "db", "db1", "db2", "database", "sql", "mysql", "postgres",
    "mongo", "mongodb", "redis", "cache", "memcache",
    "cassandra", "couchdb", "elastic2",
    "broker", "queue", "mq", "rabbitmq", "kafka",

    # ── Business / CRM / ERP ──────────────────────────────────────────────────
    "crm", "erp", "hrm", "cms", "lms",
    "salesforce", "hubspot", "dynamics", "sap",
    "intranet", "corp", "corporate", "internal",
    "partner", "partners", "vendor", "vendors",
    "investor", "investors", "ir", "finance",

    # ── Collaboration ─────────────────────────────────────────────────────────
    "jira", "confluence", "sharepoint", "teams", "chat",
    "mattermost", "rocketchat", "slack",
    "office", "workspace",
    "calendar", "meet", "zoom", "webinar", "conference",

    # ── E-commerce / billing ──────────────────────────────────────────────────
    "shop", "store", "cart", "checkout", "billing", "invoice",
    "orders", "order", "stripe", "paypal",

    # ── Media / publishing ────────────────────────────────────────────────────
    "blog", "news", "press", "media3", "video", "streaming",
    "events", "event",
    "about", "legal", "terms", "privacy", "policy",
    "marketing", "campaign", "promo",

    # ── Security / compliance ─────────────────────────────────────────────────
    "security", "pentest", "scan", "waf2",
    "backup", "backup2", "bak", "archive",
    "dr", "disaster", "recovery",

    # ── Numbered / legacy ─────────────────────────────────────────────────────
    "old", "legacy", "deprecated", "new", "next",
    "lab", "labs", "experiment", "sandbox3",
    "mirror", "replica", "standby",
    "webdav", "caldav", "carddav",
    "sip", "voip", "pbx", "phone",
    "map", "maps", "geocode", "gis",
    "ml", "ai", "nlp", "analytics", "tracking", "bi",
    "search", "solr", "opensearch",
    "cron", "scheduler", "worker", "logger",

    # ── Short/single-letter common aliases ────────────────────────────────────
    "a", "b", "c", "i", "n", "p", "r", "s", "t",
    "api1", "app1", "web1",
    "mail-in", "mail-out", "smtp-in", "smtp-out",
    "cloud", "cloud2", "smart2",
    "mobi", "mobile", "m2",
    "wap", "pwa",
    "open", "public2", "shared",
    "test3", "dev4", "stage4",
]
