// tr-TR para/tarih biçimleri; saat dilimi Europe/Istanbul.

const TZ = "Europe/Istanbul";

const moneyFmt = new Intl.NumberFormat("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const intFmt = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 0 });
const compactFmt = new Intl.NumberFormat("tr-TR", { notation: "compact", maximumFractionDigits: 1 });
const percentFmt = new Intl.NumberFormat("tr-TR", { style: "percent", maximumFractionDigits: 1 });

export function formatMoney(value: number | string | null | undefined): string {
  const n = toNumber(value);
  if (n === null) return "—";
  return `${moneyFmt.format(n)} ₺`;
}

export function formatMoneyCompact(value: number | null | undefined): string {
  const n = toNumber(value);
  if (n === null) return "—";
  return `${compactFmt.format(n)} ₺`;
}

export function formatInt(value: number | null | undefined): string {
  const n = toNumber(value);
  return n === null ? "—" : intFmt.format(n);
}

/** share 0–1 aralığında beklenir (0–100 gelirse normalize edilir). */
export function formatShare(share: number): string {
  return percentFmt.format(share > 1 ? share / 100 : share);
}

export function toNumber(value: unknown): number | null {
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  if (typeof value === "string" && value.trim() !== "") {
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

function parseDate(iso: string | null | undefined): Date | null {
  if (!iso) return null;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? null : d;
}

export function formatTime(iso: string | null | undefined): string {
  const d = parseDate(iso);
  if (!d) return "—";
  return new Intl.DateTimeFormat("tr-TR", { hour: "2-digit", minute: "2-digit", timeZone: TZ }).format(d);
}

export function formatDate(iso: string | null | undefined): string {
  const d = parseDate(iso);
  if (!d) return "—";
  return new Intl.DateTimeFormat("tr-TR", { day: "2-digit", month: "short", year: "numeric", timeZone: TZ }).format(d);
}

/** "13 Eyl 10:12" */
export function formatDateTime(iso: string | null | undefined): string {
  const d = parseDate(iso);
  if (!d) return "—";
  const date = new Intl.DateTimeFormat("tr-TR", { day: "2-digit", month: "short", timeZone: TZ }).format(d);
  const time = new Intl.DateTimeFormat("tr-TR", { hour: "2-digit", minute: "2-digit", timeZone: TZ }).format(d);
  return `${date} ${time}`;
}

/** "2026-04" veya ISO tarih → "Nis" */
export function formatMonthShort(month: string): string {
  const key = monthKey(month);
  if (!key) return month;
  const [y, m] = key.split("-").map(Number);
  return new Intl.DateTimeFormat("tr-TR", { month: "short", timeZone: "UTC" }).format(new Date(Date.UTC(y, m - 1, 1)));
}

/** "2026-04" veya ISO tarih → "Nisan 2026" */
export function formatMonthLong(month: string): string {
  const key = monthKey(month);
  if (!key) return month;
  const [y, m] = key.split("-").map(Number);
  return new Intl.DateTimeFormat("tr-TR", { month: "long", year: "numeric", timeZone: "UTC" }).format(new Date(Date.UTC(y, m - 1, 1)));
}

/** Her türlü ay gösterimini "YYYY-MM" anahtarına indirger. */
export function monthKey(value: string): string | null {
  const m = /^(\d{4})-(\d{2})/.exec(value);
  return m ? `${m[1]}-${m[2]}` : null;
}

/** ISO → <input type="date"> değeri (İstanbul günü). Boşsa bugün. */
export function toDateInputValue(iso?: string | null, now?: Date): string {
  const d = parseDate(iso) ?? now ?? new Date();
  const parts = new Intl.DateTimeFormat("en-CA", { year: "numeric", month: "2-digit", day: "2-digit", timeZone: TZ }).formatToParts(d);
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? "";
  return `${get("year")}-${get("month")}-${get("day")}`;
}

/** <input type="date"> değeri → ISO 8601 UTC (İstanbul saatiyle 12:00; Türkiye'de yaz saati yok, sabit +03:00). */
export function fromDateInputValue(ymd: string): string {
  return new Date(`${ymd}T12:00:00+03:00`).toISOString();
}

const CATEGORY_LABELS: Record<string, string> = {
  kira: "Kira",
  maas: "Maaş",
  elektrik: "Elektrik",
  kargo: "Kargo",
  reklam: "Reklam",
  tedarik: "Tedarik",
};

export function categoryLabel(category: string): string {
  if (!category) return "—";
  return CATEGORY_LABELS[category] ?? category.charAt(0).toLocaleUpperCase("tr-TR") + category.slice(1);
}

export function channelLabel(channel: string): string {
  if (channel === "online") return "Online";
  if (channel === "magaza") return "Mağaza";
  return channel;
}

const SOURCE_LABELS: Record<string, string> = {
  sales: "satışlar",
  expenses: "giderler",
  products: "ürünler",
  suppliers: "tedarikçiler",
  purchase_orders: "siparişler",
  chat_log: "sohbet kaydı",
  v_monthly_cashflow: "aylık nakit akışı",
};

export function sourceLabel(source: string): string {
  return SOURCE_LABELS[source] ?? source;
}

const MONEY_COLUMN = /(kar|gelir|gider|tutar|toplam|fiyat|maliyet|ciro|fark|net|amount|total|revenue|profit|income|expense|price|cost)/i;

/** Sütun adı para çağrıştırıyorsa (kar, gelir, tutar, total…) sayı 2 ondalıkla yazılır. */
export function isMoneyColumn(column: string): boolean {
  return MONEY_COLUMN.test(column);
}

/** Asistan tablo hücresi: sayı → tr-TR, null → "—". */
export function formatCell(value: unknown, column = ""): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return Number.isInteger(value) && !isMoneyColumn(column) ? intFmt.format(value) : moneyFmt.format(value);
  if (typeof value === "boolean") return value ? "Evet" : "Hayır";
  if (typeof value === "string") {
    if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(value)) return formatDateTime(value);
    return value;
  }
  return JSON.stringify(value);
}
