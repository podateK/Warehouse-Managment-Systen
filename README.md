# 🏭 Warehouse Management System (WMS)

Zaawansowany system zarządzania magazynem zbudowany w Pythonie z użyciem PyQt6. Aplikacja zapewnia intuicyjny interfejs do kontroli i monitorowania operacji magazynowych, zarządzania dokumentami, zarządzania robotami AGV/AMR oraz edycji map magazynów.

## ✨ Główne Cechy

- **🤖 Zarządzanie Robotami** - Ręczna kontrola robotów AGV/AMR z możliwością programowania tras
- **📦 Zarządzanie Magazynem** - Śledzenie stanu magazynów (H1, P1, W1, M1, M2, M3)
- **📄 Zarządzanie Dokumentami** - Obsługa dokumentów magazynowych z generowaniem PDF
- **🗺️ Edytor Map** - Edytor wizualny do tworzenia i modyfikowania map magazynów
- **📊 Dashboard** - Przegląd stanu systemu w czasie rzeczywistym
- **🔐 System Logowania** - Zarządzanie dostępem do systemu
- **⚙️ Ustawienia** - Konfiguracja parametrów systemu
- **🗃️ Baza Danych SQLite** - Trwałe przechowywanie danych

## 🛠️ Wymagania

- Python 3.8+
- PyQt6
- SQLite3

## 📋 Struktura Projektu

```
Warehouse-Management-System/
├── main.py                          # Punkt wejścia aplikacji
├── README.md                        # Ten plik
├── functions/                       # Moduły pomocnicze
│   ├── database_manager.py         # Zarządzanie bazą danych
│   ├── pdf_generator.py            # Generacja PDF
│   ├── RequestSender.py            # Wysyłanie żądań do robota
│   ├── RobotStatusChecker.py       # Monitorowanie stanu robota
│   ├── FloatingMessage.py          # Komunikaty zmiennoprzecinkowe
│   └── PopupMessage.py             # Okna dialogowe
├── panel/                           # Komponenty UI
│   ├── main_window.py              # Okno główne
│   ├── login_page.py               # Strona logowania
│   ├── dashboard_page.py           # Dashboard
│   ├── robot_control_page.py       # Kontrola robota
│   ├── map_editor_page.py          # Edytor map
│   ├── dokumenty_page.py           # Zarządzanie dokumentami
│   ├── warehouse_documents_page.py # Dokumenty magazynowe
│   ├── pdfGeneration_page.py       # Generacja PDF
│   ├── settings_page.py            # Ustawienia
│   ├── manual_control_page.py      # Kontrola manualna
│   ├── stock_selection_dialog.py   # Dialog wyboru zapasów
│   ├── add_document_dialog.py      # Dialog dodawania dokumentu
│   ├── map_editor/                 # Komponenty edytora map
│   │   ├── canvas.py               # Główne płótno rysujące
│   │   ├── dialogs.py              # Dialogi edytora
│   │   ├── route_selector.py       # Selektor tras
│   │   └── route_logger.py         # Logger tras
│   └── sidebar/                    # Komponenty paska bocznego
│       ├── sidebar.py              # Główny pasek boczny
│       ├── sidebar_style.py        # Style CSS
│       └── toggle_arrow.py         # Przycisk rozwijania
├── tools/                          # Narzędzia pomocnicze
│   └── route_logger.py             # Logger tras
├── icons/                          # Zasoby graficzne
├── invoices/                       # Przechowywanie faktur/dokumentów
└── wms_database.db                # Baza danych SQLite
```

## 🚀 Instalacja

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/yourusername/Warehouse-Management-System.git
cd Warehouse-Management-System
```

### 2. Tworzenie wirtualnego środowiska
```bash
python -m venv .venv
```

### 3. Aktywacja wirtualnego środowiska

**Windows:**
```bash
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 4. Instalacja zależności
```bash
pip install PyQt6
```

### 5. Uruchomienie aplikacji
```bash
python main.py
```

## 📖 Użytkowanie

### Login
- Uruchom aplikację - zobaczysz stronę logowania
- Wpisz kredencjały (domyślne: zobacz `login_page.py`)

### Dashboard
- Przegląd ogólnego stanu systemu
- Monitorowanie aktywności robotów
- Status magazynów

### Kontrola Robota
- Przycisk **⬆️ Przód** - ruch do przodu
- Przycisk **⬅️ Lewo** - ruch w lewo
- Przycisk **➡️ Prawo** - ruch w prawo
- Przycisk **⬇️ Tył** - ruch do tyłu
- Przycisk **⏹️ STOP** - zatrzymanie robota
- Przyciski **🔼 PODNIEŚ / 🔽 OPUŚĆ** - podnoszenie/opuszczanie ładunku

**Włączanie sterowania:** Użyj suwaka "Włączyć Sterowanie Manualne" (musi być w pozycji ON)

### Edytor Map
- Twórz i modyfikuj mapy magazynów wizualnie
- Definiuj trasy dla robotów
- Eksportuj konfiguracje

### Zarządzanie Dokumentami
- Dodawaj nowe dokumenty
- Generuj raporty PDF
- Przeglądaj historię dokumentów

### Ustawienia
- Konfiguruj adres serwera robota
- Dostosuj parametry systemu
- Zarządzaj użytkownikami

## 🔌 Integracja z Robotem

Aplikacja komunikuje się z robotem AGV/AMR poprzez HTTP API:

```python
# Przykład wysłania komendy do robota
from functions.RequestSender import RequestSender

sender = RequestSender("http://10.91.170.213/cmd")
sender.send_request("FORWARD")
sender.send_request("STOP")
```

Obsługiwane komendy:
- `FORWARD` - ruch do przodu
- `BACK` - ruch do tyłu
- `MOVE_LEFT` - ruch w lewo
- `MOVE_RIGHT` - ruch w prawo
- `ACTION_LIFT` - podniesienie ładunku
- `ACTION_LOWER` - opuszczenie ładunku
- `STOP` - zatrzymanie

## 💾 Baza Danych

System używa SQLite do przechowywania:
- Danych użytkowników
- Dokumentów magazynowych
- Historii operacji
- Konfiguracji map

Plik bazy danych: `wms_database.db`

**Reset bazy danych:**
```powershell
Remove-Item -Path wms_database.db -Force
python main.py
```

## 🎨 Design i Styling

Aplikacja wykorzystuje nowoczesny, przemysłowy design z wykorzystaniem:
- Paleta kolorów: Niebieska (#0066cc), Zielona (#10b981), Czerwona (#ef4444)
- Font: Segoe UI, Helvetica Neue
- Zaokrąglone przyciski i elementy
- Responsywny layout

## 🐛 Rozwiązywanie Problemów

### Aplikacja się nie uruchamia
```bash
# Usuń cache Pythona
Get-ChildItem -Recurse -Directory -Filter __pycache__ | ForEach-Object { Remove-Item -Path $_.FullName -Recurse -Force }

# Zresetuj bazę danych
Remove-Item -Path wms_database.db -Force

# Uruchom ponownie
python main.py
```

### Problem z połączeniem do robota
- Sprawdź IP robota: `http://10.91.170.213/cmd`
- Upewnij się, że robot jest w sieci
- Sprawdź konfigurację w Ustawieniach

### Problem z GUI
- Upewnij się, że PyQt6 jest prawidłowo zainstalowany
- Odinstaluj i zainstaluj ponownie: `pip uninstall PyQt6 && pip install PyQt6`

## 📝 Pliki Konfiguracyjne

### Magazyny (warehouses)
Zdefiniowane w `robot_control_page.py`:
- **H1** - Magazyn H
- **P1** - Magazyn P
- **W1** - Magazyn W
- **M1** - Magazyn M1
- **M2** - Magazyn M2
- **M3** - Magazyn M3

Każdy magazyn ma zdefiniowaną sekwencję ruchów robota.

## 🔒 Bezpieczeństwo

- System logowania chroni dostęp do aplikacji
- Operacje na bazie danych są bezpieczne
- Komunikacja z robotem powinna być zabezpieczona (rekomendacja: VPN)

## 📞 Kontakt i Wsparcie

W przypadku problemów:
1. Sprawdź issues na GitHub
2. Skontaktuj się z zespołem deweloperskim
3. Opisz problem ze szczegółami kroku do kroku

## 📄 Licencja

Projekt jest dostępny na licencji [DODAJ LICENCJĘ]

---

**Ostatnia aktualizacja:** Marzec 2026  
**Wersja:** 1.0.0
