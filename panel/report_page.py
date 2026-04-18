from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QMessageBox, QFrame, QGridLayout, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from functions.ReportGenerator import ReportGenerator
import os
import webbrowser

class ReportPage(QWidget):
    
    def __init__(self):
        super().__init__()
        self.report_generator = ReportGenerator()
        self.last_report_path = None
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Generuj Raporty")
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #0066cc;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("Twórz raporty dzienne, tygodniowe, miesięczne oraz analizy magazynu")
        subtitle.setFont(QFont('Arial', 10))
        subtitle.setStyleSheet("color: #666;")
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(20)
        
        reports_frame = QFrame()
        reports_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        reports_layout = QGridLayout(reports_frame)
        reports_layout.setSpacing(15)
        reports_layout.setColumnStretch(0, 1)
        reports_layout.setColumnStretch(1, 1)
        
        self.reports = [
            {
                'name': 'Raport Dzienny (PDF)',
                'icon': '📅',
                'description': 'Podsumowanie dzisiejszych operacji',
                'function': self.report_generator.generate_daily_report_pdf
            },
            {
                'name': 'Stan Magazynu (PDF)',
                'icon': '📦',
                'description': 'Aktualny status towarów w magazynie',
                'function': self.report_generator.generate_inventory_report_pdf
            },
            {
                'name': 'Operacje (CSV)',
                'icon': '📊',
                'description': 'Export operacji do pliku CSV',
                'function': self.report_generator.generate_operations_report_csv
            },
            {
                'name': 'Magazyn (Excel)',
                'icon': '📈',
                'description': 'Raport stanu magazynu w Excel',
                'function': self.report_generator.generate_inventory_report_excel
            },
        ]
        
        row = 0
        col = 0
        
        for report_info in self.reports:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                }
                QFrame:hover {
                    border: 2px solid #0066cc;
                }
            """)
            card_layout = QVBoxLayout(card)
            
            icon_label = QLabel(report_info['icon'])
            icon_label.setFont(QFont('Arial', 24))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon_label)
            
            name_label = QLabel(report_info['name'])
            name_label.setFont(QFont('Arial', 11, QFont.Weight.Bold))
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(name_label)
            
            desc_label = QLabel(report_info['description'])
            desc_label.setFont(QFont('Arial', 9))
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setStyleSheet("color: #666;")
            desc_label.setWordWrap(True)
            card_layout.addWidget(desc_label)
            
            card_layout.addSpacing(10)
            
            btn = QPushButton("Generuj")
            btn.setMinimumHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0066cc;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #0052a3;
                }
            """)
            
            btn.clicked.connect(lambda checked, f=report_info['function']: self.generate_report(f))
            card_layout.addWidget(btn)
            
            reports_layout.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        main_layout.addWidget(reports_frame)
        main_layout.addSpacing(20)
        
        action_layout = QHBoxLayout()
        
        open_btn = QPushButton("📁 Otwórz Folder Raportów")
        open_btn.setMinimumHeight(40)
        open_btn.setFont(QFont('Arial', 11))
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        open_btn.clicked.connect(self.open_reports_folder)
        action_layout.addWidget(open_btn)
        
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        main_layout.addStretch()
    
    def generate_report(self, report_func):
        """Generate report"""
        try:
            filepath, report_data = report_func()
            self.last_report_path = filepath
            
            format_str = report_data.get('format', 'PDF')
            report_type = report_data.get('type', 'Unknown')
            
            message = f"""✅ Raport wygenerowany!
            
Typ: {report_type.capitalize()}
Format: {format_str}
Plik: {os.path.basename(filepath)}

Raport jest gotowy do pobrania."""
            
            self.show_success(message)
            
        except Exception as e:
            self.show_error(f"Błąd przy generowaniu raportu:\n{str(e)}")
    
    def open_reports_folder(self):
        """Open reports folder"""
        reports_dir = os.path.abspath("reports")
        if os.path.exists(reports_dir):
            os.startfile(reports_dir)
        else:
            QMessageBox.warning(self, "Folder", "Folder 'reports' nie istnieje.")
    
    def show_success(self, message):
        """Show success message"""
        QMessageBox.information(self, "Sukces", message)
    
    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Błąd", message)
