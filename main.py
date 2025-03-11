import sys
import os
import asyncio
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
from gui.main_window import MainWindow
from qasync import QEventLoop
from utils.logging_config import setup_logging
from components.supabase_db import get_supabase_client, verify_table_exists
from config.settings import validate_settings

logger = logging.getLogger(__name__)

def exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler to log uncaught exceptions"""
    logger.critical("Uncaught exception", 
                   exc_info=(exc_type, exc_value, exc_traceback))
    # Show error dialog for uncaught exceptions
    error_msg = f"An unexpected error occurred:\n{exc_value}"
    QMessageBox.critical(None, "Error", error_msg)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

# Update splash message handler to reduce code duplication
def update_splash(splash, app, message):
    """Update splash screen with a message and process events immediately."""
    splash.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    app.processEvents()

def main_gui():
    """
    Main application entry point that initializes the GUI and event loop.
    """
    # Set up global exception handler
    sys.excepthook = exception_handler
    
    # Set up logging first thing
    setup_logging()
    logger.info("Application starting")
    
    # Validate configuration settings
    setting_errors = validate_settings()
    if setting_errors:
        error_message = "Configuration errors detected:\n• " + "\n• ".join(setting_errors)
        logger.error(error_message)
        # We'll show this after the GUI initializes
    
    # Create application first
    app = QApplication(sys.argv)
    
    try:
        # Create and show splash screen
        splash_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "resources", "splash_screen.png")
        
        if os.path.exists(splash_path):
            splash_pixmap = QPixmap(splash_path)
        else:
            # Create fallback splash
            splash_pixmap = QPixmap(500, 300)
            splash_pixmap.fill(Qt.white)
            
        splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        splash.setFont(QFont('Arial', 14))
        update_splash(splash, app, "Initializing components...")
        
        # Show splash screen and process events immediately
        splash.show()
        app.processEvents()
        
        # Display configuration warnings if any
        if setting_errors:
            update_splash(splash, app, "Warning: Configuration issues detected...")
        
        # Initialize database connection
        update_splash(splash, app, "Connecting to Supabase database...")
        
        try:
            # Initialize Supabase client and verify table exists
            client = get_supabase_client()
            verify_table_exists()
            logger.info("Supabase connection verified")
        except Exception as e:
            logger.warning(f"Supabase initialization warning: {e}")
            # Continue with application even if database fails
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "resources", "icon.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            update_splash(splash, app, "Loading configuration...")
        
        # Create and set up the event loop first
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Start the event loop here but keep reference
        with loop:
            # Update splash
            update_splash(splash, app, "Creating user interface...")
            
            # Create main window
            try:
                logger.debug("Initializing MainWindow")
                window = MainWindow()
                logger.debug("MainWindow initialization complete")
            except Exception as e:
                logger.critical(f"Failed to initialize MainWindow: {e}", exc_info=True)
                QMessageBox.critical(None, "Initialization Error", 
                                  f"Failed to initialize application: {str(e)}")
                return 1
            
            # Final splash update
            update_splash(splash, app, "Starting application...")
            
            # Close splash and show window in sequence with proper timing
            def finish_loading():
                splash.finish(window)
                window.show()
                logger.info("Main window displayed")
                
                # Show configuration warnings after window is displayed
                if setting_errors:
                    QMessageBox.warning(window, "Configuration Warning",
                                      "Some configuration issues were detected:\n\n• " + 
                                      "\n• ".join(setting_errors) +
                                      "\n\nPlease check your .env file and correct these issues.")
            
            QTimer.singleShot(800, finish_loading)
            
            # Continue running the event loop
            loop.run_forever()
            
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        QMessageBox.critical(None, "Startup Error", 
                           f"Failed to start application: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main_gui())