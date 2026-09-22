#!/usr/bin/env bash
# OtoHesap kurulum teşhisi. Bir şey çalışmıyorsa önce bunu koş:  ./scripts/doctor.sh
# Hiçbir şeyi değiştirmez; yalnız bakar ve ne yapman gerektiğini söyler.
set -uo pipefail
cd "$(dirname "$0")/.."

OK=0; WARN=0; FAIL=0
ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; OK=$((OK+1)); }
warn() { printf "  \033[33m!\033[0m %s\n"  "$1"; WARN=$((WARN+1)); }
bad()  { printf "  \033[31m✗\033[0m %s\n"  "$1"; FAIL=$((FAIL+1)); }
head_() { printf "\n\033[1m%s\033[0m\n" "$1"; }

head_ "1 · Depo yeri"
case "$PWD" in
  *"/Library/Mobile Documents/"*|*"/Desktop/"*|*"/Documents/"*)
    bad "Depo iCloud'a senkron olabilecek bir klasörde: $PWD — ~/code altına taşı";;
  *) ok "Depo yeri uygun: $PWD";;
esac
[ "$(git config core.hooksPath 2>/dev/null)" = "scripts/hooks" ] \
  && ok "commit-msg hook aktif (yapay zeka imzası engelli)" \
  || warn "hook kapalı — çalıştır: git config core.hooksPath scripts/hooks"

head_ "2 · Araçlar"
for t in uv bun psql git; do
  if command -v "$t" >/dev/null 2>&1; then ok "$t: $(command -v "$t")"
  else
    case "$t" in
      uv)   bad "uv yok — kur: curl -LsSf https://astral.sh/uv/install.sh | sh";;
      bun)  bad "bun yok — kur: brew install oven-sh/bun/bun";;
      psql) warn "psql yok (Neon kullanıyorsan gerekmez) — brew install postgresql@16";;
      *)    bad "$t yok";;
    esac
  fi
done
PYV=$(command -v python3.12 >/dev/null 2>&1 && python3.12 --version 2>&1 || echo "yok")
[ "$PYV" = "yok" ] && warn "python3.12 yok (uv kendi indirir, sorun değil)" || ok "$PYV"

head_ "3 · .env"
if [ ! -f .env ]; then
  bad ".env yok — çalıştır: ./scripts/setup.sh"
else
  ok ".env var"
  get() { grep -E "^$1=" .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"'; }
  DB=$(get DATABASE_URL); RO=$(get DATABASE_URL_RO); PROV=$(get LLM_PROVIDER)
  [ -n "$DB" ] && ok "DATABASE_URL dolu (${DB%%:*}://…)" || bad "DATABASE_URL boş — Murat'ın Neon adresini yaz"
  [ -n "$RO" ] && ok "DATABASE_URL_RO dolu (asistan salt-okur)" || warn "DATABASE_URL_RO boş — asistan uygulama rolüyle okur"
  case "${PROV:-}" in
    fake|"") warn "LLM_PROVIDER=fake — demo çipleri önbellekten yanıtlar, serbest soru çalışmaz";;
    anthropic) [ -n "$(get ANTHROPIC_API_KEY)" ] && ok "LLM: anthropic (anahtar dolu)" || bad "LLM_PROVIDER=anthropic ama ANTHROPIC_API_KEY boş";;
    gemini)    [ -n "$(get GEMINI_API_KEY)"   ] && ok "LLM: gemini (anahtar dolu)"    || bad "LLM_PROVIDER=gemini ama GEMINI_API_KEY boş";;
    groq)      [ -n "$(get GROQ_API_KEY)"     ] && ok "LLM: groq (anahtar dolu)"      || bad "LLM_PROVIDER=groq ama GROQ_API_KEY boş";;
    ollama)    curl -s -m 2 "$(get OLLAMA_BASE_URL | sed 's|/v1$||')/api/tags" >/dev/null 2>&1 \
                 && ok "LLM: ollama (yerel sunucu yanıt veriyor)" || bad "LLM_PROVIDER=ollama ama yerel sunucu yok — çalıştır: ollama serve";;
    *) warn "LLM_PROVIDER tanınmıyor: $PROV";;
  esac
  [ -n "$(get TELEGRAM_BOT_TOKEN)" ] && ok "Telegram token dolu" || warn "TELEGRAM_BOT_TOKEN boş — mesaj simülasyon modunda gider"
  [ "$(get NOTIFY_DRY_RUN)" = "false" ] && ok "NOTIFY_DRY_RUN=false (gerçek mesaj)" || warn "NOTIFY_DRY_RUN=true — telefona mesaj DÜŞMEZ (demoda false yap)"
  git check-ignore -q .env && ok ".env git tarafından yok sayılıyor" || bad ".env izleniyor! Hemen: git rm --cached .env"
fi

head_ "4 · Veritabanı"
if [ -f .env ] && [ -n "${DB:-}" ]; then
  if psql "$DB" -c "SELECT 1" >/dev/null 2>&1; then
    ok "Veritabanına bağlanıldı"
    T=$(psql "$DB" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('suppliers','products','sales','expenses','purchase_orders','chat_log')" 2>/dev/null)
    [ "${T:-0}" = "6" ] && ok "Şema yüklü (6 tablo)" || bad "Şema eksik ($T/6) — çalıştır: psql \"\$DATABASE_URL\" -f docs/schema.sql"
    S=$(psql "$DB" -tAc "SELECT count(*) FROM sales" 2>/dev/null || echo 0)
    C=$(psql "$DB" -tAc "SELECT count(*) FROM products WHERE stock_qty <= reorder_point" 2>/dev/null || echo 0)
    if [ "${S:-0}" -gt 500 ]; then ok "Seed yüklü ($S satış)"; else bad "Seed yok ($S satış) — çalıştır: make seed"; fi
    [ "${C:-0}" = "2" ] && ok "Tam 2 kritik ürün (demo için doğru)" || warn "Kritik ürün sayısı $C (beklenen 2) — make seed ile sıfırla"
    O=$(psql "$DB" -tAc "SELECT count(*) FROM purchase_orders WHERE status IN ('draft','approved','sent')" 2>/dev/null || echo 0)
    [ "${O:-0}" = "0" ] && ok "Açık sipariş yok (demo temiz)" || warn "$O açık sipariş var — demodan önce: ./scripts/demo-reset.sh"
  else
    bad "Veritabanına bağlanılamadı: ${DB%%\?*}"
  fi
else
  warn "DATABASE_URL yok, veritabanı kontrolü atlandı"
fi

head_ "5 · Servisler"
API_URL="${API_URL:-http://localhost:8000}"
if curl -s -m 3 "$API_URL/api/health" >/dev/null 2>&1; then
  ok "API ayakta: $(curl -s -m 3 "$API_URL/api/health")"
else
  warn "API kapalı — çalıştır: make api"
fi
if curl -s -m 3 -o /dev/null "http://localhost:3000" 2>/dev/null; then ok "Web ayakta: http://localhost:3000"; else warn "Web kapalı — çalıştır: make web"; fi
for P in 8000 3000; do
  PID=$(lsof -ti tcp:$P 2>/dev/null | head -1)
  [ -n "$PID" ] && [ "$P" = 8000 ] && ok "8000 portu: pid $PID" || true
done

head_ "Özet"
printf "  %d iyi · %d uyarı · %d hata\n" "$OK" "$WARN" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  echo "  Önce yukarıdaki ✗ satırlarını çöz. Takılırsan gruba yaz: 'doctor çıktısı: …'"
  exit 1
fi
echo "  Sistem hazır."
