"""
Widget for LCR meter configuration.
"""
import logging
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

from gui.widgets.number_pad import NumberPadLineEdit
from config.settings import DEFAULT_FREQUENCY, DEFAULT_VOLTAGE, DEFAULT_TIMEOUT, DEFAULT_RESOURCE
from gui.stylesheets import INSTRUMENT_CONFIG_STYLESHEET

logger = logging.getLogger(__name__)

class InstrumentConfigPanel(QWidget):
    """
    A widget for configuring the LCR meter parameters.
    """
    # Define signals
    config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Apply centralized stylesheet
        self.setStyleSheet(INSTRUMENT_CONFIG_STYLESHEET)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the widget UI components."""
        layout = QGridLayout(self)
        
        # Resource input
        resource_label = QLabel("LCR tester:")
        resource_label.setToolTip("VISA resource identifier for connecting to the LCR meter")
        layout.addWidget(resource_label, 0, 0, Qt.AlignRight)
        
        self.resource_input = NumberPadLineEdit()
        self.resource_input.setText(DEFAULT_RESOURCE)
        self.resource_input.setToolTip(
            "VISA resource identifier (connection address) for your LCR meter"
        )
        self.resource_input.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.resource_input, 0, 1)
        
        # Frequency input
        freq_label = QLabel("Frequency (Hz):")
        freq_label.setToolTip("Measurement signal frequency in Hertz")
        layout.addWidget(freq_label, 1, 0, Qt.AlignRight)
        
        self.frequency_input = NumberPadLineEdit()
        self.frequency_input.setPlaceholderText(str(DEFAULT_FREQUENCY))
        self.frequency_input.setText(str(DEFAULT_FREQUENCY))
        self.frequency_input.setToolTip(
            "Test signal frequency (default: 100,000 Hz)"
        )
        self.frequency_input.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.frequency_input, 1, 1)
        
        # Voltage input
        voltage_label = QLabel("Voltage (V):")
        voltage_label.setToolTip("Test signal voltage amplitude in Volts")
        layout.addWidget(voltage_label, 2, 0, Qt.AlignRight)
        
        self.voltage_input = NumberPadLineEdit()
        self.voltage_input.setPlaceholderText(str(DEFAULT_VOLTAGE))
        self.voltage_input.setText(str(DEFAULT_VOLTAGE))
        self.voltage_input.setToolTip(
            "Test signal voltage (default: 1.0 V)"
        )
        self.voltage_input.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.voltage_input, 2, 1)
        
        # Timeout input
        timeout_label = QLabel("Timeout (ms):")
        timeout_label.setToolTip("Communication timeout with the instrument")
        layout.addWidget(timeout_label, 3, 0, Qt.AlignRight)
        
        self.timeout_input = NumberPadLineEdit()
        self.timeout_input.setPlaceholderText(str(DEFAULT_TIMEOUT))
        self.timeout_input.setText(str(DEFAULT_TIMEOUT))
        self.timeout_input.setToolTip(
            "Communication timeout in milliseconds (default: 10000 ms).\n\n"
            "This controls how long the software waits for a response\n"
        )
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