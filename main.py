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

logger = logging.getLogger(__name__)

def exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler to log uncaught exceptions"""
    logger.critical("Uncaught exception", 
                   exc_info=(exc_type, exc_value, exc_traceback))
    # Show error dialog for uncaught exceptions
    error_msg = f"An unexpected error occurred:\n{exc_value}"
    QMessageBox.critical(None, "Error", error_msg)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def main_gui():
    """
    Main application entry point that initializes the GUI and event loop.
    """
    # Set up global exception handler
    sys.excepthook = exception_handler
    
    # Set up logging first thing
    setup_logging()
    logger.info("Application starting")
    
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
        splash.showMessage("Initializing components...", 
                          Qt.AlignBottom | Qt.AlignCenter, 
                          Qt.black)
        
        # Show splash screen and process events immediately
        splash.show()
        app.processEvents()
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "resources", "icon.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            splash.showMessage("Loading configuration...", 
                             Qt.AlignBottom | Qt.AlignCenter, 
                             Qt.black)
            app.processEvents()
        
        # Create and set up the event loop first
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Start the event loop here but keep reference
        with loop:
            # Update splash
            splash.showMessage("Creating user interface...", 
                             Qt.AlignBottom | Qt.AlignCenter, 
                             Qt.black)
            app.processEvents()
            
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
            splash.showMessage("Starting application...", 
                             Qt.AlignBottom | Qt.AlignCenter, 
                             Qt.black)
            app.processEvents()
            
            # Close splash and show window in sequence with proper timing
            def finish_loading():
                splash.finish(window)  # This properly transfers focus to the main window
                window.show()
                logger.info("Main window displayed")
            
            # Use timer to ensure splash screen is visible for enough time
            QTimer.singleShot(800, finish_loading)
            
            # Continue running the event loop
            loop.run_forever()
            
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        QMessageBox.critical(None, "Startup Error", 
                           f"Failed to start application: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main_gui())