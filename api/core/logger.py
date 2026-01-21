from pathlib import Path
from loguru import logger

def setup_logger():
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/app.log",retention="1 day",rotation="500 MB")
