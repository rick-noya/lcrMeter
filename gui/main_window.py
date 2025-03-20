import asyncio
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QMessageBox, QStatusBar, QMenuBar, QMenu, QAction, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon

from qasync import asyncSlot
from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT, APP_NAME, GUI_VERSION
from components.instrument.lcr_meter import LCRMeter
from components.instrument.measurement import run_measurement_sequence
from components.sample_manager import get_sample_names  # Updated import
from gui.stylesheets import (MAIN_WINDOW_STYLESHEET, START_BUTTON_STYLESHEET, 
                           START_BUTTON_RUNNING_STYLESHEET)
from components.supabase_db import upload_data as db_upload_data
from utils.error_handling import safe_async_call, to_thread_with_error_handling
from gui.widgets.sample_selection import SampleSelectionPanel
from gui.widgets.instrument_config import InstrumentConfigPanel
from gui.icon_manager import IconManager
from components.instrument.measurement import validate_measurements

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main application window that provides the UI for the LCR meter application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{GUI_VERSION}")  # Show version in title
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Try to set window icon with absolute path
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "resources", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # Apply stylesheet
        self.setStyleSheet(MAIN_WINDOW_STYLESHEET)
        
        # Data storage
        self.lcr_data = []  # Each row: [Timestamp, Sample Name, Test Type, Value 1, Value 2]
        
        # Add this field to store the LCR meter reference
        self.lcr_meter = None
        
        # Setup UI components
        self._setup_ui()
        
        # Setup menu
        self._setup_menu()
        
        # Status bar for quick feedback
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Schedule asynchronous loading of sample names
        QTimer.singleShot(100, self.init_async_tasks)

    def _setup_ui(self):
        """Set up the UI components."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Info label at the top with better explanation
        self.info_label = QLabel(
            "Enter Sample Name, Resource, Frequency, Voltage, Timeout.\n"
            "Test Type: Ls-Rs (Series Inductance and Resistance)"
        )
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setToolTip(
            "This application measures Series Inductance (Ls) and Series Resistance (Rs).\n\n"
            "Ls = Inductance in Henries (H)\n"
            "Rs = Resistance in Ohms (Ω)\n\n"
            "Measurements are made at your specified frequency and voltage,\n"
            "then recorded in the Supabase database with sample and tester information."
        )
        layout.addWidget(self.info_label)
        
        # Sample selection panel
        self.sample_panel = SampleSelectionPanel(self)
        self.sample_panel.refresh_requested.connect(self.load_sample_names_async)
        self.sample_panel.setToolTip("Enter or select a sample name for testing")
        layout.addWidget(self.sample_panel)
        
        # Replace tester name input with a drop‑down selector
        tester_layout = QHBoxLayout()
        tester_layout.addWidget(QLabel("Tester Name:"), alignment=Qt.AlignRight)
        self.tester_name_combo = QComboBox()
        # Add the preset tester names
        tester_names = ["Rick R", "Colin S", "Aditi D", "Nate G", "Matt S", "Shazia S", "Krys - ABP", "Dan - ABP"]
        self.tester_name_combo.addItems(tester_names)
        self.tester_name_combo.setToolTip(
            "Select or enter the name of the person performing the test.\n\n"
            "This information is recorded with each measurement for:\n"
            "• Quality control tracking\n"
            "• Accountability\n"
            "• Data filtering and reporting by operator\n\n"
            "Select from the dropdown list or type a new name."
        )
        tester_layout.addWidget(self.tester_name_combo)
        layout.addLayout(tester_layout)
        
        # Instrument configuration panel
        self.instrument_panel = InstrumentConfigPanel(self)
        self.instrument_panel.setToolTip("Configure LCR meter connection and test parameters")
        layout.addWidget(self.instrument_panel)
        
        # Add log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setToolTip("Test log showing measurement activities and results")
        layout.addWidget(self.log_text)
        
        # Add start button
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)
        self.start_button = QPushButton("Start Ls-Rs Measurement")
        self.start_button.setIcon(IconManager.get_icon("start", 24))
        self.start_button.setIconSize(QSize(24, 24))
        self.start_button.setStyleSheet(START_BUTTON_STYLESHEET)
        self.start_button.setToolTip(
            "Start measurement using current parameters:\n\n"
            "• Connects to the specified LCR meter\n"
            "• Configures the instrument with your Frequency and Voltage settings\n"
            "• Takes an Ls-Rs measurement (inductance and resistance)\n"
            "• Records results with sample name, tester, and timestamp\n"
            "• Uploads data to the Supabase database\n\n"
            "Ensure all parameters are set correctly before starting."
        )
        self.start_button.clicked.connect(self.on_start_sequence)
        btn_layout.addWidget(self.start_button)

    def append_log(self, message: str):
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        logger.info(message)
        # Also update status bar for immediate feedback
        self.statusBar.showMessage(message, 3000)  # Show for 3 seconds

    def get_tester_name(self) -> str:
        """Get the current tester name from the selector."""
        return self.tester_name_combo.currentText()

    def load_sample_names_async(self):
        """Start async loading of sample names."""
        # Show loading state immediately, don't wait for async operation
        self.sample_panel.show_loading_state()
        
        # Use QTimer to defer execution to the next event loop cycle
        # This avoids the coroutine/task wrapping issue
        QTimer.singleShot(0, lambda: self._trigger_load_sample_names())

    def _trigger_load_sample_names(self):
        """Helper method to safely trigger the async slot."""
        # The asyncSlot will create its own Task, so we don't need asyncio.create_task
        try:
            # Just call the method directly - the asyncSlot decorator handles the Task creation
            self.load_sample_names()
        except Exception as e:
            logger.error(f"Error starting sample name loading: {e}", exc_info=True)
            self.sample_panel.show_error_state(f"Error loading: {str(e)}")

    @asyncSlot()
    async def load_sample_names(self):
        """Load sample names from Supabase database asynchronously."""
        self.sample_panel.show_loading_state()
        
        try:
            # Fetch sample names in a background thread
            sample_names = await to_thread_with_error_handling(
                get_sample_names,
                error_message="Failed to load sample names from database",
                ui_logger=self.append_log
            )
            
            # Update UI with fetched names
            self.sample_panel.update_sample_names(sample_names or [])
            self.append_log(f"Loaded {len(sample_names or [])} sample names from database")
        except Exception as e:
            self.append_log(f"Error loading sample names: {e}")
            self.sample_panel.show_error_state()

    def init_async_tasks(self):
        """Initialize async tasks that need to run at startup."""
        # Simply call our async starter method
        self.load_sample_names_async()

    def _setup_menu(self):
        """Set up the application menu."""
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        
        # File menu
        file_menu = QMenu("&File", self)
        file_menu.setToolTip("File operations")
        menubar.addMenu(file_menu)
        
        # Export data action with modern icon
        export_action = QAction(IconManager.get_icon("export"), "&Export Database to CSV", self)
        export_action.setStatusTip("Export all measurement data to CSV file")
        export_action.setToolTip("Save all measurement data to a CSV file")
        export_action.triggered.connect(self.export_database)
        file_menu.addAction(export_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.setToolTip("Close the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Database menu
        db_menu = QMenu("&Database", self)
        db_menu.setToolTip("Database operations")
        menubar.addMenu(db_menu)
        
        # View data action with database icon
        view_data_action = QAction(IconManager.get_icon("database"), "&View Database", self)
        view_data_action.setStatusTip("View all measurement data")
        view_data_action.setToolTip("Browse all measurement records in the database")
        view_data_action.triggered.connect(self.view_recent_data)
        db_menu.addAction(view_data_action)

    @asyncSlot()
    async def on_start_sequence(self):
        """Start the measurement sequence."""
        # Get parameters
        sample_name = self.sample_panel.get_selected_sample()
        if not sample_name:
            QMessageBox.warning(self, "Missing Information", "Please enter a sample name.")
            return
            
        tester_name = self.get_tester_name().strip()
        if not tester_name:
            QMessageBox.warning(self, "Missing Information", "Please enter your name as the tester.")
            return
            
        # Get instrument parameters
        config = self.instrument_panel.get_config()
        
        try:
            frequency = float(config['frequency'])
            voltage = float(config['voltage'])
            timeout = int(config['timeout'])
            resource_name = config['resource']
        except ValueError:
            self.append_log("Invalid numeric parameter.")
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values for frequency, voltage, and timeout.")
            return
        
        # Change button appearance to indicate test is running
        self.start_button.setText("Running Test...")
        self.start_button.setStyleSheet(START_BUTTON_RUNNING_STYLESHEET)
        self.start_button.setEnabled(False)
        self.lcr_data.clear()
        
        # Create and configure LCR meter
        lcr_meter = LCRMeter(resource_name, timeout)
        
        # Store reference to the meter
        self.lcr_meter = lcr_meter
        
        try:
            # Connect to the instrument
            if not await lcr_meter.connect():
                self.append_log("Failed to connect to instrument")
                logger.error("Failed to connect to instrument")
                return
            
            # Run the measurement sequence
            self.append_log(f"Starting Ls-Rs measurement for sample: {sample_name}")
            
            # Use the LCRMeter with context manager for proper resource management
            async with LCRMeter(resource_name, timeout) as lcr_meter:
                # Configure the instrument with the specified frequency and voltage
                await safe_async_call(
                    lcr_meter.configure(frequency, voltage),
                    error_message="Failed to configure the LCR meter",
                    ui_logger=self.append_log
                )
                    
                # Run measurement sequence and get results
                results = await safe_async_call(
                    run_measurement_sequence(lcr_meter, sample_name, tester_name),
                    error_message="Error during measurement sequence",
                    ui_logger=self.append_log
                )
                
                if results:
                    # Update data and log
                    self.lcr_data.extend(results)
                    for row in results:
                        test_type = row[2]
                        L_value = row[3]  # This is now inductance
                        Rs_value = row[4]
                        self.append_log(f"{test_type}: L={L_value} H, Rs={Rs_value} ohm")
                        
                    # Validate the measurement data
                    validation_result = validate_measurements(self.lcr_data)
                    
                    if not validation_result['valid']:
                        # Format issues for display with better formatting and visibility
                        issues_text = "\n• ".join(validation_result['issues'])
                        message = (
                            f"The following issues were detected with the measurement:\n\n"
                            f"• {issues_text}\n\n"
                            f"Do you want to save this data anyway?"
                        )
                        
                        # Create a more reliable message box with explicit styling
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle("Measurement Validation Warning")
                        msg_box.setText("Measurement validation failed")
                        msg_box.setInformativeText(message)
                        msg_box.setIcon(QMessageBox.Warning)
                        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                        msg_box.setDefaultButton(QMessageBox.No)
                        
                        # Ensure text is visible regardless of styling
                        msg_box.setStyleSheet("QLabel { color: black; min-width: 400px; }")
                        
                        reply = msg_box.exec_()
                        
                        if reply == QMessageBox.No:
                            self.append_log("Data upload canceled due to validation issues.")
                            return
                        
                        # If user clicks Yes, log that they chose to proceed despite warnings
                        self.append_log("Proceeding with data upload despite validation warnings.")
                    
                    # Proceed with data upload
                    try:
                        await db_upload_data(self)
                    except Exception as e:
                        self.append_log(f"Error saving data: {e}")
                        logger.error(f"Error uploading data: {e}")
                
        except Exception as e:
            self.append_log(f"Error during test sequence: {e}")
            logger.exception("Error in test sequence")
        finally:
            # Close the connection but maintain the reference for validation
            lcr_meter.close()
            # Restore button appearance
            self.start_button.setText("Start Ls-Rs Measurement")
            self.start_button.setStyleSheet(START_BUTTON_STYLESHEET)
            self.start_button.setEnabled(True)

    def export_database(self):
        """Export database to CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Database Export", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User canceled
        
        self.append_log(f"Exporting database to {file_path}...")
        
        # Use our new utility for async operations with error handling
        async def run_export():
            from utils.db_tools import backup_database_to_csv
            
            result = await to_thread_with_error_handling(
                backup_database_to_csv, 
                file_path,
                error_message="Database export failed",
                ui_logger=self.append_log
            )
            
            if result is not None:
                self.append_log(f"Database exported to {file_path}")
        
        asyncio.create_task(run_export())

    @asyncSlot()
    async def view_recent_data(self):
        """Show a dialog with all measurement data from the Supabase database."""
        from utils.db_tools import view_recent_measurements
        from gui.dialogs.recent_data_dialog import RecentDataDialog
        
        self.append_log("Loading measurements from Supabase database...")
        
        # Set days=None to get ALL data with a higher limit
        recent_data = await to_thread_with_error_handling(
            view_recent_measurements,
            None,  # No day limit
            1000,  # Increased record limit
            error_message="Failed to load measurements",
            ui_logger=self.append_log
        )
        
        # Display data in the proper dialog
        if recent_data:
            count = len(recent_data)
            self.append_log(f"Loaded {count} recent measurements from Supabase")
            
            # Create and show the dialog with the data
            dialog = RecentDataDialog(self, recent_data)
            dialog.exec_()
        else:
            self.append_log("No recent measurements found in Supabase database")
            QMessageBox.information(self, "Recent Measurements", 
                               "No recent measurements found in the database.")
