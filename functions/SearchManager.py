import json
from datetime import datetime

class SearchIndex:
    
    def __init__(self):
        self.index = {
            'functions': self._build_functions_index(),
            'shortcuts': self._build_shortcuts_index(),
            'instructions': self._build_instructions_index(),
        }
    
    def _build_functions_index(self):
        return [
            {
                'title': 'Dashboard',
                'icon': '📊',
                'keyword': 'dashboard glavni panel metryki',
                'description': 'Główny panel z kluczowymi metrykami i wskaźnikami',
                'shortcuts': ['Ctrl+1'],
                'action': 'show_main_page'
            },
            {
                'title': 'Sterowanie Robotem',
                'icon': '🤖',
                'keyword': 'robot kontrola sterowanie kierunki',
                'description': 'Panel do ręcznego sterowania robotem',
                'shortcuts': ['Ctrl+2', '↑↓←→', 'Esc'],
                'action': 'show_manual_control_page'
            },
            {
                'title': 'Edytor Mapy',
                'icon': '🗺️',
                'keyword': 'mapa edytor magazyn schemat',
                'description': 'Edytor wizualny mapy magazynu',
                'shortcuts': [],
                'action': 'show_map_editor_page'
            },
            {
                'title': 'Dokumenty PZ/WZ',
                'icon': '📄',
                'keyword': 'dokumenty pdf druk generowanie przyjecia wydania',
                'description': 'Zarządzanie dokumentami magazynowymi (PZ - przyjęcia, WZ - wydania)',
                'shortcuts': ['Ctrl+3', 'Ctrl+N', 'Ctrl+P', 'Ctrl+E'],
                'action': 'show_dokumenty_page'
            },
            {
                'title': 'Etykiety Wysyłki',
                'icon': '🏷️',
                'keyword': 'etykiety wysylka kod kreskowy paczka paleta zwrot pobranie',
                'description': 'Generator etykiet do wysyłki z kodem kreskowym',
                'shortcuts': ['Ctrl+4'],
                'action': 'show_labels_page'
            },
            {
                'title': 'Raporty i Analizy',
                'icon': '📊',
                'keyword': 'raporty analiza export csv excel dane statystyki',
                'description': 'System tworzenia raportów i analiz magazynowych',
                'shortcuts': ['Ctrl+5'],
                'action': 'show_report_page'
            },
            {
                'title': 'Ustawienia',
                'icon': '⚙️',
                'keyword': 'ustawienia konfiguracja uzytkownik rola backup',
                'description': 'Zarządzanie ustawieniami użytkownika i systemu',
                'shortcuts': ['Ctrl+9'],
                'action': 'show_settings_page'
            },
            {
                'title': 'Logowanie',
                'icon': '🔐',
                'keyword': 'logowanie haslo login auth autentykacja',
                'description': 'Logowanie do systemu WMS',
                'shortcuts': [],
                'action': 'login'
            },
            {
                'title': 'Backup Bazy Danych',
                'icon': '💾',
                'keyword': 'backup kopia zapasowa przywrocenie restore',
                'description': 'Tworzenie i przywracanie kopii zapasowych bazy danych',
                'shortcuts': ['Ctrl+Shift+B'],
                'action': 'backup'
            },
            {
                'title': 'Audit Log',
                'icon': '📝',
                'keyword': 'audit log historia zdarzenia bezpieczeństwo',
                'description': 'Historia wszystkich zdarzeń w systemie',
                'shortcuts': [],
                'action': 'audit'
            },
            {
                'title': 'Role i Uprawnienia',
                'icon': '👥',
                'keyword': 'role uprawnienia dostep admin manager operator viewer',
                'description': 'Zarządzanie rolami i uprawnieniami użytkowników',
                'shortcuts': [],
                'action': 'roles'
            },
        ]
    
    def _build_shortcuts_index(self):
        return [
            {'key': 'Ctrl+1', 'action': 'Dashboard', 'category': 'Nawigacja'},
            {'key': 'Ctrl+2', 'action': 'Sterowanie Robotem', 'category': 'Nawigacja'},
            {'key': 'Ctrl+3', 'action': 'Dokumenty', 'category': 'Nawigacja'},
            {'key': 'Ctrl+4', 'action': 'Etykiety Wysyłki', 'category': 'Nawigacja'},
            {'key': 'Ctrl+5', 'action': 'Raporty', 'category': 'Nawigacja'},
            {'key': 'Ctrl+9', 'action': 'Ustawienia', 'category': 'Nawigacja'},
            {'key': 'Ctrl+N', 'action': 'Nowy dokument', 'category': 'Dokumenty'},
            {'key': 'Ctrl+P', 'action': 'Drukuj', 'category': 'Dokumenty'},
            {'key': 'Ctrl+E', 'action': 'Eksportuj', 'category': 'Dokumenty'},
            {'key': 'Ctrl+F', 'action': 'Wyszukaj', 'category': 'Wyszukiwanie'},
            {'key': 'F5', 'action': 'Odśwież', 'category': 'Wyszukiwanie'},
            {'key': 'F3', 'action': 'Znajdź następny', 'category': 'Wyszukiwanie'},
            {'key': '↑ / ⬆️', 'action': 'Robot do przodu', 'category': 'Robot'},
            {'key': '↓ / ⬇️', 'action': 'Robot do tyłu', 'category': 'Robot'},
            {'key': '← / ⬅️', 'action': 'Robot w lewo', 'category': 'Robot'},
            {'key': '→ / ➡️', 'action': 'Robot w prawo', 'category': 'Robot'},
            {'key': 'Esc', 'action': 'Stop robota', 'category': 'Robot'},
            {'key': 'Ctrl+Q', 'action': 'Wyloguj', 'category': 'Aplikacja'},
            {'key': 'F1', 'action': 'Pomoc', 'category': 'Aplikacja'},
            {'key': 'Del', 'action': 'Usuń dokument', 'category': 'Dokumenty'},
        ]
    
    def _build_instructions_index(self):
        return [
            {
                'title': 'Quickstart',
                'keyword': 'start uruchomienie aplikacja logowanie',
                'description': 'Szybki start - jak uruchomić aplikację'
            },
            {
                'title': 'Dodawanie Dokumentu',
                'keyword': 'nowy dokument PZ WZ dodaj',
                'description': 'Jak dodać nowy dokument do systemu'
            },
            {
                'title': 'Generowanie PDF',
                'keyword': 'pdf generuj druk dokument',
                'description': 'Jak generować PDF z dokumentów'
            },
            {
                'title': 'Generowanie Etykiet',
                'keyword': 'etykieta wysylka kod kreskowy druk',
                'description': 'Jak generować etykiety wysyłkowe'
            },
            {
                'title': 'Tworzenie Raportu',
                'keyword': 'raport analiza danych export',
                'description': 'Jak tworzyć raporty i eksportować dane'
            },
            {
                'title': 'Backup Bazy',
                'keyword': 'backup kopia zapasowa przywroc',
                'description': 'Jak tworzyć i przywracać kopie zapasowe'
            },
            {
                'title': 'Zarządzanie Użytkownikami',
                'keyword': 'uzytkownik rola uprawnienia dostep',
                'description': 'Jak zarządzać użytkownikami i rolami'
            },
            {
                'title': 'Sterowanie Robotem',
                'keyword': 'robot kontrola kierunki przod tyl lewo prawo',
                'description': 'Jak sterować robotem'
            },
        ]
    
    def search(self, query, search_type='all'):
        query = query.lower()
        results = []
        
        if search_type in ['all', 'functions']:
            for func in self.index['functions']:
                score = self._calculate_score(
                    query, 
                    f"{func['title']} {func['keyword']} {func['description']}"
                )
                if score > 0:
                    results.append({
                        'type': 'function',
                        'title': func['title'],
                        'icon': func['icon'],
                        'description': func['description'],
                        'shortcuts': func['shortcuts'],
                        'action': func['action'],
                        'score': score
                    })
        
        if search_type in ['all', 'shortcuts']:
            for shortcut in self.index['shortcuts']:
                score = self._calculate_score(
                    query,
                    f"{shortcut['key']} {shortcut['action']} {shortcut['category']}"
                )
                if score > 0:
                    results.append({
                        'type': 'shortcut',
                        'key': shortcut['key'],
                        'action': shortcut['action'],
                        'category': shortcut['category'],
                        'score': score
                    })
        
        if search_type in ['all', 'instructions']:
            for instruction in self.index['instructions']:
                score = self._calculate_score(
                    query,
                    f"{instruction['title']} {instruction['keyword']} {instruction['description']}"
                )
                if score > 0:
                    results.append({
                        'type': 'instruction',
                        'title': instruction['title'],
                        'description': instruction['description'],
                        'score': score
                    })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:20]
    
    @staticmethod
    def _calculate_score(query, text):
        text = text.lower()
        score = 0
        
        if query in text:
            score += 100
        
        query_words = query.split()
        text_words = text.split()
        
        for word in query_words:
            for text_word in text_words:
                if word in text_word:
                    score += 10
                if text_word.startswith(word):
                    score += 5
        
        return score


class SearchHistory:
    
    def __init__(self):
        self.history = []
        self.max_history = 10
    
    def add(self, query):
        if query and query not in self.history:
            self.history.insert(0, query)
            self.history = self.history[:self.max_history]
    
    def get_history(self):
        return self.history
    
    def clear(self):
        self.history = []
