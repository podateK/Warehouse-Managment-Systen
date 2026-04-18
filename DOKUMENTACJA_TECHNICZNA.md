# 👨‍💻 Dokumentacja Techniczna - WMS System

Przewodnik dla programistów i administratorów system WMS.

---

## 📦 Struktura Projektu

```
Warehouse-Managment-Systen/
├── main.py                          # Punkt wejścia aplikacji
├── config.json                       # Konfiguracja systemu
├── requirements.txt                  # Zależności Python
│
├── functions/                        # Moduły biznesowe
│   ├── database_manager.py           # Zarządzanie bazą danych
│   ├── pdf_generator.py              # Generator PDF
│   ├── RequestSender.py              # Wysyłanie requestów do robota
│   ├── RobotStatusChecker.py         # Sprawdzanie statusu robota
│   ├── RobotStatusManager.py         # Globalny manager statusu (singleton)
│   ├── ConfigManager.py              # Zarządzanie konfiguracją
│   ├── FloatingMessage.py            # Notyfikacje zmiennoprzecinkowe
│   ├── PopupMessage.py               # Okna dialogowe
│   ├── LabelGenerator.py             # Generator etykiet wysyłkowych
│   ├── ReportGenerator.py            # Generator raportów
│   ├── ExportManager.py              # Export do CSV/Excel
│   ├── AuditLogger.py                # Logowanie zdarzeń
│   ├── BackupManager.py              # Tworzenie kopii zapasowych
│   ├── ThemeManager.py               # Zarządzanie tematami
│   ├── RoleManager.py                # Kontrola dostępu (RBAC)
│   └── KeyboardShortcuts.py          # Skróty klawiszowe
│
├── panel/                            # UI Pages (PyQt6)
│   ├── main_window.py                # Główne okno aplikacji
│   ├── wms_login_page.py             # Strona logowania
│   ├── wms_dashboard_page.py         # Dashboard
│   ├── warehouse_documents_page.py   # Zarządzanie dokumentami
│   ├── robot_control_page.py         # Sterowanie robotem
│   ├── manual_control_page.py        # Ręczna kontrola
│   ├── shipment_labels_page.py       # Generowanie etykiet
│   ├── report_page.py                # Raporty
│   ├── add_document_dialog.py        # Dialog dodawania dokumentu
│   ├── stock_selection_dialog.py     # Dialog wyboru towarów
│   ├── wms_settings_page.py          # Ustawienia
│   │
│   ├── sidebar/
│   │   ├── sidebar.py                # Factory sidebar
│   │   ├── sidebar_style.py          # Komponenty sidebara
│   │   ├── toggle_arrow.py           # Animacja strzałki
│   │   └── sidebar_fuckknowswtfisthere.py  # Legacy code
│   │
│   └── map_editor/
│       ├── editor_page_v2.py         # Edytor mapy v2
│       ├── canvas_new.py             # Canvas dla mapy
│       ├── canvas.py                 # Legacy canvas
│       ├── dialogs.py                # Dialogi edytora
│       ├── route_logger.py           # Logger tras
│       └── route_selector.py         # Selektor tras
│
├── labels/                           # Wygenerowane etykiety (PDF)
├── reports/                          # Wygenerowane raporty
├── exports/                          # Exporty danych
├── backups/                          # Kopie zapasowe bazy
│
└── docs/
    ├── INSTRUKCJA_FUNKCJI.md         # Instrukcja dla użytkowników
    └── DOKUMENTACJA_TECHNICZNA.md    # Ten plik
```

---

## 🗄️ Baza Danych

**Plik:** `wms_database.db` (SQLite)

### Schemat Bazy Danych

```sql
-- Tabela użytkowników
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'operator',
    is_admin BOOLEAN,
    created_at TIMESTAMP
);

-- Tabela dokumentów magazynowych
CREATE TABLE warehouse_data (
    id INTEGER PRIMARY KEY,
    doc_number TEXT UNIQUE,
    doc_type TEXT,  -- 'PZ' lub 'WZ'
    date TEXT,
    status TEXT,
    value REAL,
    subject TEXT,
    created_at TIMESTAMP
);

-- Tabela pozycji dokumentu
CREATE TABLE warehouse_receipt_items (
    id INTEGER PRIMARY KEY,
    warehouse_id INTEGER,
    item_name TEXT,
    quantity INTEGER,
    unit TEXT,
    price REAL,
    supplier_info TEXT,
    FOREIGN KEY(warehouse_id) REFERENCES warehouse_data(id)
);

-- Tabela logów operacji
CREATE TABLE operations_log (
    id INTEGER PRIMARY KEY,
    operation_type TEXT,
    user_name TEXT,
    timestamp TEXT,
    description TEXT
);

-- Tabela audit logów (bezpieczeństwo)
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    event_type TEXT,
    user_id INTEGER,
    description TEXT,
    level TEXT,
    details TEXT
);

-- Tabela konfiguracji
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
);
```

### Użytkownik Domyślny
- **Login:** admin
- **Hasło:** admin123
- **Rola:** admin

---

## 🔌 API Modułów

### DatabaseManager
```python
from functions.database_manager import DatabaseManager

db = DatabaseManager()

# CRUD Operacje
db.add_warehouse_data(doc_number, doc_type, date, status, value, subject)
db.get_warehouse_data()
db.delete_warehouse_data(doc_id)

# Operacje
db.add_operation_log(operation, user, description)
db.get_operations()

# Zapytania
db.execute(sql, params)
db.commit()
db.close()
```

### ConfigManager (Singleton)
```python
from functions.ConfigManager import ConfigManager

# Singleton - zawsze ta sama instancja
config = ConfigManager()

# Dostęp do ustawień
robot_ip = config.get_robot_url()
timeout = config.get_robot_timeout()
interval = config.get_robot_check_interval()

# Dostęp do dowolnego klucza
value = config.get('robot.ip')
```

### RobotStatusManager (Singleton)
```python
from functions.RobotStatusManager import RobotStatusManager

# Globalny manager statusu - jedna instancja w app
manager = RobotStatusManager()

# Start w main_window.py
manager.start()  # Uruchamia checker w tle

# Sprawdzenie statusu
status = manager.get_status()  # 'Online' lub 'Offline'
is_online = manager.is_online()  # True/False

# Łączenie się do sygnałów
manager.status_changed.connect(self.on_status_change)

# Zatrzymanie
manager.stop()
```

### LabelGenerator
```python
from functions.LabelGenerator import ShipmentLabelGenerator

gen = ShipmentLabelGenerator()

# Generowanie etykiety wysyłkowej
filepath, label_data = gen.create_shipment_label(
    recipient="Jan Kowalski",
    address="ul. Główna 123",
    postal_code="00-000",
    city="Warszawa",
    sender_notes="Fragile - ostrożnie!",
    label_type='PACZKA'  # PACZKA, PALETA, POBRANIE, ZWROT
)

# label_data ma: type, label_type, wz_number, barcode, recipient, itp.
```

### ReportGenerator
```python
from functions.ReportGenerator import ReportGenerator

gen = ReportGenerator()

# Generowanie raportów
pdf_path, data = gen.generate_daily_report_pdf()
pdf_path, data = gen.generate_inventory_report_pdf()
csv_path, data = gen.generate_operations_report_csv()
excel_path, data = gen.generate_inventory_report_excel()
```

### ExportManager
```python
from functions.ExportManager import ExportManager

exp = ExportManager()

# Export do CSV
csv_path = exp.export_to_csv(
    data=[('row1col1', 'row1col2'), ('row2col1', 'row2col2')],
    filename='mydata',
    headers=['Col1', 'Col2']
)

# Export do Excel
excel_path = exp.export_to_excel(
    data=[...],
    filename='mydata',
    headers=['Col1', 'Col2'],
    sheet_name='Data',
    title='My Report'
)
```

### AuditLogger (Singleton)
```python
from functions.AuditLogger import AuditLogger

# Logowanie zdarzeń
AuditLogger.log(
    event_type='LOGIN',
    user_id=1,
    description='User jane logged in',
    level='INFO',
    details={'ip': '192.168.1.100', 'browser': 'Chrome'}
)

# Dostęp do logów
logs = AuditLogger.get_logs(limit=100)
user_logs = AuditLogger.get_user_logs(user_id=1)
security_events = AuditLogger.get_security_events()
```

### BackupManager
```python
from functions.BackupManager import BackupManager

bak = BackupManager()

# Tworzenie kopii
backup_path, metadata = bak.create_backup(description="Auto backup")

# Przywracanie kopii
success, msg = bak.restore_backup(backup_path)

# Lista kopii
backups = bak.get_backups()

# Usuwanie kopii
success, msg = bak.delete_backup(filename)

# Auto-backup
success, msg = bak.auto_backup(keep_count=5)
```

### ThemeManager (Singleton)
```python
from functions.ThemeManager import ThemeManager

theme = ThemeManager()

# Pobierz kolory bieżącego tematu
color = theme.get_color('accent')  # '#0066cc' (light) lub '#00a3ff' (dark)

# Zmiana tematu
theme.toggle_theme()  # light <-> dark
theme.set_theme('dark')

# Stylesheet dla całej aplikacji
stylesheet = theme.get_stylesheet()
app.setStyleSheet(stylesheet)
```

### RoleManager
```python
from functions.RoleManager import RoleManager, UserPermissionChecker

# Sprawdzenie uprawnień
checker = UserPermissionChecker('operator')

if checker.can_view_dashboard():
    show_dashboard()

if checker.can_control_robot():
    show_robot_control()

# Listowanie ról
roles = RoleManager.get_all_roles()  # {'admin': 'Administrator', ...}

# Sprawdzenie konkretnego uprawnienia
has_perm = RoleManager.has_permission('manager', 'edit_documents')
```

### KeyboardShortcuts
```python
from functions.KeyboardShortcuts import KeyboardShortcuts

# Pobranie skrótu
shortcut = KeyboardShortcuts.get_shortcut('dashboard')

# Listowanie wszystkich skrótów
all = KeyboardShortcuts.get_shortcuts_list()
```

---

## 🏗️ Architektura UI

### Strona Bazowa (Page Pattern)

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class MyPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        # Budowanie UI...
        self.setLayout(layout)
    
    def show_success(self, msg):
        QMessageBox.information(self, "Sukces", msg)
    
    def show_error(self, msg):
        QMessageBox.critical(self, "Błąd", msg)
```

### Integracja z Main Window

```python
# main_window.py
self.report_page = ReportPage()
self.stacked_widget.addWidget(self.report_page)

# Metoda do przełączania
def show_report_page(self):
    self.stacked_widget.setCurrentWidget(self.report_page)

# Navigation
self.sidebar.button_configs = [
    ("📊 Raporty", "show_report_page"),
]
```

---

## 🔌 Integracja Robota

### HTTP API Robota

**Endpoint Statusu:**
```
GET http://192.168.18.52:80/status
Response: {"status": "online", "battery": 95}
```

**Endpoint Poleceń:**
```
POST http://192.168.18.52:80/cmd
Body: {"command": "forward", "distance": 100}
Response: {"success": true, "execution_time": 1.2}
```

### RequestSender
```python
from functions.RequestSender import RequestSender

sender = RequestSender()

# Wysłanie polecenia
success, message = sender.send_command("forward")

if success:
    print("Robott się rusza!")
else:
    print(f"Błąd: {message}")  # "Robot wyłączony" lub "Timeout"
```

### Status Checker
```python
from functions.RobotStatusChecker import RobotStatusChecker

checker = RobotStatusChecker()
checker.status_changed.connect(self.on_status)
checker.start()  # Uruchamia w tle

# W signale
def on_status(self, status):
    print(f"Robot: {status}")  # 'Online' lub 'Offline'
```

---

## 🎨 Stylowanie

### Kolory Systemowe (Light Theme)
```
#ffffff         - Białe tło główne
#f5f5f5         - Szare tło drugoplanowe
#0066cc         - Kolor główny (niebieski)
#10b981         - Zielony (OK, sukces)
#f59e0b         - Pomarańczowy (ostrzeżenie)
#ef4444         - Czerwony (błąd)
```

### Kolory Dark Theme
```
#1a1a1a         - Ciemne tło
#2d2d2d         - Ciemne tło drugoplanowe
#00a3ff         - Jasny niebieski
```

---

## 📝 Dodawanie Nowej Strony

### 1. Stwórz plik strony
```python
# panel/my_feature_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont

class MyFeaturePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Nowa Funkcja")
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.setLayout(layout)
```

### 2. Zarejestruj w main_window.py
```python
# main_window.py
from panel.my_feature_page import MyFeaturePage

# W __init__
self.my_feature_page = MyFeaturePage()
self.stacked_widget.addWidget(self.my_feature_page)

# Metoda przełączania
def show_my_feature_page(self):
    self.stacked_widget.setCurrentWidget(self.my_feature_page)
```

### 3. Dodaj przycisk w sidebar
```python
# panel/sidebar/sidebar_style.py
self.button_configs = [
    # ...istniejące...
    ("🆕 Moja Funkcja", "show_my_feature_page"),
]
```

---

## 📦 Konfiguracja (config.json)

```json
{
  "robot": {
    "ip": "192.168.18.52",
    "port": 80,
    "status_endpoint": "/status",
    "command_endpoint": "/cmd",
    "timeout": 2,
    "check_interval": 15
  },
  "api": {
    "base_url": "http://192.168.18.52"
  },
  "database": {
    "path": "wms_database.db"
  },
  "backup": {
    "auto_enabled": true,
    "auto_interval": 3600,
    "keep_count": 5
  }
}
```

---

## 🧪 Testing

### Uruchomienie aplikacji
```bash
python main.py
```

### Testowanie modułu
```bash
# Test LabelGenerator
python -c "from functions.LabelGenerator import ShipmentLabelGenerator; gen = ShipmentLabelGenerator(); path, data = gen.create_shipment_label('Test', 'Addr', '00-000', 'City', '', 'PACZKA'); print(f'OK: {path}')"
```

### Import check
```bash
python -c "from functions import *; print('All imports OK')"
```

---

## 🐛 Debugging

### Włączanie logów
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Audit log inspection
```python
from functions.AuditLogger import AuditLogger

# Pokaż ostatnie 50 logów
for log in AuditLogger.get_logs(50):
    print(f"{log[0]} - {log[2]}: {log[3]}")  # timestamp, event, user, desc
```

---

## 📦 Zależności

```
PyQt6==6.x
reportlab==4.x
openpyxl==3.x
requests==2.x
```

Install: `pip install -r requirements.txt`

---

## 🚀 Deployment

### Budowanie EXE
```bash
pyinstaller main.py --onefile --windowed
```

### Instalacja na serwerze
1. Clone repo
2. `pip install -r requirements.txt`
3. `python main.py`
4. Open browser to `localhost:8080` (jeśli web version)

---

## 📞 Wsparcie Techniczny

**Błędy importów:** Sprawdź `requirements.txt` i venv

**Błędy bazy danych:** Usuń `wms_database.db` aby reset

**Błędy robota:** Sprawdź IP w `config.json` i połączenie sieciowe

**Błędy UI:** Sprawdź kompatybilność PyQt6

---

**Last Updated:** 28.03.2026
**Version:** 2.0
