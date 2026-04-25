export interface TechInfo {
  name: string;
  cat: string;
  v: string;
  outdated: boolean;
}

export interface HostInfo {
  name: string;
  asn: string;
  color: string;
}

export interface CountryInfo {
  country: string;
  code: string;
  flag: string;
}

export interface SSLInfo {
  issuer: string;
  subject: string;
  expires: string;
  grade: string;
}

export interface DNSRecords {
  A: string[];
  AAAA: string[];
  CNAME: string[];
  MX: string[];
  TXT: string[];
  NS: string[];
}

export interface SubdomainResult {
  id: number;
  fqdn: string;
  sub: string;
  domain: string;
  status: number;
  title: string;
  ip: string;
  ipv6: string;
  host: HostInfo;
  country: CountryInfo;
  techs: TechInfo[];
  ports: number[];
  ssl: SSLInfo | null;
  risk: number;
  takeover: boolean;
  takeoverNote: string | null;
  source: string;
  lastSeen: number;
  dns: DNSRecords;
}

export interface WhoisInfo {
  domain: string;
  registrar: string;
  registered: string;
  expires: string;
  updated: string;
  nameservers: string[];
  status: string[];
  registrant?: string;
}

export interface SortState {
  key: string;
  dir: "asc" | "desc";
}

export interface FilterState {
  q: string;
  status: "all" | "live" | "error" | "offline";
  country: string;
  tech: string;
  takeoverOnly: boolean;
}

export const DEFAULT_FILTERS: FilterState = {
  q: "",
  status: "all",
  country: "all",
  tech: "all",
  takeoverOnly: false,
};

export const ALL_COLUMNS = [
  { key: "sub",     label: "Subdomain" },
  { key: "status",  label: "Status" },
  { key: "ip",      label: "IP Address" },
  { key: "host",    label: "Hosting" },
  { key: "country", label: "Country" },
  { key: "title",   label: "Page Title" },
  { key: "techs",   label: "Tech Stack" },
  { key: "ports",   label: "Open Ports" },
  { key: "ssl",     label: "SSL Grade" },
  { key: "risk",    label: "Risk Score" },
  { key: "source",  label: "Source" },
];

export const DEFAULT_COLUMNS = ALL_COLUMNS.map((c) => c.key);
