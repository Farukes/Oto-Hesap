import type { ReactNode } from "react";
import { EmptyState } from "./EmptyState";
import { Skeleton } from "./ui";

export interface Column<T> {
  key: string;
  header: ReactNode;
  align?: "left" | "right" | "center";
  className?: string;
  render: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string | number;
  loading?: boolean;
  error?: string;
  rowClassName?: (row: T) => string;
  empty?: { title: string; description?: string; action?: ReactNode };
  dense?: boolean;
  caption?: string;
}

/* Not: yeniden yüklerken gövde ESKİDEN opacity-60 ile soluyordu — ikincil metin
   beyaz üstünde 2.8:1'e düşüyordu. Artık metin tam kontrastta kalır, yükleme
   durumu aria-busy + ekran okuyucu bildirimiyle duyurulur. */

const ALIGN = { left: "text-left", right: "text-right", center: "text-center" } as const;

export function DataTable<T>({ columns, rows, rowKey, loading = false, error, rowClassName, empty, dense = false, caption }: DataTableProps<T>) {
  const cell = dense ? "px-3 py-2" : "px-4 py-2.5";
  const showSkeleton = loading && rows.length === 0;

  return (
    <div className="overflow-x-auto">
      {loading && rows.length > 0 && (
        <p role="status" className="sr-only">
          {caption ?? "Tablo"} yenileniyor…
        </p>
      )}
      <table aria-busy={loading || undefined} className="w-full min-w-[560px] border-collapse text-[13.5px]">
        {caption && <caption className="sr-only">{caption}</caption>}
        <thead>
          <tr className="border-b border-line bg-surface-2 text-[12px] font-medium uppercase tracking-wide text-muted">
            {columns.map((c) => (
              <th key={c.key} scope="col" className={`${cell} whitespace-nowrap ${ALIGN[c.align ?? "left"]} ${c.className ?? ""}`}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {showSkeleton &&
            Array.from({ length: 5 }).map((_, i) => (
              <tr key={`sk-${i}`} className="border-b border-line/70">
                {columns.map((c) => (
                  <td key={c.key} className={cell}>
                    <Skeleton className="h-4 w-full max-w-40" />
                  </td>
                ))}
              </tr>
            ))}
          {!showSkeleton && error && (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8">
                <EmptyState tone="danger" title="Veri alınamadı" description={error} />
              </td>
            </tr>
          )}
          {!showSkeleton && !error && rows.length === 0 && (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8">
                <EmptyState title={empty?.title ?? "Kayıt yok"} description={empty?.description} action={empty?.action} />
              </td>
            </tr>
          )}
          {!showSkeleton &&
            !error &&
            rows.map((row) => (
              <tr key={rowKey(row)} className={`border-b border-line/70 last:border-b-0 hover:bg-surface-2/70 ${rowClassName?.(row) ?? ""}`}>
                {columns.map((c) => (
                  <td key={c.key} className={`${cell} align-middle ${ALIGN[c.align ?? "left"]} ${c.className ?? ""}`}>
                    {c.render(row)}
                  </td>
                ))}
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}
