from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QListWidget, QListWidgetItem, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog

from .canvas import MapCanvas
from .dialogs import PointDialog

import difflib


class MapEditorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_mode = False

        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.add_button = QPushButton("Dodaj")
        self.add_button.setCheckable(True)
        self.add_button.clicked.connect(self.toggle_add_mode)
        toolbar.addWidget(self.add_button)

        self.connect_button = QPushButton("Łącz")
        self.connect_button.setCheckable(True)
        self.connect_button.clicked.connect(self.toggle_connect_mode)
        toolbar.addWidget(self.connect_button)

        self.type_selector = QComboBox()
        self.type_selector.addItem('M (magazyn)', 'M')
        self.type_selector.addItem('H1 (home)', 'H1')
        self.type_selector.addItem('Punkt z pakunkiem', 'P')
        toolbar.addWidget(QLabel("Typ punktu:"))
        toolbar.addWidget(self.type_selector)

        self.algo_selector = QComboBox()
        self.algo_selector.addItem('Preferuj map_key, potem heurystyka', 'prefer_map_key')
        self.algo_selector.addItem('Heurystyka na nazwie (domyślna name)', 'heuristic')
        self.algo_selector.addItem('Wymagaj map_key (jeśli brak -> brak kierunku)', 'require_map_key')
        self.algo_selector.addItem('Fuzzy match (najbliższe dopasowanie)', 'fuzzy')
        toolbar.addWidget(QLabel('Algorytm:'))
        toolbar.addWidget(self.algo_selector)

        self.auto_layout_checkbox = QCheckBox('Auto-arrange levels')
        self.auto_layout_checkbox.setChecked(True)
        toolbar.addWidget(self.auto_layout_checkbox)

        self.mode_label = QLabel('Tryb: podgląd')
        toolbar.addWidget(self.mode_label)

        toolbar.addStretch()
        
        self.test_map_button = QPushButton("Testowa Mapka")
        self.test_map_button.clicked.connect(self.on_load_test_map)
        toolbar.addWidget(self.test_map_button)
        
        self.send_button = QPushButton("Wyślij trasę")
        self.send_button.clicked.connect(self.on_send_route)
        toolbar.addWidget(self.send_button)

        layout.addLayout(toolbar)

        main_h = QHBoxLayout()

        self.canvas = MapCanvas(self)
        self.canvas.on_create_requested = self.on_canvas_create
        self.canvas.on_edit_requested = self.on_canvas_edit
        self.selected_source = None
        
        # Initialize auto_layout from checkbox state
        self.canvas.auto_layout = bool(self.auto_layout_checkbox.isChecked())
        self.auto_layout_checkbox.stateChanged.connect(lambda s: setattr(self.canvas, 'auto_layout', s == 2))

        main_h.addWidget(self.canvas, stretch=3)

        self.point_list = QListWidget()
        self.point_list.setMaximumWidth(260)
        main_h.addWidget(self.point_list, stretch=1)

        layout.addLayout(main_h)

    def toggle_add_mode(self, checked):
        self.add_mode = checked
        self.mode_label.setText('Tryb: dodawanie' if checked else 'Tryb: podgląd')
        self.add_button.setText('Dodaj (aktywny)' if checked else 'Dodaj')
        
    def toggle_connect_mode(self, checked):
        self.add_mode = False
        self.add_button.setChecked(False)
        if checked:
            self.mode_label.setText('Tryb: łączenie - wybierz źródło')
        else:
            self.mode_label.setText('Tryb: podgląd')
        self.connect_mode = checked
        if not checked:
            self.selected_source = None

    def on_canvas_create(self, pos):
        if not self.add_mode:
            return
        x, y = pos
        pre_type = self.type_selector.currentData()
        dlg = PointDialog(self, point={'type': pre_type, 'name': ''}, allow_delete=False)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            accepted, data, deleted, remove_target = dlg.get_result()
            if accepted and not deleted:
                point = {'x': x, 'y': y, 'type': data['type'], 'name': data['name'], 'map_key': data.get('map_key')}
                self.canvas.add_point(point)
                self.add_point_to_list(point)

    def on_canvas_edit(self, index, pos):
        if getattr(self, 'connect_mode', False):
            if self.selected_source is None:
                self.selected_source = index
                self.mode_label.setText(f'Tryb: łączenie - źródło #{index}')
                return
            else:
                src = self.selected_source
                dst = index
                if src == dst:
                    self.selected_source = None
                    self.mode_label.setText('Tryb: łączenie - wybierz źródło')
                    return
                ok = self.canvas.add_connection(src, dst)
                if not ok:
                    self.mode_label.setText('Limit połączeń (max 2) lub już istnieje')
                else:
                    self.selected_source = dst  # Ustaw punkt docelowy jako nowe źródło
                    self.mode_label.setText(f'Połączono {src} -> {dst}. Nowe źródło: #{dst}')
                    try:
                        src_pt = self.canvas.points[src]
                        dst_pt = self.canvas.points[dst]
                        src_name = src_pt.get('name') or ''
                        dst_name = dst_pt.get('name') or ''

                        try:
                            r_src = self.resolve_key(src_name, src_pt)
                            r_dst = self.resolve_key(dst_name, dst_pt)
                            direction = None
                            if r_src and r_dst:
                                try:
                                    from tools import route_logger
                                    direction = route_logger.way(route_logger.mapa[r_src], r_dst)
                                except Exception:
                                    direction = None
                        except Exception:
                            direction = None

                        out_src = src_name if src_name else f'#{src}({src_pt.get("type","")})'
                        out_dst = dst_name if dst_name else f'#{dst}({dst_pt.get("type","")})'
                        print(f"CONNECTED {out_src} -> {out_dst} : {direction}")
                    except Exception:
                        pass
                    try:
                        from tools import route_logger
                        route_logger.print_sequence_from_canvas(self.canvas.points, self.canvas.connections)
                        route_logger.print_warehouse_declarations(self.canvas.points)
                        route_logger.print_compact_mappings(self.canvas.points)
                        try:
                            route_logger.send_route_commands(self.canvas.points, self.canvas.connections)
                        except Exception:
                            pass
                    except Exception:
                        pass
                return

        try:
            p = self.canvas.points[index]
        except Exception:
            return
        outgoing = [(dst, self.canvas.points[dst].get('name','')) for dst in self.canvas.get_outgoing(index)]
        dlg = PointDialog(self, point=p, allow_delete=True, outgoing=outgoing)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            accepted, data, deleted, remove_target = dlg.get_result()
            if deleted:
                self.canvas.remove_point(index)
                self.point_list.takeItem(index)
                try:
                    from tools import route_logger
                    route_logger.update_mapa_from_canvas(self.canvas.points, self.canvas.connections)
                except Exception:
                    pass
            else:
                if remove_target is not None:
                    removed = self.canvas.remove_connection(index, remove_target)
                    try:
                        src_pt = self.canvas.points[index]
                        src_name = src_pt.get('name') or ''
                        dst_idx = remove_target
                        dst_name = ''
                        if 0 <= dst_idx < len(self.canvas.points):
                            dst_name = self.canvas.points[dst_idx].get('name') or ''

                        try:
                            r_src = self.resolve_key(src_name, src_pt)
                            r_dst = self.resolve_key(dst_name, self.canvas.points[dst_idx] if 0 <= dst_idx < len(self.canvas.points) else {})
                            direction = None
                            if r_src and r_dst:
                                try:
                                    from tools import route_logger
                                    direction = route_logger.way(route_logger.mapa[r_src], r_dst)
                                except Exception:
                                    direction = None
                        except Exception:
                            direction = None

                        out_src = src_name if src_name else f'#{index}({src_pt.get("type","")})'
                        out_dst = dst_name if dst_name else f'#{dst_idx}'
                        print(f"REMOVED_CONNECTION {out_src} -> {out_dst} : {direction}")
                    except Exception:
                        pass
                    try:
                        from tools import route_logger
                        route_logger.print_sequence_from_canvas(self.canvas.points, self.canvas.connections)
                        route_logger.print_warehouse_declarations(self.canvas.points)
                        route_logger.print_compact_mappings(self.canvas.points)
                        try:
                            route_logger.send_route_commands(self.canvas.points, self.canvas.connections)
                        except Exception:
                            pass
                    except Exception:
                        pass
                else:
                    new_point = {'x': p['x'], 'y': p['y'], 'type': data['type'], 'name': data['name'], 'map_key': data.get('map_key')}
                    self.canvas.update_point(index, new_point)
                    item = self.point_list.item(index)
                    if item:
                        item.setText(f"{new_point['name']} ({new_point['type']}) @ ({new_point['x']}, {new_point['y']})")
                    try:
                        from tools import route_logger
                        route_logger.update_mapa_from_canvas(self.canvas.points, self.canvas.connections)
                        route_logger.print_mapa()
                    except Exception:
                        pass

    

    def add_point_to_list(self, point):
        mk = point.get('map_key')
        mk_part = f" [{mk}]" if mk else ''
        label = f"{point.get('name','')}{mk_part} ({point.get('type','')}) @ ({point.get('x')}, {point.get('y')})"
        item = QListWidgetItem(label)
        self.point_list.addItem(item)
        try:
            from tools import route_logger
            route_logger.print_sequence_from_canvas(self.canvas.points, self.canvas.connections)
            route_logger.print_warehouse_declarations()
            route_logger.print_compact_mappings()
            try:
                route_logger.send_route_commands(self.canvas.points, self.canvas.connections)
            except Exception:
                pass
        except Exception:
            pass

    def resolve_key(self, name, pt):
        """Resolve a map key for a given point according to currently selected algorithm.
        Returns a key (string) present in route_logger.mapa or None.
        """
        algo = self.algo_selector.currentData() if hasattr(self, 'algo_selector') else 'prefer_map_key'
        try:
            from tools import route_logger
            keys = list(route_logger.mapa.keys())
        except Exception:
            route_logger = None
            keys = []

        def exact_match(n):
            if not n:
                return None
            if route_logger and n in route_logger.mapa:
                return n
            for k in keys:
                if k.lower() == n.lower():
                    return k
            return None

        def substring_match(n):
            if not n:
                return None
            for k in keys:
                if n.lower() in k.lower() or k.lower() in n.lower():
                    return k
            return None

        def type_match(ptype):
            if not ptype or not route_logger:
                return None
            if ptype in route_logger.mapa:
                return ptype
            return None

        mk = pt.get('map_key') if isinstance(pt, dict) else None
        if algo == 'prefer_map_key':
            if mk and route_logger and mk in route_logger.mapa:
                return mk
            res = exact_match(name) or substring_match(name) or type_match(pt.get('type'))
            return res

        if algo == 'heuristic':
            res = exact_match(name) or substring_match(name) or type_match(pt.get('type'))
            if res:
                return res
            if mk and route_logger and mk in route_logger.mapa:
                return mk
            return None

        if algo == 'require_map_key':
            if mk and route_logger and mk in route_logger.mapa:
                return mk
            return None

        if algo == 'fuzzy':
            if name and keys:
                matches = difflib.get_close_matches(name, keys, n=1, cutoff=0.6)
                if matches:
                    return matches[0]
            if mk and route_logger and mk in route_logger.mapa:
                return mk
            return None


        if mk and route_logger and mk in route_logger.mapa:
            return mk
        return exact_match(name) or substring_match(name) or type_match(pt.get('type'))

    def on_send_route(self):
        """Handler for the 'Wyślij trasę' button: sends current canvas route to ESP."""
        try:
            from tools import route_logger
            print("Wysyłam trasę do ESP...")
            route_logger.send_route_commands(self.canvas.points, self.canvas.connections)
            print("Komenda wysłana (wywołano send_route_commands).")
        except Exception as e:
            print("Błąd podczas wysyłania trasy:", e)

    def on_load_test_map(self):
        """Load a hardcoded test map with H1 -> M1 -> M2 -> M3 -> P1 -> H1 route."""
        # Clear existing points
        self.canvas.points = []
        self.canvas.connections = []
        self.point_list.clear()
        
        # Create test points
        test_points = [
            {'x': 100, 'y': 100, 'type': 'H1', 'name': 'H1', 'level': 0},
            {'x': 220, 'y': 100, 'type': 'M', 'name': 'M1', 'level': 0},
            {'x': 340, 'y': 100, 'type': 'M', 'name': 'M2', 'level': 0},
            {'x': 460, 'y': 100, 'type': 'M', 'name': 'M3', 'level': 0},
            {'x': 580, 'y': 100, 'type': 'P', 'name': 'P1', 'level': 0},
        ]
        
        # Add points to canvas
        for point in test_points:
            self.canvas.points.append(point)
            self.add_point_to_list(point)
        
        # Create connections: H1->M1->M2->M3->P1
        connections = [(0, 1), (1, 2), (2, 3), (3, 4)]
        self.canvas.connections = connections
        
        print("Testowa mapka załadowana: H1 -> M1 -> M2 -> M3 -> P1")
        self.canvas.update()

