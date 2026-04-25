import React from "react";

type P = React.SVGProps<SVGSVGElement>;

export const Search  = (p: P) => <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14" strokeLinecap="round"/></svg>;
export const Copy    = (p: P) => <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="1.4" {...p}><rect x="4" y="4" width="9" height="9" rx="1.5"/><path d="M3 11V3a1 1 0 0 1 1-1h7"/></svg>;
export const Check   = (p: P) => <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2" {...p}><path d="M3 8.5L6.5 12 13 4.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
export const Chevron = (p: P) => <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}><path d="M5 6.5L8 9.5 11 6.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
export const Close   = (p: P) => <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}><path d="M4 4l8 8M12 4l-8 8" strokeLinecap="round"/></svg>;
export const Download= (p: P) => <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.5" {...p}><path d="M8 2v8m0 0L5 7.5M8 10l3-2.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M2.5 12.5v1A1.5 1.5 0 0 0 4 15h8a1.5 1.5 0 0 0 1.5-1.5v-1" strokeLinecap="round"/></svg>;
export const Filter  = (p: P) => <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.5" {...p}><path d="M2 3h12M4 8h8M6 13h4" strokeLinecap="round"/></svg>;
export const Shield  = (p: P) => <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.5" {...p}><path d="M8 1.5l5.5 2v4.5c0 3.5-2.5 5.5-5.5 6.5-3-1-5.5-3-5.5-6.5V3.5z" strokeLinejoin="round"/></svg>;
export const Warn    = (p: P) => <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.5" {...p}><path d="M8 2L1.5 13.5h13L8 2z" strokeLinejoin="round"/><path d="M8 6.5v3.5M8 12v.01" strokeLinecap="round"/></svg>;
export const Dot     = (p: P) => <svg viewBox="0 0 8 8" width="8" height="8" {...p}><circle cx="4" cy="4" r="3" fill="currentColor"/></svg>;
export const Globe   = (p: P) => <svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.3" {...p}><circle cx="8" cy="8" r="6.5"/><path d="M8 1.5C6.2 3 5 5.4 5 8s1.2 5 3 6.5M8 1.5C9.8 3 11 5.4 11 8s-1.2 5-3 6.5M1.5 8h13" strokeLinecap="round"/></svg>;
export const Moon    = (p: P) => <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" {...p}><path d="M13.5 10A6 6 0 0 1 6 2.5a6 6 0 1 0 7.5 7.5z" strokeLinejoin="round"/></svg>;
export const Sun     = (p: P) => <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" {...p}><circle cx="8" cy="8" r="3"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M2.9 2.9l1.4 1.4M11.7 11.7l1.4 1.4M13.1 2.9l-1.4 1.4M4.3 11.7l-1.4 1.4" strokeLinecap="round"/></svg>;
export const Settings= (p: P) => <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" {...p}><circle cx="8" cy="8" r="2.5"/><path d="M8 1v1.5M8 13.5V15M1 8h1.5M13.5 8H15M2.6 2.6l1.1 1.1M12.3 12.3l1.1 1.1M13.4 2.6l-1.1 1.1M3.7 12.3l-1.1 1.1" strokeLinecap="round"/></svg>;
