from PyQt6.QtCore import Qt
from panel.sidebar.sidebar_style import HoverableSidebar

def create_sidebar(main_window):
    sidebar = HoverableSidebar("Sidebar", main_window)
    main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, sidebar)
    return sidebar