import React from "react";
import * as I from "./Icons";
import { FilterState, ALL_COLUMNS } from "../types";

interface Props {
  filters: FilterState;
  setFilters: (f: FilterState) => void;
  visibleCols: string[];
  setVisibleCols: (c: string[]) => void;
  countries: string[];
  techs: string[];
  onExportCsv: () => void;
  onExportJson: () => void;
  total: number;
  shown: number;
}

export default function Toolbar({
  filters, setFilters, visibleCols, setVisibleCols,
  countries, techs, onExportCsv, onExportJson, total, shown,
}: Props) {
  const [colOpen, setColOpen] = React.useState(false);
  const [expOpen, setExpOpen] = React.useState(false);
  const colRef = React.useRef<HTMLDivElement>(null);
  const expRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (colRef.current && !colRef.current.contains(e.target as Node)) setColOpen(false);
      if (expRef.current && !expRef.current.contains(e.target as Node)) setExpOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const set = (patch: Partial<FilterState>) => setFilters({ ...filters, ...patch });

  return (
    <div className="toolbar">
      <div className="toolbar-filters">
        <select
          className="filter-select"
          value={filters.status}
          onChange={(e) => set({ status: e.target.value as FilterState["status"] })}
        >
          <option value="all">All status</option>
          <option value="live">Live (2xx/3xx)</option>
          <option value="error">Error (4xx/5xx)</option>
          <option value="offline">Offline</option>
        </select>

        <select
          className="filter-select"
          value={filters.country}
          onChange={(e) => set({ country: e.target.value })}
        >
          <option value="all">All countries</option>
          {countries.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>

        {techs.length > 0 ? (
          <select
            className="filter-select"
            value={filters.tech}
            onChange={(e) => set({ tech: e.target.value })}
          >
            <option value="all">All tech ({techs.length})</option>
            {techs.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        ) : (
          <span className="filter-select filter-select-empty" title="No tech data — run a Deep scan to detect technologies">
            No tech data
          </span>
        )}

        <label className="filter-check">
          <input
            type="checkbox"
            checked={filters.takeoverOnly}
            onChange={(e) => set({ takeoverOnly: e.target.checked })}
          />
          Takeover risks only
        </label>

        <span className="toolbar-count">
          {shown === total ? `${total} results` : `${shown} / ${total}`}
        </span>
      </div>

      <div className="toolbar-actions">
        <div className="dropdown-wrap" ref={colRef}>
          <button className="toolbar-btn" onClick={() => setColOpen(!colOpen)}>
            <I.Filter /> Columns
          </button>
          {colOpen && (
            <div className="dropdown">
              {ALL_COLUMNS.map((col) => (
                <label key={col.key} className="dropdown-item">
                  <input
                    type="checkbox"
                    checked={visibleCols.includes(col.key)}
                    onChange={(e) => {
                      setVisibleCols(
                        e.target.checked
                          ? [...visibleCols, col.key]
                          : visibleCols.filter((k) => k !== col.key)
                      );
                    }}
                  />
                  {col.label}
                </label>
              ))}
            </div>
          )}
        </div>

        <div className="dropdown-wrap" ref={expRef}>
          <button className="toolbar-btn" onClick={() => setExpOpen(!expOpen)}>
            <I.Download /> Export
          </button>
          {expOpen && (
            <div className="dropdown">
              <button className="dropdown-item" onClick={() => { onExportCsv(); setExpOpen(false); }}>
                Export CSV
              </button>
              <button className="dropdown-item" onClick={() => { onExportJson(); setExpOpen(false); }}>
                Export JSON
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
