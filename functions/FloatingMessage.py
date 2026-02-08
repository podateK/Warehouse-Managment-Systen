from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect


class SlidingBar(QWidget):
    def __init__(self, parent=None, duration=3000):
        super().__init__(parent)
        self.setFixedHeight(10)
        self.setStyleSheet("background-color: white;")
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(duration)
        self.animation.finished.connect(self.deleteLater)

    def start_animation(self):
        parent_width = self.parent().width()
        self.setGeometry(0, self.parent().height() - self.height(), parent_width, self.height())
        self.animation.setStartValue(QRect(0, self.parent().height() - self.height(), 0, self.height()))
        self.animation.setEndValue(QRect(0, self.parent().height() - self.height(), parent_width, self.height()))
        self.animation.start()


class FloatingMessage(QWidget):
    def __init__(self, message, parent=None, duration=3000):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: purple;
                color: black;
                border-radius: 10px;
            }
        """)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("font-size: 16px;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)

        self.sliding_bar = SlidingBar(self, duration)
        layout.addWidget(self.sliding_bar)

        self.adjustSize()
        self.resize(self.width() + 50, self.height() + 70)
        if parent:
            self.move(parent.width() - self.width() - 30, 30)

        self.timer = QTimer(self)
        self.timer.setInterval(duration)
        self.timer.timeout.connect(self.close)
        self.timer.start()

    def show_message(self):
        self.sliding_bar.start_animation()
        self.show()

    @staticmethod
    def display(parent, message, duration=3000):
        floating_message = FloatingMessage(message, parent, duration)
        floating_message.show_message()