import os
from pydantic_settings import BaseSettings

from app.common.constants import PathConstants

class Env(BaseSettings):
    app_env:str
    mongo_uri: str
    redis_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class GlobalSettings():
    STATIC_DIR: str = os.path.join(PathConstants.APP_DIR, "static")
    


    def __str__(self):
        return f"Sets global settings for application."



env = Env()
globalSettings = GlobalSettings()