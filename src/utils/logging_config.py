"""
Configure Python logging: console + rotating file
"""
import os
import logging
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger('transcriber')
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Rotating file handler
file_handler = RotatingFileHandler(
    filename=os.path.join(LOGS_DIR, 'app.log'),
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
