import os
import sys

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.celery_app import celery_app

if __name__ == "__main__":
    # Start the worker
    celery_app.start([
        'worker',
        '--loglevel=info',
        '--queues=documents',
        '--concurrency=2',
        '--pool=prefork'
    ])