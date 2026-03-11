from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from functions.database_manager import DatabaseManager
from panel.add_document_dialog import AddDocumentDialog

class DokumentyPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.db_manager = DatabaseManager()
        self.ensure_sample_data()

        layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        
        title = QLabel("Dokumenty Magazynowe")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.add_pz_btn = QPushButton("Przyjęcie (PZ)")
        self.add_pz_btn.clicked.connect(lambda: self.open_add_dialog("PZ"))
        
        self.add_wz_btn = QPushButton("Wydanie (WZ)")
        self.add_wz_btn.clicked.connect(self.delete_selected_documents)
        
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.add_pz_btn)
        top_bar.addWidget(self.add_wz_btn)
        
        layout.addLayout(top_bar)
        
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        self.load_data()

    def delete_selected_documents(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Błąd", "Nie zaznaczono żadnego dokumentu.")
            return

        reply = QMessageBox.question(self, "Potwierdzenie", 
                                     f"Czy na pewno chcesz usunąć {len(selected_rows)} dokument(ów)?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            for index in selected_rows:
                doc_id_item = self.table.item(index.row(), 0)
                if doc_id_item:
                    doc_id = int(doc_id_item.text())
                    self.db_manager.delete_document(doc_id)
            
            self.load_data()

    def open_add_dialog(self, doc_type):
        dialog = AddDocumentDialog(self, doc_type)
        if dialog.exec():
            data = dialog.get_data()
            
            if doc_type == "WZ":
                for item in data["items"]:
                    self.db_manager.remove_item_from_stock(
                        item["name"],
                        item["quantity"],
                        item["unit"]
                    )
            else:
                receipt_id = self.db_manager.add_receipt(
                    data["doc_type"],
                    data["date"], 
                    data["number"], 
                    data["original_number"], 
                    data["contractor"], 
                    data["receiver"], 
                    data["total_value"], 
                    data["total_value"], # Cost = Value for PZ
                    "-" # Related document
                )
                
                for item in data["items"]:
                    self.db_manager.add_receipt_item(
                        receipt_id,
                        item["name"],
                        item["quantity"],
                        item.get("quantity_delivered", 0),
                        item["unit"],
                        item["price_netto"],
                        item["value_netto"]
                    )
            
            self.load_data() # Refresh table

    def setup_table(self):
        columns = ["ID", "Typ", "Data", "Numer", "Nazwa", "Numer oryginału", "Dostawca/Klient", "Wartość", "Koszt", "Dokument powiązany", "Odbiorca (Docelowy)"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Read-only
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True) 
        
        self.table.setColumnWidth(0, 40) # ID
        self.table.setColumnWidth(1, 50) # Typ
        self.table.setColumnWidth(2, 90) # Data
        self.table.setColumnWidth(3, 120) # Numer
        self.table.setColumnWidth(4, 300) # Nazwa (Items)
        self.table.setColumnWidth(6, 150) # Dostawca
        self.table.setColumnWidth(10, 150) # Odbiorca

    def load_data(self):
        data = self.db_manager.get_all_receipts()
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, item in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item) if item is not None else ""))

    def ensure_sample_data(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM warehouse_receipt_items")
        count = cursor.fetchone()[0]
        conn.close()

        if count == 0:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM warehouse_data")
            cursor.execute("DELETE FROM warehouse_receipt_items")
            conn.commit()
            conn.close()

            pid1 = self.db_manager.add_receipt("PZ", "2023-10-26", "PZ/001/2023", "WZ/123", "Firma XYZ", "Magazyn Główny", 1500.00, 1200.00, "-")
            self.db_manager.add_receipt_item(pid1, "Drzwi szklane", 5, 5, "szt.", 300.0, 1500.0)
            
            pid2 = self.db_manager.add_receipt("PZ", "2023-10-27", "PZ/002/2023", "WZ/124", "Dostawca ABC", "Magazyn Główny", 2300.50, 1800.00, "ZK/55")
            self.db_manager.add_receipt_item(pid2, "Panel podłogowy", 100, 100, "m2", 23.0, 2300.0)
            
            self.db_manager.add_receipt("WZ", "2023-10-28", "WZ/001/2023", "-", "Klient 123", "Magazyn Główny", 500.00, 400.00, "PZ/001/2023")
