from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import QPropertyAnimation, Qt
from PyQt6.QtGui import QIcon

class HoverableSidebar(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)

        self.collapsed_width = 50
        self.expanded_width = 200

        self.widget = QWidget()
        self.widget.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.logo = QLabel("Logo")
        self.logo.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.layout.addWidget(self.logo)

        self.buttons = []
        self.button_names = ["Home", "Settings", "Sterowanie", "Dokumenty", "Mapa", "Help", "Logout"]
        for name in self.button_names:
            button = QPushButton(name)
            button.setStyleSheet("""
            QPushButton {
                background: none;
                color: white;
                border: none;
                padding: 5px 10px;  /* Adjust padding to reduce spacing */
                margin: 0;  /* Remove extra margins */
            }
            QPushButton:hover {
                background: white;
                color: #1F5AA9;
            }
            """)
            self.layout.addWidget(button)
            self.buttons.append(button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)

        self.settings_button = QPushButton("⚙")
        self.settings_button.setIcon(QIcon("path/to/settings_icon.png"))
        self.settings_button.setStyleSheet("""
        QPushButton {
            background: none;
            color: white;
            border: 1px solid white;
            border-radius: 15px;
            padding: 5px;
        }
        QPushButton:hover {
            background: white;
            color: #1F5AA9;
        }
        """)
        self.layout.addWidget(self.settings_button)

        self.widget.setLayout(self.layout)
        self.setWidget(self.widget)

        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)

        self.update_content_visibility(expanded=True)
        self.buttons[0].clicked.connect(self.parent().show_main_page)
        self.buttons[1].clicked.connect(self.parent().show_settings_page)
        self.buttons[2].clicked.connect(self.show_about_page)  # About
        self.buttons[3].clicked.connect(self.parent().show_dokumenty_page)
        try:
            self.buttons[4].clicked.connect(self.parent().show_map_editor_page)
        except Exception:
            pass
        self.settings_button.clicked.connect(self.parent().show_settings_page)

    def update_content_visibility(self, expanded: bool = True):
        """Show or hide sidebar content.

        Defensive: prefer dedicated attributes if available, fall back to toggling
        child widgets. Swallows exceptions so initialization won't fail.
        """
        try:
            content_widget = getattr(self, 'content_widget', None)
            if content_widget is not None:
                try:
                    content_widget.setVisible(expanded)
                    return
                except Exception:
                    pass

            content_layout = getattr(self, 'content_layout', None)
            if content_layout is not None:
                try:
                    for i in range(content_layout.count()):
                        item = content_layout.itemAt(i)
                        if item is None:
                            continue
                        widget = item.widget()
                        if widget is not None:
                            widget.setVisible(expanded)
                    return
                except Exception:
                    pass

            try:
                self.logo.setVisible(expanded)
            except Exception:
                pass
            try:
                for button, name in zip(self.buttons, self.button_names):
                    try:
                        button.setVisible(expanded)
                        button.setText(name if expanded else '')
                    except Exception:
                        continue
            except Exception:
                for child in self.findChildren(QWidget):
                    try:
                        child.setVisible(expanded)
                    except Exception:
                        continue
        except Exception:
            return

    def show_about_page(self):
        self.parent().show_manual_control_page()