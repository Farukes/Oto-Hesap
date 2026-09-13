// API'ye ulaşılamadığında (yalnız fetch ağ hatası) görünür. Gerçek API'de asla görünmez.
export function MockBadge() {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border border-warn/40 bg-warn-tint px-2.5 py-0.5 text-[11.5px] font-medium text-warn-ink"
      title="API'ye ulaşılamadı; lib/mocks altındaki örnek veri gösteriliyor."
    >
      <span className="size-1.5 rounded-full bg-warn" aria-hidden="true" />
      mock veri
    </span>
  );
}
