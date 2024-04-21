import logging

from common_engine import engine
from user_content_device_models import Base as UserBase

logger = logging.getLogger(f"TV_backend.{__name__}")


try:
    UserBase.metadata.create_all(engine)
    logger.info("Created successfully!")
except Exception as e:
    logger.error(f"Connection failed: {e}")
