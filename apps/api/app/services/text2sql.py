"""Text-to-SQL asistanı — AGENTS.md §7 (madde 1-12) birebir; DECISIONS D9, D16, D19, D20.

Hat: soru → önbellek (soru bankası) → prompt (şema + kurallar + few-shot) → llm.complete()
→ {"sql": ...} ayrıştır → koruma (sqlglot AST, defense-in-depth) → salt-okur engine_ro
→ satırlar → Türkçe özet (yalnız satırlardan) → chat_log.

Koruma katmanları (parser geçti = güvenli sanılmaz):
1. Metin: tam olarak 1 ifade; `;`, `--`, `/*` reddedilir.
2. Kök: Select veya set işlemi (UNION...), WITH ile sarılmış olabilir; CTE/alt sorgu dahil
   AST'nin herhangi bir yerinde DML/DDL düğümü → red. SELECT INTO ve FOR UPDATE → red.
3. Fonksiyon izin listesi (D19): yalnız sum, count, avg, min, max, coalesce, round, date_trunc,
   date_part, extract, now, current_date, to_char, lower, upper, cast, nullif, greatest, least, abs.
4. Tablo beyaz listesi (CTE adları hariç); şema yalnız public.
5. Sütun/yapı reddi: `suppliers.contact_address` (ve o tabloyu okuyan kapsamda `*`),
   OID ailesi tür dönüşümü (regclass/regproc), `WITH RECURSIVE`.
6. LIMIT yoksa 200 eklenir; 200'den büyükse 200'e çekilir.
7. Çalıştırma engine_ro ile (statement_timeout 5 sn + read-only işlem).
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import sqlglot
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlglot import exp
from sqlglot.errors import SqlglotError

from ..config import settings
from ..db import engine_ro
from ..models import ChatLog
from ..schemas.assistant import SQLPlan
from . import llm

log = logging.getLogger("otohesap.text2sql")

ALLOWED_TABLES = frozenset(
    {"sales", "expenses", "products", "suppliers", "purchase_orders", "v_monthly_cashflow"}
)
ALLOWED_SCHEMAS = frozenset({"", "public"})
# D19: asistana kapalı sütunlar. Salt-okur rolde sütun düzeyinde de kapalıdır (docs/schema.sql),
# ama DATABASE_URL_RO tanımlı değilse uygulama rolü kullanılır → guard bağımsız reddeder.
BLOCKED_COLUMNS = frozenset({"contact_address"})
# `*` genişlemesi kapalı sütunu da getirir; bu tabloları okuyan kapsamda yıldız yasak.
STAR_BLOCKED_TABLES = frozenset({"suppliers"})
DEFAULT_LIMIT = 200
MAX_SUMMARY_ROWS = 20
FEW_SHOT_COUNT = 6
# Soru bankası başka bir ajan tarafından yazılır; yoksa boş liste (hata yok).
QUESTION_BANK_PATH = Path(__file__).resolve().parents[1] / "data" / "soru_bankasi.json"

GUARD_MESSAGE = "Asistan yalnız okuma sorguları çalıştırır."
UNAVAILABLE_MESSAGE = "Asistan şu an yanıt veremiyor; lütfen tekrar deneyin."
NO_ANSWER = "Bu soruyu bu veriyle yanıtlayamadım."
EMPTY_RESULT = "Sorgu bu veriyle eşleşen kayıt döndürmedi."
PROFIT_ASSUMPTION = "Kâr, mevcut birim maliyetle tahmini brüt katkıdır."  # D16 / D20

DEFAULT_SUGGESTIONS: tuple[str, ...] = (
    "En çok kazancım hangi üründen?",
    "Bu ay toplam giderim ne kadar?",
    "Son 3 ayda gelir-gider farkı nasıl değişti?",
    "Hangi ürünler kritik stokta?",
    "En çok gider hangi kategoride?",
)

# Soru bankası yoksa prompt'a giren örnekler (varsayılan çiplerle birebir; aralıklar yarı açık).
BUILTIN_EXAMPLES: tuple[tuple[str, str], ...] = (
    (
        "En çok kazancım hangi üründen?",
        "SELECT p.name AS urun, SUM(s.qty * (s.unit_price - p.unit_cost)) AS kar "
        "FROM sales s JOIN products p ON p.id = s.product_id "
        "GROUP BY p.name ORDER BY kar DESC LIMIT 1",
    ),
    (
        "Bu ay toplam giderim ne kadar?",
        "SELECT COALESCE(SUM(amount), 0) AS toplam_gider FROM expenses "
        "WHERE spent_at >= date_trunc('month', now()) "
        "AND spent_at < date_trunc('month', now()) + interval '1 month'",
    ),
    (
        "Son 3 ayda gelir-gider farkı nasıl değişti?",
        "SELECT to_char(month, 'YYYY-MM') AS ay, income AS gelir, expense AS gider, net AS fark "
        "FROM v_monthly_cashflow "
        "WHERE month >= date_trunc('month', now()) - interval '2 months' ORDER BY month",
    ),
    (
        "Hangi ürünler kritik stokta?",
        "SELECT name AS urun, stock_qty AS stok, reorder_point AS kritik_esik FROM products "
        "WHERE stock_qty <= reorder_point ORDER BY stock_qty",
    ),
    (
        "En çok gider hangi kategoride?",
        "SELECT category AS kategori, SUM(amount) AS toplam FROM expenses "
        "GROUP BY category ORDER BY toplam DESC LIMIT 1",
    ),
)

_FORBIDDEN_NODE_NAMES = (
    "Insert",
    "Update",
    "Delete",
    "Create",
    "Drop",
    "Alter",
    "Command",
    "Merge",
    "TruncateTable",
    "Grant",
    "Copy",
    "Transaction",
    "Commit",
    "Rollback",
    "Set",
    "Use",
    "Describe",
    "Pragma",
)
FORBIDDEN_NODES: tuple[type[exp.Expression], ...] = tuple(
    getattr(exp, name) for name in _FORBIDDEN_NODE_NAMES if hasattr(exp, name)
)
# D19 fonksiyon izin listesi. Anahtar: exp.Anonymous için fonksiyon adı, diğerlerinde sqlglot'un
# kanonik adı (sql_name): date_trunc → TIMESTAMP_TRUNC, now() → CURRENT_TIMESTAMP,
# to_char → TIME_TO_STR, date_part → EXTRACT. version() → CURRENT_VERSION → izinli değil.
ALLOWED_FUNCTIONS = frozenset(
    {
        "sum",
        "count",
        "avg",
        "min",
        "max",
        "coalesce",
        "round",
        "date_trunc",
        "timestamp_trunc",
        "date_part",
        "extract",
        "now",
        "current_timestamp",
        "current_date",
        "to_char",
        "time_to_str",
        "lower",
        "upper",
        "cast",
        "nullif",
        "greatest",
        "least",
        "abs",
    }
)
# sqlglot'ta Func'tan türeyen ama fonksiyon çağrısı olmayan yapılar (mantık/koşul).
STRUCTURAL_FUNCS = frozenset(
    {"and", "or", "xor", "not", "case", "if", "exists", "in", "between", "like", "ilike"}
)
_WRITE_REFUSAL_RE = re.compile(
    r"yaz|sil|güncel|guncel|ekle|değiş|degis|write|delete|update|insert|drop|ddl|dml", re.I
)
_FENCE_RE = re.compile(r"```(?:json|sql)?\s*(.*?)```", re.S | re.I)
_JSON_RE = re.compile(r"\{.*\}", re.S)
_SQL_START_RE = re.compile(r"^\s*(select|with)\b", re.I)
_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WS_RE = re.compile(r"\s+")
# normalize edilmiş (ASCII) metinde: "kar", "karli", "karim", "kazanc", "kazancim"; "kargo" değil
_PROFIT_RE = re.compile(r"\bkar(\b|li|im)|kazanc")
_NET_PROFIT_RE = re.compile(r"net\s+k[aâ]r", re.I)


class GuardError(ValueError):
    """Koruma reddi; `sql` reddedilen metin (log için)."""

    def __init__(self, reason: str, sql: str | None = None) -> None:
        super().__init__(reason)
        self.sql = sql


@dataclass
class GuardedSQL:
    sql: str
    sources: list[str] = field(default_factory=list)


@dataclass
class AskResult:
    ok: bool
    answer: str
    sql: str | None
    rows: list[dict[str, Any]]
    columns: list[str]
    sources: list[str]
    asked_at: datetime
    cached: bool
    model: str


def model_label() -> str:
    """Yanıttaki `model` alanı: "{provider}/{model}"; fake → "fake/none"."""
    provider = settings.llm_provider
    if provider == "anthropic":
        return f"anthropic/{settings.anthropic_model}"
    if provider == "gemini":
        return f"gemini/{settings.gemini_model}"
    if provider == "groq":
        return f"groq/{settings.groq_model}"
    if provider == "ollama":
        return f"ollama/{settings.ollama_model}"
    return f"{provider}/none"


# --- soru bankası / önbellek ----------------------------------------------------------


def normalize_question(question: str) -> str:
    """Önbellek anahtarı: küçük harf (Türkçe İ/ı doğru), aksanlar ASCII'ye katlanır
    (ç→c, ş→s, ğ→g, ı→i, ü→u, ö→o), noktalama atılır, boşluk sadeleşir.
    "En çok kazancım?" == "EN ÇOK KAZANCIM" == "en cok kazancim"."""
    q = question.replace("İ", "i").replace("I", "ı").casefold()
    q = unicodedata.normalize("NFKD", q)
    q = "".join(ch for ch in q if not unicodedata.combining(ch)).replace("ı", "i")
    q = _PUNCT_RE.sub(" ", q)
    return _WS_RE.sub(" ", q).strip()


def is_profit_question(question: str) -> bool:
    return _PROFIT_RE.search(normalize_question(question)) is not None


def load_question_bank() -> list[dict[str, Any]]:
    path = QUESTION_BANK_PATH
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        log.warning("soru bankası okunamadı (%s): %s", path, e)
        return []
    items = data.get("questions", []) if isinstance(data, dict) else data
    if not isinstance(items, list):
        return []
    return [q for q in items if isinstance(q, dict) and q.get("question")]


def find_cached_sql(question: str, bank: list[dict[str, Any]]) -> str | None:
    """Birebir (normalize) eşleşen ve SQL'i olan kayıt; saldırgan sorularda sql=null → atlanır."""
    key = normalize_question(question)
    if not key:
        return None
    for item in bank:
        sql = item.get("sql")
        if sql and normalize_question(str(item["question"])) == key:
            return str(sql)
    return None


def find_bank_reject(question: str, bank: list[dict[str, Any]]) -> bool:
    """Soru bankasında `expected.reject` işaretli (saldırgan) bir soruyla birebir eşleşiyor mu?
    Eşleşirse LLM'e hiç gidilmez; deterministik red."""
    key = normalize_question(question)
    for item in bank:
        expected = item.get("expected") or {}
        if expected.get("reject") and normalize_question(str(item.get("question", ""))) == key:
            return True
    return False


def demo_examples(bank: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [
        (str(q["question"]), str(q["sql"])) for q in bank if q.get("demo") is True and q.get("sql")
    ][:FEW_SHOT_COUNT]


def suggestions() -> list[str]:
    bank = [q for q in load_question_bank() if q.get("demo") is True]
    bank.sort(key=lambda q: (int(q.get("demo_order", 99)), str(q.get("id", ""))))
    demo = [str(q["question"]) for q in bank]
    return demo or list(DEFAULT_SUGGESTIONS)


# --- prompt ---------------------------------------------------------------------------

ROLE = (
    "Sen OtoHesap'ın finans asistanısın. Görevin: KOBİ sahibinin Türkçe sorusunu "
    "PostgreSQL 16 için tek bir SELECT sorgusuna çevirmek."
)

# suppliers.contact_address bilerek yok: salt-okur role sütun düzeyinde kapalı (D19).
SCHEMA_DOC = """VERİ MODELİ (PostgreSQL 16; para NUMERIC(12,2) TL; zamanlar TIMESTAMPTZ):
- products: id, name (ürün adı), category (kategori), unit_cost (birim maliyet),
  sale_price (liste satış fiyatı), stock_qty (mevcut stok adedi), reorder_point (kritik eşik),
  target_stock (sipariş sonrası hedef stok), supplier_id -> suppliers.id
- sales: id, sold_at (satış zamanı), product_id -> products.id, qty (adet),
  unit_price (satıştaki birim fiyat), total (satır tutarı = qty * unit_price),
  channel ('magaza' | 'online')
- expenses: id, spent_at (gider zamanı), category (kira, maas, elektrik, kargo, reklam, tedarik),
  amount (tutar), vendor (firma), note (not)
- suppliers: id, name (tedarikçi adı), contact_channel ('telegram' | 'email'),
  lead_time_days (teslim süresi, gün)
- purchase_orders: id, created_at, product_id -> products.id, supplier_id -> suppliers.id,
  qty, est_amount (tahmini tutar), status ('draft' | 'approved' | 'sent' | 'rejected'),
  message_text, sent_at
- v_monthly_cashflow (görünüm): month (ayın ilk günü, timestamptz), income (aylık gelir),
  expense (aylık gider), net (gelir - gider)"""

RULES = """KURALLAR:
1. Tek bir SELECT (gerekirse WITH ... SELECT veya UNION). INSERT/UPDATE/DELETE/DDL yazma;
   `;` ve yorum kullanma.
2. Yalnız yukarıdaki tablo, görünüm ve sütunları kullan; sütun uydurma.
   İzinli fonksiyonlar: sum, count, avg, min, max, coalesce, round, date_trunc, date_part,
   extract, now, current_date, to_char, lower, upper, cast, nullif, greatest, least, abs.
3. METRİK SÖZLÜĞÜ: gelir/ciro = SUM(sales.total); gider = SUM(expenses.amount);
   fark = gelir - gider (net kâr DEĞİL);
   kâr/kazanç = tahmini brüt katkı = SUM(s.qty * (s.unit_price - p.unit_cost))
   (sales s JOIN products p ON p.id = s.product_id, mevcut birim maliyetle);
   kritik stok = stock_qty <= reorder_point.
4. TARİH: aralıklar daima yarı açık [başlangıç, bitiş): ">= başlangıç AND < bitiş".
   "bu ay" = sold_at >= date_trunc('month', now())
   AND sold_at < date_trunc('month', now()) + interval '1 month';
   "geçen ay" = sold_at >= date_trunc('month', now()) - interval '1 month'
   AND sold_at < date_trunc('month', now());
   "son N ay" = sold_at >= now() - interval 'N months' AND sold_at < now().
   Aylık kırılım için date_trunc('month', ...) veya v_monthly_cashflow.
   now() kullan, sabit tarih yazma; soru açıkça ay/yıl veriyorsa o ayın
   [ilk günü, sonraki ayın ilk günü) aralığını kullan.
5. Sütun takma adları ASCII ve küçük harf (urun, toplam_gelir, kar, fark, ay).
   Sonuçları anlamlı sırala; "en çok/en az" için ORDER BY ... LIMIT 1.
6. Yanıt SADECE şu JSON: {"sql": "..."} — açıklama, kod bloğu, ek metin yok.
7. Kullanıcı veri silme/güncelleme/ekleme isterse SQL üretme: {"sql": "", "refusal": "yazma"}.
   Soru bu tablolarla yanıtlanamıyorsa (ör. şifre, parola, kişisel veri):
   {"sql": "", "refusal": "veri"}."""

SUMMARY_SYSTEM = (
    "Sen OtoHesap'ın finans asistanısın. Sana bir soru ve sorgunun döndürdüğü satırlar "
    "verilecek. 1-3 kısa Türkçe cümleyle sonucu özetle. YALNIZ verilen satırlardaki sayıları "
    "ve adları kullan; tahmin ekleme, yeni sayı üretme, yorum yapma. Para TL; sayıları okunur "
    "yaz (ör. 12.450 TL). Gelir-gider farkına 'fark' de; 'net kâr' ifadesini asla kullanma. "
    "Soru kâr/kazanç ile ilgiliyse cümlede 'mevcut birim maliyetle tahmini brüt katkı' "
    "ifadesini kullan."
)


def build_sql_prompt(
    question: str,
    bank: list[dict[str, Any]],
    *,
    previous_sql: str | None = None,
    error: str | None = None,
) -> tuple[str, str]:
    """(system, user) döner; user 'SORU:' ile başlar (fake sağlayıcı ayrımı için)."""
    examples = demo_examples(bank) or list(BUILTIN_EXAMPLES)
    example_text = "\n\n".join(
        f"Soru: {q}\nJSON: {json.dumps({'sql': s}, ensure_ascii=False)}" for q, s in examples
    )
    today = datetime.now(UTC).date().isoformat()
    system = f"{ROLE}\nBugün (UTC): {today}\n\n{SCHEMA_DOC}\n\n{RULES}\n\nÖRNEKLER:\n{example_text}"
    user = f"SORU: {question}"
    if error:
        user += (
            f"\n\nÖNCEKİ SQL:\n{previous_sql or ''}\n\nHATA: {error}\n\n"
            "Hatayı düzelt; yalnız JSON döndür."
        )
    return system, user


def parse_sql_response(raw: str) -> SQLPlan:
    """Kod bloğunu temizler, JSON ayrıştırır; JSON yoksa SELECT/WITH ile başlayan satırdan alır."""
    body = (raw or "").strip()
    fence = _FENCE_RE.search(body)
    if fence:
        body = fence.group(1).strip()
    candidates = [body]
    block = _JSON_RE.search(body)
    if block and block.group(0) != body:
        candidates.append(block.group(0))
    for candidate in candidates:
        try:
            return SQLPlan.model_validate_json(candidate)
        except ValidationError:
            continue
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if _SQL_START_RE.match(line):
            return SQLPlan(sql="\n".join(lines[i:]).strip())
    return SQLPlan(sql="")


# --- koruma ---------------------------------------------------------------------------


def _function_key(node: exp.Func) -> str:
    if isinstance(node, exp.Anonymous):
        return node.name.lower()
    return node.sql_name().lower()


def _scope_tables(select: exp.Select) -> set[str]:
    """Bir SELECT'in kendi FROM/JOIN kaynaklarındaki tablo adları (alt sorgular dahil).
    WHERE içindeki alt sorgular sayılmaz: `*` yalnız kaynak tabloların sütunlarını getirir."""
    # sqlglot 30'da anahtar "from_", eskisinde "from" — ikisini de dene.
    from_node = select.args.get("from_") or select.args.get("from")
    sources: list[exp.Expression] = [from_node, *(select.args.get("joins") or [])]
    names: set[str] = set()
    for source in sources:
        if source is None:
            continue
        names.update(table.name.lower() for table in source.find_all(exp.Table))
    return names


def _star_reads_blocked_table(tree: exp.Expression) -> str | None:
    """`SELECT *` / `s.*` projeksiyonu kapalı sütunlu bir tabloyu okuyorsa o tablonun adı."""
    for star in tree.find_all(exp.Star):
        projection = star.parent
        if isinstance(projection, exp.Column):  # "s.*"
            projection = projection.parent
        if not isinstance(projection, exp.Select):  # count(*) gibi: genişleme yok
            continue
        blocked = _scope_tables(projection) & STAR_BLOCKED_TABLES
        if blocked:
            return sorted(blocked)[0]
    return None


def guard_sql(raw_sql: str) -> GuardedSQL:
    """AGENTS.md §7: tek okuma ifadesi, fonksiyon izin listesi, beyaz liste, LIMIT.

    Reddederse GuardError.
    """
    sql = (raw_sql or "").strip()
    if not sql:
        raise GuardError("boş SQL", sql)
    if ";" in sql:
        raise GuardError("noktalı virgül yasak", sql)
    if "--" in sql or "/*" in sql:
        raise GuardError("yorum yasak", sql)
    try:
        statements = sqlglot.parse(sql, dialect="postgres")
    except SqlglotError as e:
        raise GuardError(f"ayrıştırılamadı: {e}", sql) from e
    if len(statements) != 1 or statements[0] is None:
        raise GuardError("tam olarak bir ifade olmalı", sql)
    tree = statements[0]
    if not isinstance(tree, exp.Select | exp.SetOperation):
        raise GuardError(f"okuma sorgusu değil: {type(tree).__name__}", sql)
    if tree.args.get("into") is not None:
        raise GuardError("SELECT INTO yasak", sql)
    if tree.args.get("locks"):
        raise GuardError("FOR UPDATE/SHARE yasak", sql)
    # CTE ve alt sorgular dahil tüm ağaç gezilir.
    forbidden = next(iter(tree.find_all(*FORBIDDEN_NODES)), None)
    if forbidden is not None:
        raise GuardError(f"yasak ifade: {type(forbidden).__name__}", sql)
    for func in tree.find_all(exp.Func):
        key = _function_key(func)
        if key not in ALLOWED_FUNCTIONS and key not in STRUCTURAL_FUNCS:
            raise GuardError(f"izinsiz fonksiyon: {key or type(func).__name__}", sql)
    # OID ailesi ('sales'::regclass, 'pg_sleep'::regproc): katalog yoklama aracı, işimiz yok.
    if tree.find(exp.ObjectIdentifier) is not None:
        raise GuardError("izinsiz tür dönüşümü (OID ailesi)", sql)
    # WITH RECURSIVE: dış LIMIT özyinelemeyi durdurmaz; 5 sn'lik CPU/bellek tüketimi (DoS).
    if any(w.args.get("recursive") for w in tree.find_all(exp.With)):
        raise GuardError("WITH RECURSIVE yasak", sql)

    for column in tree.find_all(exp.Column):
        if column.name.lower() in BLOCKED_COLUMNS:
            raise GuardError(f"izinsiz sütun: {column.name.lower()}", sql)
    blocked_star = _star_reads_blocked_table(tree)
    if blocked_star is not None:
        raise GuardError(f"{blocked_star} tablosunda * yasak (kapalı sütun)", sql)

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    sources: list[str] = []
    for table in tree.find_all(exp.Table, bfs=False):
        name = table.name.lower()
        if name in cte_names:
            continue
        if table.catalog or table.db.lower() not in ALLOWED_SCHEMAS:
            raise GuardError(f"izinsiz şema: {table.sql(dialect='postgres')}", sql)
        if name not in ALLOWED_TABLES:
            raise GuardError(f"izinsiz tablo: {name or table.sql(dialect='postgres')}", sql)
        if name not in sources:
            sources.append(name)

    limit = tree.args.get("limit")
    if limit is None:
        tree = tree.limit(DEFAULT_LIMIT)
    else:
        try:
            n = int(limit.expression.name)
        except (ValueError, AttributeError):
            n = None
        if n is None or n > DEFAULT_LIMIT:
            tree = tree.limit(DEFAULT_LIMIT)
    return GuardedSQL(sql=tree.sql(dialect="postgres"), sources=sources)


# --- çalıştırma / özet ----------------------------------------------------------------


def json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if value is None or isinstance(value, str | int | float | bool):
        return value
    return str(value)


def run_sql(sql: str) -> tuple[list[str], list[dict[str, Any]]]:
    """Salt-okur motorla çalıştırır; (sütunlar, satırlar) döner. DB hatası SQLAlchemyError."""
    with engine_ro.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [
            {col: json_safe(val) for col, val in zip(columns, row, strict=True)} for row in result
        ]
    return columns, rows


def deterministic_summary(columns: list[str], rows: list[dict[str, Any]]) -> str:
    if not rows:
        return EMPTY_RESULT
    first = "; ".join(f"{col}={rows[0].get(col)}" for col in columns)
    return f"Sorgu {len(rows)} satır döndürdü; ilk satır: {first}."


def finalize_answer(question: str, answer: str) -> str:
    """D16/D20: 'net kâr' denmez; kâr sorusunda varsayım cümlesi mutlaka bulunur."""
    answer = _NET_PROFIT_RE.sub("fark", answer).strip()
    if is_profit_question(question) and "tahmini brüt katkı" not in answer:
        answer = f"{answer} {PROFIT_ASSUMPTION}".strip()
    return answer


def summarize(question: str, columns: list[str], rows: list[dict[str, Any]]) -> str:
    """LLM'e yalnız sütun adları + ilk 20 satır; başarısızsa deterministik özet."""
    if not rows:
        return EMPTY_RESULT
    sample = rows[:MAX_SUMMARY_ROWS]
    note = (
        f"Not: {PROFIT_ASSUMPTION} Bunu cümlende belirt.\n" if is_profit_question(question) else ""
    )
    user = (
        f"ÖZET:\nSoru: {question}\n{note}Sütunlar: {', '.join(columns)}\n"
        f"Toplam satır: {len(rows)} (ilk {len(sample)} gösteriliyor)\nSatırlar (JSON):\n"
        + "\n".join(json.dumps(r, ensure_ascii=False) for r in sample)
    )
    try:
        answer = llm.complete(SUMMARY_SYSTEM, user, max_tokens=300).strip()
    except llm.LLMError as e:
        log.warning("özet için LLM erişilemedi: %s", e)
        answer = ""
    except Exception:  # noqa: BLE001 — özet hiçbir zaman yanıtı düşürmez
        log.exception("özet üretilemedi")
        answer = ""
    if not answer or answer.startswith("{"):
        answer = deterministic_summary(columns, rows)
    return finalize_answer(question, answer)


def _db_error_text(err: SQLAlchemyError) -> str:
    orig = getattr(err, "orig", None)
    msg = str(orig) if orig is not None else str(err)
    return msg.strip().splitlines()[0][:300] if msg.strip() else "bilinmeyen SQL hatası"


def _generate_sql(
    question: str,
    bank: list[dict[str, Any]],
    *,
    previous_sql: str | None = None,
    error: str | None = None,
) -> str | None:
    """LLM'den SQL alır. None = LLM 'bu veriyle yanıtlanamaz' dedi. Yazma isteği → GuardError."""
    system, user = build_sql_prompt(question, bank, previous_sql=previous_sql, error=error)
    raw = llm.complete(system, user, max_tokens=600)
    plan = parse_sql_response(raw)
    sql = plan.sql.strip()
    if sql:
        return sql
    if plan.refusal and _WRITE_REFUSAL_RE.search(plan.refusal):
        raise GuardError(f"LLM yazma isteğini reddetti: {plan.refusal}", None)
    log.info("LLM soruyu veriyle yanıtlanamaz buldu: %s", plan.refusal)
    return None


def _log_chat(db: Session, question: str, sql: str | None, answer: str, ok: bool) -> None:
    try:
        db.add(ChatLog(question=question, sql_text=sql, answer=answer, ok=ok))
        db.commit()
    except SQLAlchemyError:
        log.exception("chat_log yazılamadı")
        db.rollback()


def _no_answer(asked_at: datetime, sql: str | None, sources: list[str]) -> AskResult:
    return AskResult(
        ok=False,
        answer=NO_ANSWER,
        sql=sql,
        rows=[],
        columns=[],
        sources=sources,
        asked_at=asked_at,
        cached=False,
        model=model_label(),
    )


def _ask(question: str, asked_at: datetime) -> AskResult:
    bank = load_question_bank()
    if find_bank_reject(question, bank):
        raise GuardError("soru bankası: yazma/izinsiz istek", None)
    cached_sql = find_cached_sql(question, bank)
    cached = cached_sql is not None
    raw_sql = cached_sql if cached_sql is not None else _generate_sql(question, bank)
    if raw_sql is None:
        return _no_answer(asked_at, None, [])
    guarded = guard_sql(raw_sql)  # önbellekten gelen SQL de korumadan geçer
    try:
        columns, rows = run_sql(guarded.sql)
    except SQLAlchemyError as first_error:
        error_text = _db_error_text(first_error)
        log.info("SQL hatası, bir kez yeniden deneniyor: %s", error_text)
        cached = False
        retry_sql = _generate_sql(question, bank, previous_sql=guarded.sql, error=error_text)
        if retry_sql is None:
            return _no_answer(asked_at, guarded.sql, guarded.sources)
        guarded = guard_sql(retry_sql)
        try:
            columns, rows = run_sql(guarded.sql)
        except SQLAlchemyError as second_error:
            log.warning("SQL ikinci denemede de başarısız: %s", _db_error_text(second_error))
            return _no_answer(asked_at, guarded.sql, guarded.sources)
    answer = summarize(question, columns, rows)
    return AskResult(
        ok=True,
        answer=answer,
        sql=guarded.sql,
        rows=rows,
        columns=columns,
        sources=guarded.sources,
        asked_at=asked_at,
        cached=cached,
        model=model_label(),
    )


def ask(question: str, db: Session) -> AskResult:
    """Uçtan uca. GuardError → 400, LLMError → 503 (router çevirir). Her soru chat_log'a yazılır."""
    asked_at = datetime.now(UTC)
    try:
        result = _ask(question, asked_at)
    except GuardError as e:
        log.warning("koruma reddi: %s", e)
        _log_chat(db, question, e.sql, GUARD_MESSAGE, ok=False)
        raise
    except llm.LLMError as e:
        log.warning("LLM erişilemedi: %s", e)
        _log_chat(db, question, None, UNAVAILABLE_MESSAGE, ok=False)
        raise
    log.info(
        "asistan: ok=%s cached=%s rows=%d sources=%s model=%s",
        result.ok,
        result.cached,
        len(result.rows),
        result.sources,
        result.model,
    )
    _log_chat(db, question, result.sql, result.answer, ok=result.ok)
    return result
