from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QCheckBox, QMessageBox, QGroupBox, QFormLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from functions.database_manager import DatabaseManager

class WMSSettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.db_manager = DatabaseManager()
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        title = QLabel("⚙️ Ustawienia Systemu")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a3a52;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        separator = QLabel()
        separator.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        user_group = QGroupBox("👤 Zarządzanie Użytkownikami")
        user_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding-top: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #1a3a52;
                font-weight: bold;
            }
        """)
        user_layout = QFormLayout(user_group)
        user_layout.setSpacing(12)
        
        username_label = QLabel("Nazwa użytkownika:")
        username_label.setStyleSheet("color: #374151; font-weight: bold;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Wpisz nową nazwę użytkownika")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
            }
        """)
        user_layout.addRow(username_label, self.username_input)
        
        password_label = QLabel("Hasło:")
        password_label.setStyleSheet("color: #374151; font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Wpisz hasło")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
            }
        """)
        user_layout.addRow(password_label, self.password_input)
        
        self.admin_cb = QCheckBox("📌 Uprawnienia Administratora")
        self.admin_cb.setStyleSheet("""
            QCheckBox {
                color: #374151;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #0066cc;
            }
        """)
        user_layout.addRow(self.admin_cb)
        
        add_btn = QPushButton("✅ Dodaj Użytkownika")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        add_btn.clicked.connect(self.add_user)
        user_layout.addRow(add_btn)
        
        layout.addWidget(user_group)

        layout.addStretch()
        
        other_group = QGroupBox("🔧 Inne Ustawienia")
        other_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding-top: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #1a3a52;
                font-weight: bold;
            }
        """)
        other_layout = QVBoxLayout(other_group)
        other_layout.setSpacing(12)
        
        version_label = QLabel("📦 Wersja Systemu: 2.0.0 (2026)")
        version_label.setStyleSheet("color: #6b7280;")
        other_layout.addWidget(version_label)
        
        layout.addWidget(other_group)
        
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        back_button = QPushButton("← Wróć do Dashboard")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        back_button.clicked.connect(self.parent_window.show_main_page)
        button_layout.addWidget(back_button)
        layout.addLayout(button_layout)

    def add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        is_admin = self.admin_cb.isChecked()
        
        if not username or not password:
            QMessageBox.warning(self, "⚠️ Błąd", "Podaj nazwę użytkownika i hasło.")
            return

        if self.db_manager.add_user(username, password, is_admin):
            role = "Administratora" if is_admin else "Użytkownika"
            QMessageBox.information(self, "✅ Sukces", f"{role} '{username}' został(a) dodany(a) pomyślnie.")
            self.username_input.clear()
            self.password_input.clear()
            self.admin_cb.setChecked(False)
        else:
            QMessageBox.warning(self, "❌ Błąd", f"Użytkownik '{username}' już istnieje w bazie danych.")

SettingsPage = WMSSettingsPage
