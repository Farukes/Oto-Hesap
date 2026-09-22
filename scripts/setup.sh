#!/usr/bin/env bash
# Tek komutla yerel kurulum. Kullanım: ./scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# macOS iCloud senkronizasyon dizini kontrolü
if [[ "$OSTYPE" == "darwin"* ]]; then
  case "$PWD" in
    *"/Library/Mobile Documents/"*|*"/Mobile Documents/com~apple~CloudDocs"*)
      echo "✗ Depo macOS iCloud Drive altında senkronizasyon hatası verebilir ($PWD). ~/code altına taşımanız önerilir." >&2
      exit 1;;
  esac
fi

if [ -d "scripts/hooks" ]; then
  git config core.hooksPath scripts/hooks
  echo "✓ Git commit-msg hook aktif"
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "✓ .env oluşturuldu — DATABASE_URL ve anahtarları yapılandırın"
fi

if [ -f apps/api/pyproject.toml ]; then
  (cd apps/api && uv sync --all-extras --dev) && echo "✓ Python/API bağımlılıkları yüklendi"
fi

if [ -f apps/web/package.json ]; then
  (cd apps/web && { [ -f bun.lock ] || [ -f bun.lockb ]; } && bun install || npm install) && echo "✓ Web bağımlılıkları yüklendi"
fi

echo "Kurulum tamamlandı."
echo "API başlatmak için : cd apps/api && uv run uvicorn app.main:app --reload"
echo "Web başlatmak için : cd apps/web && bun dev (veya npm run dev)"
