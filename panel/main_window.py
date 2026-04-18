from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel, QDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from panel.sidebar.sidebar import create_sidebar
from panel.wms_settings_page import WMSSettingsPage
from panel.wms_login_page import WMSLoginPage
from panel.wms_dashboard_page import WMSDashboardPage
from functions.PopupMessage import PopUpMessage
from functions.FloatingMessage import FloatingMessage
from panel.robot_control_page import RobotControlPage
from panel.warehouse_documents_page import WarehouseDocumentsPage
from panel.map_editor.editor_page_v2 import MapEditorPageV2
from panel.shipment_labels_page import ShipmentLabelsPage
from panel.report_page import ReportPage
from panel.search_dialog import SearchDialog
from functions.KeyboardShortcuts import KeyboardShortcuts
from functions.RobotStatusManager import RobotStatusManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WMS - Warehouse Management System")
        self.showFullScreen()  # Fullscreen mode
        self.setWindowIcon(QIcon(":/icons/app_icon.png"))
        
        self.robot_status_manager = RobotStatusManager()
        self.robot_status_manager.start()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.main_page = WMSDashboardPage(self)
        self.stacked_widget.addWidget(self.main_page)

        self.settings_page = WMSSettingsPage(self)
        self.stacked_widget.addWidget(self.settings_page)

        self.manual_control_page = RobotControlPage(self)
        self.dokumenty_page = WarehouseDocumentsPage(self)
        self.map_editor_page = MapEditorPageV2(self)
        self.labels_page = ShipmentLabelsPage()
        self.report_page = ReportPage()
        self.stacked_widget.addWidget(self.manual_control_page)
        self.stacked_widget.addWidget(self.dokumenty_page)
        self.stacked_widget.addWidget(self.map_editor_page)
        self.stacked_widget.addWidget(self.labels_page)
        self.stacked_widget.addWidget(self.report_page)

        self.sidebar = create_sidebar(self)
        self.sidebar.setVisible(False)
        self.show_login_dialog()

    def show_login_dialog(self):
        self.hide()
        
        login_dialog = WMSLoginPage(main_window=self)
        result = login_dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            self.show()
            self.stacked_widget.setCurrentWidget(self.main_page)
            self.show_sidebar()
            FloatingMessage.display(self, "Pomyślnie zalogowano!", duration=3000)
        else:
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
    def show_labels_page(self):
        self.stacked_widget.setCurrentWidget(self.labels_page)
    def show_report_page(self):
        self.stacked_widget.setCurrentWidget(self.report_page)
    
    def open_search(self):
        """Open search dialog"""
        search_dialog = SearchDialog(self)
        search_dialog.action_selected.connect(self.handle_search_action)
        search_dialog.exec()
    
    def handle_search_action(self, action):
        """Handle action from search dialog"""
        if hasattr(self, action):
            getattr(self, action)()
    
    def keyPressEvent(self, event):
        """Handle global keyboard shortcuts"""
        if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.open_search()
            event.accept()
        elif event.key() == Qt.Key.Key_Q and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            FloatingMessage.display(self, "Wylogowywanie...", duration=1000)
            self.show_login_dialog()
            event.accept()
        else:
            super().keyPressEvent(event)
