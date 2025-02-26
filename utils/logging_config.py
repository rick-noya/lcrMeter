import logging
import os
from config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    """Configure application-wide logging with file and console handlers."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up basic configuration
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(os.path.join(log_dir, LOG_FILE)),
            logging.StreamHandler()  # Console output
        ]
    )
    
    # Log startup information
    logging.info("Logging initialized")
    return logging.getLogger(__name__)