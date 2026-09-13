from app.services import llm


def test_fake_provider_default_and_handler():
    assert llm.provider_name() == "fake"
    assert "SELECT" in llm.complete("s", "u")
    llm.set_fake_handler(lambda s, u: "ozel")
    try:
        assert llm.complete("s", "u") == "ozel"
    finally:
        llm.set_fake_handler(None)


def test_openai_compatible_parses_and_masks(monkeypatch):
    """Groq/Ollama yolu: gövde ayrıştırılır; hata durumunda anahtar mesaja sızmaz."""
    import httpx

    class _Resp:
        def __init__(self, code, body):
            self.status_code, self._body = code, body

        def json(self):
            return self._body

    calls = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        calls["url"], calls["auth"] = url, headers["Authorization"]
        return _Resp(200, {"choices": [{"message": {"content": ' {"sql": "SELECT 2"} '}}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    out = llm._openai_compatible(
        "http://localhost:11434/v1", "ollama", "qwen2.5:7b", "s", "u", max_tokens=10, label="Ollama"
    )
    assert out == '{"sql": "SELECT 2"}'
    assert calls["url"].endswith("/chat/completions") and calls["auth"] == "Bearer ollama"

    monkeypatch.setattr(httpx, "post", lambda *a, **k: _Resp(401, {}))
    try:
        llm._openai_compatible(
            "https://api.groq.com/openai/v1",
            "gsk_secret",
            "m",
            "s",
            "u",
            max_tokens=10,
            label="Groq",
        )
        raise AssertionError("LLMError beklenirdi")
    except llm.LLMError as e:
        assert "gsk_secret" not in str(e)
