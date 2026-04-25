import React from "react";
import { SubdomainResult } from "../types";
import CopyCell from "./CopyCell";
import DetailPanel from "./DetailPanel";
import * as I from "./Icons";

interface Props {
  result: SubdomainResult;
  visibleCols: string[];
  expanded: boolean;
  onToggle: () => void;
  onOpen: () => void;
  copied: string | null;
  setCopied: (v: string | null) => void;
}

function statusClass(s: number) {
  if (s >= 200 && s < 400) return "status-ok";
  if (s >= 400) return "status-err";
  return "status-off";
}

function statusLabel(s: number) {
  if (s === 0) return "—";
  return String(s);
}

function riskClass(r: number) {
  if (r >= 70) return "risk-high";
  if (r >= 40) return "risk-med";
  return "risk-low";
}

function sslClass(g: string) {
  if (g === "A+" || g === "A") return "ssl-a";
  if (g === "B") return "ssl-b";
  return "ssl-c";
}

export default function Row({
  result, visibleCols, expanded, onToggle, onOpen, copied, setCopied,
}: Props) {
  const cols = visibleCols;

  return (
    <>
      <tr className={`tr ${expanded ? "tr-expanded" : ""}`} onClick={onToggle}>
        <td className="td-chevron">
          <I.Chevron className={`chevron ${expanded ? "chevron-open" : ""}`} />
        </td>

        {cols.includes("sub") && (
          <td>
            <CopyCell text={result.fqdn} copied={copied} setCopied={setCopied}>
              {result.takeover && <I.Warn className="inline-warn" />}
              {result.fqdn}
            </CopyCell>
          </td>
        )}

        {cols.includes("status") && (
          <td>
            <span className={`status-badge ${statusClass(result.status)}`}>
              {statusLabel(result.status)}
            </span>
          </td>
        )}

        {cols.includes("ip") && (
          <td>
            {result.ip
              ? <CopyCell text={result.ip} copied={copied} setCopied={setCopied} />
              : <span className="muted">—</span>
            }
          </td>
        )}

        {cols.includes("host") && (
          <td>
            {result.host?.name
              ? <span className="host-name">{result.host.name}</span>
              : <span className="muted">—</span>
            }
          </td>
        )}

        {cols.includes("country") && (
          <td>
            {result.country?.country
              ? <span>{result.country.flag} {result.country.code}</span>
              : <span className="muted">—</span>
            }
          </td>
        )}

        {cols.includes("title") && (
          <td className="td-title">
            {result.title
              ? <span className="title-text">{result.title}</span>
              : <span className="muted">—</span>
            }
          </td>
        )}

        {cols.includes("techs") && (
          <td>
            <div className="tech-chips-inline">
              {result.techs.slice(0, 3).map((t) => (
                <span key={t.name} className={`tech-chip-sm ${t.outdated ? "tech-outdated" : ""}`}>
                  {t.name}
                </span>
              ))}
              {result.techs.length > 3 && (
                <span className="tech-chip-sm muted">+{result.techs.length - 3}</span>
              )}
            </div>
          </td>
        )}

        {cols.includes("ports") && (
          <td>
            {result.ports.length > 0
              ? <span className="muted">{result.ports.slice(0, 5).join(", ")}{result.ports.length > 5 ? "…" : ""}</span>
              : <span className="muted">—</span>
            }
          </td>
        )}

        {cols.includes("ssl") && (
          <td>
            {result.ssl
              ? <span className={`ssl-badge ${sslClass(result.ssl.grade)}`}>{result.ssl.grade}</span>
              : <span className="muted">—</span>
            }
          </td>
        )}

        {cols.includes("risk") && (
          <td>
            <span className={`risk-badge ${riskClass(result.risk)}`}>{result.risk}</span>
          </td>
        )}

        {cols.includes("source") && (
          <td>
            <span className="muted source-text">{result.source}</span>
          </td>
        )}

        <td className="td-open">
          <button
            className="open-btn"
            onClick={(e) => { e.stopPropagation(); onOpen(); }}
            title="Open detail"
          >
            <I.Globe />
          </button>
        </td>
      </tr>

      {expanded && (
        <tr className="tr-detail">
          <td colSpan={cols.length + 3}>
            <DetailPanel result={result} />
          </td>
        </tr>
      )}
    </>
  );
}
