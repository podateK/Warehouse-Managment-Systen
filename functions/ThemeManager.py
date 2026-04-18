from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

class ThemeManager:
    
    LIGHT_THEME = {
        'bg_main': '#ffffff',
        'bg_secondary': '#f5f5f5',
        'bg_sidebar': '#1a3a52',
        'bg_header': '#0f2437',
        'text_primary': '#000000',
        'text_secondary': '#666666',
        'text_light': '#e2e8f0',
        'accent': '#0066cc',
        'accent_green': '#10b981',
        'accent_orange': '#f59e0b',
        'accent_red': '#ef4444',
        'border': '#e0e0e0',
        'hover': '#f0f0f0',
    }
    
    DARK_THEME = {
        'bg_main': '#1a1a1a',
        'bg_secondary': '#2d2d2d',
        'bg_sidebar': '#0f1419',
        'bg_header': '#080c0f',
        'text_primary': '#ffffff',
        'text_secondary': '#b0b0b0',
        'text_light': '#e2e8f0',
        'accent': '#00a3ff',
        'accent_green': '#10b981',
        'accent_orange': '#f59e0b',
        'accent_red': '#ef4444',
        'border': '#404040',
        'hover': '#3d3d3d',
    }
    
    current_theme = 'light'
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_theme(cls):
        """Get current theme colors"""
        if cls.current_theme == 'dark':
            return cls.DARK_THEME
        return cls.LIGHT_THEME
    
    @classmethod
    def get_color(cls, key):
        """Get specific color from current theme"""
        theme = cls.get_theme()
        return theme.get(key, '#000000')
    
    @classmethod
    def toggle_theme(cls):
        """Toggle between light and dark theme"""
        cls.current_theme = 'dark' if cls.current_theme == 'light' else 'light'
        return cls.current_theme
    
    @classmethod
    def set_theme(cls, theme_name):
        """Set specific theme"""
        if theme_name in ['light', 'dark']:
            cls.current_theme = theme_name
            return True
        return False
    
    @classmethod
    def get_stylesheet(cls):
        """Get comprehensive stylesheet for current theme"""
        theme = cls.get_theme()
        
        return f"""
            QMainWindow, QWidget {{
                background-color: {theme['bg_main']};
                color: {theme['text_primary']};
            }}
            
            QDockWidget {{
                background-color: {theme['bg_sidebar']};
                border: none;
            }}
            
            QLabel {{
                color: {theme['text_primary']};
            }}
            
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 2px solid {theme['accent']};
            }}
            
            QPushButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['accent_green']};
            }}
            
            QPushButton:pressed {{
                background-color: #005aa6;
            }}
            
            QFrame {{
                background-color: {theme['bg_main']};
                color: {theme['text_primary']};
            }}
            
            QTabWidget, QTabBar {{
                background-color: {theme['bg_main']};
                color: {theme['text_primary']};
            }}
            
            QTabBar::tab {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                padding: 5px 15px;
                border-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme['accent']};
                color: white;
            }}
        """
