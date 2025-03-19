import os
from pathlib import Path
from dotenv import load_dotenv

# Define base_dir - keep this variable as it's used multiple times
base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_file = base_dir / '.env'

# Load environment variables from .env file if it exists
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    # Try loading from system environment variables
    # or use default values as fallback
    pass

# Application settings
APP_NAME = "LCR Meter"
APP_VERSION = "0.2.0"
GUI_VERSION = os.getenv('GUI_VERSION', APP_VERSION)

# Supabase Database settings
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://your-project-url.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Normalized database tables
SAMPLES_TABLE = os.getenv('SAMPLES_TABLE', 'samples')
MEASUREMENTS_TABLE = os.getenv('MEASUREMENTS_TABLE', 'ls-rs_measurements')  # Updated table name
DB_ENABLE = os.getenv('DB_ENABLE', 'True').lower() in ('true', '1', 'yes')

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', "DEBUG")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
LOG_FILE = "lcr_meter.log"

# Default measurement settings
DEFAULT_FREQUENCY = int(os.getenv('DEFAULT_FREQUENCY', '100000'))
DEFAULT_VOLTAGE = float(os.getenv('DEFAULT_VOLTAGE', '1.0'))
DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', '10000'))
DEFAULT_RESOURCE = os.getenv(
    'DEFAULT_RESOURCE', 
    "USB0::0x2A8D::0x2F01::MY54414986::0::INSTR"
)

# UI settings
WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '500'))
WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '750'))

# Development settings
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Validate critical settings
def validate_settings():
    """Validates that critical settings are properly configured."""
    errors = []
    
    if not SUPABASE_KEY and DB_ENABLE:
        errors.append("SUPABASE_KEY is missing but database is enabled")
    
    return errors

# Add .env to gitignore if it exists
gitignore_path = base_dir / '.gitignore'
if os.path.exists(gitignore_path):
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
        
    if '.env' not in gitignore_content:
        with open(gitignore_path, 'a') as f:
            f.write('\n# Environment variables\n.env\n')