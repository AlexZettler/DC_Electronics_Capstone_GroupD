from PyQt5.QtWidgets import QSizePolicy, QFrame, QVBoxLayout


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure


import datetime
import matplotlib.dates as mdates

from collections import deque

from data_handling.data_retrieval import get_rand_data
from visualization.settings import colors


class MPLWidget(QFrame):
    frame_width = 3
    data_list_box_size = (100, 20)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = MPLCanvas()
        self.box = QVBoxLayout()
        self.box.addWidget(self.canvas)
        self.setLayout(self.box)

        self.setMinimumSize(400,300)
        self.setFrameStyle(QFrame.Box + QFrame.Raised)
        self.setLineWidth(self.frame_width)

    @property
    def figure(self):
        return self.canvas.fig

    @property
    def axes(self):
        return self.canvas.ax

    @property
    def title(self):
        return self.axes.get_title()

    @title.setter
    def title(self, value):
        self.axes.set_title(value)

    def plot(self, data, color):
        self.canvas.plot(data=data, color=color)

    def multi_plot(self, data):
        self.canvas.multi_plot(data=data)

    def plot_multi_test(self):
        self.canvas.multi_plot(get_rand_data())

    def time_format_xaxis(self, data):
        # todo: write this as a wrapper method
        my_fmt = mdates.DateFormatter('%H:%M:%S')
        self.ax.xaxis.set_major_formatter(my_fmt)


class MPLCanvas(Canvas):
    """
    A matplotlib canvas to be interfaced with
    """
    color_options = {"C0","C1","C2","C3","C4","C5","C6","C7","C8","C9"}

    def __init__(self):
        self.fig = Figure(facecolor=colors["prim"])
        self.ax = self.fig.add_subplot(111, facecolor=colors["prim"])
        self.ax.set_title("LOL a title")
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        self.updateGeometry()

    def plot(self, data, color):
        self.ax.plot(data, color=color)
        self.draw()

    def multi_plot(self, data):
        self.ax.clear()
        # todo: plot all data at once. The plot function is very costly

        # for custom color cycling
        color_deque = deque(self.color_options)

        self.ax.set_title(f"Data({datetime.datetime.now().strftime('%H:%M:%S')})")
        for d in data:
            self.plot(d, color_deque[0])
            color_deque.rotate(1)
