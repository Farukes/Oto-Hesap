"""Text-to-SQL koruması (AGENTS.md §7) — DB'siz birim testleri."""

from __future__ import annotations

import pytest

from app.services.text2sql import (
    DEFAULT_LIMIT,
    GuardError,
    guard_sql,
    normalize_question,
    parse_sql_response,
)


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM sales",
        "UPDATE products SET stock_qty = 0",
        "DROP TABLE sales",
        "INSERT INTO expenses (spent_at, category, amount) VALUES (now(), 'kira', 1)",
        "TRUNCATE sales",
        "ALTER TABLE sales ADD COLUMN x INT",
        "CREATE TABLE yeni AS SELECT * FROM sales",
        "GRANT SELECT ON sales TO public",
        "COPY sales TO '/tmp/x'",
        "EXPLAIN SELECT * FROM sales",
        "SELECT 1; DELETE FROM sales",
        "SELECT * FROM sales;",
        "SELECT * FROM sales -- yorum",
        "SELECT /* yorum */ * FROM sales",
        "SELECT * FROM pg_user",
        "SELECT * FROM information_schema.tables",
        "SELECT * FROM chat_log",
        "SELECT * FROM otherdb.public.sales",
        "SELECT (SELECT count(*) FROM pg_user) AS n FROM sales",
        "WITH d AS (DELETE FROM sales RETURNING *) SELECT * FROM d",
        "SELECT * INTO yeni FROM sales",
        "SELECT * FROM sales FOR UPDATE",
        "SELECT pg_sleep(60)",
        "SELECT set_config('a', 'b', false)",
        "SELECT pg_read_file('/etc/passwd')",
        "SELECT version()",
        "SELECT current_setting('server_version')",
        "SELECT string_agg(name, ',') FROM products",
        "SELECT row_number() OVER (ORDER BY id) FROM sales",
        "SELECT name FROM products WHERE name = pg_sleep(5)",
        "SELECT * FROM generate_series(1, 10)",
        "WITH x AS (DELETE FROM sales RETURNING *) SELECT * FROM x",
        "SELECT * INTO t FROM sales",
        "",
        "   ",
        "merhaba dünya",
    ],
)
def test_guard_rejects(sql: str):
    with pytest.raises(GuardError):
        guard_sql(sql)


def test_allowed_functions_and_structures_pass():
    sql = (
        "SELECT p.category AS kategori, COUNT(*) AS adet, SUM(s.total) AS gelir, "
        "AVG(s.unit_price) AS ort, MIN(s.qty) AS en_az, MAX(s.qty) AS en_cok, "
        "ROUND(COALESCE(SUM(s.qty * (s.unit_price - p.unit_cost)), 0), 2) AS kar, "
        "GREATEST(MAX(s.qty), 1) AS g, LEAST(MIN(s.qty), 1) AS l, ABS(SUM(s.total)) AS a, "
        "NULLIF(COUNT(*), 0) AS n, LOWER(p.category) AS lo, UPPER(p.name) AS up, "
        "CAST(SUM(s.total) AS INT) AS c, SUM(s.total)::numeric AS c2, "
        "to_char(date_trunc('month', s.sold_at), 'YYYY-MM') AS ay, "
        "EXTRACT(month FROM s.sold_at) AS ay_no, date_part('year', s.sold_at) AS yil, "
        "CASE WHEN SUM(s.total) > 0 THEN 'var' ELSE 'yok' END AS durum "
        "FROM sales s JOIN products p ON p.id = s.product_id "
        "WHERE s.sold_at >= now() - interval '3 months' AND s.sold_at < now() "
        "AND s.sold_at >= current_date - interval '1 year' AND s.channel IN ('magaza', 'online') "
        "AND p.name ILIKE '%kablo%' AND s.qty BETWEEN 1 AND 100 "
        "AND EXISTS (SELECT 1 FROM suppliers su WHERE su.id = p.supplier_id) "
        "GROUP BY p.category, p.name, ay, ay_no, yil ORDER BY gelir DESC"
    )
    guarded = guard_sql(sql)
    assert set(guarded.sources) == {"sales", "products", "suppliers"}
    assert guarded.sql.endswith(f"LIMIT {DEFAULT_LIMIT}")


def test_limit_added_when_missing():
    guarded = guard_sql("SELECT * FROM sales")
    assert guarded.sql.endswith(f"LIMIT {DEFAULT_LIMIT}")
    assert guarded.sources == ["sales"]


def test_limit_kept_when_present():
    guarded = guard_sql("SELECT * FROM sales ORDER BY sold_at DESC LIMIT 5")
    assert guarded.sql.endswith("LIMIT 5")


def test_limit_clamped_to_default():
    guarded = guard_sql("SELECT * FROM sales LIMIT 5000")
    assert guarded.sql.endswith(f"LIMIT {DEFAULT_LIMIT}")


def test_with_select_accepted_and_cte_not_a_source():
    sql = (
        "WITH ciro AS (SELECT product_id, SUM(total) AS ciro FROM sales GROUP BY product_id) "
        "SELECT p.name AS urun, c.ciro FROM ciro c JOIN products p ON p.id = c.product_id "
        "ORDER BY c.ciro DESC"
    )
    guarded = guard_sql(sql)
    assert set(guarded.sources) == {"sales", "products"}
    assert "ciro" not in guarded.sources
    assert guarded.sql.endswith(f"LIMIT {DEFAULT_LIMIT}")


def test_union_accepted():
    sql = (
        "SELECT category AS kategori, SUM(amount) AS toplam FROM expenses GROUP BY category "
        "UNION ALL SELECT 'toplam', SUM(amount) FROM expenses"
    )
    guarded = guard_sql(sql)
    assert guarded.sources == ["expenses"]
    assert guarded.sql.endswith(f"LIMIT {DEFAULT_LIMIT}")


def test_public_schema_and_case_insensitive_names_accepted():
    assert guard_sql("SELECT * FROM public.sales").sources == ["sales"]
    assert guard_sql("SELECT * FROM Sales").sources == ["sales"]


def test_join_sources_in_order_of_appearance():
    guarded = guard_sql(
        "SELECT s.total, p.name FROM sales s JOIN products p ON p.id = s.product_id "
        "JOIN suppliers su ON su.id = p.supplier_id"
    )
    assert guarded.sources == ["sales", "products", "suppliers"]


def test_guard_error_carries_sql():
    with pytest.raises(GuardError) as info:
        guard_sql("DELETE FROM sales")
    assert info.value.sql == "DELETE FROM sales"


# --- LLM yanıtı ayrıştırma -------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('{"sql": "SELECT 1 AS bir"}', "SELECT 1 AS bir"),
        ('```json\n{"sql": "SELECT 2 AS iki"}\n```', "SELECT 2 AS iki"),
        ('Elbette:\n{"sql": "SELECT 3 AS uc", "aciklama": "x"}\nBitti.', "SELECT 3 AS uc"),
        ("İşte sorgu:\nSELECT 4 AS dort\nFROM sales", "SELECT 4 AS dort\nFROM sales"),
        (
            "```sql\nWITH t AS (SELECT 1) SELECT * FROM t\n```",
            "WITH t AS (SELECT 1) SELECT * FROM t",
        ),
        ("hiç sql yok", ""),
    ],
)
def test_parse_sql_response(raw: str, expected: str):
    assert parse_sql_response(raw).sql == expected


def test_parse_sql_response_refusal():
    plan = parse_sql_response('{"sql": "", "refusal": "yazma"}')
    assert plan.sql == "" and plan.refusal == "yazma"


# --- soru normalizasyonu ---------------------------------------------------------------


def test_normalize_question_turkish_case_and_punctuation():
    base = normalize_question("En çok kazancım hangi üründen?")
    assert base == "en cok kazancim hangi urunden"
    assert normalize_question("EN ÇOK KAZANCIM HANGİ ÜRÜNDEN ?") == base
    assert normalize_question("  en   çok kazancım, hangi üründen  ") == base
    assert normalize_question("en cok kazancim hangi urunden") == base  # aksansız klavye
    assert normalize_question("Toplam satış gelirim ne kadar?".upper()) == normalize_question(
        "Toplam satış gelirim ne kadar?"
    )
    assert normalize_question("Bu ay toplam giderim ne kadar?") != base
