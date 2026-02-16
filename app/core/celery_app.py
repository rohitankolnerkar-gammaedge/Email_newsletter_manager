# app/core/celery_app.py
import os
import ssl

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL is not set")

# -----------------------------
# Celery app setup
# -----------------------------
celery_app = Celery(
    "newsletter_worker",
    broker=REDIS_URL,  # Redis Cloud
    backend=REDIS_URL,  # Redis Cloud as backend
)

# Make this Celery instance the default
celery_app.set_default()

# -----------------------------
# SSL for Redis Cloud
# -----------------------------
if REDIS_URL.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
    celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}

# -----------------------------
# Task routing
# -----------------------------
celery_app.conf.task_routes = {
    "app.tasks.send_campaign_emails.send_campaign_emails": {"queue": "emails"}
}

# -----------------------------
# Connection resilience
# -----------------------------
celery_app.conf.update(
    broker_connection_retry=True,
    broker_connection_max_retries=None,  # retry indefinitely
    broker_connection_retry_on_startup=True,
    broker_pool_limit=None,  # unlimited connections
    task_acks_late=True,  # ensures task won't be lost
    worker_prefetch_multiplier=1,  # safer for multiple workers
)

# -----------------------------
# Import tasks
# -----------------------------
celery_app.conf.imports = [
    "app.tasks.send_campaign_emails",
]
