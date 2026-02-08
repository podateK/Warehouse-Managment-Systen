from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel, QDialog
from PyQt6.QtGui import QIcon
from panel.sidebar.sidebar import create_sidebar
from panel.settings_page import SettingsPage
from panel.login_page import LoginPage
from functions.PopupMessage import PopUpMessage
from functions.FloatingMessage import FloatingMessage
from panel.manual_control_page import ManualControlPage
from panel.dokumenty_page import DokumentyPage
from panel.map_editor import MapEditorPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WMS Application")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon(":/icons/app_icon.png"))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.main_page = QWidget()
        main_layout = QVBoxLayout(self.main_page)
        main_label = QLabel("Main Page Content")
        main_layout.addWidget(main_label)
        self.stacked_widget.addWidget(self.main_page)

        self.settings_page = SettingsPage(self)
        self.stacked_widget.addWidget(self.settings_page)

        self.manual_control_page = ManualControlPage(self)
        self.dokumenty_page = DokumentyPage(self)
        self.map_editor_page = MapEditorPage(self)
        self.stacked_widget.addWidget(self.manual_control_page)
        self.stacked_widget.addWidget(self.dokumenty_page)
        self.stacked_widget.addWidget(self.map_editor_page)

        self.sidebar = create_sidebar(self)
        self.sidebar.setVisible(False)
        self.show_login_dialog()

    def show_login_dialog(self):
        login_dialog = LoginPage(main_window=self)
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            self.stacked_widget.setCurrentWidget(self.main_page)
            self.show_sidebar()
            FloatingMessage.display(self, "Pomyślnie zalogowano!", duration=3000)

    def show_sidebar(self):
        self.sidebar.setVisible(True)

    def show_settings_page(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def show_main_page(self):
        self.stacked_widget.setCurrentWidget(self.main_page)

    def show_manual_control_page(self):
        self.stacked_widget.setCurrentWidget(self.manual_control_page)
    def show_dokumenty_page(self):
        self.stacked_widget.setCurrentWidget(self.dokumenty_page)
    def show_map_editor_page(self):
        self.stacked_widget.setCurrentWidget(self.map_editor_page)