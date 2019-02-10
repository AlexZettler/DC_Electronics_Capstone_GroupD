
from PyQt5.QtWidgets import QSizePolicy, QPushButton, QAction, QTabWidget, QTabBar, QLineEdit, QLabel, QDockWidget, QApplication, QWidget, QFrame

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import custom_logger as cl

import os
import os.path
import datetime
import random
from collections import deque


class TabDock(QTabWidget):
    def __init__(self, parent, colors):
        super().__init__(parent)
        #self.setCornerWidget(None, Qt.TopRightCorner)
        self.setTabsClosable(False)
        self.setTabShape(QTabWidget.Rounded)
        #self.setStyleSheet(f"background-color: {colors['light']}")


class ConfigureTab(QWidget):

    def __init__(self, parent, colors):
        super().__init__(parent)

        text_box = QLineEdit('Drag this', self)
        text_box.setDragEnabled(True)
        text_box.move(10, 10)
        text_box.resize(100, 60)

        label = CustomLabel("Drop here", self)
        label.move(10, 70)
        label.resize(100, 60)


class VisualizeTab(QWidget):

    def __init__(self, parent, colors):
        super().__init__(parent)
        #m = PlotCanvas(self, width=5, height=4, dpi=100, colors=colors)
        #m.move(0,0)

        n = GraphWidget(self,400,300,colors)
        #n.resize(640,480)
        #n.move(20,20)

        #n.graph.move(0,0)

        #Setup button
        btn_regather_data = QPushButton("Reload data!", self)
        #button.setToolTip("I'm a button!")

        btn_regather_data.clicked.connect(n.graph.plot_temperatures)
        #btn_regather_data.clicked.connect(m.plot_temperatures)

        btn_regather_data.setStyleSheet(f"background-color: {colors['light']}")
        btn_regather_data.move(500,0)
        btn_regather_data.resize(140,100)

class GraphWidget(QFrame):
    frame_width = 3
    data_list_box_size = (100, 20)

    def __init__(self, parent, width, height, colors):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box + QFrame.Raised)
        self.setLineWidth(self.frame_width)

        self.graph = PlotCanvas(self,
                                width=width-2*self.frame_width,
                                height=height-2*self.frame_width,
                                dpi=100, colors=colors)

        self.resize(width,height)
        self.graph.move(self.frame_width*2,self.frame_width*2)



    def resize(self, *__args):

        if len(__args) == 2:
            super().resize(*__args)
            self.graph.resize(
                __args[0]-self.data_list_box_size[0]-4*self.frame_width,
                __args[1]-4*self.frame_width)

            #width = width - 2 * self.frame_width, height = height - 2 * self.frame_width, dpi = 100, colors = colors

            #self.data_draggable_box

        else:
            raise ValueError


class PlotCanvas(FigureCanvasQTAgg):

    color_options = {"C0","C1","C2","C3","C4","C5","C6","C7","C8","C9"}

    def __init__(self, parent, width, height, dpi, colors):
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor=colors["prim"])
        self.axes = self.figure.add_subplot(111, facecolor=colors["prim"])
        self.axes.set_title("LOL a title")

        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(
            self,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.updateGeometry()

        #print(self.get_device_types())


    def plot(self, data, color):
        #ax = self.figure.add_subplot(111)
        self.axes.plot(data, color=color)

        self.draw()


    def plot_temperatures(self):
        self.axes.clear()
        data = self.get_rand_data()

        #Custom color cycling
        color_deque = deque(self.color_options)

        self.axes.set_title(f"Data({datetime.datetime.now().strftime('%H:%M:%S')})")
        for d in data:
            self.plot(d, color_deque[0])
            color_deque.rotate(1)

        #print(self.get_devices_from_log_directory("../log"))

    def get_rand_data(self):
        return [[random.random() for i in range(25)]for i in range(5)]


    def get_device_types(self):
        return cl.log_directories.keys()

    def get_device_files_of_type(self, device_type):
        return cl.iget_device_files_from_log_directory(device_type)


        #return {os.path.dirname(i):os.path.abspath(i) for i in glob.iglob(base_path, recursive=False)}


        #for name, path in cl.log_directories.items():
        #    pass


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
