import logging
import os
import sys
from config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    """Configure application-wide logging with file and console handlers."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Fix for handling Unicode in Windows console, but with proper checks
    # to avoid errors when sys.stdout is redirected in packaged app
    if sys.platform == 'win32' and hasattr(sys, 'frozen') and hasattr(sys.stdout, 'buffer'):
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except (AttributeError, TypeError):
            # Skip if stdout/stderr don't have expected attributes in packaged app
            pass
    
    # Set up file handler
    file_handler = logging.FileHandler(os.path.join(log_dir, LOG_FILE))
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # Only add console handler if we're not in a frozen app or explicitly want console
    handlers = [file_handler]
    try:
        # Add console handler with error handling
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        handlers.append(console_handler)
    except (AttributeError, TypeError):
        # Skip console handler if there's an issue
        pass
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        handlers=handlers
    )
    
    # Log startup information
    logging.info("Logging initialized")
    return logging.getLogger(__name__)