import os
from dataclasses import dataclass

@dataclass(frozen=True)
class PathConstants():

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@dataclass(frozen=True)
class Constants():
    
    APP_NAME = "StreamDock"
    APP_HOST = "0.0.0.0"
    APP_PORT = 8000
    TIME_ZONE = "Asia/Kolkata"
    API_V1_URL = "/api/v1"

