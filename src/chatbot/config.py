from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str
    chat_model: str
    embedding_model: str
    chat_request_timeout_seconds: int
    max_history_messages: int
    data_directory: str

    @classmethod
    def from_environment(cls) -> "Settings":
        timeout_value = os.getenv("CHAT_REQUEST_TIMEOUT_SECONDS", "120")
        try:
            timeout_seconds = int(timeout_value)
        except ValueError as error:
            raise ValueError("CHAT_REQUEST_TIMEOUT_SECONDS must be an integer.") from error
        if timeout_seconds <= 0:
            raise ValueError("CHAT_REQUEST_TIMEOUT_SECONDS must be greater than zero.")

        history_value = os.getenv("MAX_HISTORY_MESSAGES", "20")
        try:
            max_history_messages = int(history_value)
        except ValueError as error:
            raise ValueError("MAX_HISTORY_MESSAGES must be an integer.") from error
        if max_history_messages <= 0:
            raise ValueError("MAX_HISTORY_MESSAGES must be greater than zero.")

        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
            chat_model=os.getenv("OLLAMA_CHAT_MODEL", "mistral").strip() or "mistral",
            embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text").strip(),
            chat_request_timeout_seconds=timeout_seconds,
            max_history_messages=max_history_messages,
            data_directory=os.getenv("DATA_DIRECTORY", "data").strip(),
        )