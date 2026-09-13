#!/usr/bin/env bash
# GitHub tarafı ayarları. Bir kez, `gh auth login` sonrası, Murat çalıştırır.
# Kullanım: ./scripts/github-setup.sh   (ekip GitHub kullanıcı adlarını aşağıya yaz)
set -euo pipefail
REPO="muratcan-ates/Oto-Hesap"
TEAM=( )   # örn: ( "kutay-gh" "omer-gh" "yigit-gh" )  — kullanıcı adları gelince doldur

gh auth status >/dev/null 2>&1 || { echo "önce: gh auth login"; exit 1; }

echo "→ açıklama, konular, ayarlar"
gh repo edit "$REPO" \
  --description "OtoHesap — KOBİ'ler için yapay zekâ destekli finans + stok: Türkçe soruyla veriye erişim (Text-to-SQL), insan onaylı tedarik ajanı. Medeniyet Teknopark TeknoKampüs 2026." \
  --add-topic fastapi --add-topic nextjs --add-topic postgresql --add-topic text-to-sql --add-topic llm --add-topic kobi --add-topic fintech \
  --enable-issues --enable-wiki=false --delete-branch-on-merge --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false

echo "→ etiketler"
for l in "web:0E8A16" "api:1D76DB" "agent:5319E7" "data:FBCA04" "sunum:D93F0B" "bug:B60205" "demo-blocker:000000"; do
  gh label create "${l%%:*}" --color "${l##*:}" --repo "$REPO" --force >/dev/null && echo "  ${l%%:*}"
done

echo "→ main dal koruması (PR + CI yeşil + zorla push yok)"
gh api -X PUT "repos/$REPO/branches/main/protection" --input - >/dev/null <<'JSON'
{
  "required_status_checks": { "strict": true, "contexts": ["api (ruff + pytest)", "web (lint + build)"] },
  "enforce_admins": false,
  "required_pull_request_reviews": { "required_approving_review_count": 1, "dismiss_stale_reviews": true },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true
}
JSON
echo "  ok"

if [ ${#TEAM[@]} -gt 0 ]; then
  echo "→ ekip üyeleri (push yetkisi)"
  for u in "${TEAM[@]}"; do gh api -X PUT "repos/$REPO/collaborators/$u" -f permission=push >/dev/null && echo "  $u davet edildi"; done
else
  echo "! TEAM boş: ekip GitHub kullanıcı adlarını scripts/github-setup.sh içine yazıp tekrar çalıştır."
fi
echo "bitti: https://github.com/$REPO"
