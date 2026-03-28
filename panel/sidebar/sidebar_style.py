from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import QPropertyAnimation, Qt
from PyQt6.QtGui import QIcon, QFont, QColor

class HoverableSidebar(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setFixedWidth(220)

        self.widget = QWidget()
        self.widget.setStyleSheet("""
            QWidget {
                background-color: #1a3a52;
            }
        """)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Nagłówek
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #0f2437;
                border-bottom: 2px solid #0066cc;
                padding: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 15, 15, 15)
        header_layout.setSpacing(5)
        
        logo = QLabel("WMS")
        logo.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        logo.setStyleSheet("color: #0066cc;")
        header_layout.addWidget(logo)
        
        subtitle = QLabel("Warehouse Management System")
        subtitle.setFont(QFont('Segoe UI', 8))
        subtitle.setStyleSheet("color: #94a3b8;")
        header_layout.addWidget(subtitle)
        
        self.layout.addWidget(header_widget)

        # Przyciski nawigacji
        self.buttons = []
        self.button_configs = [
            ("📊 Dashboard", "show_main_page"),
            ("🤖 Sterowanie Robotem", "show_manual_control_page"),
            ("🗺️ Edytor Mapy", "show_map_editor_page"),
            ("📄 Dokumenty", "show_dokumenty_page"),
            ("⚙️ Ustawienia", "show_settings_page"),
        ]
        
        for label, method in self.button_configs:
            button = QPushButton(label)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #1a3a52;
                    color: #e2e8f0;
                    border: none;
                    padding: 12px 15px;
                    text-align: left;
                    font-family: 'Segoe UI';
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0066cc;
                    color: white;
                    border-left: 4px solid #00d9ff;
                }
                QPushButton:pressed {
                    background-color: #003d7a;
                }
            """)
            button.setFixedHeight(40)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.layout.addWidget(button)
            self.buttons.append((button, method))

        # Separator
        separator = QLabel()
        separator.setStyleSheet("background-color: #334155; min-height: 1px;")
        separator.setFixedHeight(1)
        separator.setMargin(10)
        self.layout.addSpacing(10)
        self.layout.addWidget(separator)
        self.layout.addSpacing(10)

        # Info box
        info_box = QWidget()
        info_box.setStyleSheet("""
            QWidget {
                background-color: #0f2437;
                border-radius: 4px;
                margin: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(5)
        
        status_label = QLabel("Status Systemu")
        status_label.setFont(QFont('Segoe UI', 9, QFont.Weight.Bold))
        status_label.setStyleSheet("color: #cbd5e1;")
        info_layout.addWidget(status_label)
        
        status_value = QLabel("🟢 Online")
        status_value.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        status_value.setStyleSheet("color: #10b981;")
        info_layout.addWidget(status_value)
        
        self.layout.addWidget(info_box)

        # Spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)

        # Przycisk wylogowania
        logout_button = QPushButton("🚪 Wyloguj się")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #7f1d1d;
                color: #fca5a5;
                border: none;
                padding: 10px 15px;
                font-weight: bold;
                border-radius: 4px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
                color: white;
            }
            QPushButton:pressed {
                background-color: #7f1d1d;
            }
        """)
        self.layout.addWidget(logout_button)

        self.widget.setLayout(self.layout)
        self.setWidget(self.widget)

        # Podłączanie przycisków do akcji
        for button, method in self.buttons:
            if hasattr(self.parent(), method):
                button.clicked.connect(lambda checked=False, m=method: getattr(self.parent(), m)())
        
        logout_button.clicked.connect(self._logout)

    def _trigger_action(self, method_name):
        """Wywoływanie metod z głównego okna"""
        if hasattr(self.parent(), method_name):
            getattr(self.parent(), method_name)()

    def _logout(self):
        """Wylogowanie użytkownika"""
        if hasattr(self.parent(), 'show_login_dialog'):
            # Hide sidebar first
            self.setVisible(False)
            # Show login dialog
            self.parent().show_login_dialog()

    def show_about_page(self):
        self.parent().show_manual_control_page()