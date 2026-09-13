"""SQLAlchemy motorları: uygulama (yazar) ve asistan (salt-okur, 5 sn zaman aşımı)."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,
    connect_args={"options": "-c timezone=UTC"},  # görünüm ve özet aynı dilimde kessin
)

# Asistan bağlantısı: rol salt-okur olmasa bile işlem düzeyinde salt-okur + zaman aşımı
engine_ro = create_engine(
    settings.sqlalchemy_url_ro,
    pool_pre_ping=True,
    connect_args={
        "options": "-c timezone=UTC -c statement_timeout=5000 -c default_transaction_read_only=on"
    },
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def db_ok() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001
        return False
