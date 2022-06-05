import sys

from django.conf import settings
from loguru import logger

PRIME_DIR = f"{settings.BASE_DIR}/logs/"

dev_config = {
    "handlers": [
        {"sink": sys.stdout, "level": "INFO"},
    ],
}

logger.configure(**dev_config)

service_logger = logger
