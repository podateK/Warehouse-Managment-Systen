from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QTextEdit, QMessageBox,
                             QGridLayout, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from functions.LabelGenerator import ShipmentLabelGenerator
import os
import webbrowser

class ShipmentLabelsPage(QWidget):
    
    def __init__(self):
        super().__init__()
        self.label_generator = ShipmentLabelGenerator()
        self.last_label_path = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Generuj Etykiety Wysyłki")
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #0066cc;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("Twórz gotowe do druku etykiety z kodem kreskowym dla wysyłek")
        subtitle.setFont(QFont('Arial', 10))
        subtitle.setStyleSheet("color: #666;")
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(15)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(15)
        
        form_layout.addWidget(QLabel("Odbiorca/Recipient:"), 0, 0)
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("np. Jan Kowalski")
        self.recipient_input.setMinimumHeight(35)
        form_layout.addWidget(self.recipient_input, 0, 1)
        
        form_layout.addWidget(QLabel("Typ Etykiety/Label Type:"), 1, 0)
        self.label_type_combo = QComboBox()
        self.label_type_combo.addItems(['PACZKA', 'PALETA', 'POBRANIE', 'ZWROT'])
        self.label_type_combo.setMinimumHeight(35)
        self.label_type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        form_layout.addWidget(self.label_type_combo, 1, 1)
        
        form_layout.addWidget(QLabel("Adres/Address:"), 2, 0)
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("np. ul. Główna 123")
        self.address_input.setMinimumHeight(35)
        form_layout.addWidget(self.address_input, 2, 1)
        
        form_layout.addWidget(QLabel("Kod Pocztowy/Postal Code:"), 3, 0)
        self.postal_input = QLineEdit()
        self.postal_input.setPlaceholderText("np. 00-000")
        self.postal_input.setMinimumHeight(35)
        form_layout.addWidget(self.postal_input, 3, 1)
        
        form_layout.addWidget(QLabel("Miasto/City:"), 4, 0)
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("np. Warszawa")
        self.city_input.setMinimumHeight(35)
        form_layout.addWidget(self.city_input, 4, 1)
        
        form_layout.addWidget(QLabel("Uwagi Nadawcy/Sender Notes:"), 5, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Dodatkowe instrukcje dla kuriera (opcjonalnie)")
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setMaximumHeight(100)
        form_layout.addWidget(self.notes_input, 5, 1)
        
        main_layout.addWidget(form_frame)
        main_layout.addSpacing(15)
        
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Generuj Etykietę")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setFont(QFont('Arial', 11, QFont.Weight.Bold))
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_label)
        button_layout.addWidget(self.generate_btn)
        
        self.open_folder_btn = QPushButton("Otwórz Folder")
        self.open_folder_btn.setMinimumHeight(40)
        self.open_folder_btn.setFont(QFont('Arial', 11))
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.open_folder_btn.clicked.connect(self.open_labels_folder)
        button_layout.addWidget(self.open_folder_btn)
        
        self.print_btn = QPushButton("Drukuj")
        self.print_btn.setMinimumHeight(40)
        self.print_btn.setFont(QFont('Arial', 11))
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        self.print_btn.clicked.connect(self.print_label)
        self.print_btn.setEnabled(False)
        button_layout.addWidget(self.print_btn)
        
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(20)
        
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border-left: 4px solid #0066cc;
                padding: 15px;
                border-radius: 4px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("Dostępne Typy Etykiet:")
        info_title.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        info_layout.addWidget(info_title)
        
        label_types = [
            "🟥 PACZKA - Przesyłka zwykła (czerwona)",
            "🟧 PALETA - Paleta/transport poddostowy (pomarańczowa)",
            "🟣 POBRANIE - Przesyłka podziałem (fioletowa)",
            "🟦 ZWROT - Zwrot towaru (niebieska)"
        ]
        
        for label_type in label_types:
            type_label = QLabel(label_type)
            type_label.setFont(QFont('Arial', 9))
            info_layout.addWidget(type_label)
        
        main_layout.addWidget(info_frame)
        main_layout.addStretch()
    
    def generate_label(self):
        """Generate shipment label"""
        recipient = self.recipient_input.text().strip()
        address = self.address_input.text().strip()
        postal = self.postal_input.text().strip()
        city = self.city_input.text().strip()
        notes = self.notes_input.toPlainText().strip()
        label_type = self.label_type_combo.currentText()
        
        if not recipient or not address or not postal or not city:
            QMessageBox.warning(self, "Validation", "Uzupełnij wymagane pola: Odbiorca, Adres, Kod Pocztowy, Miasto")
            return
        
        try:
            filepath, label_data = self.label_generator.create_shipment_label(
                recipient=recipient,
                address=address,
                postal_code=postal,
                city=city,
                sender_notes=notes,
                label_type=label_type
            )
            
            self.last_label_path = filepath
            self.print_btn.setEnabled(True)
            
            message = f"""✅ Etykieta wygenerowana!
            
Plik: {os.path.basename(filepath)}
Typ: {label_type}
WZ Nr: {label_data['wz_number']}
Kod: {label_data['barcode']}

Etykieta jest gotowa do druku."""
            
            QMessageBox.information(self, "Sukces", message)
            
            self.recipient_input.clear()
            self.address_input.clear()
            self.postal_input.clear()
            self.city_input.clear()
            self.notes_input.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd przy generowaniu etykiety:\n{str(e)}")
    
    def open_labels_folder(self):
        """Open labels folder in file explorer"""
        labels_dir = os.path.abspath("labels")
        if os.path.exists(labels_dir):
            os.startfile(labels_dir)
        else:
            QMessageBox.warning(self, "Folder", "Folder 'labels' nie istnieje. Najpierw wygeneruj etykietę!")
    
    def print_label(self):
        """Print the last generated label"""
        if not self.last_label_path or not os.path.exists(self.last_label_path):
            QMessageBox.warning(self, "Błąd", "Brak etykiety do wydruku. Najpierw wygeneruj etykietę!")
            return
        
        try:
            os.startfile(self.last_label_path, "print")
            QMessageBox.information(self, "Druk", "Etykieta wysłana do drukarki!")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd przy wysyłaniu do drukarki:\n{str(e)}")
