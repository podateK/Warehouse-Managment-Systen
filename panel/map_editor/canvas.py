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
        self.points.append(point)
        self.layout_levels()
        self.update()

    def update_point(self, index, point):
        if 0 <= index < len(self.points):
            if 'level' not in point and 'y' in point:
                point['level'] = round((point['y'] - self.top_margin) / self.level_height)
            self.points[index] = point
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
        self.layout_levels()
        self.update()

    def layout_levels(self):
        """Assign x,y coordinates to points grouped by integer level.

        Points on the same level are spaced horizontally and centered.
        """
        levels = {}
        for idx, p in enumerate(self.points):
            lvl = int(p.get('level', 0))
            levels.setdefault(lvl, []).append(idx)

        width = max(self.width(), 400)
        for lvl, indices in levels.items():
            n = len(indices)
            total_width = (n - 1) * self.col_spacing
            start_x = max(self.left_margin, (width - total_width) // 2)
            y = self.top_margin + lvl * self.level_height
            for i, idx in enumerate(indices):
                x = start_x + i * self.col_spacing
                self.points[idx]['x'] = int(x)
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

            lvl_s = ps.get('level', 0)
            lvl_d = pd.get('level', 0)

            if lvl_s == lvl_d:
                painter.drawLine(x1, y1, x2, y2)
                angle = math.atan2(y2 - y1, x2 - x1)
                endx, endy = x2, y2
            else:
                if lvl_d > lvl_s:
                    side = self.direction_offset
                else:
                    side = -self.direction_offset

                mid_x = x1 + side
                painter.drawLine(x1, y1, mid_x, y1)
                painter.drawLine(mid_x, y1, mid_x, y2)
                painter.drawLine(mid_x, y2, x2, y2)
                angle = math.atan2(0, x2 - mid_x if x2 - mid_x != 0 else 1)
                endx, endy = x2, y2

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
