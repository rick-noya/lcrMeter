"""
Modern icon management for the LCR application.
Provides consistent access to application icons.
"""
import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

class IconManager:
    """Manages icons throughout the application for consistent styling."""
    
    # Base path for icons
    ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
    
    # Icon filenames - helps keep naming consistent
    ICONS = {
        "app": "app_icon.png",
        "refresh": "refresh.png",
        "start": "start.png",
        "stop": "stop.png",
        "export": "export.png",
        "database": "database.png",
        "settings": "settings.png",
    }
    
    @classmethod
    def get_icon(cls, name, size=None):
        """Get an icon by name with optional resizing."""
        icon_path = os.path.join(cls.ICON_PATH, cls.ICONS.get(name, "app_icon.png"))
        
        # Fallback to system icons if file doesn't exist
        if not os.path.exists(icon_path):
            return cls.get_system_icon(name)
            
        icon = QIcon(icon_path)
        
        # If size is specified, ensure the icon is loaded at that size
        if size is not None and isinstance(size, (int, tuple)):
            if isinstance(size, int):
                size = QSize(size, size)
            elif isinstance(size, tuple):
                size = QSize(*size)
            
            # Create a pixmap of the desired size
            pixmap = icon.pixmap(size)
            icon = QIcon(pixmap)
            
        return icon
    
    @staticmethod
    def get_system_icon(name):
        """Get a system standard icon as fallback."""
        from PyQt5.QtWidgets import QStyle, QApplication
        
        # Map our icon names to Qt standard icons
        icon_map = {
            "refresh": QStyle.SP_BrowserReload,
            "start": QStyle.SP_MediaPlay,
            "stop": QStyle.SP_MediaStop,
            "export": QStyle.SP_DialogSaveButton,
            "database": QStyle.SP_DriveNetIcon,
            "settings": QStyle.SP_FileDialogDetailedView,
            "app": QStyle.SP_ComputerIcon
        }
        
        # Get the QStyle from the application
        style = QApplication.style()
        
        # Return the appropriate standard icon
        icon_enum = icon_map.get(name, QStyle.SP_ComputerIcon)
        return style.standardIcon(icon_enum)