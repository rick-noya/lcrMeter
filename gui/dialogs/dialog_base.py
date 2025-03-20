"""
Base dialog class for consistent styling across all application dialogs.
"""
import logging
from PyQt5.QtWidgets import QDialog, QStyle, QApplication
from PyQt5.QtCore import Qt
from gui.stylesheets import DIALOG_BASE_STYLESHEET

logger = logging.getLogger(__name__)

class DialogBase(QDialog):
    """Base class for all application dialogs with consistent styling."""
    
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(DIALOG_BASE_STYLESHEET)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # Center the dialog on the screen
        self.center_on_screen()
        
    def center_on_screen(self):
        """Center the dialog on the screen."""
        self.setGeometry(
            QStyle.alignedRect(
                Qt.LeftToRight,
                Qt.AlignCenter,
                self.size(),
                QApplication.desktop().availableGeometry()
            )
        )