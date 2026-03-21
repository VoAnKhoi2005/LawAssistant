"""
Celery application configuration for document processing tasks
"""
import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "document_processor",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.document_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    "tasks.document_tasks.process_document": {"queue": "documents"},
    "tasks.document_tasks.extract_text": {"queue": "documents"},
    "tasks.document_tasks.simplify_sentences": {"queue": "documents"},
    "tasks.document_tasks.extract_triplets": {"queue": "documents"},
}

if __name__ == "__main__":
    celery_app.start()