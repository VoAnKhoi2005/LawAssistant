# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_uri: str
    db_name: str
    jwt_secret_key: str
    jwt_refresh_secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = None
    openai_api_key: str
    openai_model: str
    google_application_credentials: str
    google_cloud_storage_bucket: str
    vncorenlp_model_path: str
    phonlp_model_path: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()