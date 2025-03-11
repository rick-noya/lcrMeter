"""
Widget for LCR meter configuration.
"""
import logging
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

from gui.widgets.number_pad import NumberPadLineEdit
from config.settings import DEFAULT_FREQUENCY, DEFAULT_VOLTAGE, DEFAULT_TIMEOUT, DEFAULT_RESOURCE

logger = logging.getLogger(__name__)

class InstrumentConfigPanel(QWidget):
    """
    A widget for configuring the LCR meter parameters.
    """
    # Define signals
    config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the widget UI components."""
        layout = QGridLayout(self)
        
        # Resource input
        layout.addWidget(QLabel("LCR tester:"), 0, 0, Qt.AlignRight)
        self.resource_input = NumberPadLineEdit()
        self.resource_input.setText(DEFAULT_RESOURCE)
        self.resource_input.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.resource_input, 0, 1)
        
        # Frequency input
        layout.addWidget(QLabel("Frequency (Hz):"), 1, 0, Qt.AlignRight)
        self.frequency_input = NumberPadLineEdit()
        self.frequency_input.setPlaceholderText(str(DEFAULT_FREQUENCY))
        self.frequency_input.setText(str(DEFAULT_FREQUENCY))
        self.frequency_input.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.frequency_input, 1, 1)
        
        # Voltage input
        layout.addWidget(QLabel("Voltage (V):"), 2, 0, Qt.AlignRight)
        self.voltage_input = NumberPadLineEdit()
        self.voltage_input.setPlaceholderText(str(DEFAULT_VOLTAGE))
        self.voltage_input.setText(str(DEFAULT_VOLTAGE))
        self.voltage_input.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.voltage_input, 2, 1)
        
        # Timeout input
        layout.addWidget(QLabel("Timeout (ms):"), 3, 0, Qt.AlignRight)
        self.timeout_input = NumberPadLineEdit()
        self.timeout_input.setPlaceholderText(str(DEFAULT_TIMEOUT))
        self.timeout_input.setText(str(DEFAULT_TIMEOUT))
        self.timeout_input.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.timeout_input, 3, 1)
    
    def _on_config_changed(self):
        """Emit signal when configuration changes."""
        self.config_changed.emit(self.get_config())
    
    def get_config(self) -> dict:
        """Get the current instrument configuration."""
        return {
            'resource': self.resource_input.text().strip(),
            'frequency': self.frequency_input.text().strip() or DEFAULT_FREQUENCY,
            'voltage': self.voltage_input.text().strip() or DEFAULT_VOLTAGE,
            'timeout': self.timeout_input.text().strip() or DEFAULT_TIMEOUT
        }