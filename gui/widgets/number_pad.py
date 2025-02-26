from PyQt5.QtWidgets import (
    QLineEdit, QPushButton, QGridLayout, QDialog, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt

class NumberPad(QDialog):
    """
    A numeric keypad dialog for entering numbers.
    """
    def __init__(self, parent=None, current_text=""):
        super().__init__(parent)
        self.setWindowTitle("Number Pad")
        self.setModal(True)
        
        # Store the initial and current text
        self.current_text = current_text
        
        # Set up the UI
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Display for showing the current number
        self.display = QLineEdit(self.current_text)
        self.display.setAlignment(Qt.AlignRight)
        layout.addWidget(self.display)
        
        # Create the number pad grid
        grid = QGridLayout()
        layout.addLayout(grid)
        
        # Add number buttons (0-9)
        positions = [(i, j) for i in range(3) for j in range(3)]
        for position, num in zip(positions, range(1, 10)):
            button = QPushButton(str(num))
            button.clicked.connect(lambda _, n=num: self.add_digit(n))
            grid.addWidget(button, *position)
        
        # Add 0, decimal point, and backspace
        zero_button = QPushButton("0")
        zero_button.clicked.connect(lambda: self.add_digit(0))
        grid.addWidget(zero_button, 3, 0)
        
        decimal_button = QPushButton(".")
        decimal_button.clicked.connect(self.add_decimal)
        grid.addWidget(decimal_button, 3, 1)
        
        backspace_button = QPushButton("⌫")
        backspace_button.clicked.connect(self.backspace)
        grid.addWidget(backspace_button, 3, 2)
        
        # Add OK and Cancel buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

    def add_digit(self, digit):
        """Add a digit to the current text."""
        self.current_text += str(digit)
        self.display.setText(self.current_text)

    def add_decimal(self):
        """Add a decimal point if there isn't one already."""
        if "." not in self.current_text:
            self.current_text += "."
            self.display.setText(self.current_text)

    def backspace(self):
        """Remove the last character from the current text."""
        self.current_text = self.current_text[:-1]
        self.display.setText(self.current_text)

    def get_value(self):
        """Return the current value."""
        return self.current_text


class NumberPadLineEdit(QLineEdit):
    """
    A QLineEdit that shows a numeric keypad when clicked.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def mousePressEvent(self, event):
        """Show the number pad when the line edit is clicked."""
        super().mousePressEvent(event)
        
        # Create and show the number pad dialog
        number_pad = NumberPad(self, self.text())
        if number_pad.exec_() == QDialog.Accepted:
            # Update the text if OK was pressed
            self.setText(number_pad.get_value())