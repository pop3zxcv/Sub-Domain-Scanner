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
  results, visibleCols, sort, onSort, expandedId, onToggle, onOpen, copied, setCopied,
}: Props) {
  const cols = ALL_COLUMNS.filter((c) => visibleCols.includes(c.key));

  if (results.length === 0) {
    return <div className="empty-state">No results match the current filters.</div>;
  }

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
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
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
