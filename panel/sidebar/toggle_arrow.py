from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal

class ToggleArrow(QLabel):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_arrow()

    def mousePressEvent(self, event):
        self.expanded = not self.expanded
        self.update_arrow()
        self.toggled.emit(self.expanded)

    def update_arrow(self):
        if self.expanded:
            self.setText("◀")
        else:
            self.setText("▶")
