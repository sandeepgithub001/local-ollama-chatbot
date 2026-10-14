import pytest

from chatbot.ollama_service import OllamaService, OllamaServiceError


class FakeOllamaClient:
    def list(self):
        return {"models": [{"name": "qwen2.5:latest"}, {"model": "llama3.2:latest"}]}

    def chat(self, model, messages, stream):
        assert model == "qwen2.5:latest"
        assert messages[-1]["content"] == "Hi"
        assert stream is True
        return iter(
            [
                {"message": {"content": "Hello"}},
                {"message": {"content": " there."}},
            ]
        )


def test_lists_available_models():
    service = OllamaService("http://localhost:11434", client=FakeOllamaClient())

    assert service.list_models() == ["qwen2.5:latest", "llama3.2:latest"]


def test_streams_chat_content():
    service = OllamaService("http://localhost:11434", client=FakeOllamaClient())

    chunks = list(
        service.stream_chat(
            model="qwen2.5:latest",
            messages=[{"role": "user", "content": "Hi"}],
        )
    )

    assert chunks == ["Hello", " there."]


def test_wraps_connection_errors():
    class UnavailableClient:
        def list(self):
            raise ConnectionError("offline")

    service = OllamaService("http://localhost:11434", client=UnavailableClient())

    with pytest.raises(OllamaServiceError, match="Could not connect to Ollama"):
        service.list_models()