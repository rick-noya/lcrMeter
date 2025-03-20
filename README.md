# LCR Meter Project v0.3.0

A PyQt5-based application for measuring inductance (L) and resistance (R) using an LCR meter, with integrated database storage and Notion synchronization.

## Features

- **Modern User Interface**

  - Clean, responsive design with improved fonts and modern icons
  - Detailed tooltips explaining each parameter and feature
  - Splash screen and consistent styling throughout the app

- **Real-time Measurements**

  - Direct communication with LCR meters via VISA interface
  - Configurable frequency, voltage, and timeout settings
  - Series inductance (Ls) and resistance (Rs) measurements

- **Data Management**

  - Supabase database integration for secure storage
  - Sample and measurement history browsing
  - Normalized database schema for efficient data organization
  - Export functionality for data analysis

- **Notion Integration**

  - Automatic syncing of measurement data to Notion databases
  - Preserves sample resistance values for easy team collaboration
  - Standalone sync utility to update Notion from Supabase records

- **Quality Control**

  - Measurement validation before database submission
  - Warns about invalid or suspicious measurements
  - User confirmation for questionable results
  - Comprehensive error logging and handling

- **Security**
  - Environment-based configuration for credentials
  - No hardcoded secrets in source code

## Project Structure

```
LCR-Meter-Project
├── gui
│   ├── __init__.py
│   ├── main_window.py
│   ├── stylesheets.py
│   └── widgets
│       ├── __init__.py
│       └── number_pad.py
├── components
│   ├── __init__.py
│   ├── google_sheets.py
│   └── instrument
│       ├── __init__.py
│       ├── lcr_meter.py
│       └── measurement.py
├── utils
│   ├── __init__.py
│   └── logging_config.py
├── config
│   ├── __init__.py
│   └── settings.py
├── resources
│   ├── icon.ico
│   └── splash_screen.png
├── logs
├── main.py
├── create_splash.py
├── README.md
└── .gitignore
```

## Installation

### Prerequisites

- Python 3.9 or higher
- VISA-compatible LCR meter (e.g., Keysight E4980A)
- Supabase account (for database storage)
- Notion account (optional, for Notion integration)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/rick-noya/lcrMeter
   ```
2. Navigate to the project directory:
   ```
   cd LCR-Meter-Project
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure you have the necessary Google Sheets API credentials and update the `config/settings.py` file with your credentials.
2. Run the application:
   ```
   python main.py
   ```
3. Use the GUI to enter the sample name, tester name, frequency, voltage, and timeout.
4. Click the "Start" button to begin the measurement sequence.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
