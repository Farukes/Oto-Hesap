#!/usr/bin/env bash
# OtoHesap ısıtma betiği.
# Render 15 dk boşta uyur, Neon sıfıra iner; demodan 10 dk önce koş:
#   API_URL=https://<render-adresi> ./scripts/warmup.sh
# Adımlar: /api/health → /api/summary → /api/assistant/suggestions → ilk öneriyle /api/assistant/ask
# Her adımda durum kodu ve süre basılır; biri başarısızsa çıkış kodu 1.

set -u

API_URL="${API_URL:-http://localhost:8000}"
API_URL="${API_URL%/}"
BODY="$(mktemp)"
trap 'rm -f "$BODY"' EXIT
FAIL=0

# step <ad> <yöntem> <yol> [json]  → BODY dosyasına gövdeyi yazar, durum/süre basar
step() {
  local name="$1" method="$2" path="$3" data="${4:-}"
  local out code secs
  if [ "$method" = "POST" ]; then
    out=$(curl -sS -o "$BODY" -w '%{http_code} %{time_total}' --max-time 90 \
          -X POST -H 'Content-Type: application/json' --data "$data" "$API_URL$path" 2>/dev/null) \
      || out="000 0"
  else
    out=$(curl -sS -o "$BODY" -w '%{http_code} %{time_total}' --max-time 90 "$API_URL$path" 2>/dev/null) \
      || out="000 0"
  fi
  code="${out%% *}"
  secs="${out##* }"
  if [ "$code" = "200" ]; then
    printf '  OK   %-32s %s  %ss\n' "$name" "$code" "$secs"
  else
    printf '  HATA %-32s %s  %ss\n' "$name" "$code" "$secs"
    FAIL=1
  fi
}

first_suggestion() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; d=json.load(sys.stdin); print(d[0] if d else "")' < "$BODY" 2>/dev/null
  else
    sed -E 's/^\["([^"]*)".*/\1/' "$BODY"
  fi
}

echo "OtoHesap ısıtma → $API_URL"
step "GET /api/health" GET "/api/health"
step "GET /api/summary" GET "/api/summary"
step "GET /api/assistant/suggestions" GET "/api/assistant/suggestions"

QUESTION="$(first_suggestion)"
[ -n "$QUESTION" ] || QUESTION="Bu ay toplam giderim ne kadar?"
if command -v python3 >/dev/null 2>&1; then
  PAYLOAD=$(python3 -c 'import json,sys; print(json.dumps({"question": sys.argv[1]}, ensure_ascii=False))' "$QUESTION")
else
  PAYLOAD="{\"question\": \"$QUESTION\"}"
fi
step "POST /api/assistant/ask" POST "/api/assistant/ask" "$PAYLOAD"
if [ "$FAIL" = "0" ]; then
  echo "  soru: $QUESTION"
  head -c 300 "$BODY"; echo
  echo "Isınma tamam; demo hazır."
else
  echo "Isınma BAŞARISIZ; loglara bak (Render → Logs, Neon → Monitoring)."
fi
exit "$FAIL"
