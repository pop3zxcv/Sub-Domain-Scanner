import React from "react";
import { SubdomainResult } from "../types";
import * as I from "./Icons";

interface Props {
  result: SubdomainResult;
}

function RiskBar({ score }: { score: number }) {
  const color = score >= 70 ? "var(--bad-fg)" : score >= 40 ? "#A66A00" : "var(--ok-fg)";
  return (
    <div className="risk-bar-wrap">
      <div className="risk-bar-track">
        <div className="risk-bar-fill" style={{ width: `${score}%`, background: color }} />
      </div>
      <span className="risk-bar-label" style={{ color }}>{score}</span>
    </div>
  );
}

export default function DetailPanel({ result }: Props) {
  const { dns, ssl, ports, techs, risk, takeover, takeoverNote, host, country, ip } = result;

  return (
    <div className="detail-panel">
      <div className="detail-grid">
        <section className="detail-section">
          <h4>Risk Assessment</h4>
          <RiskBar score={risk} />
          {takeover && (
            <div className="takeover-badge">
              <I.Warn /> Takeover risk{takeoverNote ? `: ${takeoverNote}` : ""}
            </div>
          )}
        </section>

        <section className="detail-section detail-section-dns">
          <h4>DNS Records</h4>
          {(["A","AAAA","CNAME","MX","TXT","NS"] as const).map((type) => {
            const vals = dns[type];
            if (!vals?.length) return null;
            const full = vals.join(", ");
            return (
              <div key={type} className="dns-row">
                <span className="dns-type">{type}</span>
                <span className="dns-vals" title={full}>{full}</span>
              </div>
            );
          })}
          {!Object.values(dns).some((v) => v?.length) && <span className="muted">No records</span>}
        </section>

        <section className="detail-section">
          <h4>Network</h4>
          {ip && <div className="kv"><span>IPv4</span><code>{ip}</code></div>}
          {result.ipv6 && <div className="kv"><span>IPv6</span><code>{result.ipv6}</code></div>}
          {host?.name && <div className="kv"><span>Hosting</span><span>{host.name}</span></div>}
          {country?.country && (
            <div className="kv">
              <span>Country</span>
              <span>{country.flag} {country.country}</span>
            </div>
          )}
        </section>

        <section className="detail-section">
          <h4>TLS / SSL</h4>
          {ssl ? (
            <>
              <div className="kv"><span>Grade</span><span className="ssl-grade">{ssl.grade}</span></div>
              <div className="kv"><span>Issuer</span><span>{ssl.issuer}</span></div>
              <div className="kv"><span>Expires</span><span>{ssl.expires}</span></div>
            </>
          ) : (
            <span className="muted">No SSL info</span>
          )}
        </section>

        {ports.length > 0 && (
          <section className="detail-section">
            <h4>Open Ports</h4>
            <div className="ports-wrap">
              {ports.map((p) => (
                <span key={p} className="port-chip">{p}</span>
              ))}
            </div>
          </section>
        )}

        {techs.length > 0 && (
          <section className="detail-section">
            <h4>Tech Stack</h4>
            <div className="tech-wrap">
              {techs.map((t) => (
                <span key={t.name} className={`tech-chip ${t.outdated ? "tech-outdated" : ""}`}>
                  {t.name}{t.v ? ` ${t.v}` : ""}
                </span>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
