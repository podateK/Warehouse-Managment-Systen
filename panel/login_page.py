from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from functions.PopupMessage import PopUpMessage
from functions.database_manager import DatabaseManager

class LoginPage(QDialog):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.db_manager = DatabaseManager()

        self.setWindowTitle("Login")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)
        title_label = QLabel("Panel logowania")
        layout.addWidget(title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nazwa użytkownika")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("Zaloguj się")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
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