from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRect, QPointF
import math


class MapCanvas(QWidget):
    """Canvas that stores and draws points. It emits callbacks to the parent when
    the user clicks an empty area or an existing point.
    The parent should set `on_create_requested(pos)` and `on_edit_requested(index, pos)` callbacks.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: black;")
        self.points = []  # list of dicts: {x,y,type,name}

        self.connections = []

        self.level_height = 100  # pixels between horizontal levels
        self.top_margin = 60
        self.left_margin = 60
        self.col_spacing = 120
        self.direction_offset = 60  # horizontal offset when routing up/down

        self.auto_layout = True  # whether to auto-arrange blocks by level
        self.on_create_requested = None
        self.on_edit_requested = None

    def add_point(self, point):
        if 'level' in point:
            level = int(point['level'])
        else:
            if 'y' in point:
                level = round((point['y'] - self.top_margin) / self.level_height)
            else:
                level = 0
        point['level'] = int(level)
        
        # Snap X to nearest existing point's X if within snap distance
        snap_distance = 30
        if 'x' in point and len(self.points) > 0:
            existing_xs = [p.get('x', 0) for p in self.points]
            nearest_x = min(existing_xs, key=lambda x: abs(x - point['x']))
            if abs(nearest_x - point['x']) <= snap_distance:
                point['x'] = nearest_x
        
        self.points.append(point)
        if self.auto_layout:
            self.layout_levels()
        self.update()

    def update_point(self, index, point):
        if 0 <= index < len(self.points):
            if 'level' not in point and 'y' in point:
                point['level'] = round((point['y'] - self.top_margin) / self.level_height)
            self.points[index] = point
            if self.auto_layout:
                self.layout_levels()
            self.update()

    def remove_point(self, index):
        if 0 <= index < len(self.points):
            del self.points[index]
            new_conns = []
            for s, d in self.connections:
                if s == index or d == index:
                    continue
                s2 = s - 1 if s > index else s
                d2 = d - 1 if d > index else d
                new_conns.append((s2, d2))
            if self.auto_layout:
                self.connections = new_conns
            self.layout_levels()
            self.update()

    def add_connection(self, src, dst):
        if (src, dst) in self.connections:
            return False
        out = sum(1 for s, _ in self.connections if s == src)
        if out >= 2:
            return False
        self.connections.append((src, dst))
        self.update()
        return True

    def remove_connection(self, src, dst):
        try:
            self.connections.remove((src, dst))
            self.update()
            return True
        except ValueError:
            return False

    def get_outgoing(self, src):
        return [d for s, d in self.connections if s == src]

    def find_point_at(self, x, y, radius=16):
        for i, p in enumerate(self.points):
            dx = p.get('x', 0) - x
            dy = p.get('y', 0) - y
            if dx * dx + dy * dy <= radius * radius:
                return i
        return None

    def mousePressEvent(self, event):
        pos = event.position() if hasattr(event, 'position') else event.pos()
        x = int(pos.x())
        y = int(pos.y())
        idx = self.find_point_at(x, y)
        if idx is not None:
            if callable(self.on_edit_requested):
                self.on_edit_requested(idx, (x, y))
        else:
            if callable(self.on_create_requested):
                self.on_create_requested((x, y))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.auto_layout:
            self.layout_levels()
        self.update()

    def layout_levels(self):
        """Assign Y coordinate based on level.
        
        Each point keeps its X position where user placed it.
        Y is determined by the level (all points on same level have same Y).
        """
        for idx, p in enumerate(self.points):
            lvl = int(p.get('level', 0))
            y = self.top_margin + lvl * self.level_height
            # Only update Y, preserve X position where user placed it
            self.points[idx]['y'] = int(y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont('Arial', 10)
        painter.setFont(font)
        pen_color = QColor(200, 200, 200)
        painter.setPen(pen_color)
        for s, d in self.connections:
            if s < 0 or s >= len(self.points) or d < 0 or d >= len(self.points):
                continue
            ps = self.points[s]
            pd = self.points[d]
            x1, y1 = ps.get('x', 0), ps.get('y', 0)
            x2, y2 = pd.get('x', 0), pd.get('y', 0)

            # Rysuj prostą linię między punktami
            painter.drawLine(x1, y1, x2, y2)
            angle = math.atan2(y2 - y1, x2 - x1)
            endx, endy = x2, y2

            # Rysuj strzałkę na końcu
            try:
                ah = 8
                p1 = QPointF(endx - ah * math.cos(angle - math.pi / 6), endy - ah * math.sin(angle - math.pi / 6))
                p2 = QPointF(endx - ah * math.cos(angle + math.pi / 6), endy - ah * math.sin(angle + math.pi / 6))
                painter.setBrush(pen_color)
                painter.drawPolygon(p1, QPointF(endx, endy), p2)
            except Exception:
                pass

        for p in self.points:
            t = p.get('type', 'P')
            x = p.get('x', 0)
            y = p.get('y', 0)
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
