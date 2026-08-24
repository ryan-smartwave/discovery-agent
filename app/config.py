from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DA_")

    database_url: str = "postgresql+psycopg://postgres@127.0.0.1:5432/discovery"
    secret_key: str = "dev-only-not-a-secret"


def get_settings() -> Settings:
    return Settings()
