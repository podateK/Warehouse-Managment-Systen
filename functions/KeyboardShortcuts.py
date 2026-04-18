from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import Qt

class KeyboardShortcuts:
    
    SHORTCUTS = {
        'dashboard': {
            'key': 'Ctrl+1',
            'description': 'Przejdź do Dashboard',
            'action': 'show_main_page'
        },
        'robot_control': {
            'key': 'Ctrl+2',
            'description': 'Przejdź do Sterowania Robotem',
            'action': 'show_manual_control_page'
        },
        'documents': {
            'key': 'Ctrl+3',
            'description': 'Przejdź do Dokumentów',
            'action': 'show_dokumenty_page'
        },
        'labels': {
            'key': 'Ctrl+4',
            'description': 'Przejdź do Etykiet',
            'action': 'show_labels_page'
        },
        'reports': {
            'key': 'Ctrl+5',
            'description': 'Przejdź do Raportów',
            'action': 'show_report_page'
        },
        'settings': {
            'key': 'Ctrl+9',
            'description': 'Przejdź do Ustawień',
            'action': 'show_settings_page'
        },
        
        'new_document': {
            'key': 'Ctrl+N',
            'description': 'Nowy dokument',
            'action': 'new_document'
        },
        'delete_document': {
            'key': 'Delete',
            'description': 'Usuń dokument',
            'action': 'delete_document'
        },
        'export_document': {
            'key': 'Ctrl+E',
            'description': 'Eksportuj dokument',
            'action': 'export_document'
        },
        'print_document': {
            'key': 'Ctrl+P',
            'description': 'Drukuj',
            'action': 'print_document'
        },
        
        'search': {
            'key': 'Ctrl+F',
            'description': 'Wyszukaj',
            'action': 'open_search'
        },
        'find_next': {
            'key': 'F3',
            'description': 'Znajdź następny',
            'action': 'find_next'
        },
        
        'backup': {
            'key': 'Ctrl+Shift+B',
            'description': 'Utwórz kopię zapasową',
            'action': 'backup_database'
        },
        'refresh': {
            'key': 'F5',
            'description': 'Odśwież',
            'action': 'refresh_data'
        },
        
        'robot_stop': {
            'key': 'Esc',
            'description': 'Stop robota',
            'action': 'robot_stop'
        },
        'robot_forward': {
            'key': 'Up',
            'description': 'Robot do przodu',
            'action': 'robot_forward'
        },
        'robot_backward': {
            'key': 'Down',
            'description': 'Robot do tyłu',
            'action': 'robot_backward'
        },
        'robot_left': {
            'key': 'Left',
            'description': 'Robot w lewo',
            'action': 'robot_left'
        },
        'robot_right': {
            'key': 'Right',
            'description': 'Robot w prawo',
            'action': 'robot_right'
        },
        
        'logout': {
            'key': 'Ctrl+Q',
            'description': 'Wyloguj się',
            'action': 'logout'
        },
        'help': {
            'key': 'F1',
            'description': 'Pomoc',
            'action': 'show_help'
        },
    }
    
    @classmethod
    def get_shortcut(cls, action_id):
        shortcut_info = cls.SHORTCUTS.get(action_id, None)
        if shortcut_info:
            return shortcut_info['key']
        return None
    
    @classmethod
    def get_shortcuts_list(cls):
        shortcuts_list = []
        for action_id, info in cls.SHORTCUTS.items():
            shortcuts_list.append({
                'action': action_id,
                'key': info['key'],
                'description': info['description']
            })
        return shortcuts_list
    
    @classmethod
    def get_key_sequence(cls, action_id):
        return cls.get_shortcut(action_id)
    
    @classmethod
    def get_description(cls, action_id):
        """Get description for action"""
        shortcut_info = cls.SHORTCUTS.get(action_id, None)
        if shortcut_info:
            return shortcut_info['description']
        return action_id


class ShortcutsDialog:
    """Dialog to show available keyboard shortcuts"""
    
    @staticmethod
    def get_html_content():
        """Get HTML content for shortcuts dialog"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
                h2 { color: #0066cc; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th { background-color: #0066cc; color: white; padding: 10px; text-align: left; }
                td { padding: 8px; border-bottom: 1px solid #ddd; }
                tr:hover { background-color: #f9f9f9; }
                .key { background-color: #e0e0e0; padding: 3px 6px; border-radius: 3px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Skróty Klawiszowe</h1>
            
            <h2>Nawigacja</h2>
            <table>
                <tr><th>Skrót</th><th>Opis</th></tr>
                <tr><td><span class=\"key\">Ctrl+1</span></td><td>Dashboard</td></tr>
                <tr><td><span class=\"key\">Ctrl+2</span></td><td>Sterowanie Robotem</td></tr>
                <tr><td><span class=\"key\">Ctrl+3</span></td><td>Dokumenty</td></tr>
                <tr><td><span class=\"key\">Ctrl+4</span></td><td>Etykiety Wysyłki</td></tr>
                <tr><td><span class=\"key\">Ctrl+5</span></td><td>Raporty</td></tr>
                <tr><td><span class=\"key\">Ctrl+9</span></td><td>Ustawienia</td></tr>
            </table>
            
            <h2>Operacje na Dokumentach</h2>
            <table>
                <tr><th>Skrót</th><th>Opis</th></tr>
                <tr><td><span class=\"key\">Ctrl+N</span></td><td>Nowy dokument</td></tr>
                <tr><td><span class=\"key\">Ctrl+E</span></td><td>Eksportuj</td></tr>
                <tr><td><span class=\"key\">Ctrl+P</span></td><td>Drukuj</td></tr>
                <tr><td><span class=\"key\">Del</span></td><td>Usuń dokument</td></tr>
            </table>
            
            <h2>Wyszukiwanie i Odświeżanie</h2>
            <table>
                <tr><th>Skrót</th><th>Opis</th></tr>
                <tr><td><span class=\"key\">Ctrl+F</span></td><td>Wyszukaj</td></tr>
                <tr><td><span class=\"key\">F5</span></td><td>Odśwież</td></tr>
                <tr><td><span class=\"key\">F3</span></td><td>Znajdź następny</td></tr>
            </table>
            
            <h2>Sterowanie Robotem</h2>
            <table>
                <tr><th>Skrót</th><th>Opis</th></tr>
                <tr><td><span class=\"key\">↑</span></td><td>Robot do przodu</td></tr>
                <tr><td><span class=\"key\">↓</span></td><td>Robot do tyłu</td></tr>
                <tr><td><span class=\"key\">←</span></td><td>Robot w lewo</td></tr>
                <tr><td><span class=\"key\">→</span></td><td>Robot w prawo</td></tr>
                <tr><td><span class=\"key\">Esc</span></td><td>Stop robota</td></tr>
            </table>
            
            <h2>Aplikacja</h2>
            <table>
                <tr><th>Skrót</th><th>Opis</th></tr>
                <tr><td><span class=\"key\">Ctrl+Q</span></td><td>Wyloguj się</td></tr>
                <tr><td><span class=\"key\">F1</span></td><td>Pomoc</td></tr>
            </table>
        </body>
        </html>
        """
        return html
