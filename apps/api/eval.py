"""15 soruluk soru bankasını GERÇEK sağlayıcıyla koşar; sonucu gold SQL'in sonucuyla karşılaştırır.

Kullanım (apps/api içinde, .env'de LLM_PROVIDER ve anahtar dolu):
    uv run python eval.py [--provider gemini]
Ölçüt (D15): SQL metni değil SONUÇ eşdeğerliği (sıralamadan bağımsız satır kümesi, float 2 ondalık),
izinli tablolar ve yazma yok. Saldırgan sorular (sql=null) 400 ile reddedilmeli.
Çıktı: tablo + toplam; sağlayıcı seçimi bu sayıyla yapılır.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from decimal import Decimal


def _norm(rows: list[dict]) -> set[tuple]:
    out = set()
    for r in rows:
        items = []
        for k, v in sorted(r.items()):
            if isinstance(v, float | Decimal):
                v = round(float(v), 2)
            items.append((k, str(v)))
        out.add(tuple(items))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", help="anthropic | gemini | groq (varsayılan .env)")
    args = ap.parse_args()
    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    os.environ.setdefault("AGENT_SCHEDULER_ENABLED", "false")

    from app.db import SessionLocal
    from app.services import text2sql
    from app.services.llm import LLMError, provider_name

    bank = text2sql.load_question_bank()
    if not bank:
        print("soru bankası bulunamadı:", text2sql.QUESTION_BANK_PATH)
        return 2
    # Önbellek kapalı: model gerçekten SQL üretsin
    text2sql.find_cached_sql = lambda q, b: None  # type: ignore[assignment]

    print(f"sağlayıcı: {provider_name()} / model: {text2sql.model_label()}  ({len(bank)} soru)\n")
    ok_n = 0
    rows_out = []
    with SessionLocal() as db:
        for q in bank:
            qid, question, gold = q["id"], q["question"], q.get("sql")
            expect_reject = bool((q.get("expected") or {}).get("reject"))
            t0 = time.perf_counter()
            verdict, note = "?", ""
            try:
                res = text2sql.ask(question, db)
                ms = (time.perf_counter() - t0) * 1000
                if expect_reject:
                    verdict, note = "FAIL", "reddedilmeliydi, çalıştı"
                elif not res.ok:
                    verdict, note = "FAIL", "ok=false"
                else:
                    gold_cols, gold_rows = text2sql.run_sql(text2sql.guard_sql(gold).sql)
                    same = _norm(gold_rows) == _norm(res.rows)
                    verdict = "PASS" if same else "FAIL"
                    note = (
                        "" if same else f"gold {len(gold_rows)} satır / model {len(res.rows)} satır"
                    )
            except text2sql.GuardError as e:
                ms = (time.perf_counter() - t0) * 1000
                verdict = "PASS" if expect_reject else "FAIL"
                note = "guard red" if expect_reject else f"guard: {e.reason}"
            except LLMError as e:
                ms = (time.perf_counter() - t0) * 1000
                verdict, note = "ERR", f"LLM: {e}"
            ok_n += verdict == "PASS"
            rows_out.append((qid, verdict, f"{ms:6.0f} ms", question[:48], note[:60]))
            print(f"{qid:4} {verdict:4} {ms:6.0f} ms  {question[:48]:48}  {note}")
    print(f"\nSONUÇ: {ok_n}/{len(bank)} doğru  (hedef ≥ 12; demo soruları 5/5 olmalı)")
    json.dump(
        {
            "provider": provider_name(),
            "model": text2sql.model_label(),
            "ok": ok_n,
            "total": len(bank),
            "rows": rows_out,
        },
        open("eval-sonuc.json", "w"),
        ensure_ascii=False,
        indent=1,
    )
    return 0 if ok_n >= 12 else 1


if __name__ == "__main__":
    sys.exit(main())
