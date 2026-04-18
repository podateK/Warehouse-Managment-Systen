from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class PopUpMessage(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)  # Updated here

        layout = QVBoxLayout(self)

        message_label = QLabel(message)
        layout.addWidget(message_label)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    @staticmethod
    def show_message(title, message, parent=None):
        popup = PopUpMessage(title, message, parent)
        popup.exec()
