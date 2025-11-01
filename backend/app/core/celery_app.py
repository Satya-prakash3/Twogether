from celery import Celery
from app.core.config import (
    env,
)
from app.common.constants import Constants


celery_app = Celery(
    Constants.APP_NAME,
    broker=env.redis_url,         
    backend=env.redis_url,        
    include=["app.common.tasks"] 
)

celery_app.conf.update(
    broker_transport_options={"visibility_timeout": 3600},
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=Constants.TIME_ZONE,
    enable_utc=True,
)
