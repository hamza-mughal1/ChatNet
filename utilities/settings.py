from pydantic_settings import BaseSettings

class EnvSetting(BaseSettings):
    db: str = "postgresql"
    db_name: str
    db_username: str = "postgres"
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    redis_host: str
    redis_port: int
    redis_db: str
    test_db_port: int
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 43200 # (in total 1 month)

    class Config:
        env_file = ".env"


setting = EnvSetting()
