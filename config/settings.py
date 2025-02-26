import os

# Application settings
APP_NAME = "LCR Meter"
APP_VERSION = "1.0.0"

# Google Sheets settings
GOOGLE_SHEETS_CREDENTIALS_FILE = 'C:/Coding/LCR/sorbent-pressure-drop-data-160450782f01.json'
SPREADSHEET_ID = '1CTTiAvbEiF249dqL7zbPQoBwCmrYzIVuGIvOMKqWZG8'
SHEET_RANGE = 'LCR!A1:E'

# Logging settings
LOG_LEVEL = "DEBUG"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
LOG_FILE = "lcr_meter.log"

# Default measurement settings
DEFAULT_FREQUENCY = 1000
DEFAULT_VOLTAGE = 1.0
DEFAULT_TIMEOUT = 10000
DEFAULT_RESOURCE = "USB0::0x2A8D::0x2F01::MY54414986::0::INSTR"

# UI settings
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 750