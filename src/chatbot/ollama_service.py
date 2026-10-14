from collections.abc import Iterator, Mapping, Sequence
from typing import Any

from ollama import Client


class OllamaServiceError(RuntimeError):
    """Raised when a request to Ollama cannot be completed."""


class OllamaService:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: int = 120,
        client: Any | None = None,
    ) -> None:
        self._client = (
            client
            if client is not None
            else Client(host=base_url, timeout=timeout_seconds)
        )

    def list_models(self) -> list[str]:
        try:
            response = self._client.list()
            models = response.get("models", []) if isinstance(response, Mapping) else response.models
            names = []
            for model in models:
                if isinstance(model, Mapping):
                    name = model.get("model") or model.get("name")
                else:
                    name = getattr(model, "model", None) or getattr(model, "name", None)
                if name:
                    names.append(str(name))
            return names
        except Exception as error:
            raise OllamaServiceError(
                "Could not connect to Ollama. Check that it is running and the endpoint is correct."
            ) from error

    def stream_chat(
        self,
        model: str,
        messages: Sequence[Mapping[str, str]],
    ) -> Iterator[str]:
        try:
            for response in self._client.chat(
                model=model,
                messages=list(messages),
                stream=True,
            ):
                message = (
                    response.get("message", {})
                    if isinstance(response, Mapping)
                    else getattr(response, "message", None)
                )
                content = (
                    message.get("content", "")
                    if isinstance(message, Mapping)
                    else getattr(message, "content", "")
                )
                if content:
                    yield str(content)
        except Exception as error:
            raise OllamaServiceError(
                "Ollama could not complete the response. Check the model and try again."
            ) from error