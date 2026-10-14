import pytest

from chatbot.config import Settings


def test_loads_local_defaults(monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_CHAT_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("CHAT_REQUEST_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("MAX_HISTORY_MESSAGES", raising=False)
    monkeypatch.delenv("DATA_DIRECTORY", raising=False)

    settings = Settings.from_environment()

    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.chat_model == "mistral"
    assert settings.max_history_messages == 20


@pytest.mark.parametrize(
    ("variable", "value", "message"),
    [
        ("CHAT_REQUEST_TIMEOUT_SECONDS", "invalid", "must be an integer"),
        ("CHAT_REQUEST_TIMEOUT_SECONDS", "0", "greater than zero"),
        ("MAX_HISTORY_MESSAGES", "invalid", "must be an integer"),
        ("MAX_HISTORY_MESSAGES", "0", "greater than zero"),
    ],
)
def test_rejects_invalid_limits(monkeypatch, variable, value, message):
    monkeypatch.setenv(variable, value)

    with pytest.raises(ValueError, match=message):
        Settings.from_environment()