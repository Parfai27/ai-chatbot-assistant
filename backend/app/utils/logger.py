import logging
import os
from pythonjsonlogger import json as jsonlogger
from app.config import Config


def setup_logger(app):
    """Configure JSON-structured logging"""
    logger = logging.getLogger(app.config.get('APP_NAME', 'AI Chatbot Assistant'))
    logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO))

    if not logger.handlers:
        os.makedirs('logs', exist_ok=True)
        log_file = 'logs/app.log'

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO))

        # JSON formatter
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s',
            rename={'levelname': 'level', 'asctime': 'timestamp'}
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
