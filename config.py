from pydantic import BaseSettings


class Settings (BaseSettings):
    # Basic auth credentials
    api_key: str
    api_secret: str
    debug: bool

    # read from env
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
