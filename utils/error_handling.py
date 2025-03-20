"""
Standardized error handling utilities for the LCR Meter application.
Provides consistent patterns for error handling across the application.
"""

import functools
import logging
import traceback
from typing import Callable, Any, Optional
from enum import Enum, auto
import asyncio

logger = logging.getLogger(__name__)

class ErrorAction(Enum):
    """Define how errors should be handled after logging."""
    LOG_ONLY = auto()      # Just log the error
    RERAISE = auto()       # Log and re-raise the exception
    RETURN_NONE = auto()   # Log and return None
    RETURN_FALSE = auto()  # Log and return False

def handle_errors(action: ErrorAction = ErrorAction.RERAISE, ui_logger=None):
    """
    Decorator that wraps a function with standardized error handling.
    
    Args:
        action: What to do after logging the error
        ui_logger: Optional function to log to UI (MainWindow.append_log)
    """
    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func)
        
        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # Log the error with consistent format
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True
                    )
                    
                    # Log to UI if provided
                    if ui_logger:
                        ui_logger(f"Error: {str(e)}")
                    
                    # Handle according to specified action
                    if action == ErrorAction.RERAISE:
                        raise
                    elif action == ErrorAction.RETURN_NONE:
                        return None
                    elif action == ErrorAction.RETURN_FALSE:
                        return False
                    # LOG_ONLY just continues
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Log the error with consistent format
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True
                    )
                    
                    # Log to UI if provided
                    if ui_logger:
                        ui_logger(f"Error: {str(e)}")
                    
                    # Handle according to specified action
                    if action == ErrorAction.RERAISE:
                        raise
                    elif action == ErrorAction.RETURN_NONE:
                        return None
                    elif action == ErrorAction.RETURN_FALSE:
                        return False
                    # LOG_ONLY just continues
            return sync_wrapper
        
    return decorator

def ui_error_handler(func):
    """
    Specific decorator for UI operations that might fail.
    Logs errors but doesn't crash the application.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"UI error in {func.__name__}: {str(e)}", exc_info=True)
            try:
                # Attempt to log to UI if this appears to be a MainWindow instance
                if hasattr(self, 'append_log'):
                    self.append_log(f"Error: {str(e)}")
            except:
                pass  # Don't let error handling cause more errors
            return None
    return wrapper

async def safe_async_call(coro, error_message="Operation failed", ui_logger=None):
    """
    Utility function for safely calling async functions with standardized error handling.
    
    Args:
        coro: Coroutine to execute
        error_message: User-friendly message if operation fails
        ui_logger: Optional function to log to UI
    
    Returns:
        Result of coroutine or None if failed
    """
    try:
        return await coro
    except Exception as e:
        logger.error(f"{error_message}: {str(e)}", exc_info=True)
        if ui_logger:
            ui_logger(f"{error_message}: {str(e)}")
        return None

def to_thread_with_error_handling(func, *args, error_message="Operation failed", ui_logger=None, **kwargs):
    """
    Run a blocking function in a thread with standardized error handling.
    Useful for UI code that needs to run blocking operations without freezing the interface.
    
    Args:
        func: Function to execute in thread
        args: Arguments to pass to func
        error_message: User-friendly message if operation fails
        ui_logger: Optional function to log to UI
        kwargs: Keyword arguments to pass to func
        
    Returns:
        Awaitable that resolves to function result or None if failed
    """
    async def wrapped():
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}", exc_info=True)
            if ui_logger:
                ui_logger(f"{error_message}: {str(e)}")
            return None
    
    return wrapped()