# 📖 Instrukcja Użytkownika - WMS System

Kompleksowy przewodnik po wszystkich funkcjach Warehouse Management System.

---

## 📋 Spis Treści

1. [Quickstart](#quickstart)
2. [Nawigacja](#nawigacja)
3. [Funkcje Główne](#funkcje-główne)
4. [Funkcje Zaawansowane](#funkcje-zaawansowane)
5. [Skróty Klawiszowe](#skróty-klawiszowe)
6. [Role i Uprawnienia](#role-i-uprawnienia)
7. [FAQ](#faq)

---

## 🚀 Quickstart

### Uruchomienie aplikacji
```bash
python main.py
```

### Logowanie
1. Uruchom aplikację
2. Wpisz login i hasło
3. Kliknij przycisk **Zaloguj** lub naciśnij Enter
4. Po zalogowaniu zobaczysz **Dashboard** z panel nawigacyjnym po lewej

### Hasło
- Domyślnie: `admin` / `admin123`
- Możesz nacisnąć przycisk 👁️ aby podejrzeć hasło

---

## 🗂️ Nawigacja

### Sidebar (Panel Lewostronny)

Dostęp do wszystkich funkcji przez sidebar:

| Przycisk | Skrót | Opis |
|----------|-------|------|
| 📊 Dashboard | Ctrl+1 | Główny panel z metrykami |
| 🤖 Sterowanie Robotem | Ctrl+2 | Kontrola robota |
| 🗺️ Edytor Mapy | - | Edycja mapy magazynu |
| 📄 Dokumenty | Ctrl+3 | Dokumenty PZ/WZ |
| 🏷️ Etykiety Wysyłki | Ctrl+4 | Generowanie etykiet |
| 📊 Raporty | Ctrl+5 | Raporty i analizy |
| ⚙️ Ustawienia | Ctrl+9 | Ustawienia użytkownika |

**Status w Sidebarze:**
- 🟢 Online / 🔴 Offline - Status robota
- Informacje o systemie

---

## 💼 Funkcje Główne

### 1️⃣ Dashboard (📊)

**Co to jest?** Główny panel z kluczowymi metrykami i wskaźnikami.

**Zawartość:**
- **Liczba towarów w magazynie** - Łączna ilość jednostek
- **Liczba zamówień** - Aktywne zamówienia
- **Ostatnie operacje** - Historia działań
- **Status robota** - Czy robot jest online
- **Szybkie akcje** - Przyciski do częstych operacji

**Jak używać:**
1. Kliknij Dashboard w sidebarze
2. Przejrzyj metryki
3. Kliknij przycisk **"Status Robota"** aby odświeżyć status
4. Kliknij inne przyciski szybkich akcji

---

### 2️⃣ Sterowanie Robotem (🤖)

**Co to jest?** Panel do ręcznego sterowania robotem.

**Funkcje:**
- **Przyciski kierunkowe** - Sterowanie: Przód, Tył, Lewo, Prawo
- **Podnoszenia/Opuszczanie** - Regulacja wysokości
- **Stop** - Zatrzymanie robota
- **Status** - Bieżący status (Online/Offline)

**Jak używać:**
1. Kliknij **Sterowanie Robotem** w sidebarze
2. Upewnij się, że robot jest Online (🟢)
3. Kliknij przyciski do sterowania
4. Status zmieni się na "Pracuje" gdy robot się porusza
5. Jeśli robot offline - pokaże się ostrzeżenie

**Skróty klawiszowe:**
- ⬆️ (Strzałka góra) - Do przodu
- ⬇️ (Strzałka dół) - Do tyłu
- ⬅️ (Strzałka lewo) - W lewo
- ➡️ (Strzałka prawo) - W prawo
- Esc - Stop

---

### 3️⃣ Edytor Mapy (🗺️)

**Co to jest?** Edytor wizualny mapy magazynu.

**Funkcje:**
- **Dodawanie pól** - Zaznacz obszar na mapie
- **Edycja właściwości** - Zmień nazwę, typ
- **Usuwanie** - Usuń pole z mapy
- **Zapis** - Automatyczne zapisywanie

**Jak używać:**
1. Kliknij **Edytor Mapy** w sidebarze
2. Prawy klik na mapie - dodaj nowe pole
3. Lewy klik na polu - edytuj
4. Kliknij X - usuń pole
5. Zmiany są automatycznie zapisywane

---

### 4️⃣ Dokumenty (📄)

**Co to jest?** Zarządzanie dokumentami magazynowymi (PZ - przyjęcia, WZ - wydania).

**Funkcje:**
- **Przeglądanie dokumentów** - Lista wszystkich dokumentów
- **Dodawanie dokumentu** - Nowy dokument
- **Generowanie PDF** - Drukowanie dokumentu
- **Generowanie PDF z wielu** - Łączenie dokumentów w jeden PDF
- **Usuwanie** - Skasowanie dokumentu
- **Export** - Wyeksportowanie danych

**Jak dodać dokument:**
1. Kliknij **"+ Nowy dokument"**
2. Wybierz typ (PZ = przyjęcie, WZ = wydanie)
3. Wpisz dane:
   - Numer dokumentu
   - Data
   - Przedmiot transakcji
   - Wartość
4. Kliknij **"Dodaj dokument"**

**Jak generować PDF:**
1. Wybierz 1 lub więcej dokumentów (zaznaczenie checkboxem)
2. Kliknij **"Generuj PDF"**
3. Dokument otworzy się automatycznie
4. Możesz wydrukować (Ctrl+P) lub zapisać

**Jak eksportować:**
1. Zaznacz dokumenty
2. Kliknij **"Eksportuj CSV"** lub **"Eksportuj Excel"**
3. Plik zostanie pobrany do folderu `exports`

---

### 5️⃣ Etykiety Wysyłki (🏷️)

**Co to jest?** Generator etykiet do wysyłki z kodem kreskowym.

**Dostępne typy etykiet:**
- 🟥 **PACZKA** - Przesyłka standardowa (czerwona)
- 🟧 **PALETA** - Transport paletowy (pomarańczowa)
- 🟣 **POBRANIE** - Przesyłka podziałem (fioletowa)
- 🟦 **ZWROT** - Zwrot towaru (niebieska)

**Pola formularza:**
- **Odbiorca** - Nazwa odbiorcy (wymagane)
- **Typ Etykiety** - Wybór z listy
- **Adres** - Ulica i numer domu (wymagane)
- **Kod Pocztowy** - XX-XXX format (wymagane)
- **Miasto** - Nazwa miasta (wymagane)
- **Uwagi Nadawcy** - Dodatkowe instrukcje (opcjonalnie)

**Jak generować etykietę:**
1. Kliknij **Etykiety Wysyłki** w sidebarze
2. Uzupełnij wszystkie wymagane pola
3. Wybierz typ etykiety
4. Kliknij **"Generuj Etykietę"**
5. Pokaże się kod kreskowy i WZ numer
6. Kliknij **"Drukuj"** by wysłać do drukarki
7. Lub **"Otwórz Folder"** by znaleźć plik

**Kod kreskowy:**
- Generowany losowo (EAN-13)
- Gotów do skanowania
- Zawiera wszystkie dane wysyłki

---

### 6️⃣ Raporty (📊)

**Co to jest?** System tworzenia raportów i analiz magazynowych.

**Dostępne raporty:**

#### Raport Dzienny (PDF)
- 📅 Podsumowanie dzisiejszych operacji
- Liczba operacji
- Historia działań
- Aktywni użytkownicy

#### Stan Magazynu (PDF)
- 📦 Aktualny status wszystkich towarów
- Quantities i lokalizacje
- Status towarów (OK, Niskie, Krytyczne)
- Statystyki magazynu

#### Operacje (CSV)
- 📊 Export ostatnich operacji
- Możliwość analizy w Excel
- Dane: typ, użytkownik, data

#### Magazyn (Excel)
- 📈 Raport stanu z formatowaniem
- Kolorowe wyróżnienia
- Gotowy do rozsyłki
- Support do analizy

**Jak generować raport:**
1. Kliknij **Raporty** w sidebarze
2. Wybierz typ raportu (kliknij przycisk)
3. Raport został wygenerowany
4. Automatycznie otworzy się lub pobierze
5. Kliknij **"Otwórz Folder Raportów"** by znaleźć wszystkie

**Format i lokalizacja:**
- Raporty PDF - otwierają się automatycznie
- CSV/Excel - folder `reports/`

---

## 🔧 Funkcje Zaawansowane

### 1. Tworzenie Kopii Zapasowej

**Gdzie:** Ustawienia → Backup

**Jak używać:**
1. Kliknij **Ustawienia** (Ctrl+9)
2. Przejdź do sekcji "Backup"
3. Kliknij **"Utwórz Kopię Zapasową"**
4. Zostanie utworzony plik ZIP z bazą danych
5. Zapisze się w folderze `backups/`

**Auto-Backup:**
- System automatycznie tworzy kopie
- Przechowuje ostatnich 5 kopii
- Stare kopie są usuwane

**Przywrócenie:**
1. Przejdź do Ustawienia → Backup
2. Wybierz kopię z listy
3. Kliknij **"Przywróć"**
4. Baza wróci do stanu z kopii

---

### 2. Audit Log (Historia Zdarzeń)

**Gdzie:** Ustawienia → Historia → Audit Log

**Co loguje:**
- 🔐 Logowanie/Wylogowanie
- 📄 Tworzenie/Usuwanie dokumentów
- 🤖 Polecenia robota
- 📊 Generacja raportów
- 🏷️ Generacja etykiet
- ⚠️ Błędy i ostrzeżenia

**Jak przeglądać:**
1. Kliknij **Ustawienia**
2. Przejdź do **Historia**
3. Kliknij **Audit Log**
4. Widzisz wszystkie zdarzenia
5. Możesz filtrować po:
   - Typie zdarzenia
   - Użytkowniku
   - Dacie

**Informacje w logu:**
- Data i czas
- Typ zdarzenia
- Użytkownik
- Opis akcji
- Poziom (INFO/OSTRZEŻENIE/BŁĄD)

---

### 3. Role i Uprawnienia

**Gdzie:** Ustawienia → Użytkownicy

**Dostępne role:**

| Rola | Uprawnienia |
|------|-----------|
| 👑 **Admin** | Wszystkie funkcje + zarządzanie systemem |
| 📋 **Manager** | Dokumenty, raporty, użytkownicy, robot |
| 👷 **Operator** | Dokumenty, robot, etykiety |
| 👁️ **Viewer** | Tylko przeglądanie danych |

**Jak zmienić rolę użytkownika:**
1. Kliknij **Ustawienia**
2. Przejdź do **Użytkownicy**
3. Wybierz użytkownika
4. Kliknij **"Zmień rolę"**
5. Wybierz nową rolę
6. Kliknij **"Zapisz"**

---

### 4. Ustawienia Systemu

**Gdzie:** Ustawienia → System

**Opcje:**

- **IP Robota** - Adres robota (default: 192.168.18.52)
- **Port** - Port komunikacji (default: 80)
- **Timeout** - Timeout dla requestów (2 sekundy)
- **Interval statusu** - Jak często sprawdzać status (15 sekund)

Wszystkie ustawienia są w pliku `config.json`.

---

## ⌨️ Skróty Klawiszowe

### Nawigacja
| Skrót | Akcja |
|-------|-------|
| Ctrl+1 | Dashboard |
| Ctrl+2 | Sterowanie Robotem |
| Ctrl+3 | Dokumenty |
| Ctrl+4 | Etykiety Wysyłki |
| Ctrl+5 | Raporty |
| Ctrl+9 | Ustawienia |

### Operacje Dokumentów
| Skrót | Akcja |
|-------|-------|
| Ctrl+N | Nowy dokument |
| Ctrl+P | Drukuj |
| Ctrl+E | Eksportuj |
| Del | Usuń |

### Sterowanie Robotem
| Skrót | Akcja |
|-------|-------|
| ⬆️ | Do przodu |
| ⬇️ | Do tyłu |
| ⬅️ | W lewo |
| ➡️ | W prawo |
| Esc | Stop |

### Pozostałe
| Skrót | Akcja |
|-------|-------|
| Ctrl+F | Wyszukaj |
| Ctrl+Q | Wyloguj |
| F1 | Pomoc |
| F5 | Odśwież |

---

## 👥 Role i Uprawnienia

### Administrator
- ✅ Pełny dostęp do wszystkich funkcji
- ✅ Zarządzanie użytkownikami
- ✅ Tworzenie/przywracanie kopii zapasowych
- ✅ Przeglądanie audit logów
- ✅ Zmiana ustawień systemu

### Manager Magazynu
- ✅ Zarządzanie dokumentami
- ✅ Generowanie raportów
- ✅ Sterowanie robotem
- ✅ Generowanie etykiet
- ✅ Zarządzanie niektórymi użytkownikami
- ❌ Brak dostępu do backupu
- ❌ Brak dostępu do konfiguracji

### Operator
- ✅ Edycja dokumentów
- ✅ Generowanie etykiet
- ✅ Sterowanie robotem
- ✅ Przeglądanie raportów
- ❌ Brak tworzenia raportów
- ❌ Brak zarządzania użytkownikami

### Przeglądacz
- ✅ Przeglądanie dashboardu
- ✅ Przeglądanie raportów
- ✅ Historia (Audit Log)
- ❌ Brak edycji dokumentów
- ❌ Brak dostępu do robota

---

## ❓ FAQ

### P: Jak odświeżyć dane?
**O:** Naciśnij F5 lub kliknij przycisk odświeżania w danej sekcji.

### P: Robot jest offline, co robić?
**O:** Sprawdź połączenie sieciowe. IP robota jest w `config.json` (`robot.ip`). Robot powinien być na `192.168.18.52:80`.

### P: Jak zmienić hasło?
**O:** Ustawienia → Konto → Zmień hasło.

### P: Gdzie są pliki etykiet/raportów?
**O:** 
- Etykiety: folder `labels/`
- Raporty: folder `reports/`
- Exporty: folder `exports/`
- Backupy: folder `backups/`

### P: Mogę przywrócić starą kopię zapasową?
**O:** Tak, Ustawienia → Backup → wybierz kopię → Przywróć.

### P: Jakie dane zawiera PDF dokumentu?
**O:** Numer, typ (PZ/WZ), data, przedmiot, wartość, oraz wszystkie pozycje towaru.

### P: Jak kombinować wiele dokumentów w jeden PDF?
**O:** Zaznacz chequeboxy obok dokumentów → Generuj PDF. Wszystkie pozycje pojawią się w jednym pliku.

### P: Mogę drukować etykiety?
**O:** Tak, kliknij "Drukuj" po wygenerowaniu etykiety. Trafi do domyślnej drukarki.

### P: Czy kod kreskowy na etykiecie jest rzeczywisty?
**O:** Tak, to kod EAN-13. Możesz go skanować na magazynie.

### P: Jak używać szybkiego wyszukiwania?
**O:** Ctrl+F → wpisz szukaną frazę → Enter. Ctrl+Shift+F dla zaawansowanego wyszukiwania.

### P: Czy mogę dać innemu użytkownikowi dostęp do robota?
**O:** Tak, zmień jego rolę na "Manager" lub wyżej. Ustawienia → Użytkownicy.

### P: Jak wyglądają statusy robota?
**O:**
- 🟢 **Online** - Robot gotów do pracy
- 🔴 **Offline** - Nie żyje połączenie
- ⚠️ **Pracuje** - Wykonuje polecenie

---

## 📞 Wsparcie

**Błędy lub problemy?**
- Sprawdź folder `logs/` pod kątem szczegółów
- Przejrzyj Audit Log w Ustawienia → Historia
- Sprawdź połączenie z robotem
- Zainstaluj najnowszą wersję aplikacji

**Kontakt:** admin@wms.local

---

**Ostatnia aktualizacja:** 28.03.2026
**Wersja systemu:** 2.0
**Autor:** WMS Development Team
