from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    frontend_url: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    test_database_url: str | None = None

    # Local AI (Ollama). No API key: the model runs on this machine.
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: float = 90.0

    # Logging
    log_level: str = "INFO"
    log_file: str | None = "logs/helpdesk.log"

settings = Settings()
