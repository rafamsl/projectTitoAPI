import logging
import sys
from datetime import datetime

def setup_logger():
    logger = logging.getLogger('story_generator')
    logger.setLevel(logging.INFO)

    # Console handler only (Render will capture this)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Format with timestamp and request details
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger

logger = setup_logger() 