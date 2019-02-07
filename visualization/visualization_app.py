from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QSizePolicy, QPushButton, QAction, QTabWidget, QTabBar
from PyQt5.QtGui import QIcon, QColor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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

        self.primary_color = color
        self.dark_color = QColor(color).darker(125).name()
        self.light_color = QColor(color).lighter(125).name()

        print(self.primary_color, self.light_color, self.dark_color)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        #Setup color
        self.setStyleSheet(f"background-color: {self.primary_color}")

        # Set positions
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar().showMessage("statusbar thing")

        m = PlotCanvas(self, width=5, height=4, dpi=100, color=self.light_color)
        m.move(0,0)

        button = QPushButton("Reload data!", self)
        button.setToolTip("I'm a button!")
        button.clicked.connect(m.plot_temperatures)
        button.setStyleSheet(f"background-color: {self.light_color}")
        button.move(500,0)
        button.resize(140,100)

        self.show()


    def wasClicked(self):
        print("Clicked!")


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

    def __init__(self, parent, width, height, dpi, color):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor=color)
        self.axes = fig.add_subplot(111, facecolor=color)
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