import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(level=logging.INFO)
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=5)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
file_log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(file_log_handler)
