import sys
import os
import asyncio
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
from qasync import QEventLoop
from utils.logging_config import setup_logging

def main_gui():
    """
    Main application entry point that initializes the GUI and event loop.
    """
    # Set up logging first thing
    setup_logging()
    
    app = QApplication(sys.argv)
    
    # Set application icon with proper error handling
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Set up async event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main_gui()