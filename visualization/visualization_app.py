from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon, QColor, QDrag
from PyQt5.QtCore import Qt, pyqtSlot, QMimeData
import PyQt5.QtCore as QtCore



import matplotlib.pyplot as plt


import os
import os.path


from visualization.widgets import *

class VisApp(QMainWindow):
    def __init__(self, color):
        super().__init__()
        self.title = "visualization!"
        self.left = 10
        self.top = 30
        self.width = 640
        self.height = 480

        self.colors = {
            "prim": color,
            "light": QColor(color).lighter(125).name(),
            "dark": QColor(color).darker(125).name()
        }


        #print(self.primary_color, self.light_color, self.dark_color)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        #Setup color
        self.setStyleSheet(f"background-color: {self.colors['prim']}")

        # Set positions
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar().showMessage("statusbar thing")

        # Setup tabs
        self.tab_widget = TabDock(self, self.colors)



        configure = ConfigureDock(self, self.colors)
        self.tab_widget.addTab(configure, "Configure")

        visualize = VisualizeDock(self, self.colors)
        self.tab_widget.addTab(visualize, "Visualize")


        self.show()

    def resize_child_tabs(self):
        cr = self.contentsRect()
        self.tab_widget.setGeometry(
            QtCore.QRect(cr.left(), cr.top(), cr.width(), cr.height()))


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_child_tabs()

