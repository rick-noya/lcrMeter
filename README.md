# LCR Meter

## Overview

The LCR Meter is a Python application designed to accurately perform inductance measurements on Noya's sorbent. Leveraging a PyQt5-based GUI, the app allows users to input test parameters and record measurement data directly to Google Sheets, ensuring efficient and reliable analysis for quality control and research.

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

## Features

- Specialized inductance measurements tailored for Noya's sorbent samples and assemblages.
- Measurements in henries and ohms.
- Integration with Google Sheets for seamless data logging and analysis.
- User-friendly GUI with custom numeric input dialogs for effortless parameter entry.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
