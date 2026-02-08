import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from panel.main_window import MainWindow

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set App Icon
    icon_path = resource_path(os.path.join('icons', 'app_icon.jpg'))
    app.setWindowIcon(QIcon(icon_path))

    # Apply Global Dark Theme
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QDialog {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        QPushButton {
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #0b5ed7;
        }
        QPushButton:pressed {
            background-color: #0a58ca;
        }
        QLineEdit, QDateEdit, QComboBox, QSpinBox, QTextEdit {
            background-color: #3b3b3b;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
        }
        QTableWidget, QListWidget, QTreeWidget {
            background-color: #3b3b3b;
            color: #ffffff;
            gridline-color: #555555;
            border: 1px solid #555555;
        }
        QHeaderView::section {
            background-color: #4b4b4b;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
        }
        QTableCornerButton::section {
            background-color: #4b4b4b;
            border: 1px solid #555555;
        }
        QMenu {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #0d6efd;
        }
        QToolTip {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QScrollBar:vertical {
            border: none;
            background: #2b2b2b;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #555555;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())