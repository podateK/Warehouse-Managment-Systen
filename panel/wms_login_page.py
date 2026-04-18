from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt
from functions.PopupMessage import PopUpMessage
from functions.database_manager import DatabaseManager

class WMSLoginPage(QDialog):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.db_manager = DatabaseManager()

        self.setWindowTitle("WMS - Panel Logowania")
        self.setFixedSize(540, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                background-color: white;
                color: #2c3e50;
                border: 2px solid #d1d5db;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("WMS")
        title_font = QFont('Segoe UI', 32, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #0066cc; margin-bottom: 5px; padding: 10px;")
        title_label.setMinimumHeight(50)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Warehouse Management System")
        subtitle_font = QFont('Segoe UI', 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #6b7280; margin-bottom: 20px;")
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)

        separator = QLabel()
        separator.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        main_layout.addWidget(separator)

        username_label = QLabel("Nazwa użytkownika")
        username_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        username_label.setStyleSheet("color: #374151;")
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Wpisz swoją nazwę użytkownika")
        main_layout.addWidget(self.username_input)

        password_label = QLabel("Hasło")
        password_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        password_label.setStyleSheet("color: #374151;")
        main_layout.addWidget(password_label)
        
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Wpisz swoje hasło")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_input)
        
        self.toggle_password_btn = QPushButton("👁️")
        self.toggle_password_btn.setFixedSize(40, 40)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #6b7280;
                border: 2px solid #d1d5db;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                border: 2px solid #0066cc;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_btn)
        
        main_layout.addLayout(password_layout)

        main_layout.addSpacing(10)

        login_button = QPushButton("Zaloguj się")
        login_button.setMinimumHeight(40)
        login_button.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(login_button)

        main_layout.addStretch()

        footer_label = QLabel("© 2026 Warehouse Management System")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #9ca3af; font-size: 9px;")
        main_layout.addWidget(footer_label)

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("👁️")

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            PopUpMessage.show_message("Błąd", "Proszę podać wszystkie dane", self)
            return
        
        success, is_admin = self.db_manager.check_login(username, password)
        
        if success:
            if is_admin:
                print("Zalogowano jako Administrator")
                PopUpMessage.show_message("Sukces", "Zalogowano pomyślnie jako Administrator", self)
            else:
                print("Zalogowano jako Użytkownik")
                PopUpMessage.show_message("Sukces", "Zalogowano pomyślnie", self)
            self.accept()
        else:
            print("Nieprawidłowa nazwa użytkownika lub hasło")
            PopUpMessage.show_message("Błąd logowania", "Nieprawidłowa nazwa użytkownika lub hasło", self)

LoginPage = WMSLoginPage
