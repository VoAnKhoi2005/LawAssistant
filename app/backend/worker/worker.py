import os
import sys

# Add backend root directory to Python path
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

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
