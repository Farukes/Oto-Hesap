"""Tek LLM adaptörü. Sağlayıcı .env'den: anthropic | gemini | groq | ollama | fake.

Kural: iş mantığı sağlayıcıya bağımlı değildir; buradan yalnız `complete()` çağrılır.
`fake` sağlayıcı testler içindir; `set_fake_handler()` ile yanıt belirlenir.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from ..config import settings

log = logging.getLogger("otohesap.llm")


class LLMError(RuntimeError):
    """Sağlayıcıya ulaşılamadı veya anahtar eksik."""


FakeHandler = Callable[[str, str], str]
_fake_handler: FakeHandler | None = None


def set_fake_handler(handler: FakeHandler | None) -> None:
    """Testler: (system, user) -> str döndüren bir fonksiyon ver."""
    global _fake_handler
    _fake_handler = handler


def provider_name() -> str:
    return settings.llm_provider


def complete(system: str, user: str, *, max_tokens: int = 800, model: str | None = None) -> str:
    """Tek tur tamamlama. Metin döner; çağıran taraf ayrıştırır."""
    provider = settings.llm_provider
    if provider == "fake":
        if _fake_handler is None:
            return '{"sql": "SELECT 1 AS bir"}'
        return _fake_handler(system, user)
    if provider == "anthropic":
        return _anthropic(system, user, max_tokens=max_tokens, model=model)
    if provider == "gemini":
        return _gemini(system, user, max_tokens=max_tokens, model=model)
    if provider == "groq":
        return _openai_compatible(
            "https://api.groq.com/openai/v1",
            settings.groq_api_key,
            model or settings.groq_model,
            system,
            user,
            max_tokens=max_tokens,
            label="Groq",
        )
    if provider == "ollama":
        return _openai_compatible(
            settings.ollama_base_url,
            "ollama",
            model or settings.ollama_model,
            system,
            user,
            max_tokens=max_tokens,
            label="Ollama",
            timeout=120,
        )
    raise LLMError(f"Bilinmeyen sağlayıcı: {provider}")


def _anthropic(system: str, user: str, *, max_tokens: int, model: str | None) -> str:
    if not settings.anthropic_api_key:
        raise LLMError("ANTHROPIC_API_KEY tanımlı değil")
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    model_id = model or settings.anthropic_model
    kwargs: dict = {}
    # Haiku 4.5 ve 4.6 ailesi sıcaklık kabul eder; Sonnet 5 / Opus 5'te parametre reddedilir.
    if "haiku" in model_id or "4-6" in model_id:
        kwargs["temperature"] = 0
    else:
        kwargs["output_config"] = {"effort": "low"}
    try:
        resp = client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            **kwargs,
        )
    except anthropic.APIStatusError as e:  # 4xx/5xx
        raise LLMError(f"Anthropic hata {e.status_code}: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise LLMError("Anthropic'e bağlanılamadı") from e
    if resp.stop_reason == "refusal":
        raise LLMError("Model isteği reddetti")
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def _gemini(system: str, user: str, *, max_tokens: int, model: str | None) -> str:
    if not settings.gemini_api_key:
        raise LLMError("GEMINI_API_KEY tanımlı değil")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    try:
        resp = client.models.generate_content(
            model=model or settings.gemini_model,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system, temperature=0, max_output_tokens=max_tokens
            ),
        )
    except Exception as e:  # noqa: BLE001
        raise LLMError(f"Gemini hata: {e}") from e
    return (resp.text or "").strip()


def _openai_compatible(
    base_url: str,
    api_key: str | None,
    model_id: str,
    system: str,
    user: str,
    *,
    max_tokens: int,
    label: str,
    timeout: float = 30,
) -> str:
    """OpenAI uyumlu chat/completions ucu (Groq bulutu, Ollama yerel); ek SDK yok, httpx ile."""
    if not api_key:
        raise LLMError(f"{label} için API anahtarı tanımlı değil")
    import httpx

    payload = {
        "model": model_id,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    try:
        resp = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=timeout,
        )
    except httpx.HTTPError as e:
        raise LLMError(f"{label} sunucusuna bağlanılamadı") from e
    if resp.status_code >= 400:
        raise LLMError(f"{label} hata {resp.status_code}")  # gövde loglanmaz
    data = resp.json()
    try:
        return (data["choices"][0]["message"]["content"] or "").strip()
    except (KeyError, IndexError) as e:
        raise LLMError(f"{label} beklenmeyen yanıt biçimi") from e
