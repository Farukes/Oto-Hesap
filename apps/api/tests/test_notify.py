"""services/notify: dry-run yolları, Telegram gönderimi (sahte httpx istemcisi), hata → NotifyError,
token hiçbir log ve hata mesajında yer almaz. Ağa çıkılmaz."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import pytest

from app.config import settings
from app.models import Supplier
from app.services import notify
from app.services.notify import NotifyError, send_message, send_telegram

TOKEN = "123456:ABC-DEF_gizli-token"


class FakeResponse:
    def __init__(self, status_code: int, body: Any, *, raw: str | None = None) -> None:
        self.status_code = status_code
        self._body = body
        self.text = raw if raw is not None else str(body).replace("'", '"')

    def json(self) -> Any:
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


class FakeClient:
    """`httpx.Client` yerine geçer: `with ... as c: c.post(url, json=...)`."""

    def __init__(self, response: FakeResponse | Exception) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def __enter__(self) -> FakeClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def post(self, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class NetworkForbidden:
    def __call__(self) -> FakeClient:
        raise AssertionError("dry-run yolunda ağ istemcisi oluşturulmamalı")


def _telegram_supplier() -> Supplier:
    return Supplier(
        name="Kablo A.Ş.", contact_channel="telegram", contact_address="111", lead_time_days=2
    )


def _email_supplier() -> Supplier:
    return Supplier(
        name="Güç Ltd.",
        contact_channel="email",
        contact_address="guc@example.com",
        lead_time_days=3,
    )


@pytest.fixture
def live_mode(monkeypatch: pytest.MonkeyPatch):
    """Dry-run kapalı + token var: gerçek gönderim yolu (ama istemci sahte)."""
    monkeypatch.setattr(settings, "notify_dry_run", False)
    monkeypatch.setattr(settings, "telegram_bot_token", TOKEN)


def _install(monkeypatch: pytest.MonkeyPatch, response: FakeResponse | Exception) -> FakeClient:
    client = FakeClient(response)
    monkeypatch.setattr(notify, "_new_client", lambda: client)
    return client


# ---------------------------------------------------------------- dry-run yolları


def test_email_channel_is_dry_run(monkeypatch: pytest.MonkeyPatch, caplog):
    monkeypatch.setattr(settings, "notify_dry_run", False)
    monkeypatch.setattr(settings, "telegram_bot_token", TOKEN)
    monkeypatch.setattr(notify, "_new_client", NetworkForbidden())
    with caplog.at_level(logging.INFO, logger="otohesap.notify"):
        result = send_message(_email_supplier(), "merhaba")
    assert result == {"ok": True, "dry_run": True, "channel": "email"}
    assert "e-posta" in caplog.text and TOKEN not in caplog.text


def test_telegram_dry_run_flag(monkeypatch: pytest.MonkeyPatch, caplog):
    monkeypatch.setattr(settings, "notify_dry_run", True)
    monkeypatch.setattr(settings, "telegram_bot_token", TOKEN)
    monkeypatch.setattr(notify, "_new_client", NetworkForbidden())
    with caplog.at_level(logging.INFO, logger="otohesap.notify"):
        result = send_message(_telegram_supplier(), "merhaba")
    assert result == {"ok": True, "dry_run": True, "channel": "telegram"}
    assert "dry-run" in caplog.text and "chat_id=111" in caplog.text
    assert TOKEN not in caplog.text


def test_telegram_without_token_is_dry_run(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "notify_dry_run", False)
    monkeypatch.setattr(settings, "telegram_bot_token", "")
    monkeypatch.setattr(notify, "_new_client", NetworkForbidden())
    assert send_telegram("111", "x") == {"ok": True, "dry_run": True, "channel": "telegram"}


def test_unknown_channel_raises():
    s = Supplier(name="X", contact_channel="faks", contact_address="1", lead_time_days=1)
    with pytest.raises(NotifyError):
        send_message(s, "x")


# ---------------------------------------------------------------- gerçek gönderim (sahte istemci)


def test_telegram_send_success(live_mode, monkeypatch: pytest.MonkeyPatch, caplog):
    client = _install(
        monkeypatch, FakeResponse(200, {"ok": True, "result": {"message_id": 42, "chat": {}}})
    )
    with caplog.at_level(logging.INFO, logger="otohesap.notify"):
        result = send_message(_telegram_supplier(), "Merhaba Kablo A.Ş.")

    assert result == {"ok": True, "dry_run": False, "channel": "telegram", "message_id": 42}
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["url"] == f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    assert call["json"] == {"chat_id": "111", "text": "Merhaba Kablo A.Ş."}
    assert "parse_mode" not in call["json"]
    assert "message_id=42" in caplog.text and TOKEN not in caplog.text


def test_telegram_http_error_raises_without_token(live_mode, monkeypatch, caplog):
    body = '{"ok":false,"error_code":401,"description":"Unauthorized"}'
    _install(monkeypatch, FakeResponse(401, {"ok": False}, raw=body))
    with (
        caplog.at_level(logging.WARNING, logger="otohesap.notify"),
        pytest.raises(NotifyError) as ei,
    ):
        send_telegram("111", "x")
    msg = str(ei.value)
    assert "401" in msg and "Unauthorized" in msg
    assert TOKEN not in msg and TOKEN not in caplog.text


def test_telegram_ok_false_raises(live_mode, monkeypatch):
    body = '{"ok":false,"description":"Bad Request: chat not found"}'
    _install(monkeypatch, FakeResponse(200, {"ok": False}, raw=body))
    with pytest.raises(NotifyError) as ei:
        send_telegram("999", "x")
    assert "chat not found" in str(ei.value) and TOKEN not in str(ei.value)


def test_telegram_body_with_token_is_redacted(live_mode, monkeypatch, caplog):
    # Telegram token'ı geri yansıtmaz; yine de sızarsa maskelenmeli.
    raw = f'{{"ok":false,"description":"bad {TOKEN}"}}'
    _install(monkeypatch, FakeResponse(400, {"ok": False}, raw=raw))
    with (
        caplog.at_level(logging.WARNING, logger="otohesap.notify"),
        pytest.raises(NotifyError) as ei,
    ):
        send_telegram("111", "x")
    assert TOKEN not in str(ei.value) and "***" in str(ei.value)
    assert TOKEN not in caplog.text


def test_telegram_network_error_raises(live_mode, monkeypatch, caplog):
    req = httpx.Request("POST", f"https://api.telegram.org/bot{TOKEN}/sendMessage")
    _install(monkeypatch, httpx.ConnectError("connection refused", request=req))
    with (
        caplog.at_level(logging.WARNING, logger="otohesap.notify"),
        pytest.raises(NotifyError) as ei,
    ):
        send_telegram("111", "x")
    assert "ConnectError" in str(ei.value)
    assert TOKEN not in str(ei.value) and TOKEN not in caplog.text


def test_telegram_timeout_raises(live_mode, monkeypatch):
    req = httpx.Request("POST", "https://api.telegram.org/x")
    _install(monkeypatch, httpx.ReadTimeout("timed out", request=req))
    with pytest.raises(NotifyError) as ei:
        send_telegram("111", "x")
    assert "zaman aşımı" in str(ei.value)


def test_default_client_timeout_is_ten_seconds():
    with notify._new_client() as c:
        assert c.timeout.read == 10.0 and c.timeout.connect == 10.0
