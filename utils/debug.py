import functools
import logging
import traceback
from typing import Callable, Any

logger = logging.getLogger(__name__)

def catch_exceptions(func: Callable) -> Callable:
    """
    A decorator that wraps the passed function and catches exceptions.
    
    This is useful for event handlers in PyQt that might silently fail.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Exception in {func.__name__}: {str(e)}",
                exc_info=True
            )
            # You could show a message box here if desired
            # The important part is that we're logging the error
            # and allowing the application to continue running
            return None
    return wrapper
