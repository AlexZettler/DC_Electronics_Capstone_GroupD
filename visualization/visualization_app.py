from PyQt5.QtWidgets import QMainWindow
import PyQt5.QtCore as QtCore

from visualization.settings import colors
from visualization.widgets import *


class VisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Visualization!"
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        #Setup color
        self.setStyleSheet(f"background-color: {colors['prim']}")

        # Set positions
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar().showMessage("statusbar thing")

        # Setup tabs
        self.tab_widget = TabDock(self)

        # Setup configure widget
        configure = ConfigureTab(self)
        self.tab_widget.addTab(configure, "Configure")

        # Setup visualize widget
        visualize = VisualizeTab(self)
        self.tab_widget.addTab(visualize, "Visualize")

        # Display the app
        self.show()

    def resize_child_tabs(self):
        cr = self.contentsRect()
        self.tab_widget.setGeometry(
            QtCore.QRect(cr.left(), cr.top(), cr.width(), cr.height()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_child_tabs()
