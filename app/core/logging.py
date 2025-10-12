import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO"):
  formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )

  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(formatter)

  file_handler = RotatingFileHandler(
    'app.log', maxBytes=10*1024*1024, backupCount=5
  )
  file_handler.setFormatter(formatter)

  root_logger = logging.getLogger()
  root_logger.setLevel(getattr(logging, log_level))
  root_logger.addHandler(console_handler)
  root_logger.addHandler(file_handler)

  logging.getLogger("langchain").setLevel(logging.WARNING)
  logging.getLogger("chromadb").setLevel(logging.WARNING)
