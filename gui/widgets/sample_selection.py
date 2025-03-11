"""
Widget for sample selection and management.
"""
import asyncio
import logging
from typing import List, Callable, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QListWidget, QListWidgetItem, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal
from gui.stylesheets import SAMPLE_PANEL_STYLESHEET

logger = logging.getLogger(__name__)

class SampleSelectionPanel(QWidget):
    """
    A widget that manages sample selection, including the input field, 
    list of samples, and refresh functionality.
    """
    # Define signals
    sample_selected = pyqtSignal(str)
    sample_filter_changed = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sample_names = []
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the widget UI components."""
        layout = QVBoxLayout(self)
        
        # Sample name input with refresh button
        input_layout = QHBoxLayout()
        self.sample_name_label = QLabel("Sample Name:")
        input_layout.addWidget(self.sample_name_label, alignment=Qt.AlignRight)
        
        self.sample_name_input = QLineEdit()
        self.sample_name_input.setPlaceholderText("Enter sample name or select from list")
        self.sample_name_input.textChanged.connect(self._on_text_changed)
        input_layout.addWidget(self.sample_name_input)
        
        # Refresh button with icon
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh_button.setToolTip("Refresh Sample List")
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        input_layout.addWidget(self.refresh_button)
        
        layout.addLayout(input_layout)
        
        # List heading
        heading_label = QLabel("Previously Tested Samples:")
        heading_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(heading_label)
        
        # Samples list widget - apply stylesheet
        self.sample_list = QListWidget()
        self.sample_list.setMaximumHeight(150)  # Limit height
        self.sample_list.setStyleSheet(SAMPLE_PANEL_STYLESHEET)
        self.sample_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.sample_list)
        
    def update_sample_names(self, sample_names: List[str]):
        """Update the list of available sample names."""
        self.sample_names = sorted(sample_names, key=lambda name: name.lower())
        self._update_list_display()
        
    def get_selected_sample(self) -> str:
        """Get the currently selected/entered sample name."""
        return self.sample_name_input.text().strip()
    
    def set_selected_sample(self, sample_name: str):
        """Set the selected sample name."""
        self.sample_name_input.setText(sample_name)
        
    def _update_list_display(self):
        """Update the list widget based on current filter."""
        current_filter = self.sample_name_input.text().lower()
        
        filtered = (
            self.sample_names[:] if not current_filter 
            else [name for name in self.sample_names if current_filter in name.lower()]
        )
        
        self.sample_list.clear()
        
        if filtered:
            for name in filtered:
                self.sample_list.addItem(QListWidgetItem(name))
        else:
            # Show message when no matches
            message = (f"No matching samples found for '{current_filter}'. "
                     "Click \"Start\" to run a test and add a new sample.")
            item = QListWidgetItem(message)
            item.setFlags(Qt.NoItemFlags)  # Make non-selectable
            self.sample_list.addItem(item)
            
    def _on_text_changed(self, text: str):
        """Handle text changes in the input field."""
        self._update_list_display()
        self.sample_filter_changed.emit(text)
        
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle clicks on sample list items."""
        try:
            # Immediately capture the text to avoid deleted-object issues
            item_text = item.text()
            
            # Only proceed if the item is selectable
            if item.flags() & Qt.ItemIsSelectable:
                # Temporarily block signals to prevent recursive updates
                self.sample_name_input.blockSignals(True)
                self.sample_name_input.setText(item_text)
                self.sample_name_input.blockSignals(False)
                
                # Emit the signal with the captured text
                self.sample_selected.emit(item_text)
        except RuntimeError:
            # Handle case where the item has been deleted
            logger.warning("Item was deleted before it could be processed")
            
    def _on_refresh_clicked(self):
        """Handle refresh button clicks."""
        self.refresh_requested.emit()
        
    def show_loading_state(self):
        """Show loading state in the list."""
        self.sample_list.clear()
        self.sample_list.addItem("Loading sample names...")
        
    def show_error_state(self, error_msg: str = "Error loading samples"):
        """Show error state in the list."""
        self.sample_list.clear()
        self.sample_list.addItem(error_msg)