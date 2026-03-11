from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
from PyQt6.QtCore import Qt


class PointDialog(QDialog):
    """Dialog used both for creating and editing a point.
    For create: pass `point=None`. For edit: pass existing `point` and set allow_delete=True.
    Returns a tuple: (accepted: bool, data: dict or None, deleted: bool)
    """
    def __init__(self, parent=None, point=None, allow_delete=False, outgoing=None):
        super().__init__(parent)
        self.setWindowTitle('Punkt')
        self.setModal(True)

        self.deleted = False
        self.remove_target = None

        layout = QVBoxLayout(self)

        self.type_selector = QComboBox()
        self.type_selector.addItem('M (magazyn)', 'M')
        self.type_selector.addItem('H1 (home)', 'H1')
        self.type_selector.addItem('Punkt z pakunkiem', 'P')

        self.name_edit = QLineEdit()

        self.map_key_selector = None
        try:
            from tools import route_logger
            keys = list(route_logger.mapa.keys())
            if keys:
                self.map_key_selector = QComboBox()
                self.map_key_selector.addItem('---')
                for k in keys:
                    self.map_key_selector.addItem(k)
                def on_map_key_changed(idx):
                    if idx <= 0:
                        return
                    key = self.map_key_selector.itemText(idx)
                    self.name_edit.setText(key)

                self.map_key_selector.currentIndexChanged.connect(on_map_key_changed)
        except Exception:
            self.map_key_selector = None

        if point is not None:
            t = point.get('type', 'P')
            idx = [self.type_selector.itemData(i) for i in range(self.type_selector.count())].index(t)
            self.type_selector.setCurrentIndex(idx)
            self.name_edit.setText(point.get('name', ''))

        if self.map_key_selector is not None:
            layout.addWidget(QLabel('Mapa (wybierz klucz):'))
            layout.addWidget(self.map_key_selector)

        self.outgoing = outgoing or []
        if self.outgoing:
            layout.addWidget(QLabel('Połączenia wychodzące:'))
            self.outgoing_selector = QComboBox()
            for idx, name in self.outgoing:
                self.outgoing_selector.addItem(f"{name} (#{idx})", idx)
            layout.addWidget(self.outgoing_selector)

        layout.addWidget(QLabel('Typ punktu:'))
        layout.addWidget(self.type_selector)
        layout.addWidget(QLabel('Nazwa punktu:'))
        layout.addWidget(self.name_edit)

        btns = QHBoxLayout()
        self.save_btn = QPushButton('Zapisz')
        self.save_btn.clicked.connect(self.accept)
        btns.addWidget(self.save_btn)

        if allow_delete:
            self.delete_btn = QPushButton('Usuń')
            self.delete_btn.clicked.connect(self.on_delete)
            btns.addWidget(self.delete_btn)
            if self.outgoing:
                self.remove_conn_btn = QPushButton('Usuń połączenie')
                self.remove_conn_btn.clicked.connect(self.on_remove_connection)
                btns.addWidget(self.remove_conn_btn)

        self.cancel_btn = QPushButton('Anuluj')
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.cancel_btn)

        layout.addLayout(btns)

    def on_delete(self):
        self.deleted = True
        self.accept()

    def on_remove_connection(self):
        if not getattr(self, 'outgoing_selector', None):
            return
        idx = self.outgoing_selector.currentData()
        if idx is None:
            return
        self.remove_target = idx
        self.accept()

    def get_result(self):
        if self.deleted:
            return True, None, True, None
        map_key = None
        if self.map_key_selector is not None:
            idx = self.map_key_selector.currentIndex()
            if idx > 0:
                map_key = self.map_key_selector.itemText(idx)

        data = {
            'type': self.type_selector.currentData(),
            'name': self.name_edit.text().strip(),
            'map_key': map_key,
        }
        return True, data, False, self.remove_target
