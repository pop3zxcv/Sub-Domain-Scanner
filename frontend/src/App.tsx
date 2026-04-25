import React, { useState, useCallback, useMemo, useRef } from "react";
import SearchBar, { ScanMode } from "./components/SearchBar";
import StatTiles from "./components/StatTiles";
import Toolbar from "./components/Toolbar";
import DataTable from "./components/DataTable";
import DetailModal from "./components/DetailModal";
import * as I from "./components/Icons";
import {
  SubdomainResult, WhoisInfo, SortState, FilterState,
  DEFAULT_FILTERS, DEFAULT_COLUMNS,
} from "./types";

type Theme = "dark" | "light";
type Density = "default" | "compact";

function applyTheme(t: Theme) {
  document.documentElement.setAttribute("data-theme", t);
}

function applyDensity(d: Density) {
  document.documentElement.setAttribute("data-density", d);
}

function sortResults(results: SubdomainResult[], sort: SortState): SubdomainResult[] {
  return [...results].sort((a, b) => {
    let av: unknown, bv: unknown;
    switch (sort.key) {
      case "sub":     av = a.fqdn;       bv = b.fqdn; break;
      case "status":  av = a.status;     bv = b.status; break;
      case "ip":      av = a.ip;         bv = b.ip; break;
      case "host":    av = a.host?.name; bv = b.host?.name; break;
      case "country": av = a.country?.country; bv = b.country?.country; break;
      case "title":   av = a.title;      bv = b.title; break;
      case "ports":   av = a.ports.length; bv = b.ports.length; break;
      case "ssl":     av = a.ssl?.grade; bv = b.ssl?.grade; break;
      case "risk":    av = a.risk;       bv = b.risk; break;
      case "source":  av = a.source;     bv = b.source; break;
      default:        return 0;
    }
    const aStr = String(av ?? ""), bStr = String(bv ?? "");
    const cmp = typeof av === "number" && typeof bv === "number"
      ? av - bv
      : aStr.localeCompare(bStr);
    return sort.dir === "asc" ? cmp : -cmp;
  });
}

function filterResults(results: SubdomainResult[], filters: FilterState): SubdomainResult[] {
  return results.filter((r) => {
    if (filters.takeoverOnly && !r.takeover) return false;
    if (filters.status === "live"    && !(r.status >= 200 && r.status < 400)) return false;
    if (filters.status === "error"   && !(r.status >= 400)) return false;
    if (filters.status === "offline" && r.status !== 0) return false;
    if (filters.country !== "all" && r.country?.country !== filters.country) return false;
    if (filters.tech !== "all" && !r.techs.some((t) => t.name === filters.tech)) return false;
    if (filters.q) {
      const q = filters.q.toLowerCase();
      if (!r.fqdn.includes(q) && !r.ip.includes(q) && !r.title.toLowerCase().includes(q)) return false;
    }
    return true;
  });
}

export default function App() {
  const [domain, setDomain]         = useState("");
  const [results, setResults]       = useState<SubdomainResult[]>([]);
  const [scanning, setScanning]     = useState(false);
  const [error, setError]           = useState<string | null>(null);
  const [filters, setFilters]       = useState<FilterState>(DEFAULT_FILTERS);
  const [sort, setSort]             = useState<SortState>({ key: "risk", dir: "desc" });
  const [visibleCols, setVisibleCols] = useState<string[]>(DEFAULT_COLUMNS);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [openDetail, setOpenDetail] = useState<SubdomainResult | null>(null);
  const [whois, setWhois]           = useState<WhoisInfo | null>(null);
  const [whoisLoading, setWhoisLoading] = useState(false);
  const [scanMode, setScanMode]     = useState<ScanMode>("deep");
  const [theme, setTheme]           = useState<Theme>("dark");
  const [density, setDensity]       = useState<Density>("default");
  const [copied, setCopied]         = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const esRef = useRef<EventSource | null>(null);
  const idRef = useRef(0);

  React.useEffect(() => { applyTheme(theme); }, [theme]);
  React.useEffect(() => { applyDensity(density); }, [density]);

  const toggleTheme  = () => setTheme((t) => t === "dark" ? "light" : "dark");
  const toggleDensity = () => setDensity((d) => d === "default" ? "compact" : "default");

  const startScan = useCallback(() => {
    const d = domain.trim().replace(/^https?:\/\//i, "").replace(/\/.*$/, "");
    if (!d) return;
    esRef.current?.close();
    setResults([]);
    setError(null);
    setScanning(true);
    setExpandedId(null);
    setOpenDetail(null);
    setSelectedIds(new Set());
    idRef.current = 0;

    const endpoint = scanMode === "quick" ? "/api/quick" : "/api/scan";
    const es = new EventSource(`${endpoint}?domain=${encodeURIComponent(d)}`);
    esRef.current = es;

    es.addEventListener("result", (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setResults((prev) => [...prev, { ...data, id: ++idRef.current }]);
    });

    es.addEventListener("done", () => {
      es.close();
      setScanning(false);
    });

    es.addEventListener("error", (e: MessageEvent) => {
      try {
        const data = JSON.parse((e as MessageEvent).data ?? "{}");
        setError(data.detail ?? "Scan error");
      } catch {
        setError("Connection error");
      }
      es.close();
      setScanning(false);
    });

    es.onerror = () => {
      if (es.readyState === EventSource.CLOSED) {
        setScanning(false);
      }
    };
  }, [domain, scanMode]);

  const stopScan = useCallback(() => {
    esRef.current?.close();
    esRef.current = null;
    setScanning(false);
  }, []);

  const handleSort = (key: string) => {
    setSort((s) => s.key === key
      ? { key, dir: s.dir === "asc" ? "desc" : "asc" }
      : { key, dir: "desc" }
    );
  };

  const handleToggle = (id: number) => {
    setExpandedId((prev) => prev === id ? null : id);
  };

  const handleOpen = useCallback(async (r: SubdomainResult) => {
    setOpenDetail(r);
    setWhois(null);
    setWhoisLoading(true);
    try {
      const res = await fetch(`/api/whois?domain=${encodeURIComponent(r.domain)}`);
      setWhois(res.ok ? await res.json() : null);
    } catch {
      setWhois(null);
    } finally {
      setWhoisLoading(false);
    }
  }, []);

  const filtered = useMemo(() => filterResults(results, filters), [results, filters]);
  const sorted   = useMemo(() => sortResults(filtered, sort), [filtered, sort]);

  const countries = useMemo(() =>
    [...new Set(results.map((r) => r.country?.country).filter(Boolean) as string[])].sort(),
    [results]
  );
  const techs = useMemo(() =>
    [...new Set(results.flatMap((r) => r.techs.map((t) => t.name)))].sort(),
    [results]
  );

  const toggleSelect = useCallback((id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  const toggleSelectAll = useCallback((visibleResults: SubdomainResult[]) => {
    setSelectedIds((prev) => {
      const allVisible = visibleResults.map((r) => r.id);
      const allSelected = allVisible.every((id) => prev.has(id));
      if (allSelected) return new Set();
      return new Set([...prev, ...allVisible]);
    });
  }, []);

  function rowsToExport(all: SubdomainResult[]) {
    return selectedIds.size > 0 ? all.filter((r) => selectedIds.has(r.id)) : all;
  }

  const exportCsv = (rows = sorted) => {
    const data = rowsToExport(rows);
    const header = ["fqdn","status","ip","country","title","ports","ssl","risk","takeover","source"];
    const body = data.map((r) => [
      r.fqdn, r.status, r.ip, r.country?.country ?? "",
      `"${(r.title ?? "").replace(/"/g, '""')}"`,
      r.ports.join(";"), r.ssl?.grade ?? "", r.risk, r.takeover, r.source,
    ]);
    const csv = [header, ...body].map((r) => r.join(",")).join("\n");
    download("subdomains.csv", "text/csv", csv);
  };

  const exportJson = (rows = sorted) => {
    download("subdomains.json", "application/json", JSON.stringify(rowsToExport(rows), null, 2));
  };

  function download(name: string, type: string, content: string) {
    const a = Object.assign(document.createElement("a"), {
      href: URL.createObjectURL(new Blob([content], { type })),
      download: name,
    });
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <I.Shield className="brand-icon" />
          <span className="brand-name">SubSentry</span>
        </div>
        <div className="header-actions">
          <button className="icon-btn" onClick={toggleDensity} title="Toggle density">
            <I.Settings />
          </button>
          <button className="icon-btn" onClick={toggleTheme} title="Toggle theme">
            {theme === "dark" ? <I.Sun /> : <I.Moon />}
          </button>
        </div>
      </header>

      <main className="main">
        <SearchBar
          value={domain}
          onChange={setDomain}
          onScan={startScan}
          onStop={stopScan}
          scanning={scanning}
          scanMode={scanMode}
          onModeChange={setScanMode}
        />

        {error && <div className="error-banner">{error}</div>}

        {results.length > 0 && (
          <>
            <StatTiles results={results} />
            <Toolbar
              filters={filters}
              setFilters={setFilters}
              visibleCols={visibleCols}
              setVisibleCols={setVisibleCols}
              countries={countries}
              techs={techs}
              onExportCsv={() => exportCsv()}
              onExportJson={() => exportJson()}
              total={results.length}
              shown={filtered.length}
              selectedCount={selectedIds.size}
            />
            <DataTable
              results={sorted}
              visibleCols={visibleCols}
              sort={sort}
              onSort={handleSort}
              expandedId={expandedId}
              onToggle={handleToggle}
              onOpen={handleOpen}
              copied={copied}
              setCopied={setCopied}
              selectedIds={selectedIds}
              onToggleSelect={toggleSelect}
              onToggleSelectAll={() => toggleSelectAll(sorted)}
            />
          </>
        )}

        {scanning && results.length === 0 && (
          <div className="scanning-placeholder">
            <div className="scanning-spinner" />
            <span>Discovering subdomains…</span>
          </div>
        )}
      </main>

      {openDetail && (
        <DetailModal
          result={openDetail}
          whois={whois}
          whoisLoading={whoisLoading}
          onClose={() => setOpenDetail(null)}
        />
      )}
    </div>
  );
}
