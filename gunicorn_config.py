import os
import logging
from multiprocessing import cpu_count

logger = logging.getLogger(f"TV_backend.{__name__}")
port = int(os.getenv("DOMAIN", "http://127.0.0.1:8013").split(":")[2])


def max_workers():
    return max(cpu_count() // 2 - 1, 4)


timeout = False
preload_app = False
wsgi_app = "main:app"
workers = max_workers()
graceful_timeout = False
bind = f"0.0.0.0:{port}"
worker_class = "uvicorn.workers.UvicornWorker"
