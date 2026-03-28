from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from functions.database_manager import DatabaseManager
from functions.pdf_generator import generate_pdf_from_database
from panel.add_document_dialog import AddDocumentDialog
from functions.FloatingMessage import FloatingMessage
import os
import subprocess
import platform

class DokumentyPage(QWidget):
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

        # Pasek narzędzi
        toolbar_layout = QHBoxLayout()
        
        # Przyciski akcji
        button_style = """
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """
        
        self.add_pz_btn = QPushButton("✅ Przyjęcie (PZ)")
        self.add_pz_btn.setStyleSheet(button_style)
        self.add_pz_btn.clicked.connect(lambda: self.open_add_dialog("PZ"))
        toolbar_layout.addWidget(self.add_pz_btn)
        
        self.add_wz_btn = QPushButton("📤 Wydanie (WZ)")
        self.add_wz_btn.setStyleSheet(button_style)
        self.add_wz_btn.clicked.connect(lambda: self.open_add_dialog("WZ"))
        toolbar_layout.addWidget(self.add_wz_btn)
        
        self.generate_pdf_btn = QPushButton("📥 Generuj PDF")
        self.generate_pdf_btn.setStyleSheet(button_style)
        self.generate_pdf_btn.clicked.connect(self.generate_pdf_for_selected)
        toolbar_layout.addWidget(self.generate_pdf_btn)
        
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
        
        self.demo_pdf_btn = QPushButton("🎯 Demo PDF")
        self.demo_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        # self.demo_pdf_btn.clicked.connect(self.generate_demo_pdfs)
        # toolbar_layout.addWidget(self.demo_pdf_btn)
        
        # layout.addLayout(toolbar_layout)
        
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

    def generate_pdf_for_selected(self):
        """Generate PDF for selected documents"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Błąd", "Zaznacz dokument aby wygenerować PDF.")
            return
        
        success_count = 0
        error_count = 0
        pdf_paths = []
        
        for index in selected_rows:
            try:
                doc_id_item = self.table.item(index.row(), 0)
                if doc_id_item:
                    doc_id = int(doc_id_item.text())
                    pdf_path = generate_pdf_from_database(self.db_manager, doc_id)
                    if pdf_path:
                        pdf_paths.append(pdf_path)
                        success_count += 1
                    else:
                        error_count += 1
            except Exception as e:
                print(f"Błąd generowania PDF: {e}")
                error_count += 1
        
        if success_count > 0:
            output_dir = os.path.abspath("invoices")
            msg = f"Wygenerowano {success_count} PDF(y).\n\nLokalizacja: {output_dir}"
            QMessageBox.information(self, "Sukces", msg)
            
            # Show floating message
            try:
                FloatingMessage.display(self, f"PDF wygenerowane ({success_count})", duration=3000)
            except Exception:
                pass
        
        if error_count > 0:
            QMessageBox.warning(self, "Błąd", f"Nie udało się wygenerować {error_count} PDF(ów).")

    def open_invoices_folder(self):
        """Otwórz folder z fakturami"""
        invoices_dir = os.path.abspath("invoices")
        
        # Utwórz folder jeśli nie istnieje
        if not os.path.exists(invoices_dir):
            os.makedirs(invoices_dir)
        
        try:
            if platform.system() == 'Windows':
                os.startfile(invoices_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', invoices_dir])
            else:  # Linux
                subprocess.Popen(['xdg-open', invoices_dir])
            
            FloatingMessage.display(self, "Folder otwarty ✓", duration=2000)
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie można otworzyć folderu: {e}")

    # def generate_demo_pdfs(self):
    #     """Generuj demonstracyjne PDF-y testowe"""
    #     try:
    #         from examples.demo_pdf_data import (
    #             get_demo_document_pz,
    #             get_demo_document_wz,
    #             get_demo_document_elektronika
    #         )
    #         from functions.pdf_generator import PDFInvoiceGenerator
            
    #         generator = PDFInvoiceGenerator(
    #             company_name="Magazyn Główny Sp. z o.o.",
    #             output_dir="invoices"
    #         )
            
    #         # Generuj 3 demo PDFs
    #         pdfs_generated = []
            
    #         pdf1 = generator.generate_invoice(
    #             get_demo_document_pz(),
    #             filename="DEMO_PZ_PRZYJECIE.pdf"
    #         )
    #         pdfs_generated.append("DEMO_PZ_PRZYJECIE.pdf")
            
    #         pdf2 = generator.generate_invoice(
    #             get_demo_document_wz(),
    #             filename="DEMO_WZ_WYDANIE.pdf"
    #         )
    #         pdfs_generated.append("DEMO_WZ_WYDANIE.pdf")
            
    #         pdf3 = generator.generate_invoice(
    #             get_demo_document_elektronika(),
    #             filename="DEMO_ELEKTRONIKA.pdf"
    #         )
    #         pdfs_generated.append("DEMO_ELEKTRONIKA.pdf")
            
    #         invoices_dir = os.path.abspath("invoices")
    #         msg = f"✓ Wygenerowano {len(pdfs_generated)} demo PDFs:\n\n"
    #         msg += "\n".join([f"  • {pdf}" for pdf in pdfs_generated])
    #         msg += f"\n\nLokacja: {invoices_dir}\n\nMożesz je teraz otwórz i drukować!"
            
    #         QMessageBox.information(self, "Demo PDFs Gotowe!", msg)
            
    #         # Otwórz folder automatycznie
    #         try:
    #             if platform.system() == 'Windows':
    #                 os.startfile(invoices_dir)
    #             elif platform.system() == 'Darwin':
    #                 subprocess.Popen(['open', invoices_dir])
    #             else:
    #                 subprocess.Popen(['xdg-open', invoices_dir])
    #         except Exception:
    #             pass
            
    #     except ImportError as e:
    #         QMessageBox.warning(self, "Błąd", f"Nie znaleziono modułu: {e}")
    #     except Exception as e:
    #         QMessageBox.warning(self, "Błąd", f"Błąd generowania demo: {e}")

    # def open_add_dialog(self, doc_type):
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
