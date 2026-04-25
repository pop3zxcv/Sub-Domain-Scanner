import React from "react";
import { SubdomainResult, SortState, ALL_COLUMNS } from "../types";
import Row from "./Row";
import * as I from "./Icons";

interface Props {
  results: SubdomainResult[];
  visibleCols: string[];
  sort: SortState;
  onSort: (key: string) => void;
  expandedId: number | null;
  onToggle: (id: number) => void;
  onOpen: (r: SubdomainResult) => void;
  copied: string | null;
  setCopied: (v: string | null) => void;
  selectedIds: Set<number>;
  onToggleSelect: (id: number) => void;
  onToggleSelectAll: () => void;
}

function Th({ col, sort, onSort }: { col: { key: string; label: string }; sort: SortState; onSort: (k: string) => void }) {
  const active = sort.key === col.key;
  return (
    <th className={`th ${active ? "th-active" : ""}`} onClick={() => onSort(col.key)}>
      {col.label}
      <I.Chevron
        className={`sort-chevron ${active ? (sort.dir === "asc" ? "sort-asc" : "sort-desc") : ""}`}
      />
    </th>
  );
}

export default function DataTable({
  results, visibleCols, sort, onSort, expandedId, onToggle, onOpen,
  copied, setCopied, selectedIds, onToggleSelect, onToggleSelectAll,
}: Props) {
  const cols = ALL_COLUMNS.filter((c) => visibleCols.includes(c.key));

  const allSelected = results.length > 0 && results.every((r) => selectedIds.has(r.id));
  const someSelected = results.some((r) => selectedIds.has(r.id));

  if (results.length === 0) {
    return <div className="empty-state">No results match the current filters.</div>;
  }

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th className="th-checkbox">
              <input
                type="checkbox"
                className="row-checkbox"
                checked={allSelected}
                ref={(el) => { if (el) el.indeterminate = someSelected && !allSelected; }}
                onChange={onToggleSelectAll}
                title={allSelected ? "Deselect all" : "Select all visible"}
              />
            </th>
            <th className="th-chevron" />
            {cols.map((col) => (
              <Th key={col.key} col={col} sort={sort} onSort={onSort} />
            ))}
            <th className="th-open" />
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <Row
              key={r.id}
              result={r}
              visibleCols={visibleCols}
              expanded={expandedId === r.id}
              onToggle={() => onToggle(r.id)}
              onOpen={() => onOpen(r)}
              copied={copied}
              setCopied={setCopied}
              selected={selectedIds.has(r.id)}
              onToggleSelect={() => onToggleSelect(r.id)}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
