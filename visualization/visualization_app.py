from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QSizePolicy, QPushButton, QAction, QTabWidget, QTabBar, QLineEdit, QLabel, QDockWidget
from PyQt5.QtGui import QIcon, QColor, QDrag

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtCore import Qt, pyqtSlot, QMimeData

from collections import deque

import datetime

import random

class VisApp(QMainWindow):
    def __init__(self, color):
        super().__init__()
        self.title = "visualization!"
        self.left = 10
        self.top = 30
        self.width = 640
        self.height = 480

        self.colors = {"prim": color,
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


        window_switcher = QTabWidget(self)
        window_switcher.setTabsClosable(False)

        #Setup Graph

        configure = ConfigureDock(self, self.colors)
        visualize = VisualizeDock(self, self.colors)


        window_switcher.addTab(configure, "Configure")
        window_switcher.addTab(visualize, "Visualize")
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )




        self.show()

class ConfigureDock(QDockWidget):

    def __init__(self, parent, colors):
        super().__init__(parent)

        text_box = QLineEdit('Drag this', self)
        text_box.setDragEnabled(True)
        text_box.move(0, 400)
        text_box.resize(140, 100)

        label = CustomLabel("Drop here", self)
        label.move(0, 500)
        label.resize(140, 100)



class VisualizeDock(QDockWidget):

    def __init__(self, parent, colors):
        super().__init__(parent)
        m = PlotCanvas(self, width=5, height=4, dpi=100, colors=colors)
        m.move(0,0)


        #Setup button
        btn_regather_data = QPushButton("Reload data!", self)
        #button.setToolTip("I'm a button!")
        btn_regather_data.clicked.connect(m.plot_temperatures)
        btn_regather_data.setStyleSheet(f"background-color: {colors['prim']}")
        btn_regather_data.move(500,0)
        btn_regather_data.resize(140,100)



class PlotCanvas(FigureCanvasQTAgg):

    color_options = {
        "C0",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9",
    }

    def __init__(self, parent, width, height, dpi, colors):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor=colors["prim"])
        self.axes = fig.add_subplot(111, facecolor=colors["prim"])
        self.axes.set_title("LOL a title")

        #self.axes.set_facecolor = color

        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(
            self,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.updateGeometry()
        #self.


    def plot(self, data, color):
        #ax = self.figure.add_subplot(111)
        self.axes.plot(data, color=color)

        self.draw()


    def plot_temperatures(self):
        self.axes.clear()
        data = self.get_data()

        #Custom color cycling
        color_deque = deque(self.color_options)

        self.axes.set_title(f"Data({datetime.datetime.now().strftime('%H:%M:%S')})")
        for d in data:

            self.plot(d, color_deque[0])

            color_deque.rotate(1)

    def get_data(self):
        return [[random.random() for i in range(25)]for i in range(5)]


class CustomLabel(QLabel):


    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, e):
        print("drag enter")
        if e.mimeData().hasFormat('text/plain'):

            e.accept()

        else:
            e.ignore()

    def dropEvent(self, e):
        self.setText(e.mimeData().text())
