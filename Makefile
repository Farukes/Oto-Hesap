# OtoHesap — günlük komutlar. `make help`
.PHONY: help setup api web seed test lint warmup eval doctor demo
help:
	@grep -E '^[a-z]+:.*#' Makefile | sed 's/:.*#/ — /'
setup:   # hook + .env + bağımlılıklar
	./scripts/setup.sh
api:     # FastAPI geliştirme sunucusu :8000
	cd apps/api && uv run uvicorn app.main:app --reload --port 8000
web:     # Next.js geliştirme sunucusu :3000
	cd apps/web && bun dev
seed:    # sentetik veriyi sıfırla ve yükle (DATABASE_URL .env'den)
	uv run --project apps/api python data/seed.py --reset
test:    # API testleri (ayrı test veritabanı)
	cd apps/api && TEST_DB_NAME=otohesap_test uv run pytest -q
lint:    # ruff + eslint
	cd apps/api && uv run ruff format --check . && uv run ruff check .
	cd apps/web && bun run lint
doctor:  # kurulum teşhisi: araçlar, .env, veritabanı, servisler
	./scripts/doctor.sh
demo:    # demo öncesi: veriyi sıfırla, siparişleri temizle, ısıt, kontrol listesi
	./scripts/demo-reset.sh
warmup:  # demodan 10 dk önce: API + DB + LLM ısındır
	./scripts/warmup.sh
eval:    # 15 soruluk bankayı gerçek sağlayıcıyla koş, gold SQL sonucuyla karşılaştır (LLM_PROVIDER .env'den)
	cd apps/api && uv run python eval.py
