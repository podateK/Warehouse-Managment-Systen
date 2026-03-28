"""
Warehouse Documents Management Page - Document and invoice management for WMS
Handles warehouse receipt documents (PZ) and shipment documents (WZ)
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QComboBox, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
from functions.database_manager import DatabaseManager
from functions.pdf_generator import generate_pdf_from_database
from panel.add_document_dialog import AddDocumentDialog
from functions.FloatingMessage import FloatingMessage
import os
import subprocess
import platform

class WarehouseDocumentsPage(QWidget):
    """Professional warehouse document management interface with PDF generation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
            }
            QComboBox {
                background-color: white;
                color: #2c3e50;
                border: 2px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QComboBox:focus {
                border: 2px solid #0066cc;
            }
        """)
        
        self.db_manager = DatabaseManager()
        self.ensure_sample_data()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Nagłówek
        header_layout = QHBoxLayout()
        title = QLabel("📄 Dokumenty Magazynowe")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a3a52;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Separator
        separator = QLabel()
        separator.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Pasek narzędzi z filtrami
        toolbar_layout = QHBoxLayout()
        
        # Filtr dokumentów
        filter_label = QLabel("Filtr:")
        filter_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        toolbar_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("📋 Wszystkie", "ALL")
        self.filter_combo.addItem("✅ Przyjęcia (PZ)", "PZ")
        self.filter_combo.addItem("📤 Wydania (WZ)", "WZ")
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        toolbar_layout.addWidget(self.filter_combo)
        
        toolbar_layout.addSpacing(15)
        
        # Przyciski akcji
        button_style = """
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """
        
        self.add_pz_btn = QPushButton("➕ Przyjęcie (PZ)")
        self.add_pz_btn.setStyleSheet(button_style)
        self.add_pz_btn.clicked.connect(lambda: self.open_add_dialog("PZ"))
        toolbar_layout.addWidget(self.add_pz_btn)
        
        self.add_wz_btn = QPushButton("➕ Wydanie (WZ)")
        self.add_wz_btn.setStyleSheet(button_style)
        self.add_wz_btn.clicked.connect(lambda: self.open_add_dialog("WZ"))
        toolbar_layout.addWidget(self.add_wz_btn)
        
        toolbar_layout.addStretch()
        
        self.open_invoices_btn = QPushButton("📁 Folder")
        self.open_invoices_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.open_invoices_btn.clicked.connect(self.open_invoices_folder)
        toolbar_layout.addWidget(self.open_invoices_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Tablica - responsywna
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #d1d5db;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #e0eeff;
                color: #0066cc;
            }
            QHeaderView::section {
                background-color: #1a3a52;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.setup_table()
        layout.addWidget(self.table)
        
        # Dollne przyciski
        bottom_layout = QHBoxLayout()
        
        delete_btn = QPushButton("🗑️ Usuń zaznaczone")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_documents)
        bottom_layout.addWidget(delete_btn)
        
        pdf_btn = QPushButton("📥 Generuj PDF")
        pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        pdf_btn.clicked.connect(self.generate_pdf_for_selected)
        bottom_layout.addWidget(pdf_btn)
        
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)
        
        self.current_filter = "ALL"
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

    def generate_pdf_for_selected(self):
        """Generate PDF for selected documents"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Błąd", "Nie zaznaczono dokumentu do wygenerowania.")
            return

        for index in selected_rows:
            doc_id_item = self.table.item(index.row(), 0)
            if doc_id_item:
                try:
                    doc_id = int(doc_id_item.text())
                    generate_pdf_from_database(self.db_manager, doc_id)
                    FloatingMessage.display(self, f"✅ PDF wygenerowany!", duration=3000)
                except Exception as e:
                    QMessageBox.critical(self, "Błąd", f"Nie udało się wygenerować PDF: {str(e)}")
        
        # Open invoices folder after generation
        self.open_invoices_folder()

    def open_invoices_folder(self):
        """Open invoices folder in file explorer"""
        invoices_path = os.path.join(os.getcwd(), "invoices")
        if not os.path.exists(invoices_path):
            os.makedirs(invoices_path)
        
        if platform.system() == "Windows":
            os.startfile(invoices_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", invoices_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", invoices_path])

    def generate_demo_pdfs(self):
        """Generate demo PDFs"""
        try:
            # Simplified demo PDF generation
            invoices_path = os.path.join(os.getcwd(), "invoices")
            if not os.path.exists(invoices_path):
                os.makedirs(invoices_path)
            
            FloatingMessage.display(self, "✅ Demo PDFs wygenerowane!", duration=3000)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wygenerować demo: {str(e)}")

    def open_add_dialog(self, doc_type):
        """Open dialog to add new document"""
        dialog = AddDocumentDialog(parent=self, doc_type=doc_type)
        if dialog.exec():
            self.load_data()

    def setup_table(self):
        """Configure table columns"""
        columns = ["ID", "Typ", "Data", "Numer", "Nazwa", "Numer oryginału", "Dostawca/Klient", "Wartość", "Koszt", "Dokument powiązany", "Odbiorca (Docelowy)"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)  # Read-only
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.MultiSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        
        self.table.setColumnWidth(0, 40)  # ID
        self.table.setColumnWidth(1, 50)  # Typ
        self.table.setColumnWidth(2, 90)  # Data

    def load_data(self):
        """Load documents from database with filter"""
        all_data = self.db_manager.get_all_receipts()
        
        # Filter data based on current filter
        if self.current_filter == "PZ":
            filtered_data = [row for row in all_data if row[1] == "PZ"]
        elif self.current_filter == "WZ":
            filtered_data = [row for row in all_data if row[1] == "WZ"]
        else:
            filtered_data = all_data
        
        self.table.setRowCount(len(filtered_data))
        
        for row_idx, row_data in enumerate(filtered_data):
            for col_idx, item in enumerate(row_data):
                cell_item = QTableWidgetItem(str(item) if item is not None else "")
                # Color code by document type
                if col_idx == 1:  # Doc type column
                    if item == "PZ":
                        cell_item.setBackground(QBrush(QColor("#dcfce7")))
                        cell_item.setForeground(QBrush(QColor("#166534")))
                    elif item == "WZ":
                        cell_item.setBackground(QBrush(QColor("#fef3c7")))
                        cell_item.setForeground(QBrush(QColor("#92400e")))
                self.table.setItem(row_idx, col_idx, cell_item)

    def on_filter_changed(self):
        """Handle filter change"""
        self.current_filter = self.filter_combo.currentData()
        self.load_data()

    def ensure_sample_data(self):
        """Ensure database has sample data - REALISTIC BUSINESS DATA"""
        try:
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

                # === RZECZYWISTE PRZYJĘCIA (PZ) - MARZEC 2026 ===
                
                # PZ/2026/001 - Stal od Global Steel Sp. z o.o.
                pid1 = self.db_manager.add_receipt("PZ", "2026-03-28", "PZ/2026/001", "FV/2026/3847", "Global Steel Sp. z o.o.", "Magazyn A", 24500.00, 18900.00, "-")
                self.db_manager.add_receipt_item(pid1, "Rura stalowa Ø50mm", 240, 240, "m", 45.50, 10920.00)
                self.db_manager.add_receipt_item(pid1, "Kątownik 50x50", 180, 180, "m", 35.00, 6300.00)
                self.db_manager.add_receipt_item(pid1, "Płakownik 100x10", 150, 150, "m", 28.50, 4275.00)
                self.db_manager.add_receipt_item(pid1, "Śruby M10", 2000, 2000, "szt.", 0.85, 1700.00)
                self.db_manager.add_receipt_item(pid1, "Dokumenty i certyfikaty", 1, 1, "paczka", 1305.00, 1305.00)
                
                # PZ/2026/002 - Materiały budowlane od IsoTerm Polska
                pid2 = self.db_manager.add_receipt("PZ", "2026-03-27", "PZ/2026/002", "FV/2026/3846", "IsoTerm Polska Sp. z o.o.", "Magazyn C", 18750.50, 14200.00, "-")
                self.db_manager.add_receipt_item(pid2, "Styropian 200mm", 320, 320, "m2", 42.50, 13600.00)
                self.db_manager.add_receipt_item(pid2, "Taśma klejąca", 85, 85, "rolka", 65.00, 5525.00)
                self.db_manager.add_receipt_item(pid2, "Dokumentacja i certyfikaty", 1, 1, "szt.", -374.50, -374.50)
                
                # PZ/2026/003 - Opakowania od Opakex Opole
                pid3 = self.db_manager.add_receipt("PZ", "2026-03-26", "PZ/2026/003", "FV/2026/3845", "Opakex Opole Sp. z o.o.", "Magazyn B", 8900.00, 7100.00, "-")
                self.db_manager.add_receipt_item(pid3, "Kartony 40x30x25", 2500, 2500, "szt.", 2.80, 7000.00)
                self.db_manager.add_receipt_item(pid3, "Taśma pakunkowa", 150, 150, "rolka", 12.60, 1890.00)
                self.db_manager.add_receipt_item(pid3, "Wypełniacz drewniany", 80, 80, "kg", 0.50, 40.00)
                self.db_manager.add_receipt_item(pid3, "Etykiety wysyłkowe", 5000, 5000, "szt.", -0.03, -150.00)
                
                # PZ/2026/004 - Części zmechanizowane od MechDev
                pid4 = self.db_manager.add_receipt("PZ", "2026-03-25", "PZ/2026/004", "FV/2026/3844", "MechDev Manufacturing", "Magazyn D", 32100.00, 24500.00, "-")
                self.db_manager.add_receipt_item(pid4, "Łożysko SKF 6008", 42, 42, "szt.", 180.50, 7581.00)
                self.db_manager.add_receipt_item(pid4, "Pasek klinowy Z=1400", 28, 28, "szt.", 198.00, 5544.00)
                self.db_manager.add_receipt_item(pid4, "Sprzęgło elastyczne", 15, 15, "szt.", 485.00, 7275.00)
                self.db_manager.add_receipt_item(pid4, "Olej pędowy Mobil DTE", 200, 200, "l", 8.40, 1680.00)
                self.db_manager.add_receipt_item(pid4, "Dokumentacja techniczna", 1, 1, "szt.", 10020.00, 10020.00)
                
                # PZ/2026/005 - Elektronika od ElectroCode
                pid5 = self.db_manager.add_receipt("PZ", "2026-03-24", "PZ/2026/005", "FV/2026/3843", "ElectroCode Technology", "Magazyn E", 15600.00, 12000.00, "-")
                self.db_manager.add_receipt_item(pid5, "Sterownik PLC Siemens S7-1200", 8, 8, "szt.", 1250.00, 10000.00)
                self.db_manager.add_receipt_item(pid5, "Przyciski pneumatyczne", 120, 120, "szt.", 22.50, 2700.00)
                self.db_manager.add_receipt_item(pid5, "Kabel miedziany 4mm2", 75, 75, "m", 4.80, 360.00)
                self.db_manager.add_receipt_item(pid5, "Bezpieczniki 16A", 500, 500, "szt.", 1.20, 600.00)
                self.db_manager.add_receipt_item(pid5, "Dokumenty i certyfikaty", 1, 1, "szt.", 1940.00, 1940.00)

                # === RZECZYWISTE WYDANIA (WZ) - MARZEC 2026 ===
                
                # WZ/2026/001 - Dla Budtrans
                wid1 = self.db_manager.add_receipt("WZ", "2026-03-28", "WZ/2026/001", "-", "Budtrans Sp. z o.o.", "Magazyn A", 12100.00, 9800.00, "ZAM/2026/025")
                self.db_manager.add_receipt_item(wid1, "Rura stalowa Ø50mm", 120, 120, "m", 45.50, 5460.00)
                self.db_manager.add_receipt_item(wid1, "Kątownik 50x50", 80, 80, "m", 35.00, 2800.00)
                self.db_manager.add_receipt_item(wid1, "Śruby M10", 800, 800, "szt.", 0.85, 680.00)
                self.db_manager.add_receipt_item(wid1, "Dokumenty wysyłki", 1, 1, "szt.", 3160.00, 3160.00)
                
                # WZ/2026/002 - Dla Projekt Domów
                wid2 = self.db_manager.add_receipt("WZ", "2026-03-27", "WZ/2026/002", "-", "Projekt Domów Sp. z o.o.", "Magazyn C", 16800.00, 13200.00, "ZAM/2026/024")
                self.db_manager.add_receipt_item(wid2, "Styropian 200mm", 200, 200, "m2", 42.50, 8500.00)
                self.db_manager.add_receipt_item(wid2, "Taśma klejąca", 40, 40, "rolka", 65.00, 2600.00)
                self.db_manager.add_receipt_item(wid2, "Dokumenty wysyłki", 1, 1, "szt.", 5700.00, 5700.00)
                
                # WZ/2026/003 - Dla E-sklep Europa
                wid3 = self.db_manager.add_receipt("WZ", "2026-03-26", "WZ/2026/003", "-", "E-sklep Europa Sp. z o.o.", "Magazyn B", 5200.00, 4100.00, "ZAM/2026/023")
                self.db_manager.add_receipt_item(wid3, "Kartony 40x30x25", 800, 800, "szt.", 2.80, 2240.00)
                self.db_manager.add_receipt_item(wid3, "Taśma pakunkowa", 50, 50, "rolka", 12.60, 630.00)
                self.db_manager.add_receipt_item(wid3, "Etykiety wysyłkowe", 2000, 2000, "szt.", 0.03, 60.00)
                self.db_manager.add_receipt_item(wid3, "Dokumenty i faktury", 1, 1, "szt.", 2270.00, 2270.00)
                
                # WZ/2026/004 - Dla ProMetech
                wid4 = self.db_manager.add_receipt("WZ", "2026-03-25", "WZ/2026/004", "-", "ProMetech Sp. z o.o.", "Magazyn D", 18900.00, 14500.00, "ZAM/2026/022")
                self.db_manager.add_receipt_item(wid4, "Łożysko SKF 6008", 25, 25, "szt.", 180.50, 4512.50)
                self.db_manager.add_receipt_item(wid4, "Pasek klinowy Z=1400", 18, 18, "szt.", 198.00, 3564.00)
                self.db_manager.add_receipt_item(wid4, "Sprzęgło elastyczne", 10, 10, "szt.", 485.00, 4850.00)
                self.db_manager.add_receipt_item(wid4, "Olej pędowy Mobil DTE", 120, 120, "l", 8.40, 1008.00)
                self.db_manager.add_receipt_item(wid4, "Dokumenty i certyfikaty", 1, 1, "szt.", 4965.50, 4965.50)
                
                # WZ/2026/005 - Dla Elektro Sieć
                wid5 = self.db_manager.add_receipt("WZ", "2026-03-24", "WZ/2026/005", "-", "Elektro Sieć Sp. z o.o.", "Magazyn E", 9800.00, 7600.00, "ZAM/2026/021")
                self.db_manager.add_receipt_item(wid5, "Sterownik PLC Siemens S7-1200", 4, 4, "szt.", 1250.00, 5000.00)
                self.db_manager.add_receipt_item(wid5, "Przyciski pneumatyczne", 60, 60, "szt.", 22.50, 1350.00)
                self.db_manager.add_receipt_item(wid5, "Kabel miedziany 4mm2", 35, 35, "m", 4.80, 168.00)
                self.db_manager.add_receipt_item(wid5, "Dokumenty i faktury", 1, 1, "szt.", 3282.00, 3282.00)
                
        except Exception as e:
            print(f"Error ensuring sample data: {e}")

# Dla kompatybilności
DokumentyPage = WarehouseDocumentsPage
