# LCR Meter Project

## Overview

The LCR Meter Project is a Python application designed to accurately perform LCR (Inductance, Capacitance, and Resistance) measurements on Noya's sorbent. Leveraging a PyQt5-based GUI, the app allows users to input test parameters and record measurement data directly to Google Sheets, ensuring efficient and reliable analysis for quality control and research.

## Project Structure

```
LCR-Meter-Project
├── gui
│   ├── __init__.py
│   ├── main_window.py
│   ├── number_pad.py
│   └── stylesheets.py
├── components
│   ├── __init__.py
│   ├── google_sheets.py
│   └── lcr_tests.py
├── config
│   ├── __init__.py
│   └── settings.py
├── main.py
├── measure.py
└── README.md
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
3. Use the GUI to enter the sample name, resource name, frequency, voltage, and timeout.
4. Click the "Start" button to begin the measurement sequence.

## Features

- Specialized LCR measurements tailored for Noya's sorbent samples.
- Measurement of inductance, capacitance, and resistance with high precision.
- Integration with Google Sheets for seamless data logging and analysis.
- User-friendly GUI with custom numeric input dialogs for effortless parameter entry.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
