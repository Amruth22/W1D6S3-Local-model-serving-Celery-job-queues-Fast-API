import os
from celery import Celery
from pathlib import Path

# Try to import settings, use fallback if not available
try:
    from config.settings import (
        CELERY_BROKER_URL, 
        CELERY_RESULT_BACKEND,
        CELERY_TASK_SERIALIZER,
        CELERY_RESULT_SERIALIZER,
        CELERY_ACCEPT_CONTENT,
        CELERY_TIMEZONE,
        CELERY_ENABLE_UTC,
        CELERY_RESULTS_DIR,
        TASK_TIMEOUT
    )
except ImportError:
    # Fallback configuration
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    CELERY_RESULTS_DIR = DATA_DIR / "celery_results"
    
    CELERY_BROKER_URL = f"filesystem://"
    CELERY_RESULT_BACKEND = f"file://{CELERY_RESULTS_DIR}"
    
    # Create broker transport options for filesystem
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'data_folder_in': str(DATA_DIR / 'celery_broker' / 'out'),
        'data_folder_out': str(DATA_DIR / 'celery_broker' / 'out'),
        'data_folder_processed': str(DATA_DIR / 'celery_broker' / 'processed'),
    }
    
    # Create broker directories
    broker_dirs = [
        DATA_DIR / 'celery_broker' / 'out',
        DATA_DIR / 'celery_broker' / 'processed'
    ]
    for broker_dir in broker_dirs:
        os.makedirs(broker_dir, exist_ok=True)
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TIMEZONE = "UTC"
    CELERY_ENABLE_UTC = True
    TASK_TIMEOUT = 300
    print("⚠️  Using fallback Celery configuration")

# Create celery results directory
os.makedirs(CELERY_RESULTS_DIR, exist_ok=True)

# Create Celery app
celery_app = Celery('rag_tasks')

# Configure Celery
celery_app.conf.update(
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    task_serializer=CELERY_TASK_SERIALIZER,
    result_serializer=CELERY_RESULT_SERIALIZER,
    accept_content=CELERY_ACCEPT_CONTENT,
    timezone=CELERY_TIMEZONE,
    enable_utc=CELERY_ENABLE_UTC,
    task_time_limit=TASK_TIMEOUT,
    task_soft_time_limit=TASK_TIMEOUT - 30,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
    task_ignore_result=False,
    result_expires=3600,  # Results expire after 1 hour
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['tasks'])

if __name__ == '__main__':
    celery_app.start()