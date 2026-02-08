from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QLineEdit, QCheckBox, QVBoxLayout, QMessageBox
from functions.database_manager import DatabaseManager

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()

        layout = QGridLayout(self)

        settings_label = QLabel("Ustawienia")
        layout.addWidget(settings_label, 1, 0, 1, 1)

        back_button = QPushButton("X")
        back_button.clicked.connect(parent.show_main_page)
        layout.addWidget(back_button, 0, 1, 1, 1)

        # User Creation Section
        user_group = QWidget()
        user_layout = QVBoxLayout(user_group)
        
        user_layout.addWidget(QLabel("<b>Dodaj nowego użytkownika</b>"))
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nazwa użytkownika")
        user_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        user_layout.addWidget(self.password_input)
        
        self.admin_cb = QCheckBox("Administrator")
        user_layout.addWidget(self.admin_cb)
        
        add_btn = QPushButton("Dodaj")
        add_btn.clicked.connect(self.add_user)
        user_layout.addWidget(add_btn)
        
        layout.addWidget(user_group, 2, 0, 1, 2)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 3, 0)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)

    def add_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        is_admin = self.admin_cb.isChecked()
        
        if not username or not password:
            QMessageBox.warning(self, "Błąd", "Podaj nazwę użytkownika i hasło.")
            return

        if self.db_manager.add_user(username, password, is_admin):
            QMessageBox.information(self, "Sukces", f"Użytkownik {username} został dodany.")
            self.username_input.clear()
            self.password_input.clear()
            self.admin_cb.setChecked(False)
        else:
            QMessageBox.warning(self, "Błąd", "Taki użytkownik już istnieje.")