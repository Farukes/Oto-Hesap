# Specification Quality Checklist: OtoHesap MVP (Geliştirme Günü)

**Purpose**: Planlamaya geçmeden önce spec'in bütünlüğünü ve kalitesini doğrulamak
**Created**: 2026-09-13 (D16–D20 sonrası güncellendi)
**Feature**: [spec.md](../spec.md)

**Note**: Bu liste `/speckit-checklist` biçimindedir; maddeler spec.md, plan.md, contracts/api.md ve koda göre yazıldı.

## Content Quality

- [x] CHK001 Kullanıcı hikâyeleri teknolojiden bağımsız, işletme sahibinin diliyle yazıldı (endpoint adları yalnız FR'lerde parantez içinde izlenebilirlik için) [Spec §User Scenarios]
- [x] CHK002 Her hikâye "Why this priority" ve "Independent Test" taşıyor; P1'ler demo senaryosu adımlarına bağlı [Spec US1–US7]
- [x] CHK003 Tüm zorunlu bölümler dolu (User Scenarios, Edge Cases, Anahtar Kavramlar, Requirements, Key Entities, Success Criteria, Assumptions) [Spec]
- [x] CHK004 Kapsam dışı listesi AGENTS.md §2 ile birebir; D16–D20 ile gelen kapsam dışı maddeler (clarify, received/cancelled, 7/24 zamanlayıcı) eklendi [Spec §Kapsam Dışı]
- [x] CHK005 Metrik sözlüğü (D16) "Anahtar Kavramlar" olarak spec'te; "net kâr" ve "nakit akışı" ifadeleri yalnız "söylenmez" sütununda geçiyor [Spec §Anahtar Kavramlar]

## Requirement Completeness

- [x] CHK006 `[NEEDS CLARIFICATION]` işareti kalmadı; sözleşme ayrıntıları research.md R-17…R-24'te kodla hizalandı; tek açık tasarım kararı dönem birleştirme (R-17, T015) [Spec, Research]
- [x] CHK007 FR-001…FR-040 test edilebilir ve tek anlamlı; D16 (FR-034), D17 (FR-022, FR-029), D18 (FR-026), D19 (FR-012, FR-013), D20 (FR-020) karşılıkları var [Spec §Functional Requirements]
- [x] CHK008 Başarı ölçütleri ölçülebilir ve teknolojiden bağımsız (12/15 eval, 2 hatasız prova, < 2 sn pano, < 5 sn onay→telefon, %100 red, ürün başına ≤ 1 açık sipariş, "net kâr" 0 sonuç) [Spec SC-001…SC-012]
- [x] CHK009 Her hikâyenin Given/When/Then kabul senaryoları var; boş veri, LLM düşmesi, Telegram hatası (502), çift tıklama (409/indeks), saldırgan soru (CTE-DML, pg_sleep) senaryoları yazıldı [Spec §Acceptance Scenarios, §Edge Cases]
- [x] CHK010 Bağımlılıklar ve varsayımlar listelendi (soru bankası, ücretsiz katmanlar, sentetik veri, sabit seed aralığı, zamanlayıcı uyuması) [Spec §Assumptions]
- [x] CHK011 FR'ler AGENTS.md §6 sözleşmesi ve §7 güvenlik ilkeleriyle (11–12 dâhil) çelişmiyor; eklemeler research.md R-24'te gerekçeli [Spec, Research, Contracts]
- [ ] CHK012 Sözleşme eklemeleri (R-24) Murat tarafından AGENTS.md §6'ya PR ile işlendi [Gap, T090]
- [ ] CHK013 Çip sırası demo senaryosuyla aynı (ilk çip "En çok kazancım hangi üründen?") [Gap, T081]
- [ ] CHK014 Dönem tanımı summary / analytics / cashflow'da tek fonksiyona indirildi [Gap, T015, R-17]

## Feature Readiness

- [x] CHK015 Her FR'nin karşılığı bir kabul senaryosu veya uç durumda var (FR-001…FR-040 ↔ US1–US7 senaryoları) [Spec]
- [x] CHK016 Kullanıcı senaryoları demo senaryosunun 7 adımını eksiksiz kapsıyor (adım 1 US1, 2 US2, 3–4 US3, 5 US5/US2, 6 US4, 7 tampon) [Spec, docs/demo-senaryosu.md]
- [x] CHK017 Anayasa v1.1.0 ilkeleri (I–VII) plan.md "Constitution Check" tablosunda kanıtla eşlendi; ⚠ maddeleri açık görevlere bağlı (T013, T014, T078–T082, T091) [Plan]
- [x] CHK018 Veri modeli 6 tablo + görünüm, `notify_ref`, `ux_open_order_per_product`, sütun düzeyi grant ve durum makinesi `docs/schema.sql` / kodla birebir [Data Model]
- [x] CHK019 contracts/api.md alan adları kodla birebir (`product_name`, `supplier_name`, `notify`, `skipped`, `rows` nesne listesi, 409/502 metinleri); yapılacak alanlar (`model`) işaretli [Contracts, apps/api/app/schemas/*]
- [ ] CHK020 Seed hedefleri (tam 2 kritik, 1 eşiğin 1 üstünde, powerbank tek lider) Neon'da `make seed` çıktısıyla doğrulandı; soru bankası rakamları dolduruldu [Gap, T083, T084]
- [ ] CHK021 quickstart.md adımları temiz bir makinede baştan sona koşuldu (`make setup` → seed → api → web → test) [Gap, Quickstart]
- [ ] CHK022 Web tipleri (`lib/types.ts`) sözleşmeyle hizalandı; arayüz etiketleri D16'ya uygun ("net kâr" / "nakit akışı" araması 0) [Gap, T091, T092]

## Notes

- `[x]` = spec yazımında doğrulandı; `[ ]` = Geliştirme Günü'nde kapanacak boşluk (görev kimliği köşeli parantezde).
- CHK012–CHK014 Checkpoint 1–2 arasında; CHK020 11:00'de; CHK022 13:00'te; CHK021 yayın öncesi (19:00–20:00) kapanır.
