from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel, QDialog
from PyQt6.QtGui import QIcon
from panel.sidebar.sidebar import create_sidebar
from panel.wms_settings_page import WMSSettingsPage
from panel.wms_login_page import WMSLoginPage
from panel.wms_dashboard_page import WMSDashboardPage
from functions.PopupMessage import PopUpMessage
from functions.FloatingMessage import FloatingMessage
from panel.robot_control_page import RobotControlPage
from panel.warehouse_documents_page import WarehouseDocumentsPage
from panel.map_editor.editor_page_v2 import MapEditorPageV2

class MainWindow(QMainWindow):
    """Main application window for WMS System"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WMS - Warehouse Management System")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(QIcon(":/icons/app_icon.png"))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Dashboard główny zamiast prostej main page
        self.main_page = WMSDashboardPage(self)
        self.stacked_widget.addWidget(self.main_page)

        self.settings_page = WMSSettingsPage(self)
        self.stacked_widget.addWidget(self.settings_page)

        self.manual_control_page = RobotControlPage(self)
        self.dokumenty_page = WarehouseDocumentsPage(self)
        self.map_editor_page = MapEditorPageV2(self)
        self.stacked_widget.addWidget(self.manual_control_page)
        self.stacked_widget.addWidget(self.dokumenty_page)
        self.stacked_widget.addWidget(self.map_editor_page)

        self.sidebar = create_sidebar(self)
        self.sidebar.setVisible(False)
        self.show_login_dialog()

    def show_login_dialog(self):
        login_dialog = WMSLoginPage(main_window=self)
        result = login_dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # User logged in successfully
            self.stacked_widget.setCurrentWidget(self.main_page)
            self.show_sidebar()
            FloatingMessage.display(self, "Pomyślnie zalogowano!", duration=3000)
        else:
            # User cancelled login dialog (clicked X or pressed Escape)
            # Close the application
            self.close()

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