# SubSentry — Subdomain Discovery & Security Scanner

A real-time subdomain discovery and security scanning tool with a React frontend and Python/FastAPI backend.

## Requirements

- Python 3.11+
- Node.js 18+
- nmap (optional, enables full port scanning)

```bash
brew install nmap        # macOS
# sudo apt install nmap  # Ubuntu/Debian
```

## Setup

### Backend

```bash
cd "Sub Domain Scanner/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd "Sub Domain Scanner/frontend"
npm install
```

## Running

Open two terminals:

**Terminal 1 — Backend:**
```bash
cd "Sub Domain Scanner/backend"
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 3001 --reload
```

**Terminal 2 — Frontend:**
```bash
cd "Sub Domain Scanner/frontend"
npm run dev
```

Open http://localhost:5173 in your browser.

## Features

- **8 passive sources**: crt.sh, HackerTarget, AnubisDB, URLScan.io, AlienVault OTX, Wayback CDX, ThreatCrowd, RapidDNS
- **DNS bruteforce**: 200-word wordlist with 60 concurrent async resolvers
- **HTTP probing**: HTTPS→HTTP fallback, title and header extraction
- **TLS grading**: A+/A/B/C/F based on TLS version and cipher
- **Port scanning**: nmap (if installed) with async TCP fallback
- **Tech fingerprinting**: 30+ technologies from headers and body
- **IP geolocation**: ip-api.com with hosting inference
- **WHOIS lookup**: per-domain on demand
- **Risk scoring**: 0–100 composite score
- **Takeover detection**: 16 known service patterns
- **Real-time streaming**: results appear as they're found via SSE
- **Export**: CSV and JSON
- **Dark/light mode**, compact density, column visibility, filtering, sorting

## API

- `GET /api/scan?domain=example.com` — SSE stream of scan results
- `GET /api/whois?domain=example.com` — WHOIS JSON
- `GET /api/status` — health check
