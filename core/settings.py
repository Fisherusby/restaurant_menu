from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Dishes menu'
    DOCS_URL: str = "/swagger"
    API_PREFIX: str = "/api/v1"
    VERSION: str = '0.0.1'

    SQLALCHEMY_DATABASE_URL: str

    SQLALCHEMY_SYNC_DATABASE_URL: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    class Config:
        case_sensitive = True


settings: Settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
