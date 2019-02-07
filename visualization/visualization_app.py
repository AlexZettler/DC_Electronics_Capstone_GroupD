from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QSizePolicy, QPushButton, QAction
from PyQt5.QtGui import QIcon

import visualization.rand_cmap as rand_cmap

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random

class VisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "visualization!"
        self.left = 10
        self.top = 30
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage("statusbar thing")

        m = PlotCanvas(self, width=5,height=4, dpi=100)
        m.move(0,0)

        button = QPushButton("A button", self)
        button.setToolTip("I'm a button!")
        button.clicked.connect(m.plot_temperatures)
        button.move(500,0)
        button.resize(140,100)

        self.show()



    def initTriggers(self):
        pass


    def wasClicked(self):
        print("Clicked!")


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent, width, height, dpi):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_title("LOL a title")

        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(
            self,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.updateGeometry()
        #self.


    def plot(self, data, color='purple'):
        #ax = self.figure.add_subplot(111)
        self.axes.plot(data, 'r-',color=color)

        self.draw()


    def plot_temperatures(self):
        self.axes.clear()

        data = self.get_data()
        colors = self.get_cmap(len(data))
        print(data, colors)
        #for d,c in zip(data, colors):
            #print(d,c)
        self.plot(data)


    #rand_cmap(100, type='bright', first_color_black=True, last_color_black=False, verbose=True)


    def get_data(self):
        return [random.random() for i in range(25)]