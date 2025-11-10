import time
from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.example.long_task")
def long_task(x, y):
    time.sleep(5)  # Simulate a heavy computation
    return {"result": x + y, "status": "completed"}
