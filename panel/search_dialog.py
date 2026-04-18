from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
                             QListWidget, QListWidgetItem, QLabel, QComboBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from functions.SearchManager import SearchIndex, SearchHistory

class SearchDialog(QDialog):
    
    action_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.search_index = SearchIndex()
        self.search_history = SearchHistory()
        
        self.setWindowTitle("🔍 Wyszukiwanie - WMS")
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit {
                border: 2px solid #0066cc;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title = QLabel("🔍 Wyszukaj w Instrukcjach, Funkcjach i Skrótach")
        title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Wpisz szukaną frazę (np. 'robot', 'raport', 'backup')")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.on_search)
        self.search_input.returnPressed.connect(self.select_first_result)
        search_layout.addWidget(self.search_input)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(['Wszystko', 'Funkcje', 'Skróty', 'Instrukcje'])
        self.type_filter.currentTextChanged.connect(self.on_filter_changed)
        self.type_filter.setMaximumWidth(150)
        search_layout.addWidget(self.type_filter)
        
        main_layout.addLayout(search_layout)
        
        results_label = QLabel("Wyniki wyszukiwania:")
        results_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        main_layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_result_selected)
        main_layout.addWidget(self.results_list)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #666; font-size: 10px;")
        main_layout.addWidget(self.info_label)
        
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("🎯 Otwórz wybrany")
        select_btn.setMinimumHeight(35)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """)
        select_btn.clicked.connect(self.on_result_selected)
        button_layout.addWidget(select_btn)
        
        close_btn = QPushButton("✕ Zamknij")
        close_btn.setMinimumHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.search_input.setFocus()
    
    def on_search(self, query):
        """Handle search"""
        if not query:
            self.results_list.clear()
            self.info_label.setText("")
            return
        
        filter_map = {
            'Wszystko': 'all',
            'Funkcje': 'functions',
            'Skróty': 'shortcuts',
            'Instrukcje': 'instructions'
        }
        search_type = filter_map.get(self.type_filter.currentText(), 'all')
        
        results = self.search_index.search(query, search_type)
        
        self.search_history.add(query)
        
        self.results_list.clear()
        
        if not results:
            self.info_label.setText(f"❌ Brak wyników dla '{query}'")
            return
        
        for result in results:
            item_text = self._format_result(result)
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)
        
        self.info_label.setText(f"✅ Znaleziono {len(results)} wynik(ów)")
    
    def _format_result(self, result):
        """Format result for display"""
        if result['type'] == 'function':
            icon = result.get('icon', '📌')
            title = result['title']
            shortcuts = f"({', '.join(result.get('shortcuts', []))})" if result.get('shortcuts') else ""
            return f"{icon} {title} {shortcuts}"
        
        elif result['type'] == 'shortcut':
            key = result['key']
            action = result['action']
            category = result['category']
            return f"⌨️  {key} → {action} ({category})"
        
        elif result['type'] == 'instruction':
            title = result['title']
            return f"📖 {title}"
        
        return "?"
    
    def on_result_selected(self):
        """Handle result selection"""
        if not self.results_list.currentItem():
            return
        
        result = self.results_list.currentItem().data(Qt.ItemDataRole.UserRole)
        
        if result['type'] == 'function':
            action = result['action']
            self.action_selected.emit(action)
            self.close()
        
        elif result['type'] == 'shortcut':
            pass
        
        elif result['type'] == 'instruction':
            pass
    
    def select_first_result(self):
        """Select first result with Enter key"""
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
            self.on_result_selected()
    
    def on_filter_changed(self):
        """Handle filter change"""
        self.on_search(self.search_input.text())
    
    def keyPressEvent(self, event):
        """Handle key events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


class SearchWidget(QFrame):
    """Lightweight search widget for embedding in pages"""
    
    action_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_index = SearchIndex()
        self.parent_window = parent
        
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        title = QLabel("🔍 Szybkie Wyszukiwanie")
        title.setFont(QFont('Arial', 11, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Wyszukaj funkcję, skrót lub instrukcję...")
        self.search_input.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_input)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_result_clicked)
        self.results_list.setMaximumHeight(200)
        layout.addWidget(self.results_list)
        
        layout.addStretch()
    
    def on_search_changed(self, query):
        """Handle search input change"""
        self.results_list.clear()
        
        if not query or len(query) < 2:
            return
        
        results = self.search_index.search(query, 'all')
        
        for result in results[:5]:  # Show top 5
            if result['type'] == 'function':
                icon = result.get('icon', '📌')
                text = f"{icon} {result['title']}"
            elif result['type'] == 'shortcut':
                text = f"⌨️  {result['key']} → {result['action']}"
            else:
                text = f"📖 {result['title']}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)
    
    def on_result_clicked(self, item):
        """Handle result click"""
        result = item.data(Qt.ItemDataRole.UserRole)
        
        if result['type'] == 'function':
            self.action_selected.emit(result['action'])
