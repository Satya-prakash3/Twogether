import os
from pydantic_settings import BaseSettings

from app.common.constants import PathConstants
from app.api.user.models import User


class Env(BaseSettings):
    app_env: str
    mongo_uri: str
    redis_url: str = "redis://localhost:6379/0"

    enable_elk_logging: bool = False
    logstash_host: str = "localhost"
    logstash_port: int = 5044

    jwt_algorithm: str = "RS256"
    jwt_private_key_path: str = "./keys/jwt_private.pem"
    jwt_public_key_path: str = "./keys/jwt_public.pem"
    jwt_kid: str = "default"
    access_token_expire_seconds: int = 900
    refresh_token_expire_seconds: int = 1209600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class GlobalSettings:
    STATIC_DIR: str = os.path.join(PathConstants.APP_DIR, "static")
    BEANIE_MODELS: list = [User]

    def __str__(self):
        return f"Sets global settings for application."


env = Env()
globalSettings = GlobalSettings()
