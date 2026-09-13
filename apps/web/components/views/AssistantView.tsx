"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { ChatBubble, type ChatMessage } from "../ChatBubble";
import { IconLock, IconSend } from "../Icons";
import { Button, Input, Skeleton } from "../ui";
import { askAssistant, errorMessage, errorStatus, getSuggestions } from "@/lib/api";
import { useAsync } from "@/lib/use-async";

export function AssistantView() {
  const suggestions = useAsync(() => getSuggestions());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end", behavior: "smooth" });
  }, [messages.length]);

  async function ask(question: string) {
    const q = question.trim();
    if (!q || busy) return;
    const stamp = Date.now();
    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { id: `u-${stamp}`, role: "user", text: q }, { id: `p-${stamp}`, role: "assistant", pending: true }]);
    try {
      const answer = await askAssistant(q);
      setMessages((m) => m.map((x) => (x.id === `p-${stamp}` ? { id: `a-${stamp}`, role: "assistant", answer } : x)));
    } catch (err) {
      setMessages((m) => m.map((x) => (x.id === `p-${stamp}` ? { id: `e-${stamp}`, role: "assistant", error: errorMessage(err), status: errorStatus(err) } : x)));
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    void ask(input);
  }

  return (
    <div className="mx-auto flex h-[calc(100dvh-8.5rem)] max-w-4xl flex-col md:h-[calc(100dvh-9.5rem)]">
      <div className="mb-3 flex items-start gap-2.5 rounded-card border border-line bg-surface px-4 py-3 text-[13.5px] text-muted">
        <IconLock size={18} className="mt-0.5 shrink-0 text-brand-strong" />
        <p>
          Asistan verinizi <span className="font-medium text-navy">yalnız okur</span>; her yanıtta kullanılan sorgu gösterilir. Sorular Türkçe yazılır,
          yanıt gerçek veriden gelir; sayı uydurulmaz.
        </p>
      </div>

      <div className="mb-3 flex flex-wrap gap-2" aria-label="Hazır sorular">
        {suggestions.loading && !suggestions.data
          ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-8 w-44 rounded-full" />)
          : (suggestions.data ?? []).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => void ask(s)}
                disabled={busy}
                className="rounded-full border border-brand/40 bg-brand-tint px-3.5 py-1.5 text-[13px] font-medium text-brand-ink transition-colors hover:bg-brand/20 disabled:opacity-60"
              >
                {s}
              </button>
            ))}
        {suggestions.error && <span className="text-[12.5px] text-muted">Hazır sorular alınamadı: {suggestions.error}</span>}
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto rounded-card border border-line bg-surface-2 p-4" aria-live="polite">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-3 flex size-12 items-center justify-center rounded-full bg-mint text-brand-strong">
              <IconSend size={22} />
            </div>
            <div className="text-[15px] font-semibold text-navy">Verinize soru sorun</div>
            <p className="mt-1 max-w-sm text-[13px] text-muted">Yukarıdaki hazır sorulardan birine tıklayın ya da kendi sorunuzu yazın. Örnek: &quot;Geçen ay kaç satış yaptım?&quot;</p>
          </div>
        ) : (
          messages.map((m) => <ChatBubble key={m.id} message={m} />)
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={submit} className="mt-3 flex gap-2">
        <Input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              void ask(input);
            }
          }}
          placeholder="Sorunuzu yazın ve Enter'a basın"
          aria-label="Soru"
          maxLength={500}
          disabled={busy}
          autoComplete="off"
        />
        <Button type="submit" variant="primary" busy={busy} disabled={!input.trim()} icon={<IconSend size={16} />}>
          Gönder
        </Button>
      </form>
    </div>
  );
}
