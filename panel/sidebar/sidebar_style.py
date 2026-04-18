from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import QPropertyAnimation, Qt
from PyQt6.QtGui import QIcon, QFont, QColor
from functions.RobotStatusManager import RobotStatusManager

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

        self.buttons = []
        self.button_configs = [
            ("📊 Dashboard", "show_main_page"),
            ("🤖 Sterowanie Robotem", "show_manual_control_page"),
            ("🗺️ Edytor Mapy", "show_map_editor_page"),
            ("📄 Dokumenty", "show_dokumenty_page"),
            ("🏷️ Etykiety Wysyłki", "show_labels_page"),
            ("📊 Raporty", "show_report_page"),
            ("🔍 Wyszukiwanie", "open_search"),
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

        separator = QLabel()
        separator.setStyleSheet("background-color: #334155; min-height: 1px;")
        separator.setFixedHeight(1)
        separator.setMargin(10)
        self.layout.addSpacing(10)
        self.layout.addWidget(separator)
        self.layout.addSpacing(10)

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
        
        self.status_value = QLabel("🟢 Online")
        self.status_value.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        self.status_value.setStyleSheet("color: #10b981;")
        info_layout.addWidget(self.status_value)
        
        sep_line = QLabel()
        sep_line.setStyleSheet("background-color: #334155; min-height: 1px;")
        sep_line.setFixedHeight(1)
        sep_line.setMargin(5)
        info_layout.addWidget(sep_line)
        
        robot_label = QLabel("Status Robota")
        robot_label.setFont(QFont('Segoe UI', 9, QFont.Weight.Bold))
        robot_label.setStyleSheet("color: #cbd5e1;")
        info_layout.addWidget(robot_label)
        
        self.robot_status_value = QLabel("🟢 Online")
        self.robot_status_value.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        self.robot_status_value.setStyleSheet("color: #10b981;")
        info_layout.addWidget(self.robot_status_value)
        
        self.layout.addWidget(info_box)
        
        self.robot_status_manager = RobotStatusManager()
        self.robot_status_manager.status_changed.connect(self.on_robot_status_changed)
        
        self.on_robot_status_changed(self.robot_status_manager.get_status())

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)

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
            self.setVisible(False)
            self.parent().show_login_dialog()

    def on_robot_status_changed(self, status):
        """Update robot status label"""
        if status == "Online":
            self.robot_status_value.setText("🟢 Online")
            self.robot_status_value.setStyleSheet("color: #10b981;")
        else:
            self.robot_status_value.setText("🔴 Offline")
            self.robot_status_value.setStyleSheet("color: #ef4444;")

    def show_about_page(self):
        self.parent().show_manual_control_page()
