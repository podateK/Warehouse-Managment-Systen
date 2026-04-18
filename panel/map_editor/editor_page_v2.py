from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox,
    QDialog, QSpinBox, QComboBox, QFormLayout, QLineEdit, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .canvas_new import MapCanvasLinear
from .route_selector import RouteOrderPanelRight
from functions.FloatingMessage import FloatingMessage
from functions.RobotStatusManager import RobotStatusManager


class BranchEditorDialog(QDialog):
    
    def __init__(self, parent=None, branch=None, line_num=None):
        super().__init__(parent)
        self.setWindowTitle("Edytuj Gałąź")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #0066cc;
            }
        """)
        
        self.branch = branch or {}
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Edytuj parametry gałęzi")
        title.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a3a52;")
        layout.insertRow(0, title)
        layout.insertRow(1, QLabel())  # Spacer
        
        line_label = QLabel("📏 Numer linii:")
        line_label.setStyleSheet("color: #374151;")
        self.line_spin = QSpinBox()
        self.line_spin.setMinimum(1)
        self.line_spin.setMaximum(99)
        self.line_spin.setValue(line_num if line_num else self.branch.get('line_num', 1))
        layout.addRow(line_label, self.line_spin)
        
        dir_label = QLabel("🧭 Kierunek:")
        dir_label.setStyleSheet("color: #374151;")
        self.dir_combo = QComboBox()
        self.dir_combo.addItems(['⬅️ Lewo (LEFT)', '➡️ Prawo (RIGHT)'])
        current_dir = self.branch.get('direction', 'LEFT')
        idx = 0 if 'LEFT' in current_dir else 1
        self.dir_combo.setCurrentIndex(idx)
        layout.addRow(dir_label, self.dir_combo)
        
        name_label = QLabel("🏷️ Nazwa punktu:")
        name_label.setStyleSheet("color: #374151;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("np. M1, M2, P1")
        self.name_edit.setText(self.branch.get('name', ''))
        layout.addRow(name_label, self.name_edit)
        
        type_label = QLabel("📦 Typ punktu:")
        type_label.setStyleSheet("color: #374151;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(['🟢 M (Magazyn)', '🟣 H1 (Home)', '🟠 P (Paczka)'])
        type_val = self.branch.get('point_type', 'M')
        if type_val == 'H1':
            self.type_combo.setCurrentIndex(1)
        elif type_val == 'P':
            self.type_combo.setCurrentIndex(2)
        else:
            self.type_combo.setCurrentIndex(0)
        layout.addRow(type_label, self.type_combo)
        
        layout.insertRow(layout.rowCount(), QLabel())  # Spacer

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("✅ Zapisz")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("❌ Anuluj")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
    
    def get_data(self):
        """Return edited branch data."""
        dir_text = self.dir_combo.currentText()
        direction = 'LEFT' if 'LEFT' in dir_text else 'RIGHT'
        
        type_text = self.type_combo.currentText()
        if 'Home' in type_text:
            ptype = 'H1'
        elif 'Paczka' in type_text:
            ptype = 'P'
        else:
            ptype = 'M'
        
        return {
            'line_num': self.line_spin.value(),
            'direction': direction,
            'name': self.name_edit.text().strip() or 'P',
            'point_type': ptype
        }


class MapEditorPageV2(QWidget):
    """Integrated map editor: visual canvas on left, route selector on right."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        
        header_label = QLabel("🗺️ Edytor Mapy Robota")
        header_font = QFont('Segoe UI', 14, QFont.Weight.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #1a3a52;")
        left_layout.addWidget(header_label)
        
        instructions = QLabel(
            "💡 INSTRUKCJA OBSŁUGI:\n"
            "1. Kliknij na centrum (niebieska linia) aby dodać nową gałąź\n"
            "2. Wybierz kierunek (lewo/prawo) i typ punktu\n"
            "3. Kliknij na punkt aby wysłać 1 request AUTO do ESP32\n"
            "4. Ctrl+klik na punkt aby edytować\n"
            "5. Prawy przycisk myszy na punkt = usuń\n"
            "6. Najechaj kursorem aby podświetlić routes"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        instructions.setWordWrap(True)
        instructions.setMaximumWidth(560)
        instructions.setMaximumHeight(110)
        instructions.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #fef3c7;
                color: #78350f;
                padding: 8px;
                border-radius: 6px;
                border-left: 4px solid #f59e0b;
                font-family: 'Segoe UI';
                font-size: 9px;
                line-height: 1.4;
            }
        """)
        left_layout.addWidget(instructions)
        
        self.canvas = MapCanvasLinear(self)
        self.canvas.on_create_requested = self.on_canvas_create_branch
        self.canvas.on_edit_requested = self.on_canvas_edit_branch
        
        left_layout.addWidget(self.canvas)
        
        btn_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑️ Wyczyść mapę")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        self.clear_btn.clicked.connect(self.on_clear_map)
        btn_layout.addWidget(self.clear_btn)

        self.refresh_status_btn = QPushButton("🔄 Odśwież status robota")
        self.refresh_status_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.refresh_status_btn.clicked.connect(self.on_refresh_robot_status)
        btn_layout.addWidget(self.refresh_status_btn)

        self.robot_status_label = QLabel("Status robota: ---")
        self.robot_status_label.setStyleSheet("color: #374151; font-weight: bold;")
        btn_layout.addWidget(self.robot_status_label)
        
        btn_layout.addStretch()
        left_layout.addLayout(btn_layout)
        
        main_layout.addLayout(left_layout, stretch=3)
        
        self.route_panel = RouteOrderPanelRight(self)
        main_layout.addWidget(self.route_panel, stretch=1)
        
        self.setLayout(main_layout)
        
        self.canvas.mousePressEvent_original = self.canvas.mousePressEvent
        self.canvas.mousePressEvent = self.canvas_mouse_press
        self.right_click_branch = None

        self.robot_status_manager = RobotStatusManager()
        self.robot_status_manager.status_changed.connect(self.on_robot_status_changed)
        self.on_robot_status_changed(self.robot_status_manager.get_status())

        self.on_refresh_robot_status()
    
    def canvas_mouse_press(self, event):
        """Handle mouse clicks on canvas."""
        pos = event.position() if hasattr(event, 'position') else event.pos()
        x = int(pos.x())
        y = int(pos.y())
        
        if event.button() == Qt.MouseButton.RightButton:
            idx = self.canvas._get_branch_at(x, y)
            if idx is not None:
                self.canvas.branches.pop(idx)
                self.canvas.update()
                self.route_panel.refresh_route_list()
            return
        
        idx = self.canvas._get_branch_at(x, y)
        if idx is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.on_canvas_edit_branch(idx)
            else:
                self.route_panel.send_auto_for_branch(idx)
        else:
            if abs(x - self.canvas.center_x) < 40:
                line_num = round((y - self.canvas.top_margin) / self.canvas.line_height)
                if line_num >= 1:
                    self.on_canvas_create_branch(line_num)
    
    def on_canvas_create_branch(self, line_num):
        """Create new branch at specified line."""
        dialog = BranchEditorDialog(self, line_num=line_num)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.canvas.add_branch(
                line_num=data['line_num'],
                direction=data['direction'],
                name=data['name'],
                point_type=data['point_type']
            )
            
            if data['name'] and data['name'] != 'H1':
                if data['name'] not in self.route_panel.route:
                    self.route_panel.route.append(data['name'])
                    self.route_panel.set_branch_info(
                        data['name'],
                        data['line_num'],
                        data['direction']
                    )
    
    def on_canvas_edit_branch(self, branch_idx):
        """Edit existing branch."""
        if branch_idx >= 0 and branch_idx < len(self.canvas.branches):
            branch = self.canvas.branches[branch_idx]
            dialog = BranchEditorDialog(self, branch)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                old_name = branch.get('name')
                
                self.canvas.update_branch(branch_idx, data)
                
                if old_name and old_name in self.route_panel.route and old_name != data['name']:
                    idx = self.route_panel.route.index(old_name)
                    self.route_panel.route[idx] = data['name']
                
                if data['name'] and data['name'] != 'H1':
                    self.route_panel.set_branch_info(
                        data['name'],
                        data['line_num'],
                        data['direction']
                    )
    
    def on_clear_map(self):
        """Clear all branches from map."""
        reply = QMessageBox.question(
            self,
            "⚠️ Wyczyść mapę",
            "Czy na pewno wyczyścić wszystkie gałęzie?\n\nTej operacji nie można cofnąć!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.branches.clear()
            self.canvas.update()
            self.route_panel.route.clear()
            self.route_panel.point_branches.clear()
            self.route_panel.refresh_route_list()

    def on_refresh_robot_status(self):
        """Refresh robot status manually."""
        status = self.robot_status_manager.refresh_now()
        if status == "Online":
            FloatingMessage.display(self, "Robot: Online", duration=1800)
        else:
            self.robot_status_label.setText("Status robota: Offline")
            FloatingMessage.display(self, "Robot: Offline", duration=1800)

    def on_robot_status_changed(self, status):
        """Sync status label with global robot status manager."""
        if status == "Online":
            self.robot_status_label.setText("Status robota: Online")
            self.robot_status_label.setStyleSheet("color: #059669; font-weight: bold;")
        else:
            self.robot_status_label.setText("Status robota: Offline")
            self.robot_status_label.setStyleSheet("color: #dc2626; font-weight: bold;")
