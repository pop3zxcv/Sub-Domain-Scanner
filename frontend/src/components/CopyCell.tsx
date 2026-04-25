import React, { useCallback } from "react";
import * as I from "./Icons";

interface Props {
  text: string;
  children?: React.ReactNode;
  copied: string | null;
  setCopied: (v: string | null) => void;
}

export default function CopyCell({ text, children, copied, setCopied }: Props) {
  const isCopied = copied === text;

  const handle = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      navigator.clipboard?.writeText(text).catch(() => {});
      setCopied(text);
      setTimeout(() => setCopied(null), 1100);
    },
    [text, setCopied]
  );

  return (
    <button
      className={`copy-cell ${isCopied ? "copy-cell-on" : ""}`}
      onClick={handle}
      title={`Copy "${text}"`}
    >
      <span className="copy-cell-text">{children ?? text}</span>
      <span className="copy-cell-icon">
        {isCopied ? <I.Check /> : <I.Copy />}
      </span>
    </button>
  );
}
