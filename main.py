import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from panel.main_window import MainWindow

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    icon_path = resource_path(os.path.join('icons', 'app_icon.jpg'))
    app.setWindowIcon(QIcon(icon_path))

    # Profesjonalny WMS stylesheet - przemysłowy design
    app.setStyleSheet("""
        /* Kolory palety */
        QWidget {
            background-color: #f5f7fa;
            color: #2c3e50;
        }
        QDialog {
            background-color: #f5f7fa;
            color: #2c3e50;
        }
        QMainWindow {
            background-color: #f5f7fa;
            color: #2c3e50;
        }
        
        /* Etykiety */
        QLabel {
            color: #2c3e50;
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        }
        
        /* Przyciski - profesjonalny styl */
        QPushButton {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #0052a3;
        }
        QPushButton:pressed {
            background-color: #003d7a;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #999999;
        }
        
        /* Pola wejścia */
        QLineEdit {
            background-color: white;
            color: #2c3e50;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 8px;
            selection-background-color: #0066cc;
        }
        QLineEdit:focus {
            border: 2px solid #0066cc;
            border-radius: 4px;
        }
        
        /* Listy */
        QListWidget {
            background-color: white;
            color: #2c3e50;
            border: 1px solid #d1d5db;
            border-radius: 4px;
        }
        QListWidget::item:selected {
            background-color: #0066cc;
            color: white;
        }
        
        /* Combo box */
        QComboBox {
            background-color: white;
            color: #2c3e50;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 6px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: none;
        }
        
        /* Dock widgets - sidebar */
        QDockWidget {
            background-color: #f5f7fa;
            border: 1px solid #e5e7eb;
        }
        QDockWidget::title {
            background-color: #1a3a52;
            color: white;
            padding: 5px;
        }
        
        /* ScrollBary */
        QScrollBar:vertical {
            background-color: #f5f7fa;
            width: 12px;
            border: none;
        }
        QScrollBar::handle:vertical {
            background-color: #a0aec0;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #7a8fa3;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
        }
        
        /* TabWidget */
        QTabWidget::pane {
            border: 1px solid #d1d5db;
        }
        QTabBar::tab {
            background-color: #e5e7eb;
            color: #2c3e50;
            padding: 8px 20px;
            border: none;
        }
        QTabBar::tab:selected {
            background-color: #0066cc;
            color: white;
        }
        QTabBar::tab:hover {
            background-color: #0052a3;
        }
        
        /* Menu */
        QMenu {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #d1d5db;
        }
        QMenu::item:selected {
            background-color: #0066cc;
            color: white;
        }
        
        /* Tooltip */
        QToolTip {
            background-color: #1a3a52;
            color: #ffffff;
            border: 1px solid #0066cc;
            padding: 4px;
            border-radius: 4px;
        }
        
        /* SpinBox */
        QSpinBox, QDateEdit {
            background-color: white;
            color: #2c3e50;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 6px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())