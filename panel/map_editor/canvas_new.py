from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QRect, QPointF
import math


class MapCanvasLinear(QWidget):
    """Canvas that visualizes a warehouse route as a central vertical line
    with branches (offshoots) representing turns at different 'line' positions.
    
    Data model: list of 'branches' - each branch is a dict with:
        - line_num: which line this branch is at (1, 2, 3, ...)
        - direction: 'LEFT' or 'RIGHT'
        - name: point name at the end of branch
        - point_type: 'M', 'H1', or 'P'
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(700, 500)
        self.setStyleSheet("background-color: #f5f7fa;")
        
        # Data model
        self.branches = []  # list of {line_num, direction, name, point_type}
        self.line_height = 80  # pixels between horizontal lines
        self.top_margin = 60
        self.center_x = 350  # center line X position
        self.branch_length = 120  # length of branch line from center
        
        self.on_create_requested = None  # callback for add branch
        self.on_edit_requested = None  # callback for edit branch
        self.on_remove_requested = None  # callback for remove branch
        
        self.hovered_branch = None  # branch index being hovered
    
    def add_branch(self, line_num, direction, name='', point_type='P'):
        """Add a new branch to the route."""
        branch = {
            'line_num': int(line_num),
            'direction': direction,
            'name': name,
            'point_type': point_type
        }
        self.branches.append(branch)
        self.update()
    
    def update_branch(self, index, branch_data):
        """Update an existing branch."""
        if 0 <= index < len(self.branches):
            self.branches[index].update(branch_data)
            self.update()
    
    def remove_branch(self, index):
        """Remove a branch."""
        if 0 <= index < len(self.branches):
            del self.branches[index]
            self.update()
    
    def _get_branch_at(self, x, y, radius=20):
        """Find which branch (if any) is at position (x, y)."""
        for i, branch in enumerate(self.branches):
            line_num = branch['line_num']
            direction = branch['direction']
            
            # Center position of branch
            center_y = self.top_margin + line_num * self.line_height
            if direction == 'LEFT':
                branch_x = self.center_x - self.branch_length
            else:  # RIGHT
                branch_x = self.center_x + self.branch_length
            
            # Draw circle at branch endpoint
            dx = branch_x - x
            dy = center_y - y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= radius:
                return i
        
        return None
    
    def mousePressEvent(self, event):
        pos = event.position() if hasattr(event, 'position') else event.pos()
        x = int(pos.x())
        y = int(pos.y())
        
        idx = self._get_branch_at(x, y)
        if idx is not None:
            # Edit existing branch
            if callable(self.on_edit_requested):
                self.on_edit_requested(idx)
        else:
            # Try to add new branch on center line
            if abs(x - self.center_x) < 30:
                # Snap to nearest line_num
                line_num = round((y - self.top_margin) / self.line_height)
                if line_num >= 1:
                    if callable(self.on_create_requested):
                        self.on_create_requested(line_num)
    
    def mouseMoveEvent(self, event):
        pos = event.position() if hasattr(event, 'position') else event.pos()
        x = int(pos.x())
        y = int(pos.y())
        
        old_hovered = self.hovered_branch
        self.hovered_branch = self._get_branch_at(x, y)
        
        if old_hovered != self.hovered_branch:
            self.update()
    
    def leaveEvent(self, event):
        self.hovered_branch = None
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background gradient (opcjonalnie)
        painter.fillRect(self.rect(), QColor(245, 247, 250))
        
        # Draw center vertical line - główna trasa
        painter.setPen(QPen(QColor(0, 102, 204), 4))  # niebieski
        painter.drawLine(self.center_x, self.top_margin, 
                         self.center_x, self.height() - self.top_margin)
        
        # Draw start/end markers
        painter.setBrush(QColor(52, 168, 83))  # zielony
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawEllipse(self.center_x - 12, self.top_margin - 12, 24, 24)
        painter.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawText(self.center_x - 8, self.top_margin + 8, "START")
        
        # Draw line numbers and branches
        painter.setFont(QFont('Segoe UI', 9))
        
        if not self.branches:
            # Draw guide lines if no branches yet
            painter.setPen(QPen(QColor(229, 231, 235), 1))
            for i in range(1, 6):
                y = self.top_margin + i * self.line_height
                painter.drawLine(0, y, self.width(), y)
                painter.setPen(QPen(QColor(107, 114, 128), 1))
                painter.drawText(self.center_x - 40, y - 10, 80, 20, 
                               Qt.AlignmentFlag.AlignCenter, f"Linia {i}")
                painter.setPen(QPen(QColor(229, 231, 235), 1))
        
        # Draw branches
        for i, branch in enumerate(self.branches):
            line_num = branch['line_num']
            direction = branch['direction']
            name = branch.get('name', '')
            point_type = branch.get('point_type', 'P')
            
            # Y position of this line
            y = self.top_margin + line_num * self.line_height
            
            # Determine X position based on direction
            if direction == 'LEFT':
                branch_x = self.center_x - self.branch_length
                text_x = branch_x - 140
            else:  # RIGHT
                branch_x = self.center_x + self.branch_length
                text_x = branch_x + 20
            
            # Draw branch line
            is_hovered = (i == self.hovered_branch)
            line_width = 5 if is_hovered else 3
            
            if direction == 'LEFT':
                line_color = QColor(239, 68, 68)  # czerwony
            else:
                line_color = QColor(59, 130, 246)  # niebieski
            
            painter.setPen(QPen(line_color, line_width))
            painter.drawLine(self.center_x, y, branch_x, y)
            
            # Draw point circle at branch end
            circle_radius = 14 if is_hovered else 12
            
            # Kolory dla różnych typów punktów
            if point_type == 'M':
                color = QColor(16, 185, 129)  # zielony (magazyn)
            elif point_type == 'H1':
                color = QColor(139, 92, 246)  # fioletowy (home)
            else:
                color = QColor(245, 158, 11)  # pomarańczowy (paczka)
            
            painter.setBrush(color)
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawEllipse(branch_x - circle_radius, y - circle_radius, 
                              circle_radius * 2, circle_radius * 2)
            
            # Draw point type text
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont('Segoe UI', 9, QFont.Weight.Bold))
            type_text = {'M': 'M', 'H1': 'H', 'P': 'P'}.get(point_type, 'P')
            painter.drawText(branch_x - circle_radius, y - circle_radius, 
                           circle_radius * 2, circle_radius * 2, 
                           Qt.AlignmentFlag.AlignCenter, type_text)
            
            # Draw branch info text - bardziej widoczne
            painter.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
            painter.setPen(QPen(QColor(44, 62, 80), 1))
            
            dir_text = '←' if direction == 'LEFT' else '→'
            info_text = f"{dir_text} Linia {line_num}"
            if name:
                info_text += f" : {name}"
            
            # Draw info background
            painter.setPen(QPen(QColor(229, 231, 235), 1))
            painter.setBrush(QColor(255, 255, 255))
            text_rect = painter.fontMetrics().boundingRect(info_text)
            bg_rect = text_rect.adjusted(-6, -4, 6, 4)
            bg_rect.moveTo(text_x, y - 20)
            painter.drawRoundedRect(bg_rect, 3, 3)
            
            # Draw the text
            painter.setPen(QPen(QColor(44, 62, 80), 1))
            painter.drawText(text_x, y - 20, text_rect.width() + 12, text_rect.height() + 8, 
                           Qt.AlignmentFlag.AlignCenter, info_text)
