#!/usr/bin/env bash
# Tek komutla yerel kurulum. Kullanım: ./scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

case "$PWD" in
  *"/Library/Mobile Documents/"*|*"/Desktop/"*|*"/Documents/"*)
    echo "✗ Depo iCloud'a senkron olabilecek bir klasörde ($PWD). ~/code altına taşı." >&2; exit 1;;
esac

git config core.hooksPath scripts/hooks
echo "✓ commit-msg hook aktif (AI imzası engeli)"

if [ ! -f .env ]; then cp .env.example .env; echo "✓ .env oluşturuldu — DATABASE_URL ve anahtarları doldur"; fi

if [ -f apps/api/pyproject.toml ]; then
  (cd apps/api && uv sync --all-extras --dev) && echo "✓ api bağımlılıkları"
fi
if [ -f apps/web/package.json ]; then
  (cd apps/web && { [ -f bun.lock ] || [ -f bun.lockb ]; } && bun install || npm install) && echo "✓ web bağımlılıkları"
fi
echo "Hazır. api: cd apps/api && uv run uvicorn app.main:app --reload   |   web: cd apps/web && bun dev"
