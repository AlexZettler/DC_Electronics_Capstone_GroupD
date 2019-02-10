
from PyQt5.QtWidgets import QSizePolicy, QFrame, QScrollArea, QVBoxLayout


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

import custom_logger as cl

import datetime
import random
from collections import deque

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

        self.setFrameStyle(QFrame.Box + QFrame.Raised)
        self.setLineWidth(self.frame_width)


        #self.canvas.move(self.frame_width * 2, self.frame_width * 2)

    """
    def resize(self, *__args):

        if len(__args) == 2:
            super().resize(*__args)
            self.canvas.resize(
                __args[0]-self.data_list_box_size[0]-4*self.frame_width,
                __args[1]-4*self.frame_width)

            #width = width - 2 * self.frame_width, height = height - 2 * self.frame_width, dpi = 100, colors = colors

            #self.data_draggable_box

        else:
            raise ValueError
    """

class MPLCanvas(Canvas):

    color_options = {"C0","C1","C2","C3","C4","C5","C6","C7","C8","C9"}

    def __init__(self):
        self.fig = Figure(facecolor=colors["prim"])
        self.ax = self.fig.add_subplot(111, facecolor=colors["prim"])
        self.ax.set_title("LOL a title")
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        self.updateGeometry()

    def plot(self, data, color):
        #ax = self.figure.add_subplot(111)
        self.ax.plot(data, color=color)
        self.draw()

    def plot_temperatures(self):
        self.ax.clear()
        data = get_rand_data()

        #Custom color cycling
        color_deque = deque(self.color_options)

        self.ax.set_title(f"Data({datetime.datetime.now().strftime('%H:%M:%S')})")
        for d in data:
            self.plot(d, color_deque[0])
            color_deque.rotate(1)

        #print(self.get_devices_from_log_directory("../log"))


    def get_device_types(self):
        return cl.log_directories.keys()

    def get_device_files_of_type(self, device_type):
        return cl.iget_device_files_from_log_directory(device_type)


def get_rand_data():
    return [[random.random() for i in range(25)]for i in range(5)]