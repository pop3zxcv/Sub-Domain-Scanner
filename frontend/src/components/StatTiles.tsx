import React from "react";
import { SubdomainResult } from "../types";

interface Props {
  results: SubdomainResult[];
}

export default function StatTiles({ results }: Props) {
  const live      = results.filter((r) => r.status >= 200 && r.status < 400).length;
  const offline   = results.filter((r) => r.status === 0).length;
  const errors    = results.filter((r) => r.status >= 400).length;
  const highRisk  = results.filter((r) => r.risk >= 50).length;
  const takeovers = results.filter((r) => r.takeover).length;

  const tiles = [
    { label: "Total found",      value: results.length, accent: "var(--accent)" },
    { label: "Live (2xx/3xx)",   value: live,           accent: "var(--ok-fg)" },
    { label: "Errors (4xx/5xx)", value: errors,         accent: "#B23A1F" },
    { label: "Offline / none",   value: offline,        accent: "var(--gray-500)" },
    { label: "High risk (≥50)",  value: highRisk,       accent: "#A66A00" },
    { label: "Takeover risks",   value: takeovers,      accent: "var(--bad-fg)" },
  ];

  return (
    <div className="tiles">
      {tiles.map((t) => (
        <div key={t.label} className="tile">
          <div className="tile-val" style={{ color: t.accent }}>
            {t.value}
          </div>
          <div className="tile-label">{t.label}</div>
        </div>
      ))}
    </div>
  );
}
