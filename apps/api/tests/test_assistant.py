"""POST /api/assistant/ask ve GET /api/assistant/suggestions — fake sağlayıcıyla uçtan uca."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import select

from app.models import ChatLog
from app.services import llm, text2sql
from app.services.llm import LLMError

PROFIT_SQL = (
    "SELECT p.name AS urun, SUM(s.qty * (s.unit_price - p.unit_cost)) AS kar "
    "FROM sales s JOIN products p ON p.id = s.product_id GROUP BY p.name ORDER BY kar DESC"
)


class Recorder:
    """fake sağlayıcı: 'SORU:' → sıradaki SQL yanıtı, 'ÖZET:' → özet metni."""

    def __init__(self, sql_responses: list[str | Exception], summary: str | Exception):
        self.sql_responses = sql_responses
        self.summary = summary
        self.sql_calls: list[str] = []
        self.summary_calls: list[str] = []

    def __call__(self, system: str, user: str) -> str:
        if user.startswith("ÖZET:"):
            self.summary_calls.append(user)
            if isinstance(self.summary, Exception):
                raise self.summary
            return self.summary
        assert user.startswith("SORU: "), user[:40]
        self.sql_calls.append(user)
        idx = min(len(self.sql_calls) - 1, len(self.sql_responses) - 1)
        response = self.sql_responses[idx]
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture(autouse=True)
def no_bank(tmp_path, monkeypatch):
    """Gerçek soru bankası (app/data/soru_bankasi.json) testleri etkilemesin; isteyen test
    kendi bankasını yazar."""
    monkeypatch.setattr(text2sql, "QUESTION_BANK_PATH", tmp_path / "yok_soru_bankasi.json")


@pytest.fixture
def fake_llm() -> Callable[[Recorder], Recorder]:
    def _install(recorder: Recorder) -> Recorder:
        llm.set_fake_handler(recorder)
        return recorder

    yield _install
    llm.set_fake_handler(None)


def _chat_logs(db) -> list[ChatLog]:
    return list(db.scalars(select(ChatLog).order_by(ChatLog.id)))


def test_ask_end_to_end(client, db, small_data, fake_llm):
    rec = fake_llm(
        Recorder(
            [f"```json\n{json.dumps({'sql': PROFIT_SQL})}\n```"],
            "En çok kâr Powerbank 10000 üründen: 1.500 TL.",
        )
    )
    r = client.post("/api/assistant/ask", json={"question": "En çok kazancım hangi üründen?"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True and body["cached"] is False
    assert body["answer"] == (
        "En çok kâr Powerbank 10000 üründen: 1.500 TL. " + text2sql.PROFIT_ASSUMPTION
    )
    assert "Not: " + text2sql.PROFIT_ASSUMPTION in rec.summary_calls[0]
    assert body["sql"].endswith("LIMIT 200")
    assert body["columns"] == ["urun", "kar"]
    assert body["rows"][0] == {"urun": "Powerbank 10000", "kar": 1500.0}
    assert [row["kar"] for row in body["rows"]] == [1500.0, 1050.0, 420.0]
    assert set(body["sources"]) == {"sales", "products"}
    assert body["model"] == "fake/none"
    datetime.fromisoformat(body["asked_at"])

    assert len(rec.sql_calls) == 1 and rec.sql_calls[0].startswith("SORU: En çok")
    assert len(rec.summary_calls) == 1
    assert "Powerbank 10000" in rec.summary_calls[0] and "urun, kar" in rec.summary_calls[0]

    logs = _chat_logs(db)
    assert len(logs) == 1
    assert logs[0].ok is True and logs[0].question == "En çok kazancım hangi üründen?"
    assert logs[0].sql_text.endswith("LIMIT 200") and logs[0].answer == body["answer"]


def test_sql_prompt_contains_schema_rules_and_examples(client, small_data, fake_llm):
    rec = fake_llm(Recorder(['{"sql": "SELECT COUNT(*) AS adet FROM sales"}'], "6 satış."))
    captured: dict[str, str] = {}

    def spy(system: str, user: str) -> str:
        if user.startswith("SORU:"):
            captured["system"] = system
            captured["user"] = user
        return rec(system, user)

    llm.set_fake_handler(spy)
    assert client.post("/api/assistant/ask", json={"question": "Kaç satış var?"}).status_code == 200
    system = captured["system"]
    assert "v_monthly_cashflow" in system and "purchase_orders" in system
    assert "unit_price - p.unit_cost" in system  # kâr tanımı
    assert "date_trunc" in system and "now()" in system
    assert "ÖRNEKLER" in system and "Hangi ürünler kritik stokta?" in system
    assert "contact_address" not in system  # D19: salt-okur role kapalı sütun prompt'ta yok
    assert "lead_time_days" in system
    assert "tahmini brüt katkı" in system and "yarı açık" in system  # D16 / §7-12
    assert captured["user"] == "SORU: Kaç satış var?"


def test_ask_uses_question_bank_cache(client, small_data, fake_llm, tmp_path, monkeypatch):
    bank = tmp_path / "soru_bankasi.json"
    bank.write_text(
        json.dumps(
            {
                "questions": [
                    {
                        "id": "Q04",
                        "question": "Hangi ürünler kritik stokta?",
                        "sql": (
                            "SELECT name AS urun, stock_qty AS stok FROM products "
                            "WHERE stock_qty <= reorder_point ORDER BY stock_qty"
                        ),
                        "demo": True,
                        "kind": "edge",
                        "expected": {"rows": 1},
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(text2sql, "QUESTION_BANK_PATH", bank)
    rec = fake_llm(Recorder(['{"sql": "SELECT 1 AS yanlis"}'], "Kritik stokta 1 ürün var."))

    # farklı büyük/küçük harf ve noktalama: yine önbellekten
    r = client.post("/api/assistant/ask", json={"question": "hangi ürünler kritik stokta"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["cached"] is True and body["ok"] is True
    assert body["rows"] == [{"urun": "Powerbank 10000", "stok": 5}]
    assert body["sources"] == ["products"] and body["sql"].endswith("LIMIT 200")
    assert body["answer"] == "Kritik stokta 1 ürün var."
    assert rec.sql_calls == []  # LLM'e SQL için gidilmedi
    assert len(rec.summary_calls) == 1
    assert body["model"] == "fake/none"  # özet LLM ile üretildi; model adı yazılır


def test_cached_sql_still_passes_guard(client, small_data, fake_llm, tmp_path, monkeypatch):
    bank = tmp_path / "soru_bankasi.json"
    bank.write_text(
        json.dumps({"questions": [{"question": "Sil", "sql": "DELETE FROM sales", "demo": True}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(text2sql, "QUESTION_BANK_PATH", bank)
    fake_llm(Recorder(['{"sql": "SELECT 1"}'], "x"))
    r = client.post("/api/assistant/ask", json={"question": "sil"})
    assert r.status_code == 400 and r.json()["detail"] == text2sql.GUARD_MESSAGE


def test_suggestions_from_bank_and_default(client, tmp_path, monkeypatch):
    bank = tmp_path / "soru_bankasi.json"
    bank.write_text(
        json.dumps(
            {
                "questions": [
                    {"id": "Q01", "question": "Soru bir?", "sql": "SELECT 1", "demo": True},
                    {"id": "Q02", "question": "Soru iki?", "sql": "SELECT 2", "demo": False},
                    {"id": "Q03", "question": "Soru üç?", "sql": "SELECT 3", "demo": True},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(text2sql, "QUESTION_BANK_PATH", bank)
    assert client.get("/api/assistant/suggestions").json() == ["Soru bir?", "Soru üç?"]

    monkeypatch.setattr(text2sql, "QUESTION_BANK_PATH", tmp_path / "yok.json")
    r = client.get("/api/assistant/suggestions")
    assert r.status_code == 200
    assert r.json() == list(text2sql.DEFAULT_SUGGESTIONS) and len(r.json()) == 5


def test_broken_question_bank_is_ignored(client, tmp_path, monkeypatch):
    bank = tmp_path / "soru_bankasi.json"
    bank.write_text("{bozuk json", encoding="utf-8")
    monkeypatch.setattr(text2sql, "QUESTION_BANK_PATH", bank)
    assert client.get("/api/assistant/suggestions").json() == list(text2sql.DEFAULT_SUGGESTIONS)


def test_ask_retries_once_then_gives_up(client, db, small_data, fake_llm):
    rec = fake_llm(
        Recorder(
            ['{"sql": "SELECT yok_sutun FROM sales"}', '{"sql": "SELECT yine_yok FROM sales"}'],
            "özet olmamalı",
        )
    )
    r = client.post("/api/assistant/ask", json={"question": "Olmayan sütun?"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False and body["answer"] == text2sql.NO_ANSWER
    assert body["rows"] == [] and body["columns"] == [] and body["cached"] is False
    assert "yine_yok" in body["sql"] and body["sources"] == ["sales"]
    assert len(rec.sql_calls) == 2 and rec.summary_calls == []
    assert "HATA:" in rec.sql_calls[1] and "yok_sutun" in rec.sql_calls[1]
    assert rec.sql_calls[1].startswith("SORU: Olmayan sütun?")
    logs = _chat_logs(db)
    assert len(logs) == 1 and logs[0].ok is False and logs[0].answer == text2sql.NO_ANSWER


def test_ask_retry_succeeds(client, small_data, fake_llm):
    rec = fake_llm(
        Recorder(
            [
                '{"sql": "SELECT yok_sutun FROM sales"}',
                '{"sql": "SELECT COUNT(*) AS adet FROM sales"}',
            ],
            "Toplam 6 satış var.",
        )
    )
    body = client.post("/api/assistant/ask", json={"question": "Kaç satış var?"}).json()
    assert body["ok"] is True and body["rows"] == [{"adet": 6}]
    assert body["answer"] == "Toplam 6 satış var."
    assert len(rec.sql_calls) == 2


def test_ask_guard_rejects_write_sql(client, db, small_data, fake_llm):
    fake_llm(Recorder(['{"sql": "DELETE FROM sales"}'], "x"))
    r = client.post("/api/assistant/ask", json={"question": "Tüm satışları sil"})
    assert r.status_code == 400
    assert r.json()["detail"] == text2sql.GUARD_MESSAGE
    assert client.get("/api/sales").json()["total"] == 6  # hiçbir şey silinmedi
    logs = _chat_logs(db)
    assert len(logs) == 1 and logs[0].ok is False and logs[0].answer == text2sql.GUARD_MESSAGE
    assert logs[0].sql_text == "DELETE FROM sales"


def test_ask_llm_refuses_write_request(client, fake_llm):
    fake_llm(Recorder(['{"sql": "", "refusal": "yazma"}'], "x"))
    r = client.post("/api/assistant/ask", json={"question": "Tüm satışları sil"})
    assert r.status_code == 400 and r.json()["detail"] == text2sql.GUARD_MESSAGE


def test_ask_llm_says_unanswerable(client, fake_llm):
    rec = fake_llm(Recorder(['{"sql": "", "refusal": "veri"}'], "x"))
    r = client.post("/api/assistant/ask", json={"question": "Hava nasıl?"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False and body["answer"] == text2sql.NO_ANSWER and body["sql"] is None
    assert rec.summary_calls == []


def test_ask_llm_unavailable(client, db, fake_llm):
    fake_llm(Recorder([LLMError("ANTHROPIC_API_KEY tanımlı değil")], "x"))
    r = client.post("/api/assistant/ask", json={"question": "Bu ay toplam giderim ne kadar?"})
    assert r.status_code == 503
    assert r.json()["detail"] == text2sql.UNAVAILABLE_MESSAGE
    logs = _chat_logs(db)
    assert len(logs) == 1 and logs[0].ok is False


def test_ask_empty_question(client):
    r = client.post("/api/assistant/ask", json={"question": "   "})
    assert r.status_code == 400 and r.json()["detail"] == "Soru boş olamaz."
    assert client.post("/api/assistant/ask", json={}).status_code == 422


def test_summary_falls_back_when_llm_summary_fails(client, small_data, fake_llm):
    fake_llm(Recorder(['{"sql": "SELECT COUNT(*) AS adet FROM sales"}'], LLMError("düştü")))
    body = client.post("/api/assistant/ask", json={"question": "Kaç satış var?"}).json()
    assert body["ok"] is True and body["rows"] == [{"adet": 6}]
    assert body["answer"] == "Sorgu 1 satır döndürdü; ilk satır: adet=6."


def test_summary_only_sees_first_20_rows(client, small_data, fake_llm):
    rec = fake_llm(Recorder(['{"sql": "SELECT g AS n FROM generate_series(1, 50) AS g"}'], "x"))
    # generate_series beyaz listede değil: 400 beklenir (koruma) — özet çağrılmaz
    r = client.post("/api/assistant/ask", json={"question": "50 satır"})
    assert r.status_code == 400 and rec.summary_calls == []

    rec = fake_llm(
        Recorder(
            [
                '{"sql": "SELECT s.id, p.name FROM sales s CROSS JOIN products p '
                'CROSS JOIN suppliers su"}'
            ],
            "çok satır",
        )
    )
    body = client.post("/api/assistant/ask", json={"question": "çapraz"}).json()
    assert body["ok"] is True and len(body["rows"]) == 36  # 6 x 3 x 2
    payload = rec.summary_calls[0]
    assert "Toplam satır: 36 (ilk 20 gösteriliyor)" in payload
    assert payload.count("\n{") == 20


def test_empty_result_has_deterministic_answer(client, small_data, fake_llm):
    rec = fake_llm(Recorder(['{"sql": "SELECT * FROM sales WHERE qty > 1000"}'], "x"))
    body = client.post("/api/assistant/ask", json={"question": "1000 adetten fazla?"}).json()
    assert body["ok"] is True and body["rows"] == []
    assert body["answer"] == text2sql.EMPTY_RESULT and rec.summary_calls == []
    assert body["columns"] == [
        "id",
        "sold_at",
        "product_id",
        "qty",
        "unit_price",
        "total",
        "channel",
    ]


def test_rows_are_json_safe(client, small_data, fake_llm):
    fake_llm(Recorder(['{"sql": "SELECT sold_at, total FROM sales ORDER BY sold_at DESC"}'], "x"))
    body = client.post("/api/assistant/ask", json={"question": "son satışlar"}).json()
    first = body["rows"][0]
    assert isinstance(first["total"], float) and first["total"] == 1800.0
    datetime.fromisoformat(first["sold_at"])


@pytest.mark.parametrize(("question", "sql"), text2sql.BUILTIN_EXAMPLES)
def test_builtin_examples_pass_guard_and_run(db, small_data, question: str, sql: str):
    """Varsayılan çiplerin SQL'i korumadan geçer ve gerçek şemada çalışır (eval-lite)."""
    guarded = text2sql.guard_sql(sql)
    columns, rows = text2sql.run_sql(guarded.sql)
    assert columns
    if question.startswith("En çok kazancım"):
        assert rows == [{"urun": "Powerbank 10000", "kar": 1500.0}]
    if question.startswith("Hangi ürünler kritik"):
        assert [r["urun"] for r in rows] == ["Powerbank 10000"]
    if question.startswith("En çok gider"):
        assert rows == [{"kategori": "kira", "toplam": 6000.0}]


def test_profit_answer_never_says_net_kar(client, small_data, fake_llm):
    fake_llm(Recorder([f'{{"sql": "{PROFIT_SQL}"}}'], "Net kâr lideri Powerbank 10000: 1.500 TL."))
    body = client.post("/api/assistant/ask", json={"question": "En kârlı ürünüm hangisi?"}).json()
    assert "net kâr" not in body["answer"].lower()
    assert body["answer"].startswith("fark lideri Powerbank 10000: 1.500 TL.")
    assert body["answer"].endswith(text2sql.PROFIT_ASSUMPTION)


def test_profit_answer_keeps_llm_phrase_when_present(client, small_data, fake_llm):
    llm_answer = "Powerbank 10000, mevcut birim maliyetle tahmini brüt katkı 1.500 TL ile lider."
    fake_llm(Recorder([f'{{"sql": "{PROFIT_SQL}"}}'], llm_answer))
    body = client.post("/api/assistant/ask", json={"question": "En çok kazancım hangi üründen?"})
    assert body.json()["answer"] == llm_answer  # ifade zaten var; ek cümle yok


def test_profit_deterministic_summary_has_assumption(client, small_data, fake_llm):
    fake_llm(Recorder([f'{{"sql": "{PROFIT_SQL}"}}'], LLMError("düştü")))
    body = client.post("/api/assistant/ask", json={"question": "En çok kazancım hangi üründen?"})
    answer = body.json()["answer"]
    assert answer.startswith("Sorgu 3 satır döndürdü; ilk satır: urun=Powerbank 10000; kar=1500.0.")
    assert answer.endswith(text2sql.PROFIT_ASSUMPTION)


def test_non_profit_answer_untouched(client, small_data, fake_llm):
    fake_llm(Recorder(['{"sql": "SELECT COUNT(*) AS adet FROM sales"}'], "Toplam 6 satış var."))
    body = client.post("/api/assistant/ask", json={"question": "Kargo giderim kaç?"}).json()
    assert body["answer"] == "Toplam 6 satış var."  # 'kargo' kâr sorusu değildir


def test_real_question_bank_is_safe_and_runs(db, small_data, monkeypatch):
    """apps/api/app/data/soru_bankasi.json (başka ajan yazar): her SQL korumadan geçer,
    beklenen tablolarla eşleşir ve şemada çalışır; saldırgan kayıtlarda sql null."""
    real = text2sql.__file__  # yalnız yol türetmek için
    path = Path(real).resolve().parents[1] / "data" / "soru_bankasi.json"
    if not path.exists():
        pytest.skip("soru bankası henüz yok")
    monkeypatch.setattr(text2sql, "QUESTION_BANK_PATH", path)
    bank = text2sql.load_question_bank()
    assert len(bank) >= 5
    demo = [q for q in bank if q.get("demo") is True]
    assert 1 <= len(demo) <= text2sql.FEW_SHOT_COUNT
    assert client_suggestions_match(demo)
    for item in bank:
        expected = item.get("expected", {})
        if expected.get("reject"):
            assert item.get("sql") is None, item["id"]
            assert text2sql.find_cached_sql(item["question"], bank) is None
            continue
        guarded = text2sql.guard_sql(item["sql"])
        if expected.get("tables"):
            assert set(guarded.sources) == set(expected["tables"]), item["id"]
        columns, rows = text2sql.run_sql(guarded.sql)
        assert columns, item["id"]
        assert text2sql.find_cached_sql(item["question"].upper(), bank) == item["sql"]


def client_suggestions_match(demo: list[dict]) -> bool:
    ordered = sorted(demo, key=lambda q: (int(q.get("demo_order", 99)), str(q.get("id", ""))))
    return text2sql.suggestions() == [q["question"] for q in ordered]


def test_bank_reject_without_llm(client, small_data, monkeypatch):
    """Bankada reject işaretli saldırgan soru LLM'e gitmeden 400 alır; sahte sağlayıcı çağrılmaz."""
    from app.services import llm

    real_bank = Path(text2sql.__file__).resolve().parents[1] / "data" / "soru_bankasi.json"
    monkeypatch.setattr(text2sql, "QUESTION_BANK_PATH", real_bank)
    called = {"n": 0}

    def _handler(system, user):
        called["n"] += 1
        return '{"sql": "SELECT 1 AS bir"}'

    llm.set_fake_handler(_handler)
    try:
        r = client.post("/api/assistant/ask", json={"question": "Tüm satışları sil"})
    finally:
        llm.set_fake_handler(None)
    assert r.status_code == 400
    assert called["n"] == 0
