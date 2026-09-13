"""Tedarikçi bildirimi — Telegram Bot API (DECISIONS D3). Sahibi: Ömer.

Kanal `telegram`: `POST https://api.telegram.org/bot{token}/sendMessage` (chat_id = tedarikçinin
`contact_address`'i). `NOTIFY_DRY_RUN=true` ya da token boşsa gönderilmez, loglanır.
Kanal `email`: bugün gönderim yok; dry-run gibi davranır ve loglar.

Kural: bot token'ı hiçbir log satırında ve hiçbir hata mesajında yer almaz.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ..config import settings
from ..models import Supplier

log = logging.getLogger("otohesap.notify")

TELEGRAM_API_BASE = "https://api.telegram.org"
TIMEOUT_SECONDS = 10.0
_BODY_PREVIEW = 300


class NotifyError(RuntimeError):
    """Mesaj gönderilemedi (ağ ya da HTTP hatası). Mesajda durum kodu/gövde var, token yok."""


def _new_client() -> httpx.Client:
    """HTTP istemcisi. Testler bu fonksiyonu sahte bir istemciyle monkeypatch'ler."""
    return httpx.Client(timeout=TIMEOUT_SECONDS)


def _redact(text: str, token: str | None) -> str:
    """Savunma katmanı: token bir şekilde metne sızdıysa maskele."""
    if token and token in text:
        return text.replace(token, "***")
    return text


def send_message(supplier: Supplier, text: str) -> dict[str, Any]:
    """Tedarikçinin kanalına göre mesajı iletir. Dönüş: {ok, dry_run, channel[, message_id]}."""
    channel = supplier.contact_channel
    if channel == "telegram":
        return send_telegram(supplier.contact_address, text)
    if channel == "email":
        log.info(
            "e-posta kanalı bugün gönderim yapmıyor (dry-run): tedarikçi=%s adres=%s uzunluk=%d",
            supplier.name,
            supplier.contact_address,
            len(text),
        )
        return {"ok": True, "dry_run": True, "channel": "email"}
    raise NotifyError(f"Bilinmeyen bildirim kanalı: {channel}")


def send_telegram(chat_id: str, text: str) -> dict[str, Any]:
    """Telegram sendMessage. Dry-run'da ağa çıkmaz; hata durumunda NotifyError fırlatır."""
    token = settings.telegram_bot_token or ""
    if settings.notify_dry_run or not token:
        reason = "NOTIFY_DRY_RUN" if settings.notify_dry_run else "token yok"
        log.info("telegram dry-run (%s): chat_id=%s uzunluk=%d", reason, chat_id, len(text))
        return {"ok": True, "dry_run": True, "channel": "telegram"}

    url = f"{TELEGRAM_API_BASE}/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        with _new_client() as client:
            resp = client.post(url, json=payload)
    except httpx.TimeoutException as e:
        log.warning("telegram zaman aşımı: chat_id=%s", chat_id)
        raise NotifyError("Telegram yanıt vermedi (zaman aşımı 10 sn).") from e
    except httpx.HTTPError as e:
        # str(e) URL içerebilir; yalnız tür adını kullan (token sızmasın).
        log.warning("telegram ağ hatası: chat_id=%s tur=%s", chat_id, type(e).__name__)
        raise NotifyError(f"Telegram'a bağlanılamadı ({type(e).__name__}).") from e

    body_preview = _redact(resp.text[:_BODY_PREVIEW], token)
    if resp.status_code >= 400:
        log.warning(
            "telegram HTTP %s: chat_id=%s govde=%s", resp.status_code, chat_id, body_preview
        )
        raise NotifyError(f"Telegram HTTP {resp.status_code}: {body_preview}")

    try:
        data = resp.json()
    except ValueError as e:
        log.warning("telegram gecersiz JSON: chat_id=%s govde=%s", chat_id, body_preview)
        raise NotifyError(f"Telegram geçersiz yanıt: {body_preview}") from e

    if not isinstance(data, dict) or not data.get("ok"):
        log.warning("telegram ok=false: chat_id=%s govde=%s", chat_id, body_preview)
        raise NotifyError(f"Telegram isteği reddetti: {body_preview}")

    message_id = (data.get("result") or {}).get("message_id")
    log.info("telegram gönderildi: chat_id=%s message_id=%s", chat_id, message_id)
    return {"ok": True, "dry_run": False, "channel": "telegram", "message_id": message_id}
