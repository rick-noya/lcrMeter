import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QSizePolicy, QDialogButtonBox, 
    QStyle, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

logger = logging.getLogger(__name__)

class RecentDataDialog(QDialog):
    """Dialog for displaying recent measurements from the database."""
    
    def __init__(self, parent=None, measurements=None):
        super().__init__(parent)
        # Log what we received to help diagnose issues
        logger.debug(f"RecentDataDialog: Received {len(measurements) if measurements else 0} measurements")
        if measurements:
            logger.debug(f"First measurement: {measurements[0]}")
            
        self.measurements = measurements or []
        self.setWindowTitle("Recent Measurements")
        self.setMinimumSize(900, 600)  # Even larger for better visibility
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # Center the dialog on the screen
        self.setGeometry(
            QStyle.alignedRect(
                Qt.LeftToRight,
                Qt.AlignCenter,
                self.size(),
                QApplication.desktop().availableGeometry()
            )
        )
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the dialog UI components."""
        logger.debug("Setting up Recent Data Dialog UI")
        layout = QVBoxLayout(self)
        
        # Add status/info label with better visibility
        self.status_label = QLabel("Recent measurements:")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
        layout.addWidget(self.status_label)
        
        # Create table widget with better visibility
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d3d3d3;
                gridline-color: #e0e0e0;
                background-color: #ffffff;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
            }
        """)
        # Make table expand to fill available space
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.table)
        
        # Add button row using standard dialog buttons
        button_box = QDialogButtonBox()
        close_button = button_box.addButton("Close", QDialogButtonBox.AcceptRole)
        close_button.setMinimumSize(120, 40)
        close_button.setStyleSheet("font-size: 12px; font-weight: bold;")
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        # Populate table with data
        self.populate_data_table(self.measurements)
    
    def populate_data_table(self, measurements):
        """
        Populate the table with measurement data.
        
        Args:
            measurements: List of measurement dictionaries from Supabase
        """
        logger.debug(f"Populating table with {len(measurements)} measurements")
        
        self.table.setRowCount(0)  # Clear the table
        self.table.clearContents()  # Clear all contents
        
        if not measurements:
            logger.warning("No measurements provided to display")
            self.status_label.setText("No recent measurements found")
            self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: red;")
            
            # Add a single row with a message
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Message"])
            item = QTableWidgetItem("No data available")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            return
            
        # SIMPLIFIED TABLE CREATION - more robust approach
        
        # 1. Create columns based on the first measurement
        first_row = measurements[0]
        columns = []
        display_names = {}
        
        # Define column display names (what users will see)
        display_names = {
            "id": "ID",
            "created_at": "Date/Time",
            "sample_name": "Sample",
            "test_type": "Test Type",
            "impedance": "Inductance (H)",
            "resistance": "Resistance (Ω)",
            "tester": "Tester"
        }
        
        # Only use columns that we have a display name for
        for col in first_row.keys():
            if col in display_names:
                columns.append(col)
        
        # 2. Setup table dimensions
        self.table.setRowCount(len(measurements))
        self.table.setColumnCount(len(columns))
        
        # Set column headers using display names
        header_labels = [display_names.get(col, col) for col in columns]
        self.table.setHorizontalHeaderLabels(header_labels)
        
        # 3. Populate the data
        for row_idx, measurement in enumerate(measurements):
            for col_idx, column in enumerate(columns):
                # Get the value, defaulting to empty string if missing
                value = measurement.get(column, "")
                
                # Format date/time values nicely
                if column == "created_at" and value:
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        local_dt = dt.astimezone(tz=None)
                        value = local_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception as e:
                        logger.warning(f"Error formatting datetime {value}: {e}")
                
                # Format scientific notation values nicely
                if column in ["impedance", "resistance"] and 'e' in str(value).lower():
                    try:
                        # Format scientific notation more cleanly
                        float_val = float(value)
                        value = f"{float_val:.3e}"
                    except:
                        pass  # Keep original value if parsing fails
                
                # Create and set table item
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Scientific notation gets bold
                if column in ["impedance", "resistance"] and 'e' in str(value).lower():
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                
                self.table.setItem(row_idx, col_idx, item)
        
        # 4. Format table columns and rows
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        
        # Make date column wider for better visibility
        date_col = columns.index("created_at") if "created_at" in columns else -1
        if date_col >= 0:
            self.table.setColumnWidth(date_col, 180)
        
        # Make numerical columns fixed width
        for col, col_name in enumerate(columns):
            if col_name in ["impedance", "resistance"]:
                self.table.setColumnWidth(col, 150)
        
        # Set alternate row colors for better readability
        self.table.setAlternatingRowColors(True)
        
        # Update status label
        self.status_label.setText(f"Showing {len(measurements)} records")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: green;")
        
        logger.debug("Table population complete")

    def showEvent(self, event):
        """Override show event to ensure dialog is visible and data is displayed correctly"""
        logger.debug("RecentDataDialog: showEvent triggered")
        super().showEvent(event)
        
        # Force resize columns for better visibility after showing
        self.table.resizeColumnsToContents()
        
        # Ensure dialog is in a visible area of the screen
        screen_geo = QApplication.desktop().screenGeometry()
        dialog_geo = self.geometry()
        
        # Center if somehow we're offscreen
        if not screen_geo.contains(dialog_geo):
            self.setGeometry(
                QStyle.alignedRect(
                    Qt.LeftToRight,
                    Qt.AlignCenter,
                    self.size(),
                    screen_geo
                )
            )
            logger.debug("RecentDataDialog: Repositioned dialog to center of screen")
        
        # Log dialog and table dimensions for debugging
        logger.debug(f"Dialog size: {self.width()}x{self.height()}")
        logger.debug(f"Table size: {self.table.width()}x{self.table.height()}")
        logger.debug(f"Table row count: {self.table.rowCount()}, column count: {self.table.columnCount()}")