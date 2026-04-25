import React, { useEffect } from "react";
import { SubdomainResult, WhoisInfo } from "../types";
import DetailPanel from "./DetailPanel";
import * as I from "./Icons";

interface Props {
  result: SubdomainResult;
  whois: WhoisInfo | null;
  whoisLoading: boolean;
  onClose: () => void;
}

export default function DetailModal({ result, whois, whoisLoading, onClose }: Props) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  const url = result.status > 0 ? `https://${result.fqdn}` : null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="modal-title">{result.fqdn}</div>
            {url && (
              <a className="modal-link" href={url} target="_blank" rel="noopener noreferrer">
                <I.Globe /> {url}
              </a>
            )}
          </div>
          <button className="modal-close" onClick={onClose}><I.Close /></button>
        </div>

        <div className="modal-body">
          <DetailPanel result={result} />

          <section className="detail-section whois-section">
            <h4>WHOIS</h4>
            {whoisLoading && <span className="muted">Loading…</span>}
            {!whoisLoading && !whois && <span className="muted">No WHOIS data</span>}
            {whois && (
              <div className="whois-grid">
                {whois.registrar && <div className="kv"><span>Registrar</span><span>{whois.registrar}</span></div>}
                {whois.registered && <div className="kv"><span>Registered</span><span>{whois.registered}</span></div>}
                {whois.expires && <div className="kv"><span>Expires</span><span>{whois.expires}</span></div>}
                {whois.updated && <div className="kv"><span>Updated</span><span>{whois.updated}</span></div>}
                {whois.registrant && <div className="kv"><span>Registrant</span><span>{whois.registrant}</span></div>}
                {whois.nameservers?.length > 0 && (
                  <div className="kv">
                    <span>Nameservers</span>
                    <span>{whois.nameservers.join(", ")}</span>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
