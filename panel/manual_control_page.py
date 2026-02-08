from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QLabel
from PyQt6.QtCore import Qt
from functions.RequestSender import RequestSender


class ManualControlPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.request_sender = RequestSender("http://192.168.18.52/cmd")

        layout = QVBoxLayout(self)

        title = QLabel("Ręczne sterowanie robotem")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout = QGridLayout()

        self.forward_button = QPushButton("Przód")
        self.forward_button.setFixedSize(100, 50)
        self.forward_button.setStyleSheet("font-size: 16px;")
        self.forward_button.clicked.connect(lambda: self.handle_action("MOVE_FORWARD"))
        grid_layout.addWidget(self.forward_button, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.left_button = QPushButton("Lewo")
        self.left_button.setFixedSize(100, 50)
        self.left_button.setStyleSheet("font-size: 16px;")
        self.left_button.clicked.connect(lambda: self.handle_action("MOVE_LEFT"))
        grid_layout.addWidget(self.left_button, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)

        self.right_button = QPushButton("Prawo")
        self.right_button.setFixedSize(100, 50)
        self.right_button.setStyleSheet("font-size: 16px;")
        self.right_button.clicked.connect(lambda: self.handle_action("MOVE_RIGHT"))
        grid_layout.addWidget(self.right_button, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.backward_button = QPushButton("Tył")
        self.backward_button.setFixedSize(100, 50)
        self.backward_button.setStyleSheet("font-size: 16px;")
        self.backward_button.clicked.connect(lambda: self.handle_action("MOVE_BACKWARD"))
        grid_layout.addWidget(self.backward_button, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.weight_up_button = QPushButton("Podnieś")
        self.weight_up_button.setFixedSize(100, 50)
        self.weight_up_button.setStyleSheet("font-size: 16px;")
        self.weight_up_button.clicked.connect(lambda: self.handle_action("ACTION_LIFT"))
        grid_layout.addWidget(self.weight_up_button, 0, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.weight_down_button = QPushButton("Opuść")
        self.weight_down_button.setFixedSize(100, 50)
        self.weight_down_button.setStyleSheet("font-size: 16px;")
        self.weight_down_button.clicked.connect(lambda: self.handle_action("ACTION_LOWER"))
        grid_layout.addWidget(self.weight_down_button, 2, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.weight_down_button = QPushButton("DIODA")
        self.weight_down_button.setFixedSize(75, 75)
        self.weight_down_button.setStyleSheet("font-size: 16px;")
        self.weight_down_button.clicked.connect(lambda: self.handle_action("STOP"))
        grid_layout.addWidget(self.weight_down_button, 5, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(grid_layout)

    def handle_action(self, action):
        print(f"Kliknięto: {action}")
        self.request_sender.send_request(action)