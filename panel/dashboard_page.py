from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize

class StatCard(QWidget):
    """Karta ze statystyką dla dashboards"""
    def __init__(self, title, value, unit="", color="#0066cc"):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Styl karty
        self.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        
        # Tytuł
        title_label = QLabel(title)
        title_font = QFont('Segoe UI', 10)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #6b7280; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Wartość
        value_layout = QHBoxLayout()
        value_label = QLabel(str(value))
        value_font = QFont('Segoe UI', 28, QFont.Weight.Bold)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        value_layout.addWidget(value_label)
        
        # Jednostka
        if unit:
            unit_label = QLabel(unit)
            unit_font = QFont('Segoe UI', 10)
            unit_label.setFont(unit_font)
            unit_label.setStyleSheet("color: #9ca3af;")
            unit_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)


class DashboardPage(QWidget):
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
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Nagłówek
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard WMS")
        title_font = QFont('Segoe UI', 20, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1a3a52;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Linia separacyjna
        separator = QLabel()
        separator.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # Rząd kart z danymi
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        # Karty ze statystykami
        self.active_orders = StatCard("Aktywne Zamówienia", 12, "", "#0066cc")
        self.stock_items = StatCard("Artykuły w Magazynie", 1247, "szt.", "#10b981")
        self.pending_shipments = StatCard("Oczekujące Wysyłki", 5, "", "#f59e0b")
        self.system_status = StatCard("Status Systemu", "OK", "", "#06b6d4")
        
        stats_layout.addWidget(self.active_orders, 0, 0)
        stats_layout.addWidget(self.stock_items, 0, 1)
        stats_layout.addWidget(self.pending_shipments, 0, 2)
        stats_layout.addWidget(self.system_status, 0, 3)
        
        main_layout.addLayout(stats_layout)
        
        # Sekcja akcji
        action_label = QLabel("Szybkie Akcje")
        action_font = QFont('Segoe UI', 12, QFont.Weight.Bold)
        action_label.setFont(action_font)
        action_label.setStyleSheet("color: #1a3a52; margin-top: 20px;")
        main_layout.addWidget(action_label)
        
        # Linia separacyjna
        separator2 = QLabel()
        separator2.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        separator2.setFixedHeight(1)
        main_layout.addWidget(separator2)
        
        actions_layout = QHBoxLayout()
        
        # Przyciski akcji
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
        
        btn_new_order = QPushButton("Nowe Zamówienie")
        btn_new_order.setStyleSheet(btn_style)
        actions_layout.addWidget(btn_new_order)
        
        btn_check_stock = QPushButton("Sprawdź Magazyn")
        btn_check_stock.setStyleSheet(btn_style)
        actions_layout.addWidget(btn_check_stock)
        
        btn_print_label = QPushButton("Drukuj Etykietę")
        btn_print_label.setStyleSheet(btn_style)
        actions_layout.addWidget(btn_print_label)
        
        btn_robot_status = QPushButton("Status Robota")
        btn_robot_status.setStyleSheet(btn_style)
        actions_layout.addWidget(btn_robot_status)
        
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)
        
        # Informacje systemowe
        main_layout.addSpacing(30)
        
        info_label = QLabel("Ostatnie Operacje")
        info_font = QFont('Segoe UI', 12, QFont.Weight.Bold)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #1a3a52;")
        main_layout.addWidget(info_label)
        
        # Tabela operacji
        operations_box = QWidget()
        operations_box.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        operations_layout = QVBoxLayout(operations_box)
        operations_layout.setContentsMargins(15, 15, 15, 15)
        operations_layout.setSpacing(10)
        
        operations = [
            "14:32 - Zamówienie #1024 - Gotowe do wysyłki",
            "14:21 - Robot przesunął 156 szt. do strefy A",
            "14:15 - Artykuł #SKU-2847 - Niewystarczająca ilość",
            "14:08 - Nowe zamówienie #1025 otrzymane",
            "13:52 - System backup ukończony"
        ]
        
        for op in operations:
            op_label = QLabel(f"• {op}")
            op_label.setStyleSheet("color: #374151; padding: 5px 0px;")
            op_label.setFont(QFont('Segoe UI', 10))
            operations_layout.addWidget(op_label)
        
        main_layout.addWidget(operations_box)
        
        main_layout.addStretch()
