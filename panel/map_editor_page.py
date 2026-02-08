from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QFont


class MapCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: black;")
        self.points = []  # each point: dict{x,y,type}

    def mousePressEvent(self, event):
        parent = self.parent()
        if parent is None:
            return
        if not getattr(parent, 'add_mode', False):
            return
        pos = event.position() if hasattr(event, 'position') else event.pos()
        x = int(pos.x())
        y = int(pos.y())
        point_type = parent.type_selector.currentData()
        new_point = {'x': x, 'y': y, 'type': point_type}
        self.points.append(new_point)
        parent.add_point_to_list(new_point)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont('Arial', 10)
        painter.setFont(font)

        for p in self.points:
            t = p['type']
            x = p['x']
            y = p['y']
            if t == 'M':
                color = QColor(66, 135, 245)  # blue
                text = 'M'
            elif t == 'H1':
                color = QColor(75, 192, 122)  # green
                text = 'H1'
            else:
                color = QColor(245, 200, 66)  # yellow
                text = 'P'

            painter.setBrush(color)
            painter.setPen(QColor(255, 255, 255))
            r = 12
            painter.drawEllipse(x - r, y - r, r * 2, r * 2)
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(QRect(x - r, y - r, r * 2, r * 2), Qt.AlignmentFlag.AlignCenter, text)


class MapEditorPage(QWidget):
    """Prosta strona do tworzenia mapy robota: czarne tło, przycisk Dodaj i typy punktów."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_mode = False

        layout = QVBoxLayout(self)

        # toolbar
        toolbar = QHBoxLayout()
        self.add_button = QPushButton("Dodaj")
        self.add_button.setCheckable(True)
        self.add_button.clicked.connect(self.toggle_add_mode)
        toolbar.addWidget(self.add_button)

        self.type_selector = QComboBox()
        self.type_selector.addItem('M (magazyn)', 'M')
        self.type_selector.addItem('H1 (home)', 'H1')
        self.type_selector.addItem('Punkt z pakunkiem', 'P')
        toolbar.addWidget(QLabel("Typ punktu:"))
        toolbar.addWidget(self.type_selector)

        self.mode_label = QLabel('Tryb: podgląd')
        toolbar.addWidget(self.mode_label)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # main area: canvas + list
        main_h = QHBoxLayout()

        self.canvas = MapCanvas(self)
        main_h.addWidget(self.canvas, stretch=3)

        self.point_list = QListWidget()
        self.point_list.setMaximumWidth(260)
        main_h.addWidget(self.point_list, stretch=1)

        layout.addLayout(main_h)

    def toggle_add_mode(self, checked): 
        self.add_mode = checked
        self.mode_label.setText('Tryb: dodawanie' if checked else 'Tryb: podgląd')
        self.add_button.setText('Dodaj (aktywny)' if checked else 'Dodaj')

    def add_point_to_list(self, point):
        t = point['type']
        label = f"{t} @ ({point['x']}, {point['y']})"
        item = QListWidgetItem(label)
        self.point_list.addItem(item)
