import React, { Fragment } from "react";
import * as I from "./Icons";

export type ScanMode = "deep" | "quick";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onScan: () => void;
  onStop: () => void;
  scanning: boolean;
  scanMode: ScanMode;
  onModeChange: (m: ScanMode) => void;
}

const EXAMPLES = ["example.com", "github.com", "cloudflare.com"];

export default function SearchBar({
  value, onChange, onScan, onStop, scanning, scanMode, onModeChange,
}: Props) {
  return (
    <div className="search-wrap">
      <div className={`search ${scanning ? "search-scanning" : ""}`}>
        <I.Search className="search-icon" />
        <input
          className="search-input"
          placeholder="Enter a domain to scan (e.g. example.com)"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !scanning && onScan()}
          disabled={scanning}
          autoFocus
        />
        <div className="search-mode-toggle">
          <button
            className={`mode-btn ${scanMode === "quick" ? "mode-btn-active" : ""}`}
            onClick={() => onModeChange("quick")}
            disabled={scanning}
            title="Quick scan: passive sources, DNS + IP + location only"
          >
            Quick
          </button>
          <button
            className={`mode-btn ${scanMode === "deep" ? "mode-btn-active" : ""}`}
            onClick={() => onModeChange("deep")}
            disabled={scanning}
            title="Deep scan: all sources, ports, TLS, tech fingerprinting"
          >
            Deep
          </button>
        </div>
        {scanning ? (
          <button className="search-btn search-btn-stop" onClick={onStop}>
            Stop
          </button>
        ) : (
          <button
            className="search-btn"
            onClick={onScan}
            disabled={!value.trim()}
          >
            Scan
          </button>
        )}
      </div>

      <div className="search-hint">
        {scanMode === "quick"
          ? "Quick: passive sources only — domain, IP, location. Fast."
          : "Deep: all sources + ports, TLS, tech fingerprinting."}
        {" · Try: "}
        {EXAMPLES.map((d, i) => (
          <Fragment key={d}>
            {i > 0 && ", "}
            <button className="link" onClick={() => onChange(d)}>
              {d}
            </button>
          </Fragment>
        ))}
      </div>
    </div>
  );
}
