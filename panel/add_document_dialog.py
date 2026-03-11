from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, 
                             QDateEdit, QComboBox, QWidget, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QDate
from panel.stock_selection_dialog import StockSelectionDialog
from functions.database_manager import DatabaseManager

class AddDocumentDialog(QDialog):
    def __init__(self, parent=None, doc_type="PZ"):
        super().__init__(parent)
        self.doc_type = doc_type
        self.db_manager = DatabaseManager()
        title = "Przyjęcie zewnętrzne (PZ)" if doc_type == "PZ" else "Wydanie zewnętrzne (WZ)"
        self.setWindowTitle(title)
        self.resize(900, 600)
        
        self.layout = QVBoxLayout(self)
        
        self.setup_header()
        
        self.setup_items_table()
        
        self.setup_footer()
        
    def setup_header(self):
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        row1 = QHBoxLayout()
        
        self.number_edit = QLineEdit()
        default_prefix = "PZ" if self.doc_type == "PZ" else "WZ"
        self.number_edit.setPlaceholderText(f"{default_prefix} (auto)/02/2013")
        self.number_edit.setText(f"{default_prefix}/AUTO/2026") # Default
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        row1.addWidget(QLabel("Numer:"))
        row1.addWidget(self.number_edit)
        row1.addWidget(QLabel("Data:"))
        row1.addWidget(self.date_edit)
        row1.addStretch()
        
        header_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        self.contractor_edit = QLineEdit()
        self.contractor_edit.setPlaceholderText("Wybierz dostawcę..." if self.doc_type == "PZ" else "Wybierz odbiorcę...")
        
        row2.addWidget(QLabel("Dostawca:" if self.doc_type == "PZ" else "Odbiorca (Klient):"))
        row2.addWidget(self.contractor_edit)
        
        header_layout.addLayout(row2)

        row_receiver = QHBoxLayout()
        self.receiver_edit = QLineEdit()
        self.receiver_edit.setPlaceholderText("Wybierz odbiorcę...")
        
        row_receiver.addWidget(QLabel("Odbiorca (Miejsce docelowe):"))
        row_receiver.addWidget(self.receiver_edit)
        
        header_layout.addLayout(row_receiver)
        
        row3 = QHBoxLayout()
        self.original_number_edit = QLineEdit()
        self.original_number_edit.setPlaceholderText("Numer oryginału (np. WZ/123)")
        
        row3.addWidget(QLabel("Numer oryginału:"))
        row3.addWidget(self.original_number_edit)
        
        header_layout.addLayout(row3)

        self.layout.addWidget(header_widget)

    def setup_items_table(self):
        self.table = QTableWidget()
        
        if self.doc_type == "WZ":
            columns = ["Zaznacz", "Nazwa", "Ilość na stanie", "Jm", "Ilość do wydania"]
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            inventory = self.db_manager.get_inventory()
            self.table.setRowCount(len(inventory))
            
            for i, (name, unit, qty) in enumerate(inventory):
                chk_widget = QWidget()
                chk_layout = QHBoxLayout(chk_widget)
                chk_layout.addWidget(QCheckBox())
                chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                chk_layout.setContentsMargins(0,0,0,0)
                self.table.setCellWidget(i, 0, chk_widget)
                
                self.table.setItem(i, 1, QTableWidgetItem(str(name)))
                self.table.item(i, 1).setFlags(Qt.ItemFlag.ItemIsEnabled) # Read-only name
                
                self.table.setItem(i, 2, QTableWidgetItem(str(qty)))
                self.table.item(i, 2).setFlags(Qt.ItemFlag.ItemIsEnabled) # Read-only qty
                
                self.table.setItem(i, 3, QTableWidgetItem(str(unit)))
                self.table.item(i, 3).setFlags(Qt.ItemFlag.ItemIsEnabled) # Read-only unit
                
                self.table.setItem(i, 4, QTableWidgetItem("0"))
                
        else:
            columns = ["Lp", "Nazwa", "Ilość dostarczenia", "Ilość przyjęcia", "Jm", "Cena netto", "Wartość netto"]
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            self.table.setRowCount(10)
            for i in range(10):
                self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                
                combo = QComboBox()
                combo.addItems(["szt.", "kg", "m", "l", "kpl.", "op."])
                self.table.setCellWidget(i, 4, combo)
            
        self.layout.addWidget(self.table)

    def open_stock_selection(self):
        pass

        
    def setup_footer(self):
        footer_layout = QHBoxLayout()
        
        btn_text = "Usuń z magazynu" if self.doc_type == "WZ" else "Zapisz"
        self.save_btn = QPushButton(btn_text)
        self.save_btn.clicked.connect(self.accept) # Closes dialog with result code Accepted
        
        self.cancel_btn = QPushButton("Anuluj")
        self.cancel_btn.clicked.connect(self.reject)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.save_btn)
        footer_layout.addWidget(self.cancel_btn)
        
        self.layout.addLayout(footer_layout)

    def get_data(self):
        data = {
            "doc_type": self.doc_type,
            "number": self.number_edit.text(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "contractor": self.contractor_edit.text(),
            "receiver": self.receiver_edit.text(),
            "original_number": self.original_number_edit.text(),
            "items": []
        }
        
        total_value = 0.0
        
        if self.doc_type == "WZ":
            for row in range(self.table.rowCount()):
                chk_widget = self.table.cellWidget(row, 0)
                checkbox = chk_widget.layout().itemAt(0).widget()
                
                if checkbox.isChecked():
                    name = self.table.item(row, 1).text()
                    unit = self.table.item(row, 3).text()
                    try:
                        qty_to_issue = float(self.table.item(row, 4).text())
                        if qty_to_issue > 0:
                            data["items"].append({
                                "name": name,
                                "quantity": qty_to_issue,
                                "quantity_delivered": qty_to_issue, # For WZ same
                                "unit": unit,
                                "price_netto": 0.0,
                                "value_netto": 0.0
                            })
                    except ValueError:
                        pass
        else:
            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 1)
                qty_delivered_item = self.table.item(row, 2)
                qty_received_item = self.table.item(row, 3)
                unit_widget = self.table.cellWidget(row, 4)
                price_item = self.table.item(row, 5)
                
                if name_item and name_item.text().strip():
                    try:
                        qty_delivered = float(qty_delivered_item.text()) if qty_delivered_item and qty_delivered_item.text() else 0
                        qty_received = float(qty_received_item.text()) if qty_received_item and qty_received_item.text() else 0
                        
                        price = float(price_item.text()) if price_item and price_item.text() else 0
                        value = qty_received * price
                        
                        unit = unit_widget.currentText() if unit_widget else "szt."

                        data["items"].append({
                            "name": name_item.text(),
                            "quantity": qty_received,
                            "quantity_delivered": qty_delivered,
                            "unit": unit,
                            "price_netto": price,
                            "value_netto": value
                        })
                        total_value += value
                    except ValueError:
                        continue # Skip invalid rows
                    
        data["total_value"] = total_value
        return data
