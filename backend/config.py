from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    frontend_url: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env")
    test_database_url: str | None = None

settings = Settings()