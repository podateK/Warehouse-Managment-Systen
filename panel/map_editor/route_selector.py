"""Panel do zaznaczania i wysyłania tras między punktami."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QSpinBox, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from functions.RequestSender import RequestSender
from functions.RobotStatusManager import RobotStatusManager


class RouteOrderPanelRight(QWidget):
    """Right panel for selecting route waypoints and sending with line info."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        self.request_sender = RequestSender()
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("📍 Plan Trasy"))
        
        self.start_label = QLabel("🏠 Start: H1")
        self.start_label.setStyleSheet("font-weight: bold; color: green;")
        layout.addWidget(self.start_label)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("Dostępne punkty:"))
        self.points_list = QListWidget()
        self.points_list.setMaximumHeight(250)
        layout.addWidget(self.points_list)
        
        points_btn_layout = QHBoxLayout()
        self.add_point_btn = QPushButton("➕ Dodaj")
        self.add_point_btn.clicked.connect(self.on_add_point)
        points_btn_layout.addWidget(self.add_point_btn)
        
        self.remove_point_btn = QPushButton("❌ Usuń")
        self.remove_point_btn.clicked.connect(self.on_remove_point)
        points_btn_layout.addWidget(self.remove_point_btn)
        
        layout.addLayout(points_btn_layout)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("Trasa (kolejność):"))
        self.route_list = QListWidget()
        self.route_list.setMaximumHeight(300)
        layout.addWidget(self.route_list)
        
        route_btn_layout = QHBoxLayout()
        self.move_up_btn = QPushButton("⬆ Wyżej")
        self.move_up_btn.clicked.connect(self.on_move_up)
        route_btn_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("⬇ Niżej")
        self.move_down_btn.clicked.connect(self.on_move_down)
        route_btn_layout.addWidget(self.move_down_btn)
        
        layout.addLayout(route_btn_layout)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("Linia skrętu:"))
        self.line_num_label = QLabel("Wybierz punkt trasy")
        layout.addWidget(self.line_num_label)
        
        layout.addWidget(QLabel("Kierunek:"))
        self.direction_label = QLabel("---")
        layout.addWidget(self.direction_label)
        
        layout.addSpacing(15)
        self.send_route_btn = QPushButton("🚀 WYŚLIJ TRASĘ")
        self.send_route_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;"
        )
        self.send_route_btn.clicked.connect(self.on_send_route)
        layout.addWidget(self.send_route_btn)
        
        layout.addStretch()
        
        self.route = []  # List of point names in order
        self.point_branches = {}  # point_name -> {line_num, direction}
        
        self.refresh_points_list()

    def _sorted_branches(self):
        """Return branches sorted by line number, then original insertion order."""
        if not self.parent_editor or not hasattr(self.parent_editor, 'canvas'):
            return []
        branches = list(getattr(self.parent_editor.canvas, 'branches', []))
        indexed = list(enumerate(branches))
        indexed.sort(key=lambda x: (int(x[1].get('line_num', 0)), x[0]))
        return indexed

    def _build_auto_payload_for_branch(self, branch_idx):
        """Build a single AUTO payload for route prefix up to selected point."""
        ordered = self._sorted_branches()
        if not ordered:
            return {"command": "AUTO", "way": [], "turn": []}

        prefix = []
        for idx, branch in ordered:
            prefix.append((idx, branch))
            if idx == branch_idx:
                break

        side_counts = {"LEFT": 0, "RIGHT": 0}
        way = []
        turn = []

        for _, branch in prefix:
            direction = str(branch.get('direction', 'LEFT')).upper()
            if direction not in side_counts:
                continue

            side_counts[direction] += 1
            side = 'left' if direction == 'LEFT' else 'right'
            way.extend([side, str(side_counts[direction])])
            turn.append(side)

        return {
            "command": "AUTO",
            "way": way,
            "turn": turn,
        }

    def send_auto_for_branch(self, branch_idx):
        """Send a single AUTO request payload for selected branch."""
        payload = self._build_auto_payload_for_branch(branch_idx)
        print(f"📡 AUTO payload: {payload}")
        success, message = self.request_sender.send_json(payload)
        print(f"📨 AUTO result: success={success} | {message}")
        if success:
            RobotStatusManager().set_automatic_mode_local()
    
    def refresh_points_list(self):
        """Refresh available points list from mapa."""
        try:
            from tools.route_logger import mapa
            
            available = []
            for name in mapa.keys():
                if name != 'H1':  # Skip home point
                    available.append(name)
            
            self.points_list.clear()
            for point in sorted(available):
                item = QListWidgetItem(point)
                item.setData(Qt.ItemDataRole.UserRole, point)
                self.points_list.addItem(item)
        except Exception as e:
            print(f"Error refreshing points: {e}")
    
    def on_add_point(self):
        """Add selected point to route."""
        selected_items = self.points_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            point_name = item.data(Qt.ItemDataRole.UserRole)
            if point_name not in self.route:
                self.route.append(point_name)
        
        self.refresh_route_list()
    
    def on_remove_point(self):
        """Remove selected point from route."""
        selected_items = self.route_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            point_name = item.data(Qt.ItemDataRole.UserRole)
            if point_name in self.route:
                self.route.remove(point_name)
        
        self.refresh_route_list()
    
    def on_move_up(self):
        """Move selected point up in route."""
        current_row = self.route_list.currentRow()
        if current_row > 0:
            self.route[current_row], self.route[current_row - 1] = \
                self.route[current_row - 1], self.route[current_row]
            self.refresh_route_list()
            self.route_list.setCurrentRow(current_row - 1)
    
    def on_move_down(self):
        """Move selected point down in route."""
        current_row = self.route_list.currentRow()
        if current_row >= 0 and current_row < len(self.route) - 1:
            self.route[current_row], self.route[current_row + 1] = \
                self.route[current_row + 1], self.route[current_row]
            self.refresh_route_list()
            self.route_list.setCurrentRow(current_row + 1)
    
    def refresh_route_list(self):
        """Update route list display."""
        self.route_list.clear()
        
        h1_item = QListWidgetItem("🏠 H1 (START)")
        h1_item.setData(Qt.ItemDataRole.UserRole, 'H1')
        h1_item.setBackground(QColor(144, 238, 144))  # Light green
        self.route_list.addItem(h1_item)
        
        for i, point_name in enumerate(self.route):
            item_text = f"{i+1}. {point_name}"
            
            if point_name in self.point_branches:
                branch_info = self.point_branches[point_name]
                line_num = branch_info.get('line_num', '?')
                direction = branch_info.get('direction', '?')
                item_text += f" @ Linia {line_num} ({direction})"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, point_name)
            self.route_list.addItem(item)
    
    def set_branch_info(self, point_name, line_num, direction):
        """Set line number and direction for a point (from canvas)."""
        self.point_branches[point_name] = {
            'line_num': line_num,
            'direction': direction
        }
        self.refresh_route_list()
    
    def on_send_route(self):
        """Send route commands to Arduino."""
        if not self.route:
            print("❌ Brak punktów w trasie!")
            return
        
        try:
            from tools.route_logger import Way
            
            print(f"\n🚀 Wysyłam trasę: H1 → {' → '.join(self.route)}\n")
            
            RS = self.request_sender
            
            import time
            current = 'H1'
            
            for point_name in self.route:
                branch_info = self.point_branches.get(point_name, {})
                line_num = branch_info.get('line_num')
                
                print(f"\n📤 {current} → {point_name}", end='')
                if line_num:
                    print(f" at line {line_num}")
                else:
                    print()
                
                Way(current, point_name, line_num=line_num, request_sender=RS, leg_delay=0.2)
                current = point_name
                time.sleep(0.5)
            
            print(f"\n✅ Trasa wysłana!\n")
        
        except Exception as e:
            print(f"❌ Błąd wysyłania: {e}")


class RouteSelectorDialog(QWidget):
    """Standalone widget for route selection with branches."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plan Trasy")
        self.setMinimumSize(300, 600)
        
        layout = QVBoxLayout(self)
        layout.addWidget(RouteOrderPanelRight(self))
        
        self.setLayout(layout)
