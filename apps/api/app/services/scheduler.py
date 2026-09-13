"""APScheduler: tedarik ajanını AGENT_CHECK_INTERVAL_MIN dakikada bir koşturur. Sahibi: Ömer.

Demoda buton (`POST /api/agent/check`) yeter; zamanlayıcı "10 dakikada bir" cümlesi içindir.
Render uykuya girince fiilen durur (bkz. docs/team/muratcan.md, warmup notu).
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from ..config import settings
from ..db import SessionLocal
from .agent import run_check

log = logging.getLogger("otohesap.scheduler")

JOB_ID = "agent_check"


def _job() -> None:
    try:
        with SessionLocal() as db:
            result = run_check(db)
    except Exception:  # noqa: BLE001 — zamanlayıcı bir hatada ölmesin, bir sonraki turda dener
        log.exception("ajan zamanlayıcı turu başarısız")
        return
    log.info("ajan: %d taslak, %d atlandı", result["created"], len(result["skipped"]))


def start_scheduler() -> BackgroundScheduler:
    sched = BackgroundScheduler(timezone="Europe/Istanbul")
    sched.add_job(
        _job,
        "interval",
        minutes=settings.agent_check_interval_min,
        id=JOB_ID,
        misfire_grace_time=60,
        coalesce=True,
        max_instances=1,
        replace_existing=True,
    )
    sched.start()
    log.info("zamanlayıcı başladı: her %s dk", settings.agent_check_interval_min)
    return sched
