from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QScrollArea
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize
from functions.database_manager import DatabaseManager
from functions.RobotStatusManager import RobotStatusManager
from functions.FloatingMessage import FloatingMessage

class StatCard(QWidget):
    def __init__(self, title, value, unit="", color="#0066cc"):
        super().__init__()
        
        self.color = color
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        
        title_label = QLabel(title)
        title_font = QFont('Segoe UI', 10)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #6b7280; font-weight: bold;")
        layout.addWidget(title_label)
        
        value_layout = QHBoxLayout()
        self.value_label = QLabel(str(value))
        value_font = QFont('Segoe UI', 28, QFont.Weight.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {color};")
        value_layout.addWidget(self.value_label)
        
        if unit:
            unit_label = QLabel(unit)
            unit_font = QFont('Segoe UI', 10)
            unit_label.setFont(unit_font)
            unit_label.setStyleSheet("color: #9ca3af;")
            unit_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
    
    def update_value(self, new_value, new_color=None):
        """Update the card's value and optionally its color"""
        self.value_label.setText(str(new_value))
        if new_color:
            self.color = new_color
            self.value_label.setStyleSheet(f"color: {new_color};")
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: white;
                    border-radius: 8px;
                    border-left: 4px solid {new_color};
                }}
            """)


class WMSDashboardPage(QWidget):
    """Professional WMS dashboard with key metrics and system overview"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
        self.db_manager = DatabaseManager()
        pending_orders = self.db_manager.get_pending_orders()
        inventory = self.db_manager.get_inventory()
        recent_operations = self.db_manager.get_recent_operations(15)
        
        
        active_orders_count = len(pending_orders)
        stock_items_count = sum([int(item[2]) for item in inventory]) if inventory else 0
        pending_shipments_count = len([o for o in pending_orders if o[3] == "Do wysłania"])
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard WMS")
        title_font = QFont('Segoe UI', 20, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1a3a52;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        separator = QLabel()
        separator.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.active_orders = StatCard("Aktywne Zamówienia", active_orders_count, "", "#0066cc")
        self.stock_items = StatCard("Artykuły w Magazynie", stock_items_count, "szt.", "#10b981")
        self.pending_shipments = StatCard("Oczekujące Wysyłki", pending_shipments_count, "", "#f59e0b")
        self.system_status = StatCard("Status Robota", "Sprawdzanie...", "", "#06b6d4")
        self.drive_mode_card = StatCard("Tryb Robota", "Automatic", "", "#6b7280")
        
        stats_layout.addWidget(self.active_orders, 0, 0)
        stats_layout.addWidget(self.stock_items, 0, 1)
        stats_layout.addWidget(self.pending_shipments, 0, 2)
        stats_layout.addWidget(self.system_status, 0, 3)
        stats_layout.addWidget(self.drive_mode_card, 1, 0, 1, 2)
        
        self.robot_status_manager = RobotStatusManager()
        self.robot_status_manager.status_changed.connect(self.on_robot_status_changed)
        self.robot_status_manager.drive_mode_changed.connect(self.on_drive_mode_changed)
        self.on_robot_status_changed(self.robot_status_manager.get_status())
        self.on_drive_mode_changed(self.robot_status_manager.get_drive_mode())
        
        main_layout.addLayout(stats_layout)
        action_label = QLabel("Szybkie Akcje")
        action_font = QFont('Segoe UI', 12, QFont.Weight.Bold)
        action_label.setFont(action_font)
        action_label.setStyleSheet("color: #1a3a52; margin-top: 20px;")
        main_layout.addWidget(action_label)
        
        separator2 = QLabel()
        separator2.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        separator2.setFixedHeight(1)
        main_layout.addWidget(separator2)
        
        actions_layout = QHBoxLayout()
        
        btn_style = """
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """
        
        btn_generate_label = QPushButton("🏷️ Generuj Etykietę")
        btn_generate_label.setStyleSheet(btn_style)
        btn_generate_label.clicked.connect(self.on_generate_label)
        actions_layout.addWidget(btn_generate_label)

        self.btn_refresh_robot = QPushButton("🔄 Odśwież status robota")
        self.btn_refresh_robot.setStyleSheet(btn_style)
        self.btn_refresh_robot.clicked.connect(self.on_robot_status)
        actions_layout.addWidget(self.btn_refresh_robot)
        
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)
        
        main_layout.addSpacing(20)
        
        info_label = QLabel("Ostatnie Operacje (ostatnie 15)")
        info_font = QFont('Segoe UI', 12, QFont.Weight.Bold)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #1a3a52;")
        main_layout.addWidget(info_label)
        
        separator3 = QLabel()
        separator3.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        separator3.setFixedHeight(1)
        main_layout.addWidget(separator3)
        
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                background: #f5f5f5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #0066cc;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #0052a3;
            }
        """)
        scroll_area.setWidgetResizable(True)
        
        operations_box = QWidget()
        operations_box.setStyleSheet("background-color: white;")
        operations_layout = QVBoxLayout(operations_box)
        operations_layout.setContentsMargins(15, 15, 15, 15)
        operations_layout.setSpacing(8)
        operations_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        if recent_operations:
            for op in recent_operations:
                timestamp_full = op[1]  # "2026-03-28 14:35"
                description = op[3]
                op_type = op[2]
                
                op_text = f"• {timestamp_full} - {description}"
                op_label = QLabel(op_text)
                op_label.setStyleSheet("color: #374151; padding: 3px 0px; font-size: 10px;")
                op_label.setFont(QFont('Segoe UI', 9))
                op_label.setWordWrap(True)
                operations_layout.addWidget(op_label)
        else:
            no_ops_label = QLabel("• Brak ostatnich operacji")
            no_ops_label.setStyleSheet("color: #9ca3af; padding: 5px 0px;")
            operations_layout.addWidget(no_ops_label)
        
        scroll_area.setWidget(operations_box)
        scroll_area.setMaximumHeight(300)
        scroll_area.setMinimumHeight(150)
        main_layout.addWidget(scroll_area)
    
    def on_generate_label(self):
        """Navigate to shipment labels page from dashboard quick action."""
        self.db_manager.add_operation("LABEL_OPEN", "Przejście do generatora etykiet", "Ukończone", "admin")
        parent = self.parent()
        if parent and hasattr(parent, 'show_labels_page'):
            parent.show_labels_page()
        else:
            print("Nie można otworzyć strony etykiet: brak referencji do MainWindow")

    def on_robot_status(self):
        """Handle robot status button click - refresh robot status immediately"""
        self.db_manager.add_operation("ROBOT_STATUS_CHECK", "Sprawdzenie statusu robota AGV-01", "Ukończone", "system")

        details = self.robot_status_manager.refresh_now_with_details()
        status = details.get("status", "Offline")
        if status == "Online":
            FloatingMessage.display(self, "Robot: Online", duration=1800)
            print(f"Status robota: Online | {details}")
        else:
            FloatingMessage.display(self, "Robot: Offline", duration=1800)
            print(f"Status robota: Offline | {details}")

    def on_robot_status_changed(self, status):
        """Update robot status card when status changes"""
        if status == "Online":
            color = "#10b981"  # Green for online
            display_text = "Online"
        else:
            color = "#ef4444"  # Red for offline
            display_text = "Offline"
        
        self.system_status.update_value(display_text, color)

    def on_drive_mode_changed(self, mode):
        """Update dashboard mode button/card from global drive mode."""
        is_manual = mode == "MANUAL"
        display = "Manual" if is_manual else "Automatic"
        color = "#10b981" if is_manual else "#6b7280"
        self.drive_mode_card.update_value(display, color)

DashboardPage = WMSDashboardPage
