# SubSentry — Project Knowledge Base

Everything Claude needs to know about this project to work on it without re-asking questions.

---

## What This Is

**SubSentry** is a real-time subdomain discovery and security scanning tool. Given a domain name it finds as many subdomains as possible, probes each one for live status, TLS, ports, geolocation, tech stack, risk score, and potential takeover vulnerabilities. Results stream to the browser in real time as they are found.

- **GitHub**: https://github.com/pop3zxcv/Sub-Domain-Scanner
- **GitHub account**: pop3zxcv (sherali.khan@gmail.com)
- **Every commit must include**: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- **Workflow**: always branch → commit → PR → merge. Never commit directly to `main`.

---

## Folder Structure

```
Sub Domain Scanner/
├── CLAUDE.md                  ← this file
├── README.md                  ← user-facing setup instructions
├── .gitignore
├── docker-compose.yml         ← runs both services; frontend :8080, backend :3001
├── index.html                 ← original design wireframe reference (not the app)
│
├── backend/
│   ├── Dockerfile             ← python:3.12-slim + nmap; runs uvicorn on 3001
│   ├── requirements.txt       ← pinned Python deps
│   ├── main.py                ← FastAPI app, SSE endpoints, scan orchestration
│   └── scanner/
│       ├── __init__.py
│       ├── sources.py         ← all subdomain discovery (10 passive + brute + AXFR)
│       ├── wordlist.py        ← 450+ subdomain labels for DNS bruteforce
│       ├── dns_resolve.py     ← async DNS: A, AAAA, CNAME, MX, TXT, NS
│       ├── http_probe.py      ← aiohttp HTTPS→HTTP probe; returns status/title/headers/html
│       ├── tls_check.py       ← ssl module + socket; grades A+/A/B/C/F
│       ├── port_scan.py       ← nmap if available, falls back to asyncio TCP connect
│       ├── fingerprint.py     ← 30+ tech patterns from headers + HTML body
│       ├── geo.py             ← ip-api.com geolocation + hosting inference
│       ├── whois_check.py     ← python-whois in thread pool executor
│       └── risk.py            ← 0–100 risk score + takeover detection (16 services)
│
└── frontend/
    ├── Dockerfile             ← node:20-alpine build → nginx:alpine serve
    ├── nginx.conf             ← proxies /api/ to backend; SSE buffering disabled
    ├── index.html             ← Vite HTML shell
    ├── package.json           ← React 18.3.1, Vite 5.3.1, TypeScript 5.4.5
    ├── vite.config.ts         ← /api proxy to localhost:3001; SSE buffering off
    ├── tsconfig.json          ← strict mode, bundler module resolution
    └── src/
        ├── main.tsx           ← ReactDOM.createRoot entry point
        ├── App.tsx            ← all state, SSE client, filtering, sorting, export
        ├── types.ts           ← all TypeScript interfaces and constants
        ├── index.css          ← all styles (no CSS framework, no Tailwind)
        └── components/
            ├── Icons.tsx      ← 14 inline SVG icons as named exports
            ├── SearchBar.tsx  ← domain input, Quick/Deep toggle, Scan/Stop button
            ├── StatTiles.tsx  ← 6-tile summary grid (total/live/errors/offline/risk/takeover)
            ├── Toolbar.tsx    ← status/country/tech filters, column toggle, export dropdown
            ├── DataTable.tsx  ← sortable table with select-all checkbox header
            ├── Row.tsx        ← individual table row with checkbox, inline expand
            ├── DetailPanel.tsx← expanded row: risk bar, DNS, network, TLS, ports, tech
            ├── DetailModal.tsx← side-sheet slide-in with full detail + WHOIS
            └── CopyCell.tsx   ← click-to-copy button with checkmark feedback
```

---

## Tech Stack

### Backend
| Package | Version | Purpose |
|---|---|---|
| FastAPI | 0.111.0 | API framework |
| uvicorn[standard] | 0.29.0 | ASGI server |
| sse-starlette | 1.8.2 | Server-Sent Events streaming |
| aiohttp | 3.9.5 | Async HTTP client for probing + passive sources |
| dnspython | 2.6.1 | Async DNS resolution + AXFR zone transfer |
| python-nmap | 0.7.1 | Port scanning (wraps nmap CLI) |
| python-whois | 0.9.5 | WHOIS lookups |

- Python 3.12, venv at `backend/.venv`
- nmap must be installed separately (`brew install nmap`)

### Frontend
| Package | Version | Purpose |
|---|---|---|
| React | 18.3.1 | UI framework |
| Vite | 5.3.1 | Dev server + bundler |
| TypeScript | 5.4.5 | Type safety |

- **No CSS framework** — pure vanilla CSS with CSS custom properties
- **No component library** — all components hand-written
- **No external icon library** — all SVG icons inline in `Icons.tsx`

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/scan?domain=` | Deep scan — SSE stream; 10 passive sources + wordlist bruteforce + AXFR |
| GET | `/api/quick?domain=` | Quick scan — SSE stream; passive sources + DNS + geo only (no ports/TLS/tech) |
| GET | `/api/whois?domain=` | WHOIS JSON for a domain (called on demand when detail modal opens) |
| GET | `/api/status` | Health check; returns `{"ok": true, "nmap": bool}` |

### SSE Event Types
- `status` — progress message string
- `result` — one scanned subdomain (full JSON object)
- `progress` — subdomain was skipped (didn't resolve)
- `ping` — keepalive with `{probed, total}`
- `done` — scan complete with `{total}`
- `error` — scan failed

---

## Data Model (`SubdomainResult`)

```typescript
{
  id: number           // client-assigned, increments per result
  fqdn: string         // full qualified domain name
  sub: string          // bare subdomain label
  domain: string       // apex domain
  status: number       // HTTP status (0 = offline/no response)
  title: string        // page <title>
  ip: string           // first A record
  ipv6: string         // first AAAA record
  host: { name, asn, color }          // inferred hosting provider
  country: { country, code, flag }    // from ip-api.com
  techs: [{ name, cat, v, outdated }] // fingerprinted technologies
  ports: number[]      // open ports
  ssl: { issuer, subject, expires, grade } | null
  risk: number         // 0–100 composite risk score
  takeover: boolean
  takeoverNote: string | null
  source: string       // "multi-source" or "passive"
  lastSeen: number
  dns: { A, AAAA, CNAME, MX, TXT, NS }  // arrays of strings
}
```

---

## Subdomain Discovery Sources (10 passive + bruteforce + AXFR)

1. **crt.sh** — Certificate Transparency logs
2. **HackerTarget** — host search (100 req/day free)
3. **AnubisDB** — passive DNS
4. **URLScan.io** — public scan index
5. **AlienVault OTX** — passive DNS
6. **Wayback Machine CDX** — archived URLs
7. **ThreatCrowd** — threat intelligence
8. **RapidDNS** — HTML scrape
9. **CertSpotter** — separate CT log database (often finds certs crt.sh misses)
10. **BufferOver / Rapid7 FDNS** — internet-wide forward DNS dataset
11. **DNS Zone Transfer (AXFR)** — attempted against all nameservers
12. **Wordlist bruteforce** — 450+ labels, 60 concurrent async resolvers

---

## Design System

### Colors (CSS custom properties)

**Light theme (`:root`)**
| Variable | Value | Use |
|---|---|---|
| `--bg` | `#F5F7FA` | Page background |
| `--surface` | `#FFFFFF` | Cards, table |
| `--surface-2` | `#F9FAFB` | Table header, expanded rows |
| `--border` | `#E4E7EC` | All borders |
| `--fg` | `#111827` | Primary text |
| `--fg-2` | `#6B7280` | Secondary text |
| `--fg-3` | `#9CA3AF` | Muted/placeholder text |
| `--accent` | `#2563EB` | Primary blue (buttons, links, active states) |
| `--ok-fg` | `#059669` | Green (live status, low risk) |
| `--warn-fg` | `#D97706` | Amber (medium risk, warnings) |
| `--bad-fg` | `#DC2626` | Red (errors, high risk, stop button) |

**Dark theme (`[data-theme="dark"]`)**
| Variable | Value |
|---|---|
| `--bg` | `#0D0F14` |
| `--surface` | `#161B26` |
| `--surface-2` | `#1C2333` |
| `--accent` | `#3B82F6` |
| `--ok-fg` | `#34D399` |
| `--warn-fg` | `#FBBF24` |
| `--bad-fg` | `#F87171` |

### Typography
- **Font**: System font stack — `-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`
- **Base size**: `14px` on `<html>`
- **Monospace** (IPs, DNS values, FQDNs): `ui-monospace, monospace`

### Radii
- `--radius`: `8px` — cards, dropdowns, modal
- `--radius-sm`: `5px` — badges, chips, inputs

### Theming mechanism
- Theme toggled by `data-theme="dark"` attribute on `<html>`
- Density toggled by `data-density="compact"` attribute on `<html>`
- Both stored in React state in `App.tsx`, applied via `document.documentElement.setAttribute`

---

## UI Layout & Sections

```
┌─────────────────────────────────────────────────────┐
│ Header: [🛡 SubSentry]              [density] [theme]│
├─────────────────────────────────────────────────────┤
│ SearchBar: [🔍 domain input] [Quick|Deep] [Scan/Stop]│
│ Hint: mode description · Try: example.com, ...      │
├─────────────────────────────────────────────────────┤
│ StatTiles: Total | Live | Errors | Offline | Risk | Takeover │
├─────────────────────────────────────────────────────┤
│ Toolbar: [All status▼] [All countries▼] [All tech▼] │
│          [☐ Takeover only] [N results]   [Columns][Export] │
├─────────────────────────────────────────────────────┤
│ DataTable:                                           │
│ [☐] [^] Subdomain | Status | IP | Hosting | Country │
│          | Title | Tech | Ports | SSL | Risk | Source│
│  ──────────────────────────────────────────────────  │
│  [☐] [v] sub.domain.com | 200 | 1.2.3.4 | ...      │
│       └─ DetailPanel (inline expand):                │
│          [Risk] [DNS Records x2wide] [Network]       │
│          [TLS/SSL] [Open Ports] [Tech Stack]         │
└─────────────────────────────────────────────────────┘
                                    [Detail Modal →]
                                    Side-sheet slide-in:
                                    Full detail + WHOIS
```

### Stat Tiles
6 tiles in a 6-column grid (3-col on mobile):
- **Total found** — accent blue
- **Live (2xx/3xx)** — green
- **Errors (4xx/5xx)** — dark red `#B23A1F`
- **Offline / none** — gray
- **High risk (≥50)** — amber `#A66A00`
- **Takeover risks** — bad-fg red

### Detail Panel (expanded inline row)
- CSS grid: `repeat(auto-fill, minmax(200px, 1fr))`
- **DNS Records card** spans `grid-column: span 2` (wider than others)
- DNS values truncate with `…` (ellipsis); full value shown in `title` tooltip
- Cards: Risk Assessment, DNS Records, Network, TLS/SSL, Open Ports, Tech Stack
- Max-width constrained inside `tr-detail` to prevent stretching across wide table

### Detail Modal (side-sheet)
- Fixed right-side overlay, 600px wide, full viewport height
- Contains: DetailPanel + WHOIS section
- WHOIS loaded on demand when modal opens (`GET /api/whois`)
- Closes on Escape key or backdrop click

---

## User Preferences

- **Scan modes**: Quick (passive only, fast) vs Deep (full, with ports/TLS/tech)
- **Stop scan**: red Stop button replaces Scan button during scanning; closes EventSource
- **Row selection**: checkboxes on each row; select-all in header; indeterminate state when partial
- **Export**: CSV or JSON; if rows are selected, exports only those rows; label shows count
- **Column visibility**: toggle via Columns dropdown in toolbar
- **Theme**: dark (default) / light — toggle in header
- **Density**: default / compact — toggle in header
- **Copy to clipboard**: click any subdomain or IP cell; checkmark confirms, resets after 1.1s

### Filter options
- Status: All / Live (2xx/3xx) / Error (4xx/5xx) / Offline
- Country: populated dynamically from scan results
- Tech: populated dynamically; hidden/shows "No tech data" when quick scan or no detections
- Takeover risks only: checkbox filter

### Table sort
- Click any column header to sort asc/desc
- Default sort: risk descending (highest risk first)

---

## Concurrency Model

### Deep scan
- **Passive sources**: 10 sources queried in parallel via `asyncio.gather`
- **Zone transfer**: runs concurrently with passive sources
- **Wordlist bruteforce**: `asyncio.Semaphore(60)` — 60 concurrent DNS resolvers
- **HTTP probing**: `asyncio.Semaphore(20)` — 20 concurrent probes
- **Port scanning**: `asyncio.Semaphore(5)` — 5 concurrent nmap jobs
- Results stream via `asyncio.Queue` → `drain_queue()` generator with 1.5s timeout keepalives

### Quick scan
- Passive sources + AXFR only (no wordlist)
- `asyncio.Semaphore(40)` — 40 concurrent probes (lighter, no nmap)
- No TLS, no ports, no tech fingerprinting

---

## Docker Setup

```yaml
# docker-compose.yml
services:
  backend:   # python:3.12-slim + nmap; port 3001
  frontend:  # nginx:alpine serving built React app; port 8080
```

- Frontend nginx proxies `/api/` → `http://backend:3001`
- SSE buffering explicitly disabled in nginx (`proxy_buffering off`)
- Backend needs `cap_add: [NET_RAW, NET_ADMIN]` for nmap raw sockets
- Run: `docker compose up --build` → open http://localhost:8080

---

## Known Bugs Fixed

| Bug | Fix |
|---|---|
| `asyncio.coroutine(lambda: None)()` — removed in Python 3.11 | Replaced with `async def _noop(): return None` |
| DNS values overflowing card boundaries | `min-width: 0` on flex child + `overflow-wrap: anywhere` |
| Detail panel stretching across wide table | `max-width: min(1100px, calc(100vw - 48px))` on `.tr-detail .detail-panel` |
| "All tech" filter showing empty native dropdown | Hidden when `techs.length === 0`; shows "No tech data" label instead |
| KV pairs in Network/TLS cards overflowing | `text-overflow: ellipsis` + `min-width: 0` on value spans |

---

## Git Conventions

- Branch names: `feature/short-description` or `fix/short-description`
- Commit style: conventional commits (`feat:`, `fix:`, `chore:`)
- Every commit footer: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- Never mention specific scan target domains in commit messages or PR descriptions
- Always open a PR; merge via `gh pr merge` or `git merge --no-ff`

---

## How to Run Locally

```bash
# Backend
cd backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 3001 --reload

# Frontend (separate terminal)
cd frontend
npm run dev
# → http://localhost:5173

# Docker (both together)
docker compose up --build
# → http://localhost:8080
```
