# FILE: /LCR-Meter-Project/LCR-Meter-Project/gui/stylesheets.py

# This file contains the stylesheets used for the GUI components, defining the appearance of buttons, labels, and other widgets.

MAIN_WINDOW_STYLESHEET = """
    QMainWindow { background-color: #2b2b2b; }
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        font-size: 16px;
        border: none;
        border-radius: 5px;
    }
    QPushButton:hover { background-color: #45a049; }
    QPushButton#stopButton {
        background-color: red;
        color: white;
        padding: 10px;
        font-size: 16px;
        border: none;
        border-radius: 5px;
    }
    QPushButton#stopButton:hover { background-color: darkred; }
    QLabel { color: white; font-size: 14px; }
    QLineEdit {
        color: white;
        font-size: 14px;
        background-color: #3c3c3c;
        border: 1px solid #555;
        padding: 5px;
        border-radius: 3px;
    }
    QTextEdit {
        color: white;
        background-color: #3c3c3c;
        font-size: 14px;
    }
"""

START_BUTTON_STYLESHEET = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 20px;
        font-size: 24px;
        border: none;
        border-radius: 10px;
    }
    QPushButton:hover { background-color: #45a049; }
"""

START_BUTTON_RUNNING_STYLESHEET = """
    QPushButton {
        background-color: #F44336;  /* Red */
        color: white;
        padding: 20px;
        font-size: 24px;
        border: none;
        border-radius: 10px;
    }
    QPushButton:hover { background-color: #D32F2F; }  /* Darker red on hover */
"""