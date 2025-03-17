import logging

logger = logging.getLogger("uvicorn")

logger.setLevel(logging.INFO)

def get_logger():
    return logger
