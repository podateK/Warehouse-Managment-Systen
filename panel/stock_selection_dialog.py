from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QHBoxLayout, QLabel, QAbstractItemView)
from PyQt6.QtCore import Qt
from functions.database_manager import DatabaseManager

class StockSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wybierz towar z magazynu")
        self.resize(600, 400)
        self.db_manager = DatabaseManager()
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Dostępne towary:"))
        
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        self.load_data()
        
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Wybierz")
        self.select_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Anuluj")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def setup_table(self):
        columns = ["Nazwa", "Ilość dostępna", "Jm"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
    def load_data(self):
        inventory = self.db_manager.get_inventory()
        self.table.setRowCount(len(inventory))
        for row_idx, (name, unit, qty) in enumerate(inventory):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(name)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(qty)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(unit)))
            
    def get_selected_item(self):
        row = self.table.currentRow()
        if row >= 0:
            return {
                "name": self.table.item(row, 0).text(),
                "quantity": float(self.table.item(row, 1).text()),
                "unit": self.table.item(row, 2).text()
            }
        return None
