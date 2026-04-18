from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from functions.RequestSender import RequestSender


class ManualControlPage(QWidget):
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

        self.request_sender = RequestSender()  # Uses ConfigManager for URL
        self.warehouses = {
            "H1": ["-", "RIGHT", "LEFT", "2LEFT", "3LEFT", "FORWARD"],
            "P1": ["LEFT", "-", "RIGHT-LEFT", "RIGHT-2LEFT", "RIGHT-3LEFT", "RIGHT"],
            "W1": ["FORWARD", "LEFT", "3RIGHT", "2RIGHT", "RIGHT", "-"],
            "M1": ["RIGHT", "RIGHR-LEFT", "-", "LEFT-LEFT", "LEFT-2RIGHT", "LEFT"],
            "M2": ["RIGHT", "RIGHT-LEFT", "RIGHT-RIGHT", "-", "LEFT-RIGHT", "LEFT"],
            "M3": ["RIGHT", "RIGHT_LEFT", "RIGHT-2RIGHT", "RIGHT-RIGHT", "-", "LEFT"],
        }

        self.moves = [
            move for seq in self.warehouses.values() for move in seq if move != "-"
        ]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("🤖 Ręczne Sterowanie Robotem")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a3a52;")
        layout.addWidget(title)
        
        separator = QLabel()
        separator.setStyleSheet("background-color: #d1d5db; min-height: 1px;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        info_label = QLabel("Status: 🟢 Gotowy | Steruj robotem w poniżej za pomocą przycisków")
        info_label.setStyleSheet("color: #10b981; font-weight: bold; padding: 10px; background-color: white; border-radius: 4px;")
        layout.addWidget(info_label)

        control_box = QWidget()
        control_box.setStyleSheet("background-color: white; border-radius: 8px; padding: 20px;")
        grid_layout = QGridLayout(control_box)
        grid_layout.setSpacing(10)

        move_button_style = """
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 0px;
                min-height: 70px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """
        
        action_button_style = """
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                padding: 0px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """
        
        stop_button_style = """
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-height: 80px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """

        self.forward_button = QPushButton("⬆️\nPrzód")
        self.forward_button.setStyleSheet(move_button_style)
        self.forward_button.pressed.connect(lambda: self.handle_action("FORWARD"))
        self.forward_button.released.connect(lambda: self.handle_action("STOP"))
        grid_layout.addWidget(self.forward_button, 0, 1)

        self.left_button = QPushButton("⬅️\nLewo")
        self.left_button.setStyleSheet(move_button_style)
        self.left_button.pressed.connect(lambda: self.handle_action("MOVE_LEFT"))
        self.left_button.released.connect(lambda: self.handle_action("STOP"))
        grid_layout.addWidget(self.left_button, 1, 0)

        self.stop_button = QPushButton("⏹️\nSTOP")
        self.stop_button.setStyleSheet(stop_button_style)
        self.stop_button.clicked.connect(lambda: self.handle_action("STOP"))
        grid_layout.addWidget(self.stop_button, 0, 1, 2, 1)
        
        self.right_button = QPushButton("➡️\nPrawo")
        self.right_button.setStyleSheet(move_button_style)
        self.right_button.pressed.connect(lambda: self.handle_action("MOVE_RIGHT"))
        self.right_button.released.connect(lambda: self.handle_action("STOP"))
        grid_layout.addWidget(self.right_button, 1, 2)

        self.backward_button = QPushButton("⬇️\nTył")
        self.backward_button.setStyleSheet(move_button_style)
        self.backward_button.pressed.connect(lambda: self.handle_action("BACK"))
        self.backward_button.released.connect(lambda: self.handle_action("STOP"))
        grid_layout.addWidget(self.backward_button, 2, 1)

        self.weight_up_button = QPushButton("🔼 PODNIEŚ")
        self.weight_up_button.setStyleSheet(action_button_style)
        self.weight_up_button.pressed.connect(lambda: self.handle_action("ACTION_LIFT"))
        self.weight_up_button.released.connect(lambda: self.handle_action("STOP"))
        grid_layout.addWidget(self.weight_up_button, 0, 3)

        self.weight_down_button = QPushButton("🔽 OPUŚĆ")
        self.weight_down_button.setStyleSheet(action_button_style)
        self.weight_down_button.pressed.connect(lambda: self.handle_action("ACTION_LOWER"))
        self.weight_down_button.released.connect(lambda: self.handle_action("STOP"))
        grid_layout.addWidget(self.weight_down_button, 1, 3)

        layout.addWidget(control_box)
        layout.addStretch()

    def handle_action(self, action):
        print(f"Kliknięto: {action}")
        self.request_sender.send_request(action)

    def get_moves(self):
        return list(self.moves)

    def get_moves_for_warehouse(self, name):
        """Zwraca listę ruchów dla podanej nazwy magazynu (np. 'H1')."""
        seq = self.warehouses.get(name)
        if seq is None:
            return []
        return [m for m in seq if m != "-"]

    def notify_map_changed(self, map_moves=None):
        """Wywołać po stworzeniu nowych rzeczy na mapie.

        - Loguje listę ruchów wygenerowaną przez mapę (jeśli przekazana).
        - ZAWSZE używa i wysyła zhardcodowanej listy `self.moves`.
        """
        print("Map changed. Moves from map:", map_moves)
        print("Using hardcoded moves (will be sent):", self.moves)

        for action in self.moves:
            try:
                print(f"Wysyłam (hardcoded): {action}")
                self.request_sender.send_request(action)
            except Exception as e:
                print(f"Błąd podczas wysyłania akcji {action}: {e}")
