import logging
import os
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

LOG_DIR = "log"
LOG_FILE = os.path.join(LOG_DIR, f"errors_{timestamp}.log")

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set default logging level

c_handler = logging.StreamHandler() # Console handler
f_handler = logging.FileHandler(LOG_FILE) # File handler

c_handler.setLevel(logging.INFO) # Console shows INFO and above
f_handler.setLevel(logging.ERROR) # File shows ERROR and above (for detailed errors)

c_format = logging.Formatter('%(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

if not logger.handlers:
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

def log_error(message, exc_info=False):
    logger.error(message, exc_info=exc_info)

def log_info(message):
    logger.info(message)
