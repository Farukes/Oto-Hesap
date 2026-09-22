#!/usr/bin/env bash
# Demo öncesi tek komut: veriyi bilinen hale döndür, servisleri ısıt, kontrol listesini bas.
# Kullanım:  ./scripts/demo-reset.sh          (yerel)
#            API_URL=https://... ./scripts/demo-reset.sh   (canlı)
set -euo pipefail
cd "$(dirname "$0")/.."

API_URL="${API_URL:-http://localhost:8000}"
say() { printf "\n\033[1m%s\033[0m\n" "$1"; }

say "1 · Sentetik veri sıfırlanıyor (seed=42)"
uv run --project apps/api python data/seed.py --reset >/tmp/otohesap-seed.json
python3 - <<'PY'
import json
d = json.load(open("/tmp/otohesap-seed.json"))
print(f"  {d['sales_rows']} satış · {d['expense_rows']} gider · {d['products']} ürün")
print(f"  gelir {d['income']:,.2f} ₺ · gider {d['expense']:,.2f} ₺ · fark {d['net']:,.2f} ₺".replace(",", "."))
for c in d["critical"]:
    print(f"  kritik: {c['name']} {c['stock_qty']}/{c['reorder_point']} → {c['supplier']} ({c['channel']})")
print(f"  kâr lideri: {d['top_profit'][0]['name']} {d['top_profit'][0]['profit']:,.0f} ₺".replace(",", "."))
PY

say "2 · Açık siparişler temizleniyor"
DB=$(grep -E "^DATABASE_URL=" .env | head -1 | cut -d= -f2- | tr -d '"')
if [ -n "${DB:-}" ]; then
  N=$(psql "$DB" -tAc "DELETE FROM purchase_orders RETURNING 1" 2>/dev/null | wc -l | tr -d ' ')
  echo "  $N sipariş kaydı silindi (taslak/gönderilmiş)"
  psql "$DB" -tAc "DELETE FROM chat_log RETURNING 1" >/dev/null 2>&1 || true
  echo "  sohbet geçmişi temizlendi"
else
  echo "  DATABASE_URL okunamadı, atlandı"
fi

say "3 · Servisler ısıtılıyor ($API_URL)"
API_URL="$API_URL" ./scripts/warmup.sh || { echo "  ✗ ısınma başarısız — API ayakta mı? make api"; exit 1; }

say "4 · Demo öncesi kontrol listesi"
cat <<'EOF'
  [ ] Telefonda Telegram sohbeti açık, ses açık, şarj yeterli
  [ ] .env içinde NOTIFY_DRY_RUN=false (gerçek mesaj için)
  [ ] Tarayıcıda 4 sekme: /  /asistan  /tedarik  /stok
  [ ] Hotspot hazır (yedek internet için)
  [ ] Demo provası tamamlandı
EOF
echo
echo "  Hazır. Bol şans."
