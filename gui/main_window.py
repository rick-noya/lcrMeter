import asyncio
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QGridLayout, QLineEdit, QListWidget, QListWidgetItem, QStyle,
    QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from qasync import asyncSlot
from config.settings import DEFAULT_FREQUENCY, DEFAULT_VOLTAGE, DEFAULT_TIMEOUT, DEFAULT_RESOURCE, WINDOW_WIDTH, WINDOW_HEIGHT
from components.instrument.lcr_meter import LCRMeter
from components.instrument.measurement import run_measurement_sequence
from components.google_sheets import get_sample_names, upload_data
from gui.widgets.number_pad import NumberPadLineEdit
from gui.stylesheets import MAIN_WINDOW_STYLESHEET, START_BUTTON_STYLESHEET

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main application window that provides the UI for the LCR meter application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCR Meter")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Try to set window icon with absolute path
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "resources", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # Apply stylesheet
        self.setStyleSheet(MAIN_WINDOW_STYLESHEET)
        
        # Setup UI components
        self._setup_ui()
        
        # Data storage
        self.lcr_data = []  # Each row: [Timestamp, Sample Name, Test Type, Value 1, Value 2]
        self.sample_names = []
        
        # Status bar for quick feedback
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Schedule asynchronous loading of sample names
        QTimer.singleShot(0, lambda: asyncio.create_task(self.load_sample_names()))

    def _setup_ui(self):
        """Set up the UI components."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Info label at the top
        self.info_label = QLabel(
            "Enter Sample Name, Resource, Frequency, Voltage, Timeout.\n"
            "Test Type: Ls-Rs (Series Inductance and Resistance)"
        )
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Create grid layout for input fields
        grid = QGridLayout()
        layout.addLayout(grid)
        
        # Add Sample Name input with refresh button
        self._add_sample_name_input(grid)
        
        # Add Tester Name input
        self._add_tester_name_input(grid)
        
        # Add available samples list
        self._add_samples_list(layout)
        
        # Add instrument configuration fields
        self._add_instrument_config(grid)
        
        # Add log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Add start button
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)
        self.start_button = QPushButton("Start Ls-Rs Measurement")
        self.start_button.setStyleSheet(START_BUTTON_STYLESHEET)
        self.start_button.clicked.connect(self.on_start_sequence)
        btn_layout.addWidget(self.start_button)

    def _add_sample_name_input(self, grid):
        """Add the sample name input field with refresh button."""
        sample_name_layout = QHBoxLayout()
        grid.addWidget(QLabel("Sample Name:"), 0, 0, Qt.AlignRight)
        self.sampleNameLineEdit = QLineEdit()
        self.sampleNameLineEdit.setPlaceholderText("Enter sample name or select from list")
        self.sampleNameLineEdit.textChanged.connect(self.filter_sample_names)
        sample_name_layout.addWidget(self.sampleNameLineEdit)
        
        # Refresh button with icon
        self.refreshButton = QPushButton()
        self.refreshButton.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refreshButton.setToolTip("Refresh Sample List")
        self.refreshButton.setFixedSize(30, 30)
        self.refreshButton.clicked.connect(lambda: asyncio.create_task(self.load_sample_names()))
        sample_name_layout.addWidget(self.refreshButton)
        
        grid.addLayout(sample_name_layout, 0, 1)

    def _add_tester_name_input(self, grid):
        """Add the tester name input field."""
        grid.addWidget(QLabel("Tester Name:"), 1, 0, Qt.AlignRight)
        self.tester_name_input = QLineEdit()
        grid.addWidget(self.tester_name_input, 1, 1)

    def _add_samples_list(self, layout):
        """Add the sample list widget and its heading."""
        heading_label = QLabel("Available Sample Names:")
        heading_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(heading_label)
        
        self.sampleNameListWidget = QListWidget()
        self.sampleNameListWidget.setMaximumHeight(150)  # Limit height
        self.sampleNameListWidget.itemClicked.connect(self.handle_item_clicked)
        layout.addWidget(self.sampleNameListWidget)

    def _add_instrument_config(self, grid):
        """Add instrument configuration fields."""
        grid.addWidget(QLabel("LCR tester:"), 2, 0, Qt.AlignRight)
        self.resourceLineEdit = NumberPadLineEdit()
        self.resourceLineEdit.setText(DEFAULT_RESOURCE)
        grid.addWidget(self.resourceLineEdit, 2, 1)
        
        grid.addWidget(QLabel("Frequency (Hz):"), 3, 0, Qt.AlignRight)
        self.freqLineEdit = NumberPadLineEdit()
        self.freqLineEdit.setPlaceholderText(str(DEFAULT_FREQUENCY))
        self.freqLineEdit.setText(str(DEFAULT_FREQUENCY))
        grid.addWidget(self.freqLineEdit, 3, 1)
        
        grid.addWidget(QLabel("Voltage (V):"), 4, 0, Qt.AlignRight)
        self.voltLineEdit = NumberPadLineEdit()
        self.voltLineEdit.setPlaceholderText(str(DEFAULT_VOLTAGE))
        self.voltLineEdit.setText(str(DEFAULT_VOLTAGE))
        grid.addWidget(self.voltLineEdit, 4, 1)
        
        grid.addWidget(QLabel("Timeout (ms):"), 5, 0, Qt.AlignRight)
        self.timeoutLineEdit = NumberPadLineEdit()
        self.timeoutLineEdit.setPlaceholderText(str(DEFAULT_TIMEOUT))
        self.timeoutLineEdit.setText(str(DEFAULT_TIMEOUT))
        grid.addWidget(self.timeoutLineEdit, 5, 1)

    def append_log(self, message: str):
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        logger.info(message)
        # Also update status bar for immediate feedback
        self.statusBar.showMessage(message, 3000)  # Show for 3 seconds

    def get_tester_name(self) -> str:
        """Get the current tester name from the input field."""
        return self.tester_name_input.text()

    async def load_sample_names(self):
        """Load sample names from Google Sheets asynchronously."""
        self.sampleNameListWidget.clear()
        self.sampleNameListWidget.addItem(QListWidgetItem("Loading sample names..."))
        
        try:
            # Fetch sample names in a background thread
            self.sample_names = await asyncio.to_thread(get_sample_names)
            
            # Sort the master list alphabetically
            self.sample_names.sort(key=lambda name: name.lower())
            
            # Update UI with fetched names
            self.sampleNameListWidget.clear()
            if self.sample_names:
                for name in self.sample_names:
                    self.sampleNameListWidget.addItem(QListWidgetItem(name))
                self.append_log(f"Loaded {len(self.sample_names)} sample names")
            else:
                self.sampleNameListWidget.addItem(QListWidgetItem("No samples found"))
                self.append_log("No sample names found")
        except Exception as e:
            self.append_log(f"Error loading sample names: {e}")
            self.sampleNameListWidget.clear()
            self.sampleNameListWidget.addItem(QListWidgetItem("Error loading samples"))
    
    def filter_sample_names(self, text: str):
        """Filter sample names based on input text."""
        if not self.sample_names:
            return
            
        search = text.lower()
        filtered = (
            self.sample_names[:] if search == "" 
            else [name for name in self.sample_names if search in name.lower()]
        )
        filtered.sort(key=lambda name: name.lower())
        
        # Update the list widget
        self.sampleNameListWidget.clear()
        if filtered:
            for name in filtered:
                self.sampleNameListWidget.addItem(QListWidgetItem(name))
        else:
            # Show message when no matches
            message = (f"No matching samples found for '{text}'. "
                      "Click \"Start\" to run a test and add a new sample.")
            item = QListWidgetItem(message)
            item.setFlags(Qt.NoItemFlags)  # Make non-selectable
            self.sampleNameListWidget.addItem(item)
    
    def handle_item_clicked(self, item: QListWidgetItem):
        """Handle when a sample name is selected from the list."""
        if item.flags() & Qt.ItemIsSelectable:
            self.sampleNameLineEdit.setText(item.text())

    @asyncSlot()
    async def on_start_sequence(self):
        """Start the measurement sequence."""
        # Get parameters
        sample_name = self.sampleNameLineEdit.text().strip()
        if not sample_name:
            QMessageBox.warning(self, "Missing Information", "Please enter a sample name.")
            return
            
        tester_name = self.get_tester_name().strip()
        if not tester_name:
            QMessageBox.warning(self, "Missing Information", "Please enter your name as the tester.")
            return
            
        # Get instrument parameters
        resource_name = self.resourceLineEdit.text().strip()
        
        try:
            frequency = float(self.freqLineEdit.text().strip() or DEFAULT_FREQUENCY)
            voltage = float(self.voltLineEdit.text().strip() or DEFAULT_VOLTAGE)
            timeout = int(self.timeoutLineEdit.text().strip() or DEFAULT_TIMEOUT)
        except ValueError:
            self.append_log("Invalid numeric parameter.")
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values for frequency, voltage, and timeout.")
            return
        
        # Disable start button during test
        self.start_button.setEnabled(False)
        self.lcr_data.clear()
        
        try:
            # Run the measurement sequence
            self.append_log(f"Starting Ls-Rs measurement for sample: {sample_name}")
            
            # Create LCR meter instance
            lcr_meter = LCRMeter(resource_name, timeout)
            
            # Connect to the instrument
            if not await lcr_meter.connect():
                self.append_log("Failed to connect to the LCR meter.")
                QMessageBox.critical(self, "Connection Error", "Failed to connect to the LCR meter.")
                self.start_button.setEnabled(True)
                return
            
            # Configure the instrument with the specified frequency and voltage
            await lcr_meter.configure(frequency, voltage)
                
            # Run measurement sequence and get results
            results = await run_measurement_sequence(
                lcr_meter, sample_name, tester_name
            )
            
            # Update data and log
            self.lcr_data.extend(results)
            for row in results:
                test_type = row[2]
                L_value = row[3]
                Rs_value = row[4]
                self.append_log(f"{test_type}: L={L_value} H, Rs={Rs_value} Ω")
                
            # Upload data
            await upload_data(self)
            
        except Exception as e:
            self.append_log(f"Error during test sequence: {e}")
            logger.exception("Error in test sequence")
        finally:
            # Re-enable start button
            self.start_button.setEnabled(True)