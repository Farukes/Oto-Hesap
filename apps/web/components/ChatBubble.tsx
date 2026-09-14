"use client";

import type { ReactNode } from "react";
import { Badge } from "./Badge";
import { IconAlert, IconLock } from "./Icons";
import { SqlBlock } from "./SqlBlock";
import { Spinner } from "./ui";
import { formatCell, formatTime, sourceLabel } from "@/lib/format";
import type { AssistantAnswer, AssistantRow } from "@/lib/types";

const MAX_ROWS = 20;

export type ChatMessage =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; answer: AssistantAnswer }
  | { id: string; role: "assistant"; error: string; status: number | null }
  | { id: string; role: "assistant"; pending: true };

function Bubble({ role, children, tone = "default" }: { role: "user" | "assistant"; children: ReactNode; tone?: "default" | "warn" | "danger" }) {
  const isUser = role === "user";
  const shell = isUser
    ? "bg-navy text-white rounded-br-md"
    : tone === "danger"
      ? "bg-danger-tint text-danger-ink border border-danger/30 rounded-bl-md"
      : tone === "warn"
        ? "bg-warn-tint text-warn-ink border border-warn/40 rounded-bl-md"
        : "bg-surface text-ink border border-line rounded-bl-md";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[92%] rounded-2xl px-4 py-3 text-[14px] leading-relaxed md:max-w-[80%] ${shell}`}>{children}</div>
    </div>
  );
}

function cellValue(row: AssistantRow, column: string, index: number): unknown {
  if (Array.isArray(row)) return row[index];
  return row[column];
}

function ResultTable({ columns, rows }: { columns: string[]; rows: AssistantRow[] }) {
  if (!columns.length || !rows.length) return null;
  const shown = rows.slice(0, MAX_ROWS);
  return (
    <div className="mt-3 overflow-x-auto rounded-lg border border-line">
      <table className="w-full border-collapse text-[13px]">
        <caption className="sr-only">Sorgu sonucu tablosu: {columns.join(", ")}</caption>
        <thead>
          <tr className="bg-surface-2 text-left text-[11.5px] font-medium uppercase tracking-wide text-muted">
            {columns.map((c) => (
              <th key={c} scope="col" className="whitespace-nowrap px-3 py-1.5">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {shown.map((row, i) => (
            <tr key={i} className="border-t border-line/70">
              {columns.map((c, j) => {
                const v = cellValue(row, c, j);
                return (
                  <td key={c} className={`whitespace-nowrap px-3 py-1.5 ${typeof v === "number" ? "text-right tabular-nums" : ""}`}>
                    {formatCell(v, c)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > MAX_ROWS && (
        <div className="border-t border-line bg-surface-2 px-3 py-1.5 text-[12px] text-muted">
          İlk {MAX_ROWS} satır gösteriliyor · toplam {rows.length} satır
        </div>
      )}
    </div>
  );
}

export function ChatBubble({ message }: { message: ChatMessage }) {
  if (message.role === "user") return <Bubble role="user">{message.text}</Bubble>;

  if ("pending" in message) {
    return (
      <Bubble role="assistant">
        <div className="flex items-center gap-2 text-muted">
          <Spinner className="size-4" />
          Sorgu hazırlanıyor ve veritabanında çalıştırılıyor…
        </div>
      </Bubble>
    );
  }

  if ("error" in message) {
    const calm = message.status === 400 || message.status === 422 || message.status === 503;
    return (
      <Bubble role="assistant" tone={calm ? "warn" : "danger"}>
        <div className="flex items-start gap-2">
          {message.status === 400 ? <IconLock size={18} className="mt-0.5 shrink-0" /> : <IconAlert size={18} className="mt-0.5 shrink-0" />}
          <div>
            <div>{message.error}</div>
            {message.status === 503 && <div className="mt-1 text-[12.5px] opacity-80">Hazır sorulardan birini deneyebilirsiniz.</div>}
          </div>
        </div>
      </Bubble>
    );
  }

  const a = message.answer;
  const ok = a.ok !== false;
  const meta = [
    a.sources?.length ? `Kaynak: ${a.sources.map(sourceLabel).join(", ")}` : null,
    formatTime(a.asked_at),
    a.model || null,
  ].filter(Boolean);

  return (
    <Bubble role="assistant" tone={ok ? "default" : "warn"}>
      <p className="whitespace-pre-wrap">{a.answer || (ok ? "Bu soru için kayıt bulunamadı." : "Bu soruyu bu veriyle yanıtlayamadım.")}</p>
      {ok && <ResultTable columns={a.columns ?? []} rows={a.rows ?? []} />}
      {a.sql ? <SqlBlock sql={a.sql} /> : null}
      {meta.length > 0 && (
        <div className="mt-2.5 flex flex-wrap items-center gap-x-1.5 gap-y-1 text-[12px] text-muted">
          <span>{meta.join(" · ")}</span>
          {a.cached && (
            <Badge tone="neutral" title="SQL soru bankasından geldi; LLM'e gidilmedi.">
              önbellek
            </Badge>
          )}
        </div>
      )}
    </Bubble>
  );
}
