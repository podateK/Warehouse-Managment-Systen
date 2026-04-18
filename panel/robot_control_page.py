
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QLabel, QHBoxLayout, QSlider, QMessageBox
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from functions.RequestSender import RequestSender
from functions.RobotStatusManager import RobotStatusManager


class _ActionWorker(QObject):
    finished = pyqtSignal(str, bool, str)

    def __init__(self, sender, action):
        super().__init__()
        self.sender = sender
        self.action = action

    def run(self):
        success, message = self.sender.send_request(self.action)
        self.finished.emit(self.action, success, message)


class RobotControlPage(QWidget):
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
        self._action_threads = []
        self._offline_warning_shown = False

        self.robot_status_manager = RobotStatusManager()
        self.robot_status_manager.status_changed.connect(self.on_robot_status_changed)
        self.robot_status_manager.drive_mode_changed.connect(self.on_drive_mode_changed)
        self.robot_is_online = self.robot_status_manager.is_online()
        self.warehouses = {
            "H1": ["-", "RIGHT", "LEFT", "2LEFT", "3LEFT", "FORWARD"],
            "P1": ["LEFT", "-", "RIGHT-LEFT", "RIGHT-2LEFT", "RIGHT-3LEFT", "RIGHT"],
            "W1": ["FORWARD", "LEFT", "3RIGHT", "2RIGHT", "RIGHT", "-"],
            "M1": ["RIGHT", "RIGHR-LEFT", "-", "LEFT-LEFT", "LEFT-2RIGHT", "LEFT"],
            "M2": ["RIGHT", "RIGHT-LEFT", "RIGHT-RIGHT", "-", "LEFT-RIGHT", "LEFT"],
            "M3": ["RIGHT", "RIGHT_LEFT", "RIGHT-2RIGHT", "RIGHT-RIGHT", "-", "LEFT"],
        }

        self.moves = [move for seq in self.warehouses.values() for move in seq if move != "-"]

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

        self.info_label = QLabel("Status: 🟢 Gotowy | Steruj robotem w poniżej za pomocą przycisków")
        self.info_label.setStyleSheet("color: #10b981; font-weight: bold; padding: 10px; background-color: white; border-radius: 4px;")
        layout.addWidget(self.info_label)

        toggle_layout = QHBoxLayout()
        toggle_layout.setContentsMargins(0, 10, 0, 10)

        toggle_label = QLabel("Włączyć Sterowanie Manualne")
        toggle_label.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        toggle_label.setStyleSheet("color: #374151;")
        toggle_layout.addWidget(toggle_label)

        toggle_layout.addSpacing(10)

        self.control_slider = QSlider(Qt.Orientation.Horizontal)
        self.control_slider.setMinimum(0)
        self.control_slider.setMaximum(1)
        self.control_slider.setValue(0)
        self.control_slider.setMaximumWidth(60)
        self.control_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #d1d5db;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #ef4444;
                width: 24px;
                margin: -8px 0px;
                border-radius: 12px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #dc2626;
            }
        """)
        self.control_slider.valueChanged.connect(self.on_slider_changed)
        toggle_layout.addWidget(self.control_slider)

        self.toggle_status = QLabel("OFF")
        self.toggle_status.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        self.toggle_status.setStyleSheet("color: #ef4444;")
        toggle_layout.addWidget(self.toggle_status)

        toggle_layout.addStretch()
        layout.addLayout(toggle_layout)

        control_box = QWidget()
        control_box.setStyleSheet("background-color: white; border-radius: 8px; padding: 30px;")
        grid_layout = QGridLayout(control_box)
        grid_layout.setSpacing(15)

        move_button_style = """
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 0px;
                min-height: 80px;
                min-width: 80px;
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
                font-size: 12px;
                padding: 0px;
                min-height: 70px;
                min-width: 100px;
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
                font-size: 15px;
                min-height: 100px;
                min-width: 100px;
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
        grid_layout.addWidget(self.stop_button, 1, 1)

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

    def _apply_slider_style(self, is_manual):
        color = "#10b981" if is_manual else "#ef4444"
        hover = "#059669" if is_manual else "#dc2626"
        self.control_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background-color: #d1d5db;
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background-color: {color};
                width: 24px;
                margin: -8px 0px;
                border-radius: 12px;
            }}
            QSlider::handle:horizontal:hover {{
                background-color: {hover};
            }}
        """)

    def _set_controls_enabled(self, enabled):
        self.forward_button.setEnabled(enabled)
        self.left_button.setEnabled(enabled)
        self.right_button.setEnabled(enabled)
        self.backward_button.setEnabled(enabled)
        self.weight_up_button.setEnabled(enabled)
        self.weight_down_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)

    def on_slider_changed(self, value):
        """Handle slider position change to enable/disable robot control"""
        manual_selected = value == 1
        is_enabled = manual_selected and self.robot_is_online  # Check both slider AND robot status
        
        if value == 1 and not self.robot_is_online:
            self.toggle_status.setText("OFF")
            self.toggle_status.setStyleSheet("color: #ef4444;")
            self.control_slider.blockSignals(True)
            self.control_slider.setSliderPosition(0)  # Reset slider
            self.control_slider.blockSignals(False)
            self._apply_slider_style(False)
            QMessageBox.warning(self, "⚠️ Robot offline", "Robot jest wyłączony. Nie można włączyć sterowania.")
            return

        if is_enabled:
            self.toggle_status.setText("ON")
            self.toggle_status.setStyleSheet("color: #10b981;")
            self._apply_slider_style(True)
        else:
            self.toggle_status.setText("OFF")
            self.toggle_status.setStyleSheet("color: #ef4444;")
            self._apply_slider_style(False)
        
        self._set_controls_enabled(is_enabled)

        if not self.robot_is_online:
            return

        success, message = self.robot_status_manager.set_manual_mode(is_enabled)
        if not success:
            QMessageBox.warning(self, "⚠️ Błąd trybu jazdy", f"Nie udało się wysłać trybu {self.robot_status_manager.get_drive_mode()}: {message}")

    def handle_action(self, action):
        request_url = self.request_sender.build_send_request_url(action)
        print(f"Kliknięto: {action} | REQUEST: GET {request_url}", flush=True)

        manual_enabled = self.control_slider.value() == 1
        if not self.robot_is_online and action != "STOP":
            print(f"⏭ ACTION skipped: {action} | reason=robot_offline", flush=True)
            if not self._offline_warning_shown:
                self._offline_warning_shown = True
                QMessageBox.warning(self, "⚠️ Robot offline", "Robot jest wyłączony lub niedostępny.")
            return

        if not manual_enabled and action != "STOP":
            print(f"⏭ ACTION skipped: {action} | reason=manual_mode_off", flush=True)
            return

        thread = QThread(self)
        worker = _ActionWorker(self.request_sender, action)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._on_action_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._cleanup_action_thread(thread))

        self._action_threads.append(thread)
        thread.start()

    def _on_action_finished(self, action, success, message):
        print(f"📨 ACTION result: success={success} | {message}")
        if success:
            self._offline_warning_shown = False
            return

        if action != "STOP":
            QMessageBox.warning(self, "⚠️ Błąd sterownika", message)

    def _cleanup_action_thread(self, finished_thread):
        self._action_threads = [t for t in self._action_threads if t is not finished_thread]

    def on_robot_status_changed(self, status):
        """Update info label based on robot status"""
        self.robot_is_online = (status == "Online")
        
        if self.robot_is_online:
            self._offline_warning_shown = False
            self.info_label.setText("Status: 🟢 Gotowy | Steruj robotem za pomocą przycisków poniżej")
            self.info_label.setStyleSheet("color: #10b981; font-weight: bold; padding: 10px; background-color: white; border-radius: 4px;")
            self.control_slider.setEnabled(True)
            self._set_controls_enabled(self.control_slider.value() == 1)
        else:
            self.info_label.setText("Status: 🔴 ROBOT OFFLINE | Urządzenie jest wyłączone lub niedostępne")
            self.info_label.setStyleSheet("color: #ef4444; font-weight: bold; padding: 10px; background-color: #fff5f5; border-radius: 4px;")
            
            self._set_controls_enabled(False)
            self.control_slider.setEnabled(False)

    def on_drive_mode_changed(self, mode):
        """Keep local UI synced with global drive mode variable."""
        should_be_on = mode == "MANUAL"
        if self.control_slider.value() != (1 if should_be_on else 0):
            self.control_slider.blockSignals(True)
            self.control_slider.setValue(1 if should_be_on else 0)
            self.control_slider.blockSignals(False)

        if should_be_on:
            self.toggle_status.setText("ON")
            self.toggle_status.setStyleSheet("color: #10b981;")
            self._apply_slider_style(True)
        else:
            self.toggle_status.setText("OFF")
            self.toggle_status.setStyleSheet("color: #ef4444;")
            self._apply_slider_style(False)

        self._set_controls_enabled(should_be_on and self.robot_is_online)

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

ManualControlPage = RobotControlPage
