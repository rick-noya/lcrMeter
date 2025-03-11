# FILE: /LCR-Meter-Project/LCR-Meter-Project/gui/stylesheets.py

"""
Centralized styling system for the LCR Meter application.
This file contains all styles used throughout the application to ensure consistency.
"""

# Theme colors - define once, use everywhere
COLORS = {
    # Primary palette
    "primary": "#4CAF50",
    "primary_hover": "#45a049",
    "primary_dark": "#3b8c3e",
    
    # Secondary actions
    "secondary": "#2196F3",
    "secondary_hover": "#1976D2",
    
    # Alerts/Status
    "danger": "#F44336",
    "danger_hover": "#D32F2F",
    "warning": "#FFC107",
    "success": "#4CAF50",
    "info": "#2196F3",
    
    # Background colors
    "bg_dark": "#2b2b2b",
    "bg_medium": "#3c3c3c",
    "bg_light": "#f0f0f0",
    "bg_white": "#ffffff",
    
    # Border colors
    "border_dark": "#555",
    "border_medium": "#d3d3d3",
    "border_light": "#e0e0e0",
    
    # Text colors
    "text_dark": "#212121",
    "text_medium": "#757575",
    "text_light": "#ffffff",
}

# Font sizes - for consistency
FONTS = {
    "small": "12px",
    "normal": "14px",
    "large": "16px",
    "xlarge": "24px",
}

# Common dimensions
DIMENSIONS = {
    "padding_small": "5px",
    "padding_normal": "10px",
    "padding_large": "20px",
    "border_radius_small": "3px",
    "border_radius_normal": "5px",
    "border_radius_large": "10px",
}

# Main application window stylesheet
MAIN_WINDOW_STYLESHEET = f"""
    QMainWindow {{ background-color: {COLORS["bg_dark"]}; }}
    QPushButton {{
        background-color: {COLORS["primary"]};
        color: {COLORS["text_light"]};
        padding: {DIMENSIONS["padding_normal"]};
        font-size: {FONTS["large"]};
        border: none;
        border-radius: {DIMENSIONS["border_radius_normal"]};
    }}
    QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
    QPushButton#stopButton {{
        background-color: {COLORS["danger"]};
        color: {COLORS["text_light"]};
        padding: {DIMENSIONS["padding_normal"]};
        font-size: {FONTS["large"]};
        border: none;
        border-radius: {DIMENSIONS["border_radius_normal"]};
    }}
    QPushButton#stopButton:hover {{ background-color: {COLORS["danger_hover"]}; }}
    QLabel {{ color: {COLORS["text_light"]}; font-size: {FONTS["normal"]}; }}
    QLineEdit {{
        color: {COLORS["text_light"]};
        font-size: {FONTS["normal"]};
        background-color: {COLORS["bg_medium"]};
        border: 1px solid {COLORS["border_dark"]};
        padding: {DIMENSIONS["padding_small"]};
        border-radius: {DIMENSIONS["border_radius_small"]};
    }}
    QTextEdit {{
        color: {COLORS["text_light"]};
        background-color: {COLORS["bg_medium"]};
        font-size: {FONTS["normal"]};
    }}
"""

# Start button styles
START_BUTTON_STYLESHEET = f"""
    QPushButton {{
        background-color: {COLORS["primary"]};
        color: {COLORS["text_light"]};
        padding: {DIMENSIONS["padding_large"]};
        font-size: {FONTS["xlarge"]};
        border: none;
        border-radius: {DIMENSIONS["border_radius_large"]};
    }}
    QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
"""

START_BUTTON_RUNNING_STYLESHEET = f"""
    QPushButton {{
        background-color: {COLORS["danger"]};
        color: {COLORS["text_light"]};
        padding: {DIMENSIONS["padding_large"]};
        font-size: {FONTS["xlarge"]};
        border: none;
        border-radius: {DIMENSIONS["border_radius_large"]};
    }}
    QPushButton:hover {{ background-color: {COLORS["danger_hover"]}; }}
"""

# Dialog styling
DIALOG_BASE_STYLESHEET = f"""
    QDialog {{ background-color: {COLORS["bg_dark"]}; }}
    QLabel {{ color: {COLORS["text_light"]}; font-size: {FONTS["normal"]}; }}
    QPushButton {{
        background-color: {COLORS["secondary"]};
        color: {COLORS["text_light"]};
        padding: {DIMENSIONS["padding_small"]} {DIMENSIONS["padding_normal"]};
        font-size: {FONTS["normal"]};
        border: none;
        border-radius: {DIMENSIONS["border_radius_normal"]};
        min-width: 80px;
    }}
    QPushButton:hover {{ background-color: {COLORS["secondary_hover"]}; }}
"""

# Table styling
DATA_TABLE_STYLESHEET = f"""
    QTableWidget {{
        border: 1px solid {COLORS["border_medium"]};
        gridline-color: {COLORS["border_light"]};
        background-color: {COLORS["bg_white"]};
        color: {COLORS["text_dark"]};
    }}
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {COLORS["border_light"]};
    }}
    QHeaderView::section {{
        background-color: {COLORS["bg_light"]};
        padding: 8px;
        border: 1px solid {COLORS["border_medium"]};
        font-weight: bold;
        font-size: {FONTS["normal"]};
    }}
    QTableWidget QTableCornerButton::section {{
        background-color: {COLORS["bg_light"]};
        border: 1px solid {COLORS["border_medium"]};
    }}
"""

# Status label styling
STATUS_LABEL_STYLESHEET = {
    "normal": f"font-weight: bold; font-size: {FONTS['normal']}; margin: 5px;",
    "error": f"font-weight: bold; font-size: {FONTS['normal']}; color: {COLORS['danger']}; margin: 5px;",
    "success": f"font-weight: bold; font-size: {FONTS['normal']}; color: {COLORS['success']}; margin: 5px;"
}

# Dialog button styling
DIALOG_BUTTON_STYLESHEET = f"font-size: {FONTS['normal']}; font-weight: bold; min-width: 120px; min-height: 40px;"

# Sample selection panel styling
SAMPLE_PANEL_STYLESHEET = f"""
    QListWidget {{
        background-color: {COLORS["bg_white"]};
        border: 1px solid {COLORS["border_medium"]};
        color: {COLORS["text_dark"]};
    }}
    QListWidget::item {{
        padding: {DIMENSIONS["padding_small"]};
    }}
    QListWidget::item:selected {{
        background-color: {COLORS["secondary"]};
        color: {COLORS["text_light"]};
    }}
"""

# Instrument config panel styling
INSTRUMENT_CONFIG_STYLESHEET = f"""
    QLabel {{
        font-weight: bold;
        color: {COLORS["text_light"]};
    }}
    QLineEdit {{
        background-color: {COLORS["bg_medium"]};
        color: {COLORS["text_light"]};
        border: 1px solid {COLORS["border_dark"]};
        padding: {DIMENSIONS["padding_small"]};
        border-radius: {DIMENSIONS["border_radius_small"]};
    }}
"""

# NumberPad styling
NUMBER_PAD_STYLESHEET = f"""
    QDialog {{
        background-color: {COLORS["bg_dark"]};
    }}
    QLineEdit {{
        font-size: {FONTS["large"]};
        background-color: {COLORS["bg_white"]};
        color: {COLORS["text_dark"]};
        border: 1px solid {COLORS["border_medium"]};
        padding: {DIMENSIONS["padding_normal"]};
        margin-bottom: {DIMENSIONS["padding_normal"]};
    }}
    QPushButton {{
        background-color: {COLORS["primary"]};
        color: {COLORS["text_light"]};
        font-size: {FONTS["large"]};
        min-height: 50px;
        border: none;
        border-radius: {DIMENSIONS["border_radius_normal"]};
    }}
    QPushButton:hover {{
        background-color: {COLORS["primary_hover"]};
    }}
"""