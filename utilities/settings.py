from pydantic_settings import BaseSettings

class EnvSetting(BaseSettings):
    db: str = "postgresql"
    db_name: str
    db_username: str = "postgres"
    db_password: str
    db_host: str = "localhost"
    host: str = "127.0.0.1"
    port: str = "8000"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 43200 # (in total 1 month)

    class Config:
        env_file = ".env"


setting = EnvSetting()
