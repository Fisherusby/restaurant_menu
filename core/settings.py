from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Dishes menu'
    DOCS_URL: str = '/swagger'
    API_PREFIX: str = '/api/v1'
    VERSION: str = '0.0.1'
    CONTACT_NAME: str = 'Alexei F.'
    CONTACT_EMAIL: str = 'fisheriusby@gmail.com'
    SUMMARY: str = 'This is project as a result of YLab`s intensive course'

    SQLALCHEMY_DATABASE_URL: str

    SQLALCHEMY_SYNC_DATABASE_URL: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    REDIS_CACHE_PASSWORD: str
    REDIS_CACHE_HOST: str
    REDIS_CACHE_PORT: int

    CACHE_LIFETIME: int = 60 * 5

    class Config:
        case_sensitive = True


settings: Settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
