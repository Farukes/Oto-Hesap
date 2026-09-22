#!/usr/bin/env bash
# GitHub repository ayarları (etiketler, koruma kuralları vb.)
# Kullanım: ./scripts/github-setup.sh [kullanici/repo]
set -euo pipefail

REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")}"

if [ -z "$REPO" ]; then
  echo "Hata: Hedef repo belirlenemedi. Kullanım: ./scripts/github-setup.sh <kullanici/repo>" >&2
  exit 1
fi

gh auth status >/dev/null 2>&1 || { echo "Önce 'gh auth login' ile giriş yapın."; exit 1; }

echo "→ Açıklama, konular ve ayarlar yapılandırılıyor: $REPO"
gh repo edit "$REPO" \
  --description "OtoHesap — KOBİ'ler için yapay zekâ destekli finans ve stok yönetim platformu. Doğal dilde Text-to-SQL analitiği ve otonom tedarik ajanı." \
  --add-topic fastapi --add-topic nextjs --add-topic postgresql --add-topic text-to-sql --add-topic llm --add-topic kobi --add-topic fintech \
  --enable-issues --enable-wiki=false --delete-branch-on-merge --enable-squash-merge

echo "→ Etiketler oluşturuluyor"
for l in "web:0E8A16" "api:1D76DB" "agent:5319E7" "data:FBCA04" "sunum:D93F0B" "bug:B60205"; do
  gh label create "${l%%:*}" --color "${l##*:}" --repo "$REPO" --force >/dev/null 2>&1 || true
done

echo "Tamamlandı: https://github.com/$REPO"
