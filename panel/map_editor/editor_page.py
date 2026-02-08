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

        # toolbar
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

        # algorithm selector for resolving map keys / routes
        self.algo_selector = QComboBox()
        self.algo_selector.addItem('Preferuj map_key, potem heurystyka', 'prefer_map_key')
        self.algo_selector.addItem('Heurystyka na nazwie (domyślna name)', 'heuristic')
        self.algo_selector.addItem('Wymagaj map_key (jeśli brak -> brak kierunku)', 'require_map_key')
        self.algo_selector.addItem('Fuzzy match (najbliższe dopasowanie)', 'fuzzy')
        toolbar.addWidget(QLabel('Algorytm:'))
        toolbar.addWidget(self.algo_selector)

        # auto-arrange toggle: when off, points keep manual x/y positions
        self.auto_layout_checkbox = QCheckBox('Auto-arrange levels')
        self.auto_layout_checkbox.setChecked(True)
        # we'll connect it to the canvas instance after the canvas is constructed
        toolbar.addWidget(self.auto_layout_checkbox)

        self.mode_label = QLabel('Tryb: podgląd')
        toolbar.addWidget(self.mode_label)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # main area: canvas + list
        main_h = QHBoxLayout()

        self.canvas = MapCanvas(self)
        # set callbacks
        self.canvas.on_create_requested = self.on_canvas_create
        self.canvas.on_edit_requested = self.on_canvas_edit
        self.selected_source = None

        # wire auto-layout checkbox to canvas.auto_layout
        try:
            self.canvas.auto_layout = bool(self.auto_layout_checkbox.isChecked())
            self.auto_layout_checkbox.stateChanged.connect(lambda s: setattr(self.canvas, 'auto_layout', s == Qt.Checked))
        except Exception:
            pass

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
        # if enabling connect mode, disable add mode
        self.add_mode = False
        self.add_button.setChecked(False)
        if checked:
            self.mode_label.setText('Tryb: łączenie - wybierz źródło')
        else:
            self.mode_label.setText('Tryb: podgląd')
        # when enabling connect mode we track selected_source via canvas clicks
        self.connect_mode = checked
        if not checked:
            self.selected_source = None

    def on_canvas_create(self, pos):
        # only allow create when add_mode enabled
        if not self.add_mode:
            return
        x, y = pos
        # prefill type from selector
        pre_type = self.type_selector.currentData()
        dlg = PointDialog(self, point={'type': pre_type, 'name': ''}, allow_delete=False)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            accepted, data, deleted, remove_target = dlg.get_result()
            if accepted and not deleted:
                point = {'x': x, 'y': y, 'type': data['type'], 'name': data['name'], 'map_key': data.get('map_key')}
                self.canvas.add_point(point)
                self.add_point_to_list(point)

    def on_canvas_edit(self, index, pos):
        # if in connect mode handle connection creation/removal
        if getattr(self, 'connect_mode', False):
            # if no selected source, set this as source
            if self.selected_source is None:
                self.selected_source = index
                self.mode_label.setText(f'Tryb: łączenie - źródło #{index}')
                return
            else:
                src = self.selected_source
                dst = index
                if src == dst:
                    # deselect
                    self.selected_source = None
                    self.mode_label.setText('Tryb: łączenie - wybierz źródło')
                    return
                # attempt to add connection
                ok = self.canvas.add_connection(src, dst)
                if not ok:
                    # if failed due to max outgoing, show a simple message by reusing QLabel
                    self.mode_label.setText('Limit połączeń (max 2) lub już istnieje')
                else:
                    self.mode_label.setText(f'Połączono {src} -> {dst}')
                    # log the connection to console using route logic if available
                    try:
                        src_pt = self.canvas.points[src]
                        dst_pt = self.canvas.points[dst]
                        src_name = src_pt.get('name') or ''
                        dst_name = dst_pt.get('name') or ''

                        # resolve keys using selected algorithm and helper
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

                        # print helpful output even if direction couldn't be resolved
                        out_src = src_name if src_name else f'#{src}({src_pt.get("type","")})'
                        out_dst = dst_name if dst_name else f'#{dst}({dst_pt.get("type","")})'
                        print(f"CONNECTED {out_src} -> {out_dst} : {direction}")
                    except Exception:
                        # avoid any exceptions from logging to affect UI
                        pass
                # keep source selected to allow second connection
                return

        # edit existing point
        try:
            p = self.canvas.points[index]
        except Exception:
            return
        # prepare outgoing list for this point
        outgoing = [(dst, self.canvas.points[dst].get('name','')) for dst in self.canvas.get_outgoing(index)]
        dlg = PointDialog(self, point=p, allow_delete=True, outgoing=outgoing)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            accepted, data, deleted, remove_target = dlg.get_result()
            if deleted:
                self.canvas.remove_point(index)
                self.point_list.takeItem(index)
            else:
                if remove_target is not None:
                    # remove connection from index -> remove_target
                    removed = self.canvas.remove_connection(index, remove_target)
                    # log removal
                    try:
                        src_pt = self.canvas.points[index]
                        src_name = src_pt.get('name') or ''
                        dst_idx = remove_target
                        dst_name = ''
                        if 0 <= dst_idx < len(self.canvas.points):
                            dst_name = self.canvas.points[dst_idx].get('name') or ''

                        # resolve keys using selected algorithm for removal log
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
                else:
                    new_point = {'x': p['x'], 'y': p['y'], 'type': data['type'], 'name': data['name'], 'map_key': data.get('map_key')}
                    self.canvas.update_point(index, new_point)
                    # update list item text
                    item = self.point_list.item(index)
                    if item:
                        item.setText(f"{new_point['name']} ({new_point['type']}) @ ({new_point['x']}, {new_point['y']})")

    

    def add_point_to_list(self, point):
        # show map_key if present to make it clear which canonical key is used
        mk = point.get('map_key')
        mk_part = f" [{mk}]" if mk else ''
        label = f"{point.get('name','')}{mk_part} ({point.get('type','')}) @ ({point.get('x')}, {point.get('y')})"
        item = QListWidgetItem(label)
        self.point_list.addItem(item)

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

        # helpers
        def exact_match(n):
            if not n:
                return None
            if route_logger and n in route_logger.mapa:
                return n
            # case-insensitive
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

        # prefer explicit map_key
        mk = pt.get('map_key') if isinstance(pt, dict) else None
        if algo == 'prefer_map_key':
            if mk and route_logger and mk in route_logger.mapa:
                return mk
            # fallthrough to heuristics
            res = exact_match(name) or substring_match(name) or type_match(pt.get('type'))
            return res

        if algo == 'heuristic':
            # try name heuristics first, then fallback to map_key
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
            # use difflib to find closest key
            if name and keys:
                matches = difflib.get_close_matches(name, keys, n=1, cutoff=0.6)
                if matches:
                    return matches[0]
            if mk and route_logger and mk in route_logger.mapa:
                return mk
            return None

        # default fallback
        if mk and route_logger and mk in route_logger.mapa:
            return mk
        return exact_match(name) or substring_match(name) or type_match(pt.get('type'))
